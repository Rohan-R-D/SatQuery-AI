from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseVLMAdapter(ABC):
    """
    Standardized abstract interface for Vision-Language Model adapters.
    Enables plug-and-play swapping between Google Gemini, custom fine-tuned Qwen3-VL,
    GeoChat, and local sovereign RS checkpoints.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if model weights / API endpoints are operational."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the human-readable identifier of the VLM provider."""
        pass

    @abstractmethod
    def generate_vqa(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        """Execute single-image Remote Sensing Visual Question Answering."""
        pass

    @abstractmethod
    def generate_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        """Execute comprehensive remote sensing scene captioning."""
        pass

    @abstractmethod
    def generate_change_explanation(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        overlay_bytes: bytes,
        query: str,
        change_percentage: float
    ) -> Dict[str, Any]:
        """Execute explanatory bi-temporal change reasoning."""
        pass

    @abstractmethod
    def generate_optical_sar(
        self,
        optical_bytes: bytes,
        sar_bytes: bytes,
        query: str
    ) -> Dict[str, Any]:
        """Execute cross-modal joint reasoning over optical and SAR channels."""
        pass

    @abstractmethod
    def locate_regions(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        """Execute text-guided spatial grounding and bounding box localization."""
        pass
