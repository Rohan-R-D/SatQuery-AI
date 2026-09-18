import os
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io
from config import settings

def validate_query(query: str) -> str:
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )
    return query.strip()

def validate_image_file(file: UploadFile, param_name: str = "image") -> None:
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Uploaded file '{param_name}' is missing or invalid."
        )

    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}' for parameter '{param_name}'. Allowed: PNG, JPG, JPEG, TIFF, GeoTIFF."
        )

    # Check file size if available from headers/spool
    if file.size and file.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File '{file.filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

def validate_analysis_request(
    input_type: str,
    image: UploadFile,
    second_image: UploadFile | None,
    query: str
) -> None:
    # 1. Query Validation
    validate_query(query)

    # 2. Input Type Validation
    valid_types = {"single", "bi_temporal", "optical_sar"}
    if input_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input_type '{input_type}'. Allowed values: 'single', 'bi_temporal', 'optical_sar'."
        )

    # 3. Image Count & Presence Validation
    validate_image_file(image, param_name="image")

    if input_type in {"bi_temporal", "optical_sar"}:
        if not second_image or not second_image.filename:
            image_requirement_desc = (
                "Two images (T1 Before and T2 After) are required for bi-temporal analysis."
                if input_type == "bi_temporal"
                else "Two images (Optical and SAR) are required for joint Optical + SAR analysis."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=image_requirement_desc
            )
        validate_image_file(second_image, param_name="second_image")

async def verify_image_readability(file: UploadFile) -> None:
    """Verify that the uploaded file can be opened and parsed as a valid image within pixel safety limits."""
    try:
        content = await file.read()
        file.file.seek(0)  # Reset file pointer after reading
        
        # Attempt to open with PIL and inspect dimensions before full decode
        with Image.open(io.BytesIO(content)) as img:
            width, height = img.size
            if width * height > settings.MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Image dimensions ({width}x{height} = {width * height:,} pixels) exceed maximum allowed limit of {settings.MAX_IMAGE_PIXELS:,} pixels (50 MP)."
                )
            img.verify()
    except Image.DecompressionBombError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds decompression pixel limit: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File '{file.filename}' could not be decoded as a valid image. Detail: {str(e)}"
        )
