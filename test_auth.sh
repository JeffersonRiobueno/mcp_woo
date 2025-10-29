#!/bin/bash
#
# Script para probar la autenticación del servidor MCP WooCommerce.
#
# Este script prueba diferentes escenarios de autenticación:
# 1. Sin API key configurada (desarrollo)
# 2. Con API key configurada (producción)
# 3. Con API key incorrecta (debe fallar)
#

# Configuración
SERVER_URL="http://localhost:8200/mcp"
CONTENT_TYPE="Content-Type: application/json"
ACCEPT="Accept: application/json, text/event-stream"

echo "🔐 Probando Autenticación del Servidor MCP WooCommerce"
echo "Servidor: $SERVER_URL"
echo

# Función para probar una petición
test_request() {
    local description="$1"
    local auth_header="$2"
    local expected_status="$3"

    echo "🧪 $description"

    local headers="$CONTENT_TYPE"
    if [ -n "$auth_header" ]; then
        headers="$headers\n$auth_header"
    fi

    # Hacer petición de inicialización
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$SERVER_URL" \
      -H "$CONTENT_TYPE" \
      -H "$ACCEPT" \
      $([ -n "$auth_header" ] && echo "-H \"$auth_header\"") \
      -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
          "protocolVersion": "2024-11-05",
          "capabilities": {},
          "clientInfo": {"name": "auth-test", "version": "1.0.0"}
        }
      }')

    # Extraer status HTTP
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/HTTP_STATUS:/d')

    if [ "$http_status" = "$expected_status" ]; then
        echo "✅ PASÓ - Status: $http_status"
    else
        echo "❌ FALLÓ - Status esperado: $expected_status, obtenido: $http_status"
    fi

    # Mostrar respuesta si es error
    if [ "$http_status" != "200" ]; then
        echo "   Respuesta: $(echo "$body" | jq -r '.error.message // .detail // "Sin mensaje"' 2>/dev/null || echo "$body")"
    fi

    echo
}

# Prueba 1: Verificar si el servidor está corriendo
echo "🏥 Verificando que el servidor esté corriendo..."
if curl -s --max-time 5 "$SERVER_URL" > /dev/null 2>&1; then
    echo "✅ Servidor responde"
else
    echo "❌ Servidor no responde. Asegúrate de que esté corriendo:"
    echo "   docker compose up"
    exit 1
fi
echo

# Prueba 2: Sin autenticación (debería funcionar si no hay API key)
test_request "Sin autenticación (modo desarrollo)" "" "200"

# Prueba 3: Con API key válida (debería funcionar)
API_KEY="${MCP_API_KEY:-test_key_12345}"
test_request "Con API key válida" "Authorization: Bearer $API_KEY" "200"

# Prueba 4: Con API key inválida (debería fallar si hay autenticación)
test_request "Con API key inválida" "Authorization: Bearer invalid_key_12345" "401"

# Prueba 5: Con formato Bearer incorrecto
test_request "Con formato Bearer incorrecto" "Authorization: Token $API_KEY" "401"

echo "📋 Resumen de pruebas:"
echo "• Sin autenticación: Debería funcionar solo en desarrollo"
echo "• API key válida: Siempre debería funcionar"
echo "• API key inválida: Debería fallar si autenticación está habilitada"
echo
echo "🔧 Para configurar autenticación:"
echo "1. Agrega MCP_API_KEY=tu_clave_secreta al archivo .env"
echo "2. Reinicia el servidor: docker compose restart"
echo "3. Todas las peticiones deben incluir: -H 'Authorization: Bearer TU_CLAVE'"
echo
echo "🛡️  Mejores prácticas de seguridad:"
echo "• Usa claves aleatorias de 32+ caracteres"
echo "• Rota las claves regularmente"
echo "• Usa HTTPS en producción"
echo "• Limita el acceso a redes confiables"