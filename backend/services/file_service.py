import io
import os
import logging
from typing import Dict, Any, Tuple, Optional
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from config import settings

logger = logging.getLogger("satquery.services.file")


class FileService:
    @staticmethod
    async def read_file_bytes(file: UploadFile) -> bytes:
        """Read uploaded file content as raw bytes and reset file offset."""
        content = await file.read()
        await file.seek(0)
        return content

    @staticmethod
    def get_file_metadata(file: UploadFile, size_bytes: int) -> Dict[str, Any]:
        """Extract metadata summary for logging and processing."""
        filename = file.filename or "unknown"
        ext = filename.split(".")[-1].upper() if "." in filename else "UNKNOWN"
        return {
            "filename": filename,
            "format": ext,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
        }

    @staticmethod
    def inspect_image_bytes(image_bytes: bytes) -> Tuple[int, int, str]:
        """Inspect image dimensions and format from raw bytes."""
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            img_format = img.format or "UNKNOWN"
            return width, height, img_format

    @staticmethod
    def validate_file_constraints(file: UploadFile, param_name: str = "image") -> None:
        """Validate filename presence, extension whitelist, and maximum size limits."""
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded file '{param_name}' is missing or invalid."
            )

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}' for parameter '{param_name}'. Allowed: PNG, JPG, JPEG, TIFF, GeoTIFF."
            )

        if file.size and file.size > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
            )


file_service = FileService()
