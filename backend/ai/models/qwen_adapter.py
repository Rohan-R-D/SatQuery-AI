"""
SatQuery AI - Remote Qwen Vision-Language Model Adapter.

Adapter for Qwen3-VL (Qwen/Qwen3-VL-2B-Instruct).
OPERATES AS A REMOTE-ONLY MULTIMODAL PROVIDER via HTTP API endpoint.
No local weights, no local CUDA requirement. Normalizes responses into BaseVLMAdapter interface.
"""

import os
import logging
from typing import Any, Dict, List, Optional

from .base_model import BaseVLMAdapter
from .remote_http_client import RemoteVLMHttpClient
from backend.ai.grounding_interface import (
    BaseGroundingAdapter,
    CoordinateConvention,
    GroundingBox,
    GroundingRequest,
    GroundingResponse,
    validate_grounding_coordinates,
)

logger = logging.getLogger("satquery.ai.models.qwen")


class QwenAdapter(BaseVLMAdapter, BaseGroundingAdapter):
    """
    Remote-only adapter for Qwen3-VL (Qwen/Qwen3-VL-2B-Instruct).
    Communicates via HTTP API endpoints (vLLM / Ollama / OpenAI-compatible servers).
    """

    def __init__(
        self,
        endpoint_url: str = "",
        model_id: str = "",
        api_key: str = "",
        timeout: int = 30
    ):
        self.enabled = os.getenv("SATQUERY_QWEN_ENABLED", "false").lower() in ("true", "1", "yes")
        self.endpoint_url = endpoint_url or os.getenv("SATQUERY_QWEN_ENDPOINT_URL", "")
        self.model_id = model_id or os.getenv("SATQUERY_QWEN_MODEL_ID", "Qwen/Qwen3-VL-2B-Instruct")
        self.api_key = api_key or os.getenv("SATQUERY_QWEN_API_KEY", "")
        
        try:
            self.timeout = int(os.getenv("SATQUERY_QWEN_TIMEOUT", str(timeout)))
        except ValueError:
            self.timeout = 30

        self.model_name = "Qwen3-VL Remote Multimodal VLM (2B)"
        self.enable_grounding = os.getenv("SATQUERY_QWEN_GROUNDING_ENABLED", "false").lower() in ("true", "1", "yes")

    def is_available(self) -> bool:
        """
        Returns True ONLY if Qwen is explicitly enabled AND a remote endpoint URL is configured.
        """
        return bool(self.enabled and self.endpoint_url)

    def get_provider_name(self) -> str:
        return f"{self.model_name} [{self.model_id}]"

    def supports_grounding(self) -> bool:
        """
        Returns True ONLY if model is available AND remote Qwen endpoint grounding is explicitly enabled.
        """
        return bool(self.is_available() and self.enable_grounding)

    # -------------------------------------------------------------------------
    # BaseVLMAdapter Interface Methods
    # -------------------------------------------------------------------------

    def generate_vqa(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        logger.info(f"QwenAdapter: Querying remote endpoint '{self.endpoint_url}' for VQA query '{query}'")

        if not self.is_available():
            return {
                "answer": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "evidence": ["Remote Qwen endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "QWEN_ENDPOINT_UNCONFIGURED",
                "warnings": [
                    "Qwen model is disabled or missing endpoint URL. "
                    "Configure SATQUERY_QWEN_ENABLED=true and SATQUERY_QWEN_ENDPOINT_URL."
                ],
            }

        return RemoteVLMHttpClient.query_openai_multimodal_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=image_bytes,
            prompt=query,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def generate_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        logger.info(f"QwenAdapter: Querying remote captioning for model {self.model_id}")

        if not self.is_available():
            return {
                "caption": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "scene_features": [],
                "evidence": ["Remote Qwen endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "QWEN_ENDPOINT_UNCONFIGURED",
                "warnings": ["Qwen endpoint URL unconfigured."],
            }

        prompt = "Provide a comprehensive, high-resolution remote sensing scene description."
        return RemoteVLMHttpClient.query_openai_multimodal_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=image_bytes,
            prompt=prompt,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def generate_change_explanation(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        overlay_bytes: bytes,
        query: str,
        change_percentage: float
    ) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "answer": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "evidence": ["Remote Qwen endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "QWEN_ENDPOINT_UNCONFIGURED",
                "warnings": ["Qwen endpoint URL unconfigured."],
            }

        prompt = f"Analyze surface changes between observations showing {change_percentage:.1f}% change. {query}"
        return RemoteVLMHttpClient.query_openai_multimodal_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=after_bytes,
            prompt=prompt,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def generate_optical_sar(
        self,
        optical_bytes: bytes,
        sar_bytes: bytes,
        query: str
    ) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "answer": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "built_up_regions": [],
                "water_regions": [],
                "evidence": ["Remote Qwen endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "QWEN_ENDPOINT_UNCONFIGURED",
                "warnings": ["Qwen endpoint URL unconfigured."],
            }

        prompt = f"Perform joint optical and Synthetic Aperture Radar (SAR) cross-modal reasoning. {query}"
        return RemoteVLMHttpClient.query_openai_multimodal_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=optical_bytes,
            prompt=prompt,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def locate_regions(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        req = GroundingRequest(image_bytes=image_bytes, query=query)
        resp = self.locate_grounded_regions(req)
        return {
            "answer": resp.answer,
            "bounding_boxes": [b.model_dump() for b in resp.bounding_boxes],
            "evidence": resp.evidence,
            "confidence": resp.confidence or 0.0,
            "is_error": resp.is_error,
            "error_code": resp.error_code,
            "warnings": resp.warnings,
        }

    # -------------------------------------------------------------------------
    # BaseGroundingAdapter Interface Methods
    # -------------------------------------------------------------------------

    def locate_grounded_regions(self, request: GroundingRequest) -> GroundingResponse:
        """
        Executes remote spatial grounding if remote Qwen endpoint explicitly supports grounding.
        Otherwise returns capability_supported=False without fabricating bounding boxes.
        """
        if not self.is_available():
            return GroundingResponse(
                answer=f"[{self.model_name}]: Remote endpoint unconfigured.",
                bounding_boxes=[],
                source_model=self.model_id,
                provider="qwen",
                capability_supported=False,
                is_error=True,
                error_code="QWEN_ENDPOINT_UNCONFIGURED",
                warnings=["Remote Qwen endpoint URL unconfigured."],
            )

        if not self.supports_grounding():
            return GroundingResponse(
                answer=f"[{self.model_name}]: Spatial grounding capability is not enabled for this Qwen remote endpoint.",
                bounding_boxes=[],
                source_model=self.model_id,
                provider="qwen",
                capability_supported=False,
                is_error=False,
                error_code="GROUNDING_UNSUPPORTED",
                warnings=["Remote Qwen model endpoint does not provide explicit spatial grounding bounding boxes."],
            )

        # Query remote endpoint with explicit grounding request
        res = RemoteVLMHttpClient.query_openai_multimodal_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=request.image_bytes,
            prompt=f"Locate and return bounding boxes for target: {request.query}",
            api_key=self.api_key,
            timeout=self.timeout
        )

        if res.get("is_error"):
            return GroundingResponse(
                answer=res.get("answer", "Remote Qwen grounding query failed."),
                bounding_boxes=[],
                source_model=self.model_id,
                provider="qwen",
                capability_supported=True,
                is_error=True,
                error_code=res.get("error_code"),
                warnings=res.get("warnings", []),
            )

        # Parse raw bounding boxes if returned by remote API
        boxes: List[GroundingBox] = []
        raw_boxes = res.get("bounding_boxes", [])
        for rb in raw_boxes:
            if isinstance(rb, dict) and "box" in rb:
                b_coords = rb["box"]
                is_valid, _ = validate_grounding_coordinates(b_coords, convention=request.coordinate_convention)
                if is_valid:
                    boxes.append(GroundingBox(
                        label=rb.get("label", "target_feature"),
                        box=b_coords,
                        confidence=rb.get("confidence", 0.9)
                    ))

        return GroundingResponse(
            answer=res.get("answer", f"Grounding query completed for '{request.query}'."),
            bounding_boxes=boxes,
            source_model=self.model_id,
            provider="qwen",
            coordinate_convention=request.coordinate_convention,
            capability_supported=True,
            is_error=False,
            warnings=[],
        )


qwen_adapter = QwenAdapter()
