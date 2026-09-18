import os
from pathlib import Path
from typing import List, Set
from dotenv import load_dotenv

# Load environment variables from .env file if available
backend_env_path = Path(__file__).resolve().parent / ".env"
root_env_path = Path(__file__).resolve().parent.parent / ".env"
if backend_env_path.exists():
    load_dotenv(dotenv_path=backend_env_path)
if root_env_path.exists():
    load_dotenv(dotenv_path=root_env_path)


class Settings:
    PROJECT_NAME: str = "SatQuery AI Backend"
    SERVICE_NAME: str = "satquery-backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Host & Server Config
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Security & Authentication
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "https://sat-query-ai-six.vercel.app,http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip() and origin.strip() != "*"
    ]

    # Google Gemini Multimodal Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_FALLBACK_MODELS: List[str] = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-3.5-flash",
        "gemini-flash-latest"
    ]

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_IMAGE_PIXELS: int = int(os.getenv("MAX_IMAGE_PIXELS", "50000000"))
    ALLOWED_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}

    # Rate Limiting Limits
    RATE_LIMIT_ANALYZE_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_ANALYZE_PER_MINUTE", "10"))
    RATE_LIMIT_UPLOAD_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_UPLOAD_PER_MINUTE", "30"))

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parent / 'satquery.db'}")

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    DEMO_DATA_DIR: Path = BASE_DIR.parent / "demo-data"


settings = Settings()
