import logging
from typing import Dict, List, Optional
from schemas.responses import ModelInfo, ModelStatusEnum, ModelListResponse

logger = logging.getLogger("satquery.orchestration.model_registry")

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    "gemini-vlm": ModelInfo(
        id="gemini-vlm",
        name="Gemini Multimodal VLM",
        type="vision-language",
        tasks=["single_image_vqa", "captioning", "grounding", "change_vqa", "optical_sar_fusion"],
        status=ModelStatusEnum.TEMPORARY_BASELINE,
        description="Active multimodal vision-language foundation model for remote sensing visual reasoning, grounding, and multimodal interpretation."
    ),
    "opencv-change": ModelInfo(
        id="opencv-change",
        name="OpenCV Difference Engine",
        type="image-processing",
        tasks=["bi_temporal_change", "change_vqa"],
        status=ModelStatusEnum.BASELINE,
        description="Deterministic pixel-difference, morphological filtering, and contour region change detection pipeline."
    ),
    "geochat-rs": ModelInfo(
        id="geochat-rs",
        name="GeoChat Remote Sensing VLM (7B)",
        type="remote-sensing-vlm",
        tasks=["single_image_vqa", "captioning", "grounding"],
        status=ModelStatusEnum.CANDIDATE,
        description="Domain-adapted LLaVA-based model fine-tuned on high-resolution aerial and satellite datasets for remote sensing VQA."
    ),
    "qwen3-vl-rs": ModelInfo(
        id="qwen3-vl-rs",
        name="Qwen3-VL Fine-Tuned RS (8B)",
        type="remote-sensing-vlm",
        tasks=["single_image_vqa", "captioning", "change_vqa"],
        status=ModelStatusEnum.CANDIDATE,
        description="High-resolution vision-language model trained for remote sensing scene interpretation and dense multi-target grounding."
    ),
    "changeformer": ModelInfo(
        id="changeformer",
        name="ChangeFormer Bi-Temporal Network",
        type="change-detection",
        tasks=["bi_temporal_change"],
        status=ModelStatusEnum.CANDIDATE,
        description="Siamese Transformer network for deep-learning dense pixel-level bi-temporal change detection on satellite pairs."
    ),
    "grama-fusion": ModelInfo(
        id="grama-fusion",
        name="GRAMA Optical + SAR Cross-Modal Fusion",
        type="multimodal-fusion",
        tasks=["optical_sar_fusion"],
        status=ModelStatusEnum.CANDIDATE,
        description="Cross-attention transformer network for joint Sentinel-1 SAR and Sentinel-2 Optical deep feature fusion."
    ),
    "geobox-grounding": ModelInfo(
        id="geobox-grounding",
        name="GeoBox Spatial Bounding Grounder",
        type="spatial-grounding",
        tasks=["grounding"],
        status=ModelStatusEnum.PLANNED,
        description="Precision geospatial bounding box coordinate extractor with sub-meter spatial localization."
    ),
}


class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelInfo] = dict(MODEL_REGISTRY)

    def get_registered_models(
        self,
        task: Optional[str] = None,
        status_filter: Optional[ModelStatusEnum] = None
    ) -> ModelListResponse:
        """Return list of models matching optional filters."""
        models: List[ModelInfo] = []
        for model in self._models.values():
            if task and model.tasks and task not in model.tasks:
                continue
            if status_filter and model.status != status_filter:
                continue
            models.append(model)
        return ModelListResponse(models=models)

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Fetch model by ID."""
        return self._models.get(model_id)

    def register_model(self, model_info: ModelInfo) -> None:
        """Register or update a model capability."""
        self._models[model_info.id] = model_info
        logger.info(f"Registered model capability: {model_info.id} ({model_info.status})")


model_registry = ModelRegistry()
