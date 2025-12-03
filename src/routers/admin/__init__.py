"""Admin Mobile API"""

from src.routers.factory import create_sub_app


admin_app = create_sub_app(
    title="Nexus Admin API's",
    description="API for Admin mobile application",
)

# Include routers for each business domain
