import os
import requests
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# WooCommerce API configuration
WOO_URL = os.getenv("WOO_URL", "https://yourstore.com")
WOO_CONSUMER_KEY = os.getenv("WOO_CONSUMER_KEY")
WOO_CONSUMER_SECRET = os.getenv("WOO_CONSUMER_SECRET")

# Authentication configuration
API_KEY = os.getenv("MCP_API_KEY")
if not API_KEY:
    logger.warning("MCP_API_KEY not set - server will run without authentication (NOT RECOMMENDED FOR PRODUCTION)")

# Validate required environment variables
if not WOO_CONSUMER_KEY or not WOO_CONSUMER_SECRET:
    logger.error("WOO_CONSUMER_KEY and WOO_CONSUMER_SECRET must be set in environment variables")
    exit(1)

if WOO_URL == "https://yourstore.com":
    logger.error("WOO_URL must be configured with your actual WooCommerce store URL")
    exit(1)

logger.info(f"Initializing WooCommerce MCP Server for {WOO_URL}")
if API_KEY:
    logger.info("Authentication enabled with API key")
else:
    logger.warning("Running without authentication - use MCP_API_KEY for security")

# Initialize MCP server
mcp = FastMCP("WooCommerce MCP Server")

# Pydantic models for structured output
class Product(BaseModel):
    id: int
    name: str
    price: str
    regular_price: str
    sale_price: str
    stock_status: str
    categories: List[Dict] = Field(default_factory=list)

class Order(BaseModel):
    id: int
    status: str
    total: str
    customer_id: int
    line_items: List[Dict] = Field(default_factory=list)

def get_auth():
    """Get WooCommerce authentication"""
    return (WOO_CONSUMER_KEY, WOO_CONSUMER_SECRET)

def make_request(endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
    """Make authenticated request to WooCommerce API"""
    try:
        url = f"{WOO_URL}/wp-json/wc/v3/{endpoint}"
        auth = get_auth()

        logger.info(f"Making {method} request to {url}")

        if method == "GET":
            response = requests.get(url, auth=auth, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, auth=auth, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        logger.info(f"Request successful, status: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for endpoint {endpoint}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in make_request: {e}")
        raise

@mcp.tool()
def search_products(query: str, per_page: int = 10) -> List[Product]:
    """Search for products by name or SKU"""
    try:
        logger.info(f"Searching products with query: {query}")
        params = {"search": query, "per_page": per_page}
        products = make_request("products", params=params)
        result = [Product(**product) for product in products]
        logger.info(f"Found {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"Error in search_products: {e}")
        return []

@mcp.tool()
def list_products(per_page: int = 20, page: int = 1) -> List[Product]:
    """List all products with pagination"""
    try:
        logger.info(f"Listing products: page {page}, per_page {per_page}")
        params = {"per_page": per_page, "page": page}
        products = make_request("products", params=params)
        result = [Product(**product) for product in products]
        logger.info(f"Retrieved {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"Error in list_products: {e}")
        return []

@mcp.tool()
def create_order(customer_id: int, line_items: List[Dict[str, int]], billing: Dict[str, str], shipping: Optional[Dict[str, str]] = None) -> Order:
    """Create a new order"""
    try:
        logger.info(f"Creating order for customer {customer_id}")
        order_data = {
            "customer_id": customer_id,
            "line_items": [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in line_items],
            "billing": billing,
            "shipping": shipping or billing,
            "set_paid": False
        }
        order = make_request("orders", method="POST", data=order_data)
        result = Order(**order)
        logger.info(f"Order created with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error in create_order: {e}")
        raise

@mcp.tool()
def get_order(order_id: int) -> Order:
    """Retrieve a specific order by ID"""
    try:
        logger.info(f"Retrieving order {order_id}")
        order = make_request(f"orders/{order_id}")
        result = Order(**order)
        logger.info(f"Retrieved order {order_id}")
        return result
    except Exception as e:
        logger.error(f"Error in get_order: {e}")
        raise

@mcp.tool()
def list_orders(customer_id: Optional[int] = None, status: Optional[str] = None, per_page: int = 10) -> List[Order]:
    """List orders with optional filters"""
    try:
        logger.info(f"Listing orders with filters: customer_id={customer_id}, status={status}")
        params = {"per_page": per_page}
        if customer_id:
            params["customer"] = customer_id
        if status:
            params["status"] = status

        orders = make_request("orders", params=params)
        result = [Order(**order) for order in orders]
        logger.info(f"Retrieved {len(result)} orders")
        return result
    except Exception as e:
        logger.error(f"Error in list_orders: {e}")
        return []

def authenticate_request(request: Request) -> bool:
    """Authenticate incoming requests using API key"""
    if not API_KEY:
        # If no API key is configured, allow all requests (for development)
        return True

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False

    # Support both "Bearer <token>" and "API-Key <key>" formats
    if auth_header.startswith("Bearer "):
        provided_key = auth_header[7:]  # Remove "Bearer "
    elif auth_header.startswith("API-Key "):
        provided_key = auth_header[8:]  # Remove "API-Key "
    else:
        provided_key = auth_header

    return provided_key == API_KEY

async def authenticated_mcp_handler(request: Request):
    """Handle MCP requests with authentication"""
    if not authenticate_request(request):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # Get the MCP ASGI app
    mcp_app = mcp.asgi_app()

    # Forward the request to MCP
    return await mcp_app(request.scope, request.receive, request.send)

if __name__ == "__main__":
    if API_KEY:
        # Create FastAPI app with authentication
        app = FastAPI(title="WooCommerce MCP Server", description="Authenticated MCP server for WooCommerce")

        @app.get("/")
        async def root():
            return {"message": "WooCommerce MCP Server", "authenticated": True}

        @app.api_route("/mcp", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        async def mcp_endpoint(request: Request):
            return await authenticated_mcp_handler(request)

        # Run with uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run without authentication (original behavior)
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = 8000
        mcp.run(transport="streamable-http")