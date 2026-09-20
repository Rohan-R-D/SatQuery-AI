from typing import Dict, Any
from .base_model import BaseVLMAdapter
from backend.services.gemini_service import gemini_service


class GeminiAdapter(BaseVLMAdapter):
    """
    Adapter for Google Gemini Multimodal VLM (Temporary Baseline Provider).
    """

    def is_available(self) -> bool:
        return gemini_service.is_available()

    def get_provider_name(self) -> str:
        return "Gemini Multimodal VLM (Baseline)"

    def generate_vqa(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        return gemini_service.analyze_image(image_bytes, query)

    def generate_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        return gemini_service.generate_caption(image_bytes)

    def generate_change_explanation(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        overlay_bytes: bytes,
        query: str,
        change_percentage: float
    ) -> Dict[str, Any]:
        return gemini_service.analyze_change_images(
            before_bytes=before_bytes,
            after_bytes=after_bytes,
            overlay_bytes=overlay_bytes,
            query=query,
            change_percentage=change_percentage
        )

    def generate_optical_sar(
        self,
        optical_bytes: bytes,
        sar_bytes: bytes,
        query: str
    ) -> Dict[str, Any]:
        return gemini_service.analyze_optical_sar(optical_bytes, sar_bytes, query)

    def locate_regions(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        return gemini_service.locate_regions(image_bytes, query)


gemini_adapter = GeminiAdapter()
