import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("satquery.orchestration.workflow_manager")


class WorkflowStepDefinition(BaseModel):
    id: int
    title: str
    description: str
    agent: str


class WorkflowDefinition(BaseModel):
    name: str
    description: str
    steps: List[WorkflowStepDefinition]
    required_agents: List[str]
    required_artifacts: List[str]


WORKFLOWS: Dict[str, WorkflowDefinition] = {
    "single_image_vqa_workflow": WorkflowDefinition(
        name="single_image_vqa_workflow",
        description="Targeted single image visual question answering pipeline.",
        required_agents=["vqa_agent", "response_agent"],
        required_artifacts=["vqa_evidence"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Parse natural language query intent and visual target.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Raster Validation", description="Verify image dimensions, color channels, and format integrity.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Single Image VQA pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select Gemini Multimodal VLM engine.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="VLM Inference", description="Execute vision-language feature extraction and visual question answering.", agent="vqa_agent"),
            WorkflowStepDefinition(id=6, title="Evidence Generation", description="Extract grounded visual observation checklist.", agent="evidence_service"),
            WorkflowStepDefinition(id=7, title="Confidence Evaluation", description="Compute multi-factor empirical confidence score.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Assemble verified analytical response and execution trace.", agent="response_agent"),
        ]
    ),
    "scene_captioning_workflow": WorkflowDefinition(
        name="scene_captioning_workflow",
        description="Comprehensive remote sensing scene captioning and land-cover mapping pipeline.",
        required_agents=["vqa_agent", "response_agent"],
        required_artifacts=["scene_summary", "land_cover_breakdown"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Identify scene description and land-cover extraction request.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Raster Validation", description="Check image resolution and spatial characteristics.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Scene Captioning pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select Gemini Multimodal Scene Understanding engine.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="Scene Caption Inference", description="Generate detailed land-cover and structural summary.", agent="vqa_agent"),
            WorkflowStepDefinition(id=6, title="Evidence Synthesis", description="Extract feature checklist and dominant land classes.", agent="evidence_service"),
            WorkflowStepDefinition(id=7, title="Confidence Evaluation", description="Evaluate descriptive certainty and scene clarity.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Assemble structured scene summary response.", agent="response_agent"),
        ]
    ),
    "spatial_grounding_workflow": WorkflowDefinition(
        name="spatial_grounding_workflow",
        description="Visual grounding and spatial bounding box localization pipeline.",
        required_agents=["grounding_agent", "response_agent"],
        required_artifacts=["bounding_boxes", "region_coordinates"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Parse target expression and bounding box localization requirements.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Raster Validation", description="Validate image resolution and bounding coordinate frame.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Spatial Grounding pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select Grounding Engine and VLM localization.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="Grounding Localization", description="Compute spatial bounding boxes for identified features.", agent="grounding_agent"),
            WorkflowStepDefinition(id=6, title="Evidence Synthesis", description="Assemble bounding box coordinates and region metrics.", agent="evidence_service"),
            WorkflowStepDefinition(id=7, title="Confidence Evaluation", description="Assess spatial detection confidence and box coverage.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Synthesize spatial annotations and response payload.", agent="response_agent"),
        ]
    ),
    "bi_temporal_change_workflow": WorkflowDefinition(
        name="bi_temporal_change_workflow",
        description="Bi-temporal image alignment and quantitative difference mapping pipeline.",
        required_agents=["change_agent", "response_agent"],
        required_artifacts=["difference_map", "change_mask", "change_overlay"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Parse bi-temporal comparison intent.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Temporal Pair Validation", description="Validate T1 (Before) and T2 (After) image integrity and dimension alignment.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Bi-Temporal Change Detection pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select OpenCV Difference Engine.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="Change Computation", description="Execute pixel differencing, morphological noise filtering, and contour analysis.", agent="change_agent"),
            WorkflowStepDefinition(id=6, title="Artifact Generation", description="Generate change mask, difference map, and visual overlay rasters.", agent="change_agent"),
            WorkflowStepDefinition(id=7, title="Confidence Evaluation", description="Evaluate spatial signal strength and contour consistency.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Assemble quantitative change metrics and visual artifacts.", agent="response_agent"),
        ]
    ),
    "bi_temporal_change_vqa_workflow": WorkflowDefinition(
        name="bi_temporal_change_vqa_workflow",
        description="Combined quantitative change detection with multimodal explanatory reasoning pipeline.",
        required_agents=["change_agent", "vqa_agent", "response_agent"],
        required_artifacts=["difference_map", "change_mask", "change_overlay"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Parse explanatory change question and temporal targets.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Temporal Pair Validation", description="Validate T1 (Before) and T2 (After) image integrity and alignment.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Change VQA pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select OpenCV Change Engine + Gemini Multimodal VLM.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="Change Computation", description="Compute quantitative pixel difference and visual overlay.", agent="change_agent"),
            WorkflowStepDefinition(id=6, title="VLM Multimodal Reasoning", description="Interpret 3-image sequence (T1, T2, Change Overlay) for explanatory reasoning.", agent="vqa_agent"),
            WorkflowStepDefinition(id=7, title="Evidence & Confidence Assessment", description="Synthesize change metrics with visual evidence.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Assemble unified quantitative + qualitative response.", agent="response_agent"),
        ]
    ),
    "optical_sar_fusion_workflow": WorkflowDefinition(
        name="optical_sar_fusion_workflow",
        description="Joint Optical spectral reflectance and SAR synthetic aperture radar multimodal analysis.",
        required_agents=["fusion_agent", "response_agent"],
        required_artifacts=["cross_modal_metrics", "dual_sensor_evidence"],
        steps=[
            WorkflowStepDefinition(id=1, title="Query Understanding", description="Parse Optical + SAR cross-modal inquiry.", agent="supervisor_agent"),
            WorkflowStepDefinition(id=2, title="Dual-Sensor Validation", description="Validate Optical (spectral) and SAR (radar backscatter) raster inputs.", agent="file_service"),
            WorkflowStepDefinition(id=3, title="Task Classification", description="Route to Optical-SAR Fusion pipeline.", agent="task_classifier"),
            WorkflowStepDefinition(id=4, title="Model Selection", description="Select Gemini Multimodal VLM + Optical-SAR Engine.", agent="model_registry"),
            WorkflowStepDefinition(id=5, title="Cross-Modal Feature Analysis", description="Analyze optical reflectance and radar backscatter double-bounce scattering.", agent="fusion_agent"),
            WorkflowStepDefinition(id=6, title="Feature Partitioning", description="Extract built-up structures and water body boundaries from radar signatures.", agent="fusion_agent"),
            WorkflowStepDefinition(id=7, title="Confidence Assessment", description="Evaluate cross-sensor consensus and radiometric clarity.", agent="confidence_service"),
            WorkflowStepDefinition(id=8, title="Response Synthesis", description="Synthesize joint multimodal findings and evidence.", agent="response_agent"),
        ]
    ),
}


class WorkflowManager:
    @staticmethod
    def get_workflow(name: str) -> Optional[WorkflowDefinition]:
        return WORKFLOWS.get(name)

    @staticmethod
    def list_workflows() -> List[WorkflowDefinition]:
        return list(WORKFLOWS.values())


workflow_manager = WorkflowManager()
