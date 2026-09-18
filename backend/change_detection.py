"""
Backward compatibility layer for Change Detection Engine.
Change detection algorithms are now encapsulated in `agents/change_agent.py`.
"""
from typing import Dict, Any
from agents.change_agent import change_agent, ChangeAgent


class ChangeDetectionEngine:
    @staticmethod
    def detect_changes(
        before_bytes: bytes,
        after_bytes: bytes,
        threshold_val: int = 35,
        min_region_area: int = 50
    ) -> Dict[str, Any]:
        res = change_agent.compute_opencv_change(
            before_bytes=before_bytes,
            after_bytes=after_bytes,
            threshold_val=threshold_val,
            min_region_area=min_region_area
        )
        res["disclaimer"] = (
            "Scientific Disclaimer: This analysis uses an OpenCV pixel-difference thresholding prototype engine. "
            "It serves as a baseline spatial change pipeline."
        )
        return res


change_detection_engine = ChangeDetectionEngine()

__all__ = [
    "change_detection_engine",
    "ChangeDetectionEngine",
    "change_agent",
    "ChangeAgent"
]
