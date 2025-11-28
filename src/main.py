"""Main FastAPI application - Entry point"""

from fastapi import FastAPI

app = FastAPI(
    title="Nexus Cortex",
    description="NexusT Cortex API's - Clean Architecture with FastAPI",
    version="0.1.0",
)


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy"}
