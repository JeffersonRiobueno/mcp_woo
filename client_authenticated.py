#!/usr/bin/env python3
"""
Cliente MCP autenticado para probar el servidor WooCommerce MCP.

Este cliente demuestra cómo conectarse al servidor MCP con autenticación
usando requests directamente para tener control completo sobre los headers.

Funciona con la arquitectura modular del servidor (src/server.py).
"""

import os
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SERVER_URL = "http://localhost:8200/mcp"
API_KEY = os.getenv("MCP_API_KEY")


class MCPAuthenticatedClient:
    """Cliente MCP con autenticación completa usando requests"""

    def __init__(self, server_url: str, api_key: str = None):
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

    def initialize_session(self) -> bool:
        """Inicializar sesión MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "authenticated-client", "version": "1.0.0"}
            }
        }

        try:
            response = self.session.post(self.server_url, json=payload, timeout=30)

            if response.status_code == 200:
                # Extraer session ID del header
                self.session_id = response.headers.get("Mcp-Session-Id")
                if self.session_id:
                    self.session.headers.update({"Mcp-Session-Id": self.session_id})
                    print(f"✅ Sesión inicializada. Session ID: {self.session_id}")
                    return True
                else:
                    print("❌ Error: No se recibió session ID del servidor")
                    return False

            elif response.status_code == 401:
                print("❌ Error de autenticación: API key inválida o faltante")
                return False
            else:
                print(f"❌ Error HTTP {response.status_code} inicializando sesión")
                print(f"Respuesta: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            return False

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parsear respuesta del servidor MCP (maneja SSE)"""
        if response.status_code != 200:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": response.status_code,
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
            }

        content_type = response.headers.get('content-type', '')
        if 'text/event-stream' in content_type:
            # Parsear respuesta SSE
            text = response.text.strip()
            if not text:
                return {"error": {"message": "Respuesta vacía del servidor"}}

            # Extraer línea de datos
            for line in text.split('\n'):
                if line.startswith('data: '):
                    json_str = line[6:]  # Remover 'data: '
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        return {"error": {"message": f"JSON inválido: {e}"}}
        else:
            # Respuesta JSON directa
            try:
                return response.json()
            except json.JSONDecodeError as e:
                return {"error": {"message": f"JSON inválido: {e}"}}

        return {"error": {"message": "Formato de respuesta desconocido"}}

    def list_tools(self) -> Dict[str, Any]:
        """Listar herramientas disponibles"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
            "params": {}
        }

        response = self.session.post(self.server_url, json=payload)
        return self._parse_response(response)

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a una herramienta"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = self.session.post(self.server_url, json=payload)
        return self._parse_response(response)

    def list_resources(self) -> Dict[str, Any]:
        """Listar recursos disponibles"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "resources/list",
            "params": {}
        }

        response = self.session.post(self.server_url, json=payload)
        return self._parse_response(response)

    def list_prompts(self) -> Dict[str, Any]:
        """Listar prompts disponibles"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "prompts/list",
            "params": {}
        }

        response = self.session.post(self.server_url, json=payload)
        return self._parse_response(response)


def display_products(products: List[Dict[str, Any]], title: str, max_display: int = 5):
    """Mostrar productos de forma legible"""
    if not products:
        print(f"📭 No se encontraron productos en {title}")
        return

    print(f"🛍️  {title} - Total: {len(products)} productos")
    for i, product in enumerate(products[:max_display]):
        name = product.get('name', 'Sin nombre')
        price = product.get('price', 'N/A')
        stock_status = product.get('stock_status', 'N/A')
        print(f"   {i+1}. {name} - ${price} ({stock_status})")

    if len(products) > max_display:
        print(f"   ... y {len(products) - max_display} productos más")


def main():
    """Función principal"""

    print("🔐 Cliente MCP Autenticado para WooCommerce")
    print(f"Servidor: {SERVER_URL}")
    print(f"Arquitectura: Modular (src/server.py)")

    if not API_KEY:
        print("❌ Error: MCP_API_KEY no configurada en variables de entorno")
        print("Agrega MCP_API_KEY=tu_api_key al archivo .env")
        return

    print("🔑 API Key configurada ✓")

    # Crear cliente autenticado
    client = MCPAuthenticatedClient(SERVER_URL, API_KEY)

    # Inicializar sesión
    if not client.initialize_session():
        print("❌ No se pudo inicializar la sesión. Abortando.")
        return

    print("\n🔧 Listando herramientas disponibles...")
    try:
        tools_response = client.list_tools()
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools = tools_response["result"]["tools"]
            print(f"📋 Encontradas {len(tools)} herramientas:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'Sin descripción')}")
        else:
            print(f"❌ Error listando herramientas: {tools_response}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n📁 Listando recursos disponibles...")
    try:
        resources_response = client.list_resources()
        if "result" in resources_response and "resources" in resources_response["result"]:
            resources = resources_response["result"]["resources"]
            print(f"📋 Encontrados {len(resources)} recursos:")
            for resource in resources[:5]:  # Mostrar máximo 5
                print(f"  - {resource.get('uri', 'N/A')}")
        else:
            print(f"❌ Error listando recursos: {resources_response}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🛍️  Probando herramienta 'list_products'...")
    try:
        result = client.call_tool("list_products", {"per_page": 5})
        if "result" in result and not result["result"].get("isError", False):
            print("✅ Llamada exitosa")
            structured_content = result["result"].get("structuredContent", {})
            if isinstance(structured_content, dict) and "result" in structured_content:
                products = structured_content["result"]
                display_products(products, "Productos listados")
            else:
                print("⚠️  Formato de respuesta inesperado")
        else:
            error = result.get("error", {})
            print(f"❌ Error en llamada: {error.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🔍 Probando herramienta 'search_products'...")
    try:
        result = client.call_tool("search_products", {"query": "pulsera", "per_page": 5})
        if "result" in result and not result["result"].get("isError", False):
            print("✅ Búsqueda exitosa")
            structured_content = result["result"].get("structuredContent", {})
            if isinstance(structured_content, dict) and "result" in structured_content:
                products = structured_content["result"]
                display_products(products, "Productos encontrados")
            else:
                print("⚠️  Formato de respuesta inesperado")
        else:
            error = result.get("error", {})
            print(f"❌ Error en búsqueda: {error.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n📊 Probando herramienta 'get_order'...")
    try:
        # Intentar obtener un pedido (usando ID de ejemplo)
        result = client.call_tool("get_order", {"order_id": 1})
        if "result" in result and not result["result"].get("isError", False):
            print("✅ Pedido obtenido exitosamente")
            structured_content = result["result"].get("structuredContent", {})
            if isinstance(structured_content, dict):
                order = structured_content
                print(f"   Pedido ID: {order.get('id', 'N/A')}")
                print(f"   Estado: {order.get('status', 'N/A')}")
                print(f"   Total: ${order.get('total', 'N/A')}")
        else:
            error = result.get("error", {})
            if "not found" in error.get("message", "").lower():
                print("ℹ️  Pedido no encontrado (ID 1 no existe)")
            else:
                print(f"❌ Error obteniendo pedido: {error.get('message', 'Error desconocido')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🎉 Cliente autenticado completado!")
    print("\n💡 Para más funcionalidades, revisa los scripts curl:")
    print("   ./curl_list_products.sh")
    print("   ./curl_search_products.sh pulsera")


if __name__ == "__main__":
    main()