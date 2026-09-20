import logging
from typing import Dict, Any
from ai.adapters.model_adapter import get_active_vlm_adapter

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
        adapter = get_active_vlm_adapter()
        provider_name = adapter.get_provider_name()
        logger.info(f"VQAAgent: executing VQA via {provider_name} for query='{query}'")
        res = adapter.generate_vqa(image_bytes, query)
        return {
            "answer": res.get("answer", ""),
            "evidence": res.get("evidence", []),
            "confidence": res.get("confidence", 85),
            "is_error": res.get("is_error", False),
            "error_code": res.get("error_code"),
            "model_used": provider_name
        }

    def execute_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        """Execute comprehensive scene captioning and land-cover summary."""
        adapter = get_active_vlm_adapter()
        provider_name = adapter.get_provider_name()
        logger.info(f"VQAAgent: executing scene captioning via {provider_name}")
        res = adapter.generate_caption(image_bytes)
        answer_text = res.get("caption", res.get("answer", ""))
        return {
            "answer": answer_text,
            "scene_features": res.get("scene_features", []),
            "evidence": res.get("evidence", []),
            "confidence": res.get("confidence", 90),
            "is_error": res.get("is_error", False),
            "error_code": res.get("error_code"),
            "model_used": provider_name
        }


vqa_agent = VQAAgent()

