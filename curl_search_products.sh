#!/bin/bash
#
# Script curl para buscar productos por nombre en el servidor MCP WooCommerce.
#
# Este script hace peticiones HTTP directas al servidor MCP usando curl
# para buscar productos por nombre o SKU.
#

# Configuración del servidor MCP
SERVER_URL="http://localhost:8200/mcp"
CONTENT_TYPE="Content-Type: application/json"
ACCEPT="Accept: application/json, text/event-stream"
AUTH_HEADER="Authorization: Bearer YOUR_API_KEY_HERE"  # Cambia esto por tu API key real

# Parámetros de búsqueda
SEARCH_QUERY="${1:-pulseras}"  # Usar primer argumento o "pulseras" por defecto
PER_PAGE="${2:-10}"            # Usar segundo argumento o 10 por defecto

echo "🔍 Buscando productos en el servidor MCP WooCommerce"
echo "Servidor: $SERVER_URL"
echo "Búsqueda: '$SEARCH_QUERY'"
echo "Resultados por página: $PER_PAGE"
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

# Paso 2: Llamar a la herramienta search_products
echo "🔎 Buscando productos con query: '$SEARCH_QUERY'..."
SEARCH_RESPONSE=$(curl -s -X POST "$SERVER_URL" \
  -H "$CONTENT_TYPE" \
  -H "$ACCEPT" \
  -H "$AUTH_HEADER" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 2,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"search_products\",
      \"arguments\": {
        \"query\": \"$SEARCH_QUERY\",
        \"per_page\": $PER_PAGE
      }
    }
  }")

echo "📦 Respuesta del servidor:"
echo "$SEARCH_RESPONSE" | jq . 2>/dev/null || echo "$SEARCH_RESPONSE"
echo

# Extraer y mostrar información de productos si la respuesta es exitosa
if echo "$SEARCH_RESPONSE" | grep -q '"result"'; then
    echo "✅ Búsqueda completada!"

    # Intentar extraer productos de structuredContent
    PRODUCTS=$(echo "$SEARCH_RESPONSE" | jq -r '.result.structuredContent // empty' 2>/dev/null)

    if [ -n "$PRODUCTS" ] && [ "$PRODUCTS" != "null" ] && [ "$PRODUCTS" != "[]" ]; then
        echo "🛍️  Productos encontrados:"
        echo "$PRODUCTS" | jq -r '.[] | "• \(.name) - $\(.price) (\(.stock_status))"' 2>/dev/null || echo "Formato de productos no estándar"
        echo
        echo "📊 Total de productos: $(echo "$PRODUCTS" | jq '. | length' 2>/dev/null || echo "N/A")"
    else
        echo "📭 No se encontraron productos con el término '$SEARCH_QUERY'"
        echo "💡 Sugerencias:"
        echo "   • Verifica que la tienda WooCommerce tenga productos"
        echo "   • Revisa las credenciales de API en el archivo .env"
        echo "   • Intenta con otros términos de búsqueda"
    fi
else
    echo "❌ Error en la búsqueda"
fi

# Limpiar archivo temporal
rm -f /tmp/headers.txt

echo
echo "💡 Uso: $0 [término_de_búsqueda] [resultados_por_página]"
echo "   Ejemplo: $0 'anillo' 5"