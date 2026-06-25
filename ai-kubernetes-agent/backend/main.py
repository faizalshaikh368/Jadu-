from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.logger import logger as app_logger
from .api.routes import router

# Create FastAPI app
app = FastAPI(
    title="AI Kubernetes Agent",
    description="AI-powered Kubernetes troubleshooting system",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("AI Kubernetes Agent starting up...")
    logger.info("FastAPI backend initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("AI Kubernetes Agent shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )