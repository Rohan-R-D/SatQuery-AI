import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from config import settings
from api.routes import api_router
from agents.supervisor_agent import supervisor_agent, agent_orchestrator
from orchestration.router import task_router
from orchestration.model_registry import model_registry
from orchestration.execution_manager import execution_manager
from schemas.responses import HealthResponse

# Setup Structured Server Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("satquery.api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic Vision-Language Assistant Backend for Remote-Sensing Analysis"
)

# Enable CORS for local development and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Directory for Demo Datasets if directory exists
demo_data_path = settings.DEMO_DATA_DIR
if demo_data_path.exists():
    app.mount("/demo-data", StaticFiles(directory=str(demo_data_path)), name="demo-data")

# Mount API Routers under /api and also at root level for maximum compatibility
app.include_router(api_router, prefix="/api")
app.include_router(api_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def root_health_check():
    """Root health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# Top-level backward compatible exports
__all__ = [
    "app",
    "supervisor_agent",
    "agent_orchestrator",
    "task_router",
    "model_registry",
    "execution_manager",
    "settings"
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
