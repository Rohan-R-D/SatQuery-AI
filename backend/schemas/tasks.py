from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskEnum(str, Enum):
    SINGLE_IMAGE_VQA = "single_image_vqa"
    CAPTIONING = "captioning"
    IMAGE_CAPTIONING = "image_captioning"
    GROUNDING = "grounding"
    REGION_GROUNDING = "region_grounding"
    BI_TEMPORAL_CHANGE = "bi_temporal_change"
    CHANGE_VQA = "change_vqa"
    OPTICAL_SAR_FUSION = "optical_sar_fusion"
    OPTICAL_SAR_ANALYSIS = "optical_sar_analysis"


class InputTypeEnum(str, Enum):
    SINGLE = "single"
    BI_TEMPORAL = "bi_temporal"
    OPTICAL_SAR = "optical_sar"


class TaskClassificationResult(BaseModel):
    task: str = Field(description="Normalized task identifier")
    workflow: str = Field(description="Identifier for execution workflow sequence")
    required_agents: List[str] = Field(default_factory=list, description="Specialist agents required for execution")
    required_artifacts: List[str] = Field(default_factory=list, description="Expected visual or data artifacts")
    required_tools: List[str] = Field(default_factory=list, description="Tool names required for execution")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Routing certainty score")
    reason: str = Field(description="Explanation of routing decision")
