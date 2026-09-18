import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from schemas.responses import UploadResponse
from services.file_service import file_service

logger = logging.getLogger("satquery.api.upload")
router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...)
):
    """
    Validates and inspects an uploaded remote-sensing raster image.
    """
    logger.info(f"POST /api/upload received file: {file.filename}")
    file_service.validate_file_constraints(file, param_name="file")

    try:
        content = await file_service.read_file_bytes(file)
        width, height, img_format = file_service.inspect_image_bytes(content)

        return UploadResponse(
            success=True,
            filename=file.filename or "unknown",
            size_bytes=len(content),
            format=img_format,
            dimensions=[width, height],
            message=f"Raster successfully validated ({width}x{height} px, {img_format})."
        )
    except Exception as e:
        logger.error(f"Image inspection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file '{file.filename}' could not be decoded as a valid image: {str(e)}"
        )
