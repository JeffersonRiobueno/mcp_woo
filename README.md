# MCP WooCommerce Server

A Model Context Protocol (MCP) server that provides tools to interact with WooCommerce REST API.

## Features

- **Search Products**: Search for products by name or SKU
- **List Products**: Retrieve all products with pagination
- **Create Orders**: Create new orders with line items
- **Get Orders**: Retrieve specific orders by ID
- **List Orders**: List orders with optional filters
- **🔐 Authentication**: API Key-based authentication for secure access

## Setup

1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your WooCommerce API credentials:
   ```bash
   WOO_URL=https://yourstore.com
   WOO_CONSUMER_KEY=your_consumer_key
   WOO_CONSUMER_SECRET=your_consumer_secret
   MCP_API_KEY=your_secure_api_key_here
   ```

3. Get your WooCommerce API credentials:
   - Go to WooCommerce > Settings > Advanced > REST API
   - Create a new key with read/write permissions
   - Copy the Consumer Key and Consumer Secret

4. Generate a secure API key for MCP authentication:
   ```bash
   # Generate a random API key (Linux/Mac)
   openssl rand -hex 32

   # Or use Python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Security

### Authentication

The server implements **API Key authentication** to protect against unauthorized access. When `MCP_API_KEY` is configured, all requests must include the API key in the `Authorization` header.

#### Without Authentication (Development Only)
If `MCP_API_KEY` is not set, the server runs without authentication for development purposes.

#### With Authentication (Production Recommended)
When `MCP_API_KEY` is set, clients must include:
```
Authorization: Bearer YOUR_API_KEY_HERE
```

### Security Best Practices

- **Always set `MCP_API_KEY`** in production environments
- Use strong, randomly generated API keys (32+ characters)
- Rotate API keys regularly
- Use HTTPS in production
- Limit network access to trusted sources only
- Monitor access logs for suspicious activity

## Running Locally

### With Docker Compose

```bash
docker-compose up --build
```

The server will start on `http://localhost:8200/mcp` with modular architecture.

### With Python

```bash
pip install -r requirements.txt
python -m src.server
```

## Architecture

The project uses a modular architecture with the following structure:

- `src/server.py` - FastAPI application with MCP integration and authentication
- `src/tools.py` - MCP tools implementation (5 tools for WooCommerce operations)
- `src/config.py` - Environment configuration and validation
- `src/woo_client.py` - WooCommerce API client wrapper
- `src/models.py` - Pydantic models for structured data
- `test/client_authenticated.py` - Full-featured authenticated MCP client (recommended)
- `test/client_example.py` - Basic MCP client using official libraries (limited auth support)
- `test/list_tools.py` - Simple tool listing script

## Client Compatibility Matrix

| Component | With API Key (Production) | Without API Key (Development) | Notes |
|-----------|---------------------------|-------------------------------|-------|
| **`test/client_authenticated.py`** | ✅ **Fully Supported** | ❌ Requires API key | Recommended client with full auth support |
| **Curl Scripts** (`test/*.sh`) | ✅ **Fully Supported** | ❌ Requires API key | Manual testing with proper auth headers |
| **`test/test_auth.sh`** | ✅ **Fully Supported** | ❌ Requires API key | Authentication validation script |
| **`test/list_tools.py`** | ❌ Limited support¹ | ✅ **Works** | Uses official MCP libraries |
| **`test/client_example.py`** | ❌ Limited support¹ | ✅ **Works** | Uses official MCP libraries |

¹ *Limited support: May fail with authentication errors when API key is required*

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

#### Authenticated Client (Recommended)

```bash
python test/client_authenticated.py
```

This is the **recommended client** for testing. It provides:
- ✅ Full API key authentication support
- ✅ Proper SSE response parsing
- ✅ Complete tool testing (list_products, search_products, etc.)
- ✅ Detailed output with product information
- ✅ Error handling and session management

#### Simple Tool Lister

```bash
python test/list_tools.py
```

This script connects to the MCP server and lists all available tools with their descriptions and parameters.

#### Basic Example Client (Limited)

```bash
python test/client_example.py
```

This client uses official MCP libraries but has limitations:
- ❌ Limited authentication support (may fail with API key auth)
- ❌ May encounter connection errors with authenticated servers
- ✅ Good for understanding MCP protocol structure

### Testing Scripts

The project includes curl scripts for easy testing:

```bash
# Update the AUTH_HEADER in the scripts with your API key
# Then run:
./test/curl_list_products.sh
./test/curl_search_products.sh pulseras
./test/curl_create_order.sh
```

These scripts demonstrate proper authentication and SSE response handling.

### Authentication Testing

```bash
# Run authentication tests
./test/test_auth.sh
```

This script validates that authentication is working correctly by testing different scenarios.