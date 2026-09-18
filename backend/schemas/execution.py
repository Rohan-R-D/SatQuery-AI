from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StepStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class TraceStep(BaseModel):
    id: int = Field(description="Step sequence number")
    title: str = Field(description="Step name or operational phase")
    description: str = Field(description="Detailed description of step action or outcome")
    status: StepStatusEnum = Field(default=StepStatusEnum.PENDING, description="Execution status of step")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp of step completion")


class ExecutionRecord(BaseModel):
    execution_id: str = Field(description="Unique UUID for this analysis execution")
    task: str = Field(description="Task performed")
    status: str = Field(description="Final execution status (e.g. COMPLETED, FAILED)")
    query: str = Field(description="User prompt / query")
    input_type: str = Field(description="Input modality type (single, bi_temporal, optical_sar)")
    started_at: str = Field(description="ISO start timestamp")
    completed_at: Optional[str] = Field(default=None, description="ISO completion timestamp")
    duration_sec: float = Field(default=0.0, description="Total execution duration in seconds")
    trace_steps: List[TraceStep] = Field(default_factory=list, description="List of trace steps")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result payload summary")
