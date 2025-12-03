"""Factory for creating FastAPI sub-applications."""

from fastapi import FastAPI

from src.core import settings
from src.utilities.enums import Environment


def create_sub_app(title: str, description: str, version: str = "1.0.0") -> FastAPI:
    """Create a FastAPI sub-application with standard configuration.

    Args:
        title: API title for OpenAPI docs.
        description: API description for OpenAPI docs.
        version: API version string.

    Returns:
        Configured FastAPI application instance.
    """
    is_production = settings.environment == Environment.PRODUCTION

    return FastAPI(
        title=title,
        description=description,
        version=version,
        redirect_slashes=False,
        docs_url=None if is_production else "/",
        redoc_url=None,
        openapi_url=None if is_production else "/openapi.json",
    )
