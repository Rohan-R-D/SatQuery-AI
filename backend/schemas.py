from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class InputTypeEnum(str, Enum):
    SINGLE = "single"
    BI_TEMPORAL = "bi_temporal"
    OPTICAL_SAR = "optical_sar"

class StepStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TraceStep(BaseModel):
    id: int
    title: str
    description: str
    status: StepStatusEnum
    timestamp: Optional[str] = None

class EvidenceItem(BaseModel):
    id: str
    title: str
    description: str
    type: str = Field(description="Evidence type: image, bbox, mask, metrics")
    url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class ModelStatusEnum(str, Enum):
    AVAILABLE = "available"
    PLANNED = "planned"

class ModelInfo(BaseModel):
    id: str
    name: str
    type: str
    status: ModelStatusEnum
    description: Optional[str] = None

class ModelListResponse(BaseModel):
    models: List[ModelInfo]

class AnalysisResponse(BaseModel):
    success: bool
    task: str
    input_type: str
    answer: str
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence score out of 100")
    confidence_explanation: str
    model_used: str
    evidence: List[EvidenceItem] = []
    execution_trace: List[TraceStep] = []
    processing_time: float = Field(description="Processing execution time in seconds")
    change_percentage: Optional[float] = None
    built_up_regions: Optional[List[Dict[str, Any]]] = None
    water_regions: Optional[List[Dict[str, Any]]] = None
    regions: Optional[List[Dict[str, Any]]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None

class HealthResponse(BaseModel):
    status: str
    service: str

class ReportRequest(BaseModel):
    query: str
    input_type: str
    task: str = "satellite_vqa"
    answer: str
    confidence: float
    confidence_explanation: str
    model_used: str
    evidence: List[EvidenceItem] = []
    execution_trace: List[TraceStep] = []
    processing_time: float = 0.0
    change_percentage: Optional[float] = None
    timestamp: Optional[str] = None

