# MCP WooCommerce Server

A Model Context Protocol (MCP) server that provides tools to interact with WooCommerce REST API.

## Features

- **Search Products**: Search for products by name or SKU
- **List Products**: Retrieve all products with pagination
- **Create Orders**: Create new orders with line items
- **Get Orders**: Retrieve specific orders by ID
- **List Orders**: List orders with optional filters

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your WooCommerce API credentials:
   ```
   WOO_URL=https://yourstore.com
   WOO_CONSUMER_KEY=your_consumer_key
   WOO_CONSUMER_SECRET=your_consumer_secret
   ```

3. Get your WooCommerce API credentials:
   - Go to WooCommerce > Settings > Advanced > REST API
   - Create a new key with read/write permissions
   - Copy the Consumer Key and Consumer Secret

## Running Locally

### With Docker Compose

```bash
docker-compose up --build
```

### With Python

```bash
pip install -r requirements.txt
python main.py
```

## API Endpoints

The server exposes the following MCP tools:

- `search_products(query: str, per_page: int = 10)` - Search products
- `list_products(per_page: int = 20, page: int = 1)` - List all products
- `create_order(customer_id: int, line_items: List[Dict], billing: Dict, shipping: Optional[Dict])` - Create order
- `get_order(order_id: int)` - Get specific order
- `list_orders(customer_id: Optional[int], status: Optional[str], per_page: int = 10)` - List orders

## WooCommerce API Requirements

- WooCommerce 3.5+
- WordPress 4.4+
- Pretty permalinks enabled
- REST API enabled (default)

## Testing the MCP Server

### Using the Example Clients

The project includes example MCP clients to test the server:

#### Simple Tool Lister

```bash
python list_tools.py
```

This script connects to the MCP server and lists all available tools with their descriptions and parameters.

#### Complete Example Client

```bash
python client_example.py
```

This comprehensive client demonstrates:
- Connecting to the MCP server
- Listing tools, resources, and prompts
- Calling tools (`list_products` and `search_products`)
- Handling structured responses

### Manual Testing

You can also test the server manually using curl:

```bash
# Initialize session
curl -X POST http://localhost:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}'

# List tools
curl -X POST http://localhost:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
```