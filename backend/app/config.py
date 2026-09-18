"""
SatQuery AI — Application Configuration.

Loads settings from environment variables / .env file using Pydantic BaseSettings.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- App ---
    app_env: str = "development"
    app_debug: bool = True
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://satquery:devpassword@localhost:5432/satquery"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379"

    # --- S3 / MinIO ---
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "satquery-uploads"

    # --- Model Paths ---
    qwen3_vl_model_path: str | None = None
    geochat_model_path: str | None = None
    geobox_model_path: str | None = None
    changeformer_model_path: str | None = None
    grama_model_path: str | None = None

    # --- Upload ---
    max_upload_size_mb: int = 500
    upload_dir: Path = Path("uploads")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
