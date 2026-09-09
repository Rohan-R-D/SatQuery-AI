from fastapi import UploadFile

class FileService:
    @staticmethod
    async def read_file_bytes(file: UploadFile) -> bytes:
        """Read uploaded file content as raw bytes and reset file offset."""
        content = await file.read()
        await file.seek(0)
        return content

    @staticmethod
    def get_file_metadata(file: UploadFile, size_bytes: int) -> dict:
        """Extract metadata summary for logging and processing."""
        filename = file.filename or "unknown"
        ext = filename.split(".")[-1].upper() if "." in filename else "UNKNOWN"
        return {
            "filename": filename,
            "format": ext,
            "size_bytes": size_bytes,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
        }

file_service = FileService()
