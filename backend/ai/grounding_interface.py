"""
SatQuery AI - Provider-Independent Grounding Interface & Schemas.

Establishes the contract, coordinate scaling helpers, and Pydantic schemas for spatial feature
grounding across Vision-Language Models (Gemini, GeoChat, Qwen2.5-VL, etc.) for Phase 4 integration.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class CoordinateConvention(str, Enum):
    """Supported bounding box coordinate conventions."""
    PIXEL = "pixel"                     # Absolute pixel coordinates: [x1, y1, x2, y2]
    NORMALIZED_1000 = "normalized_1000" # Normalized integer range [0, 1000]: [y1, x1, y2, x2] or [x1, y1, x2, y2]
    NORMALIZED_1 = "normalized_1"       # Normalized float range [0.0, 1.0]: [x1, y1, x2, y2]
    GEO_COORDINATE = "geo_coordinate"   # Geographic WGS84: [min_lon, min_lat, max_lon, max_lat]


class GroundingBox(BaseModel):
    """Schema representing a single detected bounding box region."""
    label: str = Field(default="target_feature", description="Entity or feature label")
    box: List[float] = Field(description="Bounding box coordinates [x1, y1, x2, y2]")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Detection confidence [0.0, 1.0]")
    polygon: Optional[List[List[float]]] = Field(default=None, description="Optional polygon vertices [[x, y], ...]")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional feature attributes")


class GroundingRequest(BaseModel):
    """Schema representing a spatial grounding request."""
    image_bytes: bytes = Field(description="Raw image bytes payload")
    query: str = Field(description="Text prompt or feature query to ground")
    image_width: Optional[int] = Field(default=None, ge=1, description="Image width in pixels")
    image_height: Optional[int] = Field(default=None, ge=1, description="Image height in pixels")
    target_labels: Optional[List[str]] = Field(default=None, description="Optional target label list")
    coordinate_convention: CoordinateConvention = Field(
        default=CoordinateConvention.PIXEL,
        description="Target coordinate convention"
    )


class GroundingResponse(BaseModel):
    """Schema representing a standardized spatial grounding response."""
    answer: str = Field(description="Textual explanation of spatial detection results")
    bounding_boxes: List[GroundingBox] = Field(default_factory=list, description="List of detected regions")
    source_model: str = Field(description="Model or adapter used for grounding")
    provider: str = Field(description="Provider identifier")
    coordinate_convention: CoordinateConvention = Field(default=CoordinateConvention.PIXEL)
    image_width: Optional[int] = Field(default=None)
    image_height: Optional[int] = Field(default=None)
    confidence: Optional[float] = Field(default=None)
    evidence: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    is_error: bool = Field(default=False)
    error_code: Optional[str] = Field(default=None)
    capability_supported: bool = Field(default=True, description="Whether the underlying model natively supports grounding")


def validate_grounding_coordinates(
    box: List[float],
    image_width: Optional[int] = None,
    image_height: Optional[int] = None,
    convention: CoordinateConvention = CoordinateConvention.PIXEL
) -> Tuple[bool, List[str]]:
    """
    Validates bounding box coordinates for structural correctness and bounds limits.
    
    Returns (is_valid, list_of_warning_or_error_messages).
    """
    issues = []
    if len(box) != 4:
        return False, [f"Invalid coordinate count: expected 4 values [x1, y1, x2, y2], got {len(box)}."]

    x1, y1, x2, y2 = box

    if convention == CoordinateConvention.PIXEL:
        if x1 < 0 or y1 < 0:
            issues.append(f"Negative pixel coordinates detected: [{x1}, {y1}].")
        if x2 <= x1 or y2 <= y1:
            issues.append(f"Degenerate bounding box: x2 ({x2}) <= x1 ({x1}) or y2 ({y2}) <= y1 ({y1}).")
        if image_width and x2 > image_width:
            issues.append(f"Coordinate x2 ({x2}) exceeds image width ({image_width}).")
        if image_height and y2 > image_height:
            issues.append(f"Coordinate y2 ({y2}) exceeds image height ({image_height}).")

    elif convention == CoordinateConvention.NORMALIZED_1000:
        if any(v < 0 or v > 1000 for v in box):
            issues.append(f"Normalized_1000 coordinates out of range [0, 1000]: {box}.")

    elif convention == CoordinateConvention.NORMALIZED_1:
        if any(v < 0.0 or v > 1.0 for v in box):
            issues.append(f"Normalized_1 coordinates out of range [0.0, 1.0]: {box}.")

    is_valid = len(issues) == 0
    return is_valid, issues


def scale_normalized_coordinates(
    box_1000: List[float], image_width: int, image_height: int
) -> List[float]:
    """
    Scales normalized [0, 1000] integer token coordinates to absolute pixel coordinates [x1, y1, x2, y2].
    """
    if len(box_1000) != 4 or image_width <= 0 or image_height <= 0:
        return box_1000
    y1, x1, y2, x2 = box_1000  # Standard token order (y1, x1, y2, x2)
    px_x1 = round((x1 / 1000.0) * image_width, 1)
    px_y1 = round((y1 / 1000.0) * image_height, 1)
    px_x2 = round((x2 / 1000.0) * image_width, 1)
    px_y2 = round((y2 / 1000.0) * image_height, 1)
    return [px_x1, px_y1, px_x2, px_y2]


class BaseGroundingAdapter(ABC):
    """
    Abstract extension interface for spatial feature grounding engines.
    """

    @abstractmethod
    def supports_grounding(self) -> bool:
        """Returns True if the underlying model natively supports bounding box prediction."""
        pass

    @abstractmethod
    def locate_grounded_regions(self, request: GroundingRequest) -> GroundingResponse:
        """Executes text-guided spatial grounding and returns structured bounding boxes."""
        pass
