#!/usr/bin/env python3
"""
Cliente MCP simple para listar herramientas disponibles.
"""

import asyncio
import sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def list_tools():
    """Lista todas las herramientas disponibles en el servidor MCP."""

    try:
        # URL del servidor MCP (ajusta si es diferente)
        server_url = "http://localhost:8200/mcp"

        print(f"Conectando al servidor MCP en: {server_url}")

        # Conectar al servidor MCP usando transporte streamable HTTP
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Inicializar la sesión MCP
                await session.initialize()
                print("✅ Sesión MCP inicializada correctamente")

                tools_response = await session.list_tools()
                tools = tools_response.tools

                print(f"🔧 Herramientas disponibles ({len(tools)}):")
                print("-" * 50)

                for tool in tools:
                    print(f"📋 {tool.name}")
                    print(f"   Descripción: {tool.description}")

                    if tool.inputSchema and 'properties' in tool.inputSchema:
                        print("   Parámetros:")
                        for param_name, param_info in tool.inputSchema['properties'].items():
                            required = param_name in tool.inputSchema.get('required', [])
                            desc = param_info.get('description', 'Sin descripción')
                            print(f"     - {param_name} ({'requerido' if required else 'opcional'}): {desc}")

                    print()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de que el servidor MCP esté corriendo con: docker compose up")


if __name__ == "__main__":
    asyncio.run(list_tools())