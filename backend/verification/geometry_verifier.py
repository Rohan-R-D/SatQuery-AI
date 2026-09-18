from typing import Tuple, List, Dict, Any, Optional
import numpy as np


class GeometryVerifier:
    """Verifies spatial consistency, bounding box validity, and sub-pixel co-registration RMSE."""

    @staticmethod
    def verify_dimensions(dim1: Tuple[int, int], dim2: Optional[Tuple[int, int]] = None) -> Tuple[bool, Optional[str]]:
        w1, h1 = dim1
        if w1 <= 0 or h1 <= 0:
            return False, f"Invalid primary image dimensions: ({w1}x{h1})."
        if dim2:
            w2, h2 = dim2
            if w2 <= 0 or h2 <= 0:
                return False, f"Invalid secondary image dimensions: ({w2}x{h2})."
            aspect1 = round(w1 / h1, 2)
            aspect2 = round(w2 / h2, 2)
            if abs(aspect1 - aspect2) > 0.15:
                return False, f"Aspect ratio mismatch between paired images: {aspect1} vs {aspect2}."
        return True, None

    @staticmethod
    def verify_bounding_boxes(boxes: List[Dict[str, Any]], image_width: int, image_height: int) -> Tuple[bool, List[str]]:
        warnings = []
        for idx, box in enumerate(boxes, 1):
            x = box.get("x", 0)
            y = box.get("y", 0)
            w = box.get("width", 0)
            h = box.get("height", 0)
            if x < 0 or y < 0:
                warnings.append(f"Box #{idx} has negative coordinates ({x}, {y}).")
            if x + w > image_width * 1.05 or y + h > image_height * 1.05:
                warnings.append(f"Box #{idx} exceeds image boundaries ({x+w} > {image_width} or {y+h} > {image_height}).")
            if w <= 0 or h <= 0:
                warnings.append(f"Box #{idx} has non-positive dimensions ({w}x{h}).")
        return len(warnings) == 0, warnings

    @staticmethod
    def verify_coregistration(rmse: Optional[float]) -> Tuple[bool, Optional[str], float]:
        """Enforces RMSE <= 0.8px threshold. Returns (passed, warning_str, confidence_penalty)."""
        if rmse is None:
            return True, None, 0.0
        if rmse > 0.8:
            penalty = 15.0 if rmse > 2.0 else 10.0
            return False, f"Co-registration RMSE ({rmse:.2f}px) exceeds sub-pixel threshold (0.8px). Potential false-alarm risk.", penalty
        return True, None, 0.0


geometry_verifier = GeometryVerifier()
