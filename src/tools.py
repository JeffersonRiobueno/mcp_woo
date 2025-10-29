from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from .woo_client import make_request
from .models import Product, Order
from .config import logger

mcp = FastMCP("WooCommerce MCP Server")

@mcp.tool()
def list_products(per_page: int = 20, page: int = 1) -> List[Product]:
    """List all products with pagination"""
    try:
        logger.info(f"Listing products: page {page}, per_page {per_page}")
        params = {"per_page": per_page, "page": page}
        products = make_request("products", params=params)
        result = [Product(**p) for p in products]
        logger.info(f"Retrieved {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"Error in list_products: {e}")
        return []

@mcp.tool()
def search_products(query: str, per_page: int = 10) -> List[Product]:
    """Search for products by name or SKU"""
    try:
        logger.info(f"Searching products with query: {query}")
        params = {"search": query, "per_page": per_page}
        products = make_request("products", params=params)
        result = [Product(**p) for p in products]
        logger.info(f"Found {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"Error in search_products: {e}")
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
