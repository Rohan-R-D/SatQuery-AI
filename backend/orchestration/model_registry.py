import logging
from typing import Dict, List, Optional
from backend.schemas.responses import ModelInfo, ModelStatusEnum, ModelListResponse

logger = logging.getLogger("satquery.orchestration.model_registry")

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    "gemini-vlm": ModelInfo(
        id="gemini-vlm",
        name="Gemini Multimodal VLM",
        type="conversational-vlm",
        tasks=["single_image_vqa", "captioning", "grounding", "change_vqa", "optical_sar_fusion"],
        status=ModelStatusEnum.TEMPORARY_BASELINE,
        description="Active multimodal vision-language foundation model for remote sensing visual reasoning, grounding, and multimodal interpretation.",
        version="1.5-flash",
        provider="google-gemini",
        execution_type="cloud_api",
        hardware_req="0 GB (Cloud API)",
        license="Proprietary Commercial API",
        limitations=["Requires external HTTPS internet access", "Accepts 3-channel RGB imagery only"]
    ),
    "qwen2.5-vl-7b": ModelInfo(
        id="qwen2.5-vl-7b",
        name="Qwen2.5-VL-7B-Instruct",
        type="conversational-vlm",
        tasks=["single_image_vqa", "captioning", "grounding", "change_vqa"],
        status=ModelStatusEnum.CANDIDATE,
        description="Lead open-weights multimodal model with native dynamic resolution visual encoder and absolute bounding box coordinate grounding.",
        version="7B-Instruct (2025)",
        provider="qwen",
        execution_type="local_server",
        hardware_req="~16 GB (FP16 est.) / ~7.5-8 GB (4-bit AWQ est.)",
        license="Apache 2.0",
        limitations=["Requires Phase 4 live endpoint validation", "Requires local vLLM / Ollama server"]
    ),
    "qwen3-vl-rs": ModelInfo(
        id="qwen3-vl-rs",
        name="Qwen3-VL Fine-Tuned RS (8B)",
        type="remote-sensing-vlm",
        tasks=["single_image_vqa", "captioning", "change_vqa"],
        status=ModelStatusEnum.CANDIDATE,
        description="High-resolution vision-language model trained for remote sensing scene interpretation and dense multi-target grounding.",
        version="8B Candidate",
        provider="qwen",
        execution_type="local_weights",
        hardware_req="~16 GB (FP16 est.) / ~8 GB (4-bit est.)",
        license="Apache 2.0",
        limitations=["Candidate model checkpoint"]
    ),
    "geochat-7b": ModelInfo(
        id="geochat-7b",
        name="GeoChat Remote Sensing VLM (7B)",
        type="remote-sensing-vlm",
        tasks=["single_image_vqa", "captioning", "grounding"],
        status=ModelStatusEnum.CANDIDATE,
        description="Domain-adapted LLaVA-based model fine-tuned on 318k high-resolution aerial and satellite instruction pairs for remote sensing VQA.",
        version="7B (CVPR 2024)",
        provider="geochat",
        execution_type="local_weights",
        hardware_req="~16 GB (FP16 est.) / ~7 GB (4-bit est.)",
        license="Non-Commercial (Vicuna base)",
        limitations=["Fixed-resolution CLIP vision backbone causes blurring on large rasters", "Non-commercial license"]
    ),
    "bigearthnet-resnet50": ModelInfo(
        id="bigearthnet-resnet50",
        name="BigEarthNet Multi-Label Backbone",
        type="multispectral-classifier",
        tasks=["multi_label_classification", "land_cover_scoring"],
        status=ModelStatusEnum.PLANNED,
        description="Deep ResNet-50 / ViT backbone for quantitative 19-class CORINE land-cover multi-label classification on Sentinel-1/2 rasters.",
        version="ResNet-50 / ViT",
        provider="bigearthnet",
        execution_type="local_weights",
        hardware_req="~2-4 GB (Inference Est.)",
        license="CDLA-Permissive-1.0 (v1.0) / CC BY 4.0 (v2.0 reBEN)",
        limitations=["Non-conversational classifier", "Checkpoint selection pending Phase 2 evaluation"]
    ),
    "changeformer": ModelInfo(
        id="changeformer",
        name="ChangeFormer Bi-Temporal Network",
        type="change-detection",
        tasks=["bi_temporal_change"],
        status=ModelStatusEnum.CANDIDATE,
        description="Siamese Transformer network for deep-learning dense pixel-level bi-temporal change detection on satellite pairs.",
        version="Transformer (2022)",
        provider="changeformer",
        execution_type="local_weights",
        hardware_req="~4-6 GB (Inference Est.)",
        license="Apache 2.0",
        limitations=["Non-conversational model", "Requires pre-aligned bi-temporal input rasters"]
    ),
    "skysense-remoteclip": ModelInfo(
        id="skysense-remoteclip",
        name="RemoteCLIP / SkySense",
        type="embedding-retrieval",
        tasks=["zero_shot_classification", "embedding_retrieval"],
        status=ModelStatusEnum.CANDIDATE,
        description="Contrastive vision-language encoder (CLIP-style) for cross-modal similarity scoring, zero-shot classification, and RS retrieval.",
        version="Base / Large",
        provider="remoteclip",
        execution_type="local_weights",
        hardware_req="~4-8 GB (Inference Est.)",
        license="Apache 2.0 / CC BY-NC",
        limitations=["Embedding scorer only", "Non-generative text output"]
    ),
    "opencv-change": ModelInfo(
        id="opencv-change",
        name="OpenCV Difference Engine",
        type="scientific-component",
        tasks=["bi_temporal_change", "change_vqa"],
        status=ModelStatusEnum.BASELINE,
        description="Deterministic pixel-difference, morphological filtering, and contour region change detection pipeline.",
        version="OpenCV 4.x",
        provider="opencv",
        execution_type="local_weights",
        hardware_req="<1 GB (CPU)",
        license="Apache 2.0",
        limitations=["Pixel-level heuristic engine", "No semantic reasoning"]
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
        from backend.ai.models.geochat_adapter import geochat_adapter
        from backend.ai.models.gemini_adapter import gemini_adapter

        models: List[ModelInfo] = []
        for model in self._models.values():
            # Dynamic operational status update
            if model.id in {"geochat", "geochat-7b"} and geochat_adapter.is_available():
                model.status = ModelStatusEnum.AVAILABLE
            elif model.id == "gemini-vlm" and gemini_adapter.is_available():
                model.status = ModelStatusEnum.TEMPORARY_BASELINE

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
