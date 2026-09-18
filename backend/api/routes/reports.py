import logging
from fastapi import APIRouter, HTTPException, status, Response
from schemas.responses import ReportRequest
from report import generate_analysis_report

logger = logging.getLogger("satquery.api.reports")
router = APIRouter(tags=["Reports"])


@router.post("/report")
async def create_analysis_report(request_data: ReportRequest):
    """Generates and downloads a formatted Markdown analysis report."""
    logger.info("POST /api/report received request.")
    try:
        report_content, filename = generate_analysis_report(request_data)
        return Response(
            content=report_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        logger.error(f"Error generating analysis report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analysis report."
        )
