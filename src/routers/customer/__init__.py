"""Customer Mobile API"""

from src.routers.factory import create_sub_app


customer_app = create_sub_app(
    title="Nexus Customer API's",
    description="API for Customer mobile application",
)

# Include routers for each business domain
