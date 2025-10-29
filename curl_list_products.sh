#!/bin/bash
#
# Script curl para consultar la lista de productos del servidor MCP WooCommerce.
#
# Este script hace peticiones HTTP directas al servidor MCP usando curl
# para obtener la lista de productos disponibles.
#

# Configuración del servidor MCP
SERVER_URL="http://localhost:8200/mcp"
CONTENT_TYPE="Content-Type: application/json"
ACCEPT="Accept: application/json, text/event-stream"
AUTH_HEADER="Authorization: Bearer your_secure_api_key_here"  # API key configurada en .env

echo "🔍 Consultando lista de productos del servidor MCP WooCommerce"
echo "Servidor: $SERVER_URL"
echo

# Paso 1: Inicializar sesión MCP
echo "📡 Inicializando sesión MCP..."
INIT_RESPONSE=$(curl -s -D /tmp/headers.txt -X POST "$SERVER_URL" \
  -H "$CONTENT_TYPE" \
  -H "$ACCEPT" \
  -H "$AUTH_HEADER" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl-client", "version": "1.0.0"}
    }
  }')

# Extraer el session ID de los headers
SESSION_ID=$(grep -i "mcp-session-id" /tmp/headers.txt | cut -d: -f2 | tr -d ' ' | tr -d '\r')

if [ -z "$SESSION_ID" ]; then
    echo "❌ Error: No se pudo obtener el session ID"
    echo "Headers:"
    cat /tmp/headers.txt
    echo "Respuesta: $INIT_RESPONSE"
    exit 1
fi

echo "✅ Sesión inicializada. Session ID: $SESSION_ID"
echo

# Paso 2: Llamar a la herramienta list_products
echo "🛍️  Obteniendo lista de productos..."
PRODUCTS_RESPONSE=$(curl -s -X POST "$SERVER_URL" \
  -H "$CONTENT_TYPE" \
  -H "$ACCEPT" \
  -H "$AUTH_HEADER" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_products",
      "arguments": {
        "per_page": 10,
        "page": 1
      }
    }
  }')

echo "📦 Respuesta del servidor:"
echo "$PRODUCTS_RESPONSE" | jq . 2>/dev/null || echo "$PRODUCTS_RESPONSE"
echo

# Extraer y mostrar información de productos si la respuesta es exitosa
if echo "$PRODUCTS_RESPONSE" | grep -q '"result"'; then
    echo "✅ Consulta exitosa!"
    # Intentar extraer información de productos de la respuesta
    echo "$PRODUCTS_RESPONSE" | jq -r '.result.content[0].text // .result.structuredContent // empty' 2>/dev/null || echo "Formato de respuesta no estándar"
else
    echo "❌ Error en la consulta"
fi

# Limpiar archivo temporal
rm -f /tmp/headers.txt