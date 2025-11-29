"""Atlas Mobile API"""

from fastapi import FastAPI

from src.core import settings
from src.shared.enums import Environment

# Create atlas FastAPI application
customer_app = FastAPI(
    title="Nexus Customer API's",
    description="API for Customer mobile application",
    version="1.0.0",
    redirect_slashes=False,
    docs_url="/" if settings.environment != Environment.PRODUCTION else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.environment != Environment.PRODUCTION else None,
)

# Include routers for each business domain
