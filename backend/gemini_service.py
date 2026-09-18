"""
Backward compatibility layer for Gemini Service.
Core multimodal service logic is now encapsulated in `services/gemini_service.py`.
"""
from services.gemini_service import (
    gemini_service,
    GeminiService,
    GeminiVQAOutput,
    GeminiOpticalSarOutput,
    GeminiGroundingOutput,
    GeminiCaptionOutput
)

__all__ = [
    "gemini_service",
    "GeminiService",
    "GeminiVQAOutput",
    "GeminiOpticalSarOutput",
    "GeminiGroundingOutput",
    "GeminiCaptionOutput"
]
