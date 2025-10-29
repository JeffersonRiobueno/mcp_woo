# Guía de Prueba del Cliente MCP

Esta guía te ayuda a probar el servidor MCP WooCommerce usando los clientes de ejemplo incluidos.

## Paso 1: Iniciar el Servidor MCP

Primero, asegúrate de que el servidor esté corriendo:

```bash
# En una terminal, inicia el servidor
docker-compose up -d

# Verifica que esté corriendo
docker-compose ps
```

Deberías ver algo como:
```
NAME                COMMAND             SERVICE             STATUS              PORTS
mcp_woo-mcp-woo-1   python main.py      mcp-woo             running             0.0.0.0:8200->8000/tcp
```

## Paso 2: Probar el Cliente Simple

El cliente `list_tools.py` es perfecto para verificar que todo funciona:

```bash
# En otra terminal
python list_tools.py
```

**Salida esperada:**
```
🔧 Herramientas disponibles (5):
--------------------------------------------------
📋 search_products
   Descripción: Search for products by name or SKU
   Parámetros:
     - query (requerido): Query string to search for
     - per_page (opcional): Number of products per page

📋 list_products
   Descripción: List all products with pagination
   Parámetros:
     - per_page (opcional): Number of products per page
     - page (opcional): Page number

📋 create_order
   Descripción: Create a new order
   Parámetros:
     - customer_id (requerido): Customer ID
     - line_items (requerido): List of line items
     - billing (requerido): Billing address
     - shipping (opcional): Shipping address

📋 get_order
   Descripción: Retrieve a specific order by ID
   Parámetros:
     - order_id (requerido): Order ID

📋 list_orders
   Descripción: List orders with optional filters
   Parámetros:
     - customer_id (opcional): Filter by customer ID
     - status (opcional): Filter by order status
     - per_page (opcional): Number of orders per page
```

## Paso 3: Probar el Cliente Completo

El cliente `client_example.py` hace una demostración completa:

```bash
python client_example.py
```

Este cliente:
1. Se conecta al servidor MCP
2. Lista herramientas, recursos y prompts
3. Llama a `list_products` para obtener productos
4. Llama a `search_products` con una búsqueda de prueba

## Paso 4: Probar Manualmente con curl

También puedes probar directamente con curl:

```bash
# 1. Inicializar sesión
curl -X POST http://localhost:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl-test", "version": "1.0.0"}
    }
  }'

# 2. Listar herramientas
curl -X POST http://localhost:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'

# 3. Llamar a una herramienta (ejemplo: listar productos)
curl -X POST http://localhost:8200/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_products",
      "arguments": {"per_page": 5}
    }
  }'
```

## Solución de Problemas

### Error de conexión
- Asegúrate de que el servidor esté corriendo: `docker-compose ps`
- Verifica que el puerto 8200 esté disponible
- Revisa los logs: `docker-compose logs`

### Error de credenciales WooCommerce
- Verifica que las variables en `.env` sean correctas
- Asegúrate de que la tienda WooCommerce tenga la API REST habilitada
- Confirma que las claves de API tengan permisos read/write

### Error de importación en Python
- Instala las dependencias: `pip install -r requirements.txt`
- Usa el entorno virtual: `source .venv/bin/activate`

## Próximos Pasos

Una vez que los clientes de ejemplo funcionen, puedes:

1. **Integrar con Claude Desktop**: Instala el servidor MCP en Claude Desktop
2. **Crear tu propio cliente**: Usa los ejemplos como base para tu aplicación
3. **Agregar más herramientas**: Extiende el servidor con nuevas funcionalidades
4. **Configurar autenticación**: Implementa OAuth si es necesario