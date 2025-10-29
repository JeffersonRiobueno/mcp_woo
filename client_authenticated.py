#!/usr/bin/env python3
"""
Cliente MCP autenticado para probar el servidor WooCommerce MCP.

Este cliente demuestra cómo conectarse al servidor MCP con autenticación
usando requests directamente para tener control completo sobre los headers.
"""

import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SERVER_URL = "http://localhost:8200/mcp"
API_KEY = os.getenv("MCP_API_KEY")

class MCPAuthenticatedClient:
    """Cliente MCP con autenticación completa"""

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

    def initialize_session(self) -> bool:
        """Inicializar sesión MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "authenticated-client", "version": "1.0.0"}
            }
        }

        response = self.session.post(self.server_url, json=payload)

        if response.status_code == 200:
            # Extraer session ID del header
            self.session_id = response.headers.get("Mcp-Session-Id")
            if self.session_id:
                self.session.headers.update({"Mcp-Session-Id": self.session_id})
                print(f"✅ Sesión inicializada. Session ID: {self.session_id}")
                return True

        print(f"❌ Error inicializando sesión: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

    def list_tools(self) -> Dict[str, Any]:
        """Listar herramientas disponibles"""
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        response = self.session.post(self.server_url, json=payload)
        return response.json()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a una herramienta"""
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        response = self.session.post(self.server_url, json=payload)
        return response.json()


def main():
    """Función principal"""

    print("🔐 Cliente MCP Autenticado para WooCommerce")
    print(f"Servidor: {SERVER_URL}")

    if not API_KEY:
        print("❌ Error: MCP_API_KEY no configurada en variables de entorno")
        print("Agrega MCP_API_KEY=tu_api_key al archivo .env")
        return

    print("🔑 API Key configurada ✓")
    # Crear cliente autenticado
    client = MCPAuthenticatedClient(SERVER_URL, API_KEY)

    # Inicializar sesión
    if not client.initialize_session():
        return

    print("\n🔧 Listando herramientas disponibles...")
    try:
        tools_response = client.list_tools()
        if "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print(f"📋 Encontradas {len(tools)} herramientas:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'Sin descripción')}")
        else:
            print(f"❌ Error listando herramientas: {tools_response}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🛍️  Probando herramienta 'list_products'...")
    try:
        result = client.call_tool("list_products", {"per_page": 3})
        if "result" in result:
            print("✅ Llamada exitosa")
            structured_content = result["result"].get("structuredContent", {})
            if isinstance(structured_content, dict) and "result" in structured_content:
                products = structured_content["result"]
                print(f"   Productos encontrados: {len(products)}")
                if products:
                    product = products[0]
                    print(f"   Ejemplo: {product.get('name', 'N/A')} - ${product.get('price', 'N/A')}")
        else:
            print(f"❌ Error en llamada: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🔍 Probando herramienta 'search_products'...")
    try:
        result = client.call_tool("search_products", {"query": "pulsera", "per_page": 2})
        if "result" in result:
            print("✅ Búsqueda exitosa")
            structured_content = result["result"].get("structuredContent", {})
            if isinstance(structured_content, dict) and "result" in structured_content:
                products = structured_content["result"]
                print(f"   Productos encontrados: {len(products)}")
                for product in products[:2]:  # Mostrar máximo 2
                    print(f"   • {product.get('name', 'N/A')} - ${product.get('price', 'N/A')}")
        else:
            print(f"❌ Error en búsqueda: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n🎉 Cliente autenticado completado!")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()