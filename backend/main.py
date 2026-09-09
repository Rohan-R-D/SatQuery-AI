import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from schemas import AnalysisResponse, ModelListResponse, HealthResponse, ReportRequest
from models.model_registry import model_registry
from utils.validation import validate_analysis_request, verify_image_readability
from agent import agent_orchestrator
from report import generate_analysis_report

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

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Directory for Demo Datasets
demo_data_path = Path(__file__).resolve().parent.parent / "demo-data"
if demo_data_path.exists():
    app.mount("/demo-data", StaticFiles(directory=str(demo_data_path)), name="demo-data")


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def get_health():
    """Health check endpoint to verify backend operational status."""
    logger.info("Health check endpoint pinged.")
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME
    )


@app.get("/api/models", response_model=ModelListResponse, tags=["Registry"])
async def list_models():
    """List available and planned model capabilities."""
    logger.info("Model registry query received.")
    return model_registry.get_registered_models()


@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_general(
    image: UploadFile = File(...),
    second_image: Optional[UploadFile] = File(None),
    input_type: str = Form("single"),
    query: str = Form(...)
):
    """Unified analysis endpoint supporting single, bi_temporal, and optical_sar queries."""
    logger.info(f"POST /api/analyze received: input_type='{input_type}'")

    validate_analysis_request(input_type, image, second_image, query)
    await verify_image_readability(image)
    if second_image:
        await verify_image_readability(second_image)

    try:
        response = await agent_orchestrator.run_pipeline(
            input_type=input_type,
            image=image,
            second_image=second_image,
            query=query
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing analysis pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis execution: {str(e)}"
        )


@app.post("/api/analyze/single", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_single(
    image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for Single Image VQA and description."""
    return await analyze_general(
        image=image,
        second_image=None,
        input_type="single",
        query=query
    )


@app.post("/api/analyze/change", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_change(
    image: UploadFile = File(...),
    second_image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for Bi-Temporal change detection (T1 and T2)."""
    return await analyze_general(
        image=image,
        second_image=second_image,
        input_type="bi_temporal",
        query=query
    )


@app.post("/api/analyze/optical-sar", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_optical_sar(
    image: UploadFile = File(...),
    second_image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for joint Optical + SAR multimodal analysis."""
    return await analyze_general(
        image=image,
        second_image=second_image,
        input_type="optical_sar",
        query=query
    )


@app.post("/api/report", tags=["Report"])
async def generate_report(request_data: ReportRequest):
    """Generates and downloads a formatted Markdown analysis report."""
    logger.info("POST /api/report received request.")
    try:
        report_content, filename = generate_analysis_report(request_data)
        return Response(
            content=report_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error generating analysis report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analysis report: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

