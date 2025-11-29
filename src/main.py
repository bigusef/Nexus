"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.events import lifespan
from src.core.middleware import RequestHeadersMiddleware
from src.shared.enums import Environment


settings = get_settings()

# Create main FastAPI application with lifespan
app = FastAPI(
    title="Nexus Cortex",
    description="Nexus Cortex API's - Clean Architecture with FastAPI",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
    docs_url="/" if settings.environment != Environment.PRODUCTION else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.environment != Environment.PRODUCTION else None,
)

# ─── Middleware ────────────────────────────────────────────────────────
# Note: Middleware execution order is bottom-to-top (last added runs first)

# Request headers middleware (validates X-Source header, parses Accept-Language)
app.add_middleware(RequestHeadersMiddleware)

# CORS middleware (must be outermost to handle preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Main Routers ──────────────────────────────────────────────────────
@app.get("/health", include_in_schema=False)
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }
