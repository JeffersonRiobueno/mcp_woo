#!/bin/bash
#
# Script de ejemplo para ingesta de productos desde MCP WooCommerce
# Formato correcto para evitar error 406 Not Acceptable
#

# Configuración
SERVER_URL="http://localhost:8200/mcp"
API_KEY=$(grep MCP_API_KEY .env | cut -d'=' -f2)  # Leer API key del .env

echo "🔄 Iniciando ingesta de productos desde MCP WooCommerce"
echo "Servidor: $SERVER_URL"
echo

# Paso 1: Inicializar sesión MCP
echo "📡 Inicializando sesión MCP..."
INIT_RESPONSE=$(curl -s -D /tmp/mcp_headers.txt -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "ingestion-client", "version": "1.0.0"}
    }
  }')

# Extraer session ID
SESSION_ID=$(grep -i "mcp-session-id" /tmp/mcp_headers.txt | cut -d: -f2 | tr -d ' ' | tr -d '\r')

if [ -z "$SESSION_ID" ]; then
    echo "❌ Error: No se pudo inicializar sesión"
    echo "Respuesta: $INIT_RESPONSE"
    exit 1
fi

echo "✅ Sesión inicializada. Session ID: $SESSION_ID"
echo

# Paso 2: Obtener lista de productos
echo "🛍️  Consultando productos..."
PRODUCTS_RESPONSE=$(curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_products",
      "arguments": {
        "per_page": 50,
        "page": 1
      }
    }
  }')

echo "📦 Respuesta obtenida:"
echo "$PRODUCTS_RESPONSE" | head -c 200
echo "..."
echo

# Paso 3: Procesar respuesta SSE y extraer JSON
echo "🔄 Procesando respuesta SSE..."
if echo "$PRODUCTS_RESPONSE" | grep -q "event: message"; then
    # Extraer JSON de respuesta SSE
    JSON_DATA=$(echo "$PRODUCTS_RESPONSE" | grep "data: " | sed 's/data: //' | head -1)

    if [ -n "$JSON_DATA" ]; then
        echo "✅ Datos JSON extraídos correctamente"
        echo "📊 Procesando productos..."

        # Aquí puedes agregar tu lógica de ingesta
        # Por ejemplo, guardar en base de datos, archivo, etc.

        echo "✅ Ingesta completada exitosamente!"
    else
        echo "❌ Error: No se pudo extraer JSON de respuesta SSE"
    fi
else
    echo "❌ Error: Respuesta no es formato SSE esperado"
fi

# Limpiar
rm -f /tmp/mcp_headers.txt