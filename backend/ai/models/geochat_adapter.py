"""
SatQuery AI - Remote GeoChat Remote Sensing VLM Adapter.

Adapter for GeoChat (MBZUAI/geochat-7B, CVPR 2024).
OPERATES AS A REMOTE-ONLY MULTIMODAL PROVIDER via HTTP API endpoint.
No local weights, no local CUDA requirement. Supports remote VQA, scene captioning,
and spatial region grounding over satellite imagery.
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
    scale_normalized_coordinates,
)

logger = logging.getLogger("satquery.ai.models.geochat")


class GeoChatAdapter(BaseVLMAdapter, BaseGroundingAdapter):
    """
    Remote-only adapter for GeoChat 7B Remote Sensing Vision-Language Model.
    Communicates via remote HTTP API endpoint (vLLM / Triton / REST API server).
    """

    def __init__(
        self,
        endpoint_url: str = "",
        model_id: str = "",
        api_key: str = "",
        timeout: int = 30
    ):
        self.enabled = os.getenv("SATQUERY_GEOCHAT_ENABLED", "false").lower() in ("true", "1", "yes")
        self.endpoint_url = endpoint_url or os.getenv("SATQUERY_GEOCHAT_ENDPOINT_URL", "")
        self.model_id = model_id or os.getenv("SATQUERY_GEOCHAT_MODEL_ID", "MBZUAI/geochat-7B")
        self.api_key = api_key or os.getenv("SATQUERY_GEOCHAT_API_KEY", "")

        try:
            self.timeout = int(os.getenv("SATQUERY_GEOCHAT_TIMEOUT", str(timeout)))
        except ValueError:
            self.timeout = 30

        self.model_name = "GeoChat Remote Sensing VLM (7B)"

    def is_available(self) -> bool:
        """
        Returns True ONLY if GeoChat is explicitly enabled AND a remote endpoint URL is configured.
        """
        return bool(self.enabled and self.endpoint_url)

    def get_provider_name(self) -> str:
        return f"{self.model_name} [{self.model_id}]"

    def supports_grounding(self) -> bool:
        """Returns True if remote model endpoint is available."""
        return self.is_available()

    # -------------------------------------------------------------------------
    # BaseVLMAdapter Interface Methods
    # -------------------------------------------------------------------------

    def generate_vqa(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        logger.info(f"GeoChatAdapter: Querying remote endpoint '{self.endpoint_url}' for VQA '{query}'")

        if not self.is_available():
            return {
                "answer": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "evidence": ["Remote GeoChat endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "GEOCHAT_UNCONFIGURED",
                "warnings": [
                    "GeoChat model is disabled or missing endpoint URL. "
                    "Configure SATQUERY_GEOCHAT_ENABLED=true and SATQUERY_GEOCHAT_ENDPOINT_URL."
                ],
            }

        return RemoteVLMHttpClient.query_rest_vlm_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=image_bytes,
            prompt=query,
            task="vqa",
            api_key=self.api_key,
            timeout=self.timeout
        )

    def generate_caption(self, image_bytes: bytes) -> Dict[str, Any]:
        logger.info(f"GeoChatAdapter: Querying remote captioning for model {self.model_id}")

        if not self.is_available():
            return {
                "caption": f"[{self.model_name}]: Remote endpoint URL not configured in environment.",
                "scene_features": [],
                "evidence": ["Remote GeoChat endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "GEOCHAT_UNCONFIGURED",
                "warnings": ["GeoChat endpoint URL unconfigured."],
            }

        return RemoteVLMHttpClient.query_rest_vlm_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=image_bytes,
            prompt="Describe this remote sensing satellite scene in detail.",
            task="caption",
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
                "evidence": ["Remote GeoChat endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "GEOCHAT_UNCONFIGURED",
                "warnings": ["GeoChat endpoint URL unconfigured."],
            }

        prompt = f"Analyze the bi-temporal satellite image pair showing {change_percentage:.1f}% surface change. {query}"
        return RemoteVLMHttpClient.query_rest_vlm_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=after_bytes,
            prompt=prompt,
            task="change_vqa",
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
                "evidence": ["Remote GeoChat endpoint unconfigured."],
                "confidence": 0.0,
                "is_error": True,
                "error_code": "GEOCHAT_UNCONFIGURED",
                "warnings": ["GeoChat endpoint URL unconfigured."],
            }

        prompt = f"Perform joint optical and Synthetic Aperture Radar (SAR) cross-modal reasoning. {query}"
        return RemoteVLMHttpClient.query_rest_vlm_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=optical_bytes,
            prompt=prompt,
            task="optical_sar",
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
        Executes remote spatial grounding over satellite imagery using GeoChat's region tokenizer.
        """
        if not self.is_available():
            return GroundingResponse(
                answer=f"[{self.model_name}]: Remote endpoint unconfigured.",
                bounding_boxes=[],
                source_model=self.model_id,
                provider="geochat",
                capability_supported=False,
                is_error=True,
                error_code="GEOCHAT_UNCONFIGURED",
                warnings=["GeoChat remote endpoint URL unconfigured."],
            )

        res = RemoteVLMHttpClient.query_rest_vlm_endpoint(
            endpoint_url=self.endpoint_url,
            model_id=self.model_id,
            image_bytes=request.image_bytes,
            prompt=f"Please locate: {request.query}",
            task="grounding",
            api_key=self.api_key,
            timeout=self.timeout
        )

        if res.get("is_error"):
            return GroundingResponse(
                answer=res.get("answer", "Remote GeoChat grounding query failed."),
                bounding_boxes=[],
                source_model=self.model_id,
                provider="geochat",
                capability_supported=True,
                is_error=True,
                error_code=res.get("error_code"),
                warnings=res.get("warnings", []),
            )

        # Parse region tokens [y1, x1, y2, x2] and scale to pixel dimensions if image dimensions provided
        boxes: List[GroundingBox] = []
        raw_boxes = res.get("bounding_boxes", [])
        for rb in raw_boxes:
            if isinstance(rb, dict) and "box" in rb:
                raw_coords = rb["box"]
                # Convert normalized_1000 to pixel if dimensions present
                if len(raw_coords) == 4 and request.image_width and request.image_height:
                    scaled_px = scale_normalized_coordinates(
                        box_1000=raw_coords,
                        image_width=request.image_width,
                        image_height=request.image_height
                    )
                    is_valid, _ = validate_grounding_coordinates(scaled_px, convention=CoordinateConvention.PIXEL)
                    if is_valid:
                        boxes.append(GroundingBox(
                            label=rb.get("label", request.query),
                            box=scaled_px,
                            confidence=rb.get("confidence", 0.92)
                        ))
                else:
                    is_valid, _ = validate_grounding_coordinates(raw_coords, convention=request.coordinate_convention)
                    if is_valid:
                        boxes.append(GroundingBox(
                            label=rb.get("label", request.query),
                            box=raw_coords,
                            confidence=rb.get("confidence", 0.92)
                        ))

        return GroundingResponse(
            answer=res.get("answer", f"Grounding query completed for '{request.query}'."),
            bounding_boxes=boxes,
            source_model=self.model_id,
            provider="geochat",
            coordinate_convention=CoordinateConvention.PIXEL if request.image_width else request.coordinate_convention,
            capability_supported=True,
            is_error=False,
            warnings=[],
        )


geochat_adapter = GeoChatAdapter()
