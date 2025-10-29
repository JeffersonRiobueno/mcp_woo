import contextlib
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uvicorn
from .tools import mcp
from .config import API_KEY, logger

app = FastAPI(title="WooCommerce MCP Server", redirect_slashes=False)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Authenticate all requests when API key is configured
        if API_KEY:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return Response(
                    content='{"error": {"code": -32000, "message": "Missing API key"}}',
                    status_code=401,
                    media_type="application/json"
                )

            # Support Bearer token format
            if auth_header.startswith("Bearer "):
                provided_key = auth_header[7:]
            else:
                provided_key = auth_header

            if provided_key != API_KEY:
                return Response(
                    content='{"error": {"code": -32000, "message": "Invalid API key"}}',
                    status_code=401,
                    media_type="application/json"
                )

        return await call_next(request)

app.add_middleware(AuthMiddleware)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app.router.lifespan_context = lifespan
app.mount("/", mcp.streamable_http_app())

def start_server():
    logger.info("Starting WooCommerce MCP Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server()
