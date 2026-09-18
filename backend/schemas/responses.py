from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from schemas.evidence import EvidenceItem, RegionBoundingBox, AnalysisArtifact
from schemas.execution import TraceStep


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Health status indicator")
    service: str = Field(default="satquery-backend", description="Service identifier name")
    version: Optional[str] = Field(default="0.1.0", description="Service version")


class ModelStatusEnum(str, Enum):
    AVAILABLE = "available"
    BASELINE = "baseline"
    TEMPORARY_BASELINE = "temporary_baseline"
    CANDIDATE = "candidate"
    PLANNED = "planned"


class ModelInfo(BaseModel):
    id: str = Field(description="Unique model identifier")
    name: str = Field(description="Human-readable model name")
    type: str = Field(description="Model category or architecture type")
    tasks: Optional[List[str]] = Field(default=None, description="List of supported task IDs")
    status: ModelStatusEnum = Field(description="Operational readiness status")
    description: Optional[str] = Field(default=None, description="Detailed description of model capabilities")


class ModelListResponse(BaseModel):
    models: List[ModelInfo]


class AnalysisResponse(BaseModel):
    success: bool = Field(description="Whether the analysis completed successfully")
    task: str = Field(description="Identified analysis task")
    input_type: str = Field(description="Input modality type (single, bi_temporal, optical_sar)")
    answer: str = Field(description="Analytical response text")
    confidence: float = Field(ge=0.0, le=100.0, description="Calibrated confidence score out of 100")
    confidence_explanation: str = Field(description="Transparent breakdown and justification of the confidence score")
    model_used: str = Field(description="Primary model or tool pipeline used for inference")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Extracted visual and quantitative evidence")
    execution_trace: List[TraceStep] = Field(default_factory=list, description="Step-by-step agent execution timeline")
    processing_time: float = Field(description="Processing time in seconds")
    change_percentage: Optional[float] = Field(default=None, description="Percentage of detected surface change")
    built_up_regions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Built-up structure regions")
    water_regions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Water body regions")
    regions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detected bounding boxes/regions")
    artifacts: Optional[List[Dict[str, Any]]] = Field(default=None, description="Generated visual artifacts")


class ReportRequest(BaseModel):
    query: str
    input_type: str
    task: str = "satellite_vqa"
    answer: str
    confidence: float
    confidence_explanation: str
    model_used: str
    evidence: List[EvidenceItem] = Field(default_factory=list)
    execution_trace: List[TraceStep] = Field(default_factory=list)
    processing_time: float = 0.0
    change_percentage: Optional[float] = None
    timestamp: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool = True
    filename: str
    size_bytes: int
    format: str
    dimensions: Optional[List[int]] = None
    preview_url: Optional[str] = None
    message: Optional[str] = None
