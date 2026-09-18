import logging
from typing import Dict, Any
from services.gemini_service import gemini_service

logger = logging.getLogger("satquery.agents.vqa")


class VQAAgent:
    """
    Specialist Agent for Single-Image Remote Sensing Visual Question Answering & Scene Captioning.
    """

    def __init__(self):
        self.name = "vqa_agent"
        self.description = "Interprets visual remote-sensing rasters for direct question answering and land-cover description."

    def execute_vqa(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        """Execute visual question answering on a single satellite image."""
        logger.info(f"VQAAgent: executing VQA for query='{query}'")
        res = gemini_service.analyze_image(image_bytes, query)
        return {
            "answer": res.get("answer", ""),
            "evidence": res.get("evidence", []),
            "confidence": res.get("confidence", 85),
            "is_error": res.get("is_error", False),
            "error_code": res.get("error_code"),
            "model_used": "Gemini Multimodal VLM"
        }

    def execute_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        """Execute comprehensive scene captioning and land-cover summary."""
        logger.info("VQAAgent: executing scene captioning")
        res = gemini_service.generate_caption(image_bytes)
        return {
            "answer": res.get("caption", ""),
            "scene_features": res.get("scene_features", []),
            "evidence": res.get("evidence", []),
            "confidence": res.get("confidence", 90),
            "is_error": res.get("is_error", False),
            "error_code": res.get("error_code"),
            "model_used": "Gemini Multimodal VLM"
        }


vqa_agent = VQAAgent()
