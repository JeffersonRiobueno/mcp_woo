#!/usr/bin/env python3
"""
Ejemplo de ingesta de productos desde MCP WooCommerce
Formato correcto para evitar error 406 Not Acceptable
"""

import os
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MCPIngestionClient:
    """Cliente para ingesta de datos desde MCP WooCommerce"""

    def __init__(self, server_url: str, api_key: str):
        self.server_url = server_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        })
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

        self.session_id = None
        self.request_id = 1

    def _next_request_id(self) -> int:
        """Generar ID único para cada request"""
        self.request_id += 1
        return self.request_id - 1

    def _parse_sse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parsear respuesta SSE del servidor MCP"""
        if response.status_code != 200:
            return {
                "error": {
                    "code": response.status_code,
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
            }

        text = response.text.strip()
        if not text:
            return {"error": {"message": "Respuesta vacía del servidor"}}

        # Extraer línea de datos de SSE
        for line in text.split('\n'):
            if line.startswith('data: '):
                json_str = line[6:]  # Remover 'data: '
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    return {"error": {"message": f"JSON inválido: {e}"}}

        return {"error": {"message": "Formato de respuesta desconocido"}}

    def initialize_session(self) -> bool:
        """Inicializar sesión MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ingestion-client", "version": "1.0.0"}
            }
        }

        response = self.session.post(self.server_url, json=payload)

        if response.status_code == 200:
            # Extraer session ID de headers
            session_header = response.headers.get('Mcp-Session-Id')
            if session_header:
                self.session_id = session_header
                self.session.headers.update({"Mcp-Session-Id": self.session_id})
                return True

        return False

    def get_products(self, per_page: int = 50, page: int = 1) -> List[Dict[str, Any]]:
        """Obtener lista de productos"""
        if not self.session_id:
            raise Exception("Sesión no inicializada. Llama a initialize_session() primero.")

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": "list_products",
                "arguments": {
                    "per_page": per_page,
                    "page": page
                }
            }
        }

        response = self.session.post(self.server_url, json=payload)
        result = self._parse_sse_response(response)

        if "error" in result:
            raise Exception(f"Error en la consulta: {result['error']}")

        # Extraer productos de la respuesta estructurada
        if "result" in result and "structuredContent" in result["result"]:
            return result["result"]["structuredContent"].get("result", [])

        return []


def main():
    """Función principal de ingesta"""

    # Configuración
    server_url = "http://localhost:8200/mcp"
    api_key = os.getenv("MCP_API_KEY")

    if not api_key:
        print("❌ Error: MCP_API_KEY no configurada en .env")
        return

    print("🔄 Iniciando ingesta de productos desde MCP WooCommerce")
    print(f"Servidor: {server_url}")
    print()

    try:
        # Crear cliente
        client = MCPIngestionClient(server_url, api_key)

        # Inicializar sesión
        print("📡 Inicializando sesión MCP...")
        if not client.initialize_session():
            print("❌ Error: No se pudo inicializar sesión")
            return

        print(f"✅ Sesión inicializada. Session ID: {client.session_id}")
        print()

        # Obtener productos
        print("🛍️  Consultando productos...")
        products = client.get_products(per_page=50, page=1)

        print(f"📦 Se obtuvieron {len(products)} productos")
        print()

        # Procesar productos (aquí puedes agregar tu lógica de ingesta)
        print("📊 Procesando productos...")

        for i, product in enumerate(products[:5], 1):  # Mostrar primeros 5
            print(f"  {i}. {product.get('name', 'N/A')} - ${product.get('price', 'N/A')} ({product.get('stock_status', 'N/A')})")

        if len(products) > 5:
            print(f"  ... y {len(products) - 5} productos más")

        print()
        print("✅ Ingesta completada exitosamente!")

        # Aquí puedes agregar código para:
        # - Guardar en base de datos
        # - Exportar a CSV/JSON
        # - Procesar datos adicionales
        # - etc.

    except Exception as e:
        print(f"❌ Error durante la ingesta: {e}")


if __name__ == "__main__":
    main()