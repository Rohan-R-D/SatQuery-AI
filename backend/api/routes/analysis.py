import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends

from schemas.responses import AnalysisResponse
from utils.validation import validate_analysis_request, verify_image_readability
from utils.rate_limiter import analyze_rate_limiter
from agents.supervisor_agent import supervisor_agent

logger = logging.getLogger("satquery.api.analysis")
router = APIRouter(tags=["Analysis"], dependencies=[Depends(analyze_rate_limiter)])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_general(
    image: UploadFile = File(...),
    second_image: Optional[UploadFile] = File(None),
    input_type: str = Form("single"),
    query: str = Form(...)
):
    """
    Unified multimodal analysis endpoint supporting single-image, bi-temporal, and optical-SAR workflows.
    """
    logger.info(f"POST /api/analyze received: input_type='{input_type}', query='{query[:60]}...'")

    validate_analysis_request(input_type, image, second_image, query)
    await verify_image_readability(image)
    if second_image:
        await verify_image_readability(second_image)

    try:
        response = await supervisor_agent.run_pipeline(
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


@router.post("/analyze/single", response_model=AnalysisResponse)
async def analyze_single(
    image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for single-image VQA, spatial grounding, and scene captioning."""
    return await analyze_general(
        image=image,
        second_image=None,
        input_type="single",
        query=query
    )


@router.post("/analyze/change", response_model=AnalysisResponse)
async def analyze_change(
    image: UploadFile = File(...),
    second_image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for bi-temporal change detection and temporal reasoning."""
    return await analyze_general(
        image=image,
        second_image=second_image,
        input_type="bi_temporal",
        query=query
    )


@router.post("/analyze/optical-sar", response_model=AnalysisResponse)
async def analyze_optical_sar(
    image: UploadFile = File(...),
    second_image: UploadFile = File(...),
    query: str = Form(...)
):
    """Dedicated endpoint for joint Optical and SAR cross-modal multimodal analysis."""
    return await analyze_general(
        image=image,
        second_image=second_image,
        input_type="optical_sar",
        query=query
    )
