from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class EvidenceTypeEnum(str, Enum):
    IMAGE = "image"
    BBOX = "bbox"
    MASK = "mask"
    METRICS = "metrics"
    GEOJSON = "geojson"


class EvidenceItem(BaseModel):
    source: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    id: str = Field(description="Unique identifier for the evidence point")
    title: str = Field(description="Short human-readable title of the observation")
    description: str = Field(description="Evidence description text")
    type: str = Field(description="Evidence type: image, bbox, mask, metrics, geojson")
    url: Optional[str] = Field(default=None, description="Optional URL or base64 data URI of visual artifact")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Optional key-value quantitative metrics")


class RegionBoundingBox(BaseModel):
    x: int = Field(description="X coordinate of top-left corner in pixels")
    y: int = Field(description="Y coordinate of top-left corner in pixels")
    width: int = Field(description="Width of bounding box in pixels")
    height: int = Field(description="Height of bounding box in pixels")
    area: int = Field(description="Total area of region in pixels")
    label: Optional[str] = Field(default=None, description="Semantic classification label")
    confidence: Optional[float] = Field(default=None, description="Detection confidence score")


class AnalysisArtifact(BaseModel):
    name: str = Field(description="Artifact filename or identifier")
    type: str = Field(description="MIME type of the artifact, e.g. image/png")
    url: str = Field(description="Data URL or relative download link")
    description: Optional[str] = Field(default=None, description="Short description of the artifact")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional spatial or image metadata")
