"""
Backward compatibility re-export layer for schemas.
All core schema models are defined modularly in `schemas/`.
"""
from schemas.tasks import (
    TaskEnum,
    InputTypeEnum,
    TaskClassificationResult,
)
from schemas.evidence import (
    EvidenceTypeEnum,
    EvidenceItem,
    RegionBoundingBox,
    AnalysisArtifact,
)
from schemas.execution import (
    StepStatusEnum,
    TraceStep,
    ExecutionRecord,
)
from schemas.responses import (
    HealthResponse,
    ModelStatusEnum,
    ModelInfo,
    ModelListResponse,
    AnalysisResponse,
    ReportRequest,
    UploadResponse,
)

__all__ = [
    "TaskEnum",
    "InputTypeEnum",
    "TaskClassificationResult",
    "EvidenceTypeEnum",
    "EvidenceItem",
    "RegionBoundingBox",
    "AnalysisArtifact",
    "StepStatusEnum",
    "TraceStep",
    "ExecutionRecord",
    "HealthResponse",
    "ModelStatusEnum",
    "ModelInfo",
    "ModelListResponse",
    "AnalysisResponse",
    "ReportRequest",
    "UploadResponse",
]
