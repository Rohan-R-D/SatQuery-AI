import logging
from typing import Any, Dict, Optional
from ai.vqa_inference import run_caption_inference, run_vqa_inference

logger = logging.getLogger("satquery.agents.vqa")


class VQAAgent:
    """
    Specialist Agent for Single-Image Remote Sensing Visual Question Answering & Scene Captioning.
    """

    def __init__(self):
        self.name = "vqa_agent"
        self.description = "Interprets visual remote-sensing rasters for direct question answering and land-cover description."

    def execute_vqa(
        self,
        image_bytes: bytes,
        query: str,
        scientific_evidence: Optional[Any] = None,
        provider_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute visual question answering on a single satellite image."""
        logger.info(f"VQAAgent: executing VQA for query='{query}'")
        return run_vqa_inference(
            image_bytes=image_bytes,
            query=query,
            scientific_evidence=scientific_evidence,
            provider_override=provider_override
        )

    def execute_caption(
        self,
        image_bytes: bytes,
        scientific_evidence: Optional[Any] = None,
        provider_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute comprehensive scene captioning and land-cover summary."""
        logger.info("VQAAgent: executing scene captioning")
        return run_caption_inference(
            image_bytes=image_bytes,
            scientific_evidence=scientific_evidence,
            provider_override=provider_override
        )


vqa_agent = VQAAgent()
