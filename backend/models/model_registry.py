from schemas import ModelInfo, ModelStatusEnum, ModelListResponse

class ModelRegistry:
    @staticmethod
    def get_registered_models() -> ModelListResponse:
        models = [
            ModelInfo(
                id="gemini-vlm",
                name="Gemini Multimodal VLM",
                type="vision-language",
                status=ModelStatusEnum.AVAILABLE,
                description="Multimodal VLM for satellite visual question answering, captioning, and scene understanding."
            ),
            ModelInfo(
                id="opencv-change",
                name="Prototype Change Detection Engine",
                type="image-processing",
                status=ModelStatusEnum.AVAILABLE,
                description="Bi-temporal image alignment and spectral difference change detection."
            ),
            ModelInfo(
                id="future-rs-vqa",
                name="Remote Sensing VQA Backbone (BigEarthNet / RSVQA)",
                type="remote-sensing-vlm",
                status=ModelStatusEnum.PLANNED,
                description="Fine-tuned remote sensing transformer model trained on RSVQA and CDVQA datasets."
            ),
            ModelInfo(
                id="future-captioning",
                name="Dedicated Satellite Scene Captioner",
                type="remote-sensing-captioning",
                status=ModelStatusEnum.PLANNED,
                description="Specialized remote sensing image captioning model for land-cover classification."
            ),
            ModelInfo(
                id="future-grounding",
                name="Spatial Bounding Region Grounder",
                type="object-detection-grounding",
                status=ModelStatusEnum.PLANNED,
                description="Geospatial bounding box localization engine for object identification."
            ),
            ModelInfo(
                id="future-change-vqa",
                name="Bi-Temporal Change VQA Backbone",
                type="change-vqa",
                status=ModelStatusEnum.PLANNED,
                description="Bi-temporal change reasoning model for explanatory change assessment."
            ),
            ModelInfo(
                id="future-optical-sar",
                name="Optical + SAR Fusion Network",
                type="multimodal-remote-sensing",
                status=ModelStatusEnum.PLANNED,
                description="Deep learning model for Sentinel-1 (SAR) and Sentinel-2 (Optical) joint interpretation."
            ),
        ]
        return ModelListResponse(models=models)

model_registry = ModelRegistry()
