import io
import base64
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image

from ai.adapters.model_adapter import get_active_vlm_adapter

logger = logging.getLogger("satquery.agents.grounding")


class GroundingAgent:
    """
    Specialist Agent for Remote Sensing Spatial Grounding, Feature Localization, and Bounding Box Extraction.
    """

    def __init__(self):
        self.name = "grounding_agent"
        self.description = "Identifies, localizes, and extracts pixel bounding coordinates for geographic features."

    def _draw_grounding_overlay(self, image_bytes: bytes, boxes: List[Dict[str, Any]]) -> str:
        """Draw bounding boxes on image and return base64 PNG."""
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            h, w = cv_img.shape[:2]

            for box in boxes:
                bx = max(0, min(w, int(box.get("x", 0))))
                by = max(0, min(h, int(box.get("y", 0))))
                bw = max(1, min(w - bx, int(box.get("width", 50))))
                bh = max(1, min(h - by, int(box.get("height", 50))))
                label = box.get("label", "target")

                # Draw rectangle
                cv2.rectangle(cv_img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
                # Draw label background
                cv2.rectangle(cv_img, (bx, max(0, by - 20)), (bx + bw, by), (0, 255, 0), cv2.FILLED)
                cv2.putText(cv_img, label, (bx + 2, max(12, by - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

            success, buffer = cv2.imencode(".png", cv_img)
            if success:
                b64_str = base64.b64encode(buffer).decode("utf-8")
                return f"data:image/png;base64,{b64_str}"
        except Exception as e:
            logger.warning(f"Failed to generate grounding overlay: {e}")
        return ""

    def execute_grounding(self, image_bytes: bytes, query: str) -> Dict[str, Any]:
        """Execute visual grounding and region localization."""
        adapter = get_active_vlm_adapter()
        provider_name = adapter.get_provider_name()
        logger.info(f"GroundingAgent: executing spatial localization via {provider_name} for query='{query}'")
        res = adapter.locate_regions(image_bytes, query)

        boxes = res.get("bounding_boxes", [])
        artifacts = []
        if boxes:
            overlay_url = self._draw_grounding_overlay(image_bytes, boxes)
            if overlay_url:
                artifacts.append({
                    "name": "grounding_overlay",
                    "type": "image/png",
                    "url": overlay_url,
                    "description": f"Spatial grounding bounding boxes for '{query}'"
                })

        return {
            "answer": res.get("answer", f"Spatial localization completed for: '{query}'."),
            "regions": boxes,
            "evidence": res.get("evidence", []),
            "confidence": res.get("confidence", 85),
            "artifacts": artifacts,
            "is_error": res.get("is_error", False),
            "error_code": res.get("error_code"),
            "model_used": f"{provider_name} + Grounding Engine"
        }



grounding_agent = GroundingAgent()
