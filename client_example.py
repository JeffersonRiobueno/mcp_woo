#!/usr/bin/env python3
"""
Ejemplo de cliente MCP para probar el servidor WooCommerce MCP.

Este cliente se conecta al servidor MCP corriendo en localhost:8200
y demuestra cómo listar herramientas y usar algunas de ellas.
"""

import asyncio
import os
import requests
from typing import Dict, Any
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Authentication
API_KEY = os.getenv("MCP_API_KEY")


class AuthenticatedStreamableHTTPClient:
    """Wrapper para streamablehttp_client con autenticación"""

    def __init__(self, url: str, api_key: str = None):
        self.url = url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    async def __aenter__(self):
        # Usar el cliente original pero con sesión autenticada
        # Nota: Esta es una simplificación. En producción necesitarías
        # modificar el streamablehttp_client para aceptar headers
        return streamablehttp_client(self.url)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def main():
    """Función principal del cliente MCP."""

    # URL del servidor MCP (ajusta si es diferente)
    server_url = "http://localhost:8200/mcp"

    print(f"Conectando al servidor MCP en: {server_url}")
    if API_KEY:
        print("🔐 Usando autenticación con API key")
    else:
        print("⚠️  Sin autenticación configurada")

    try:
        # Conectar al servidor MCP usando transporte streamable HTTP
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Si hay API key, agregar header de autorización
                if API_KEY:
                    # Nota: El cliente streamablehttp_client no soporta headers fácilmente
                    # Para producción, necesitarías un cliente personalizado
                    print("⚠️  Advertencia: El cliente actual no soporta autenticación completa")
                    print("   Usa los scripts curl con --header 'Authorization: Bearer YOUR_KEY'")

                # Inicializar la sesión MCP
                await session.initialize()
                print("✅ Sesión MCP inicializada correctamente")

                # Listar herramientas disponibles
                print("\n🔧 Listando herramientas disponibles...")
                tools_response = await session.list_tools()
                tools = tools_response.tools

                print(f"📋 Encontradas {len(tools)} herramientas:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Listar recursos disponibles
                print("\n📁 Listando recursos disponibles...")
                resources_response = await session.list_resources()
                resources = resources_response.resources

                print(f"📋 Encontrados {len(resources)} recursos:")
                for resource in resources:
                    print(f"  - {resource.uri}")

                # Listar prompts disponibles
                print("\n💬 Listando prompts disponibles...")
                prompts_response = await session.list_prompts()
                prompts = prompts_response.prompts

                print(f"📋 Encontrados {len(prompts)} prompts:")
                for prompt in prompts:
                    print(f"  - {prompt.name}: {prompt.description}")

                # Ejemplo: Llamar a la herramienta list_products
                print("\n🛍️  Probando herramienta 'list_products'...")
                try:
                    result = await session.call_tool("list_products", arguments={"per_page": 5})
                    print("✅ Resultado de list_products:")
                    print(f"   Tipo de contenido: {result.content[0].type if result.content else 'Sin contenido'}")
                    if result.structuredContent:
                        products = result.structuredContent
                        print(f"   Productos encontrados: {len(products) if isinstance(products, list) else 'N/A'}")
                        if isinstance(products, list) and products:
                            print(f"   Primer producto: {products[0].get('name', 'N/A')}")
                except Exception as e:
                    print(f"❌ Error al llamar list_products: {e}")

                # Ejemplo: Llamar a la herramienta search_products
                print("\n🔍 Probando herramienta 'search_products'...")
                try:
                    result = await session.call_tool("search_products", arguments={"query": "test", "per_page": 3})
                    print("✅ Resultado de search_products:")
                    if result.structuredContent:
                        products = result.structuredContent
                        print(f"   Productos encontrados: {len(products) if isinstance(products, list) else 'N/A'}")
                except Exception as e:
                    print(f"❌ Error al llamar search_products: {e}")

                print("\n🎉 Cliente MCP completado exitosamente!")

    except Exception as e:
        print(f"❌ Error conectando al servidor MCP: {e}")
        print("Asegúrate de que el servidor esté corriendo con: docker compose up")


if __name__ == "__main__":
    asyncio.run(main())