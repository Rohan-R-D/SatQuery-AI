import os
import logging
from ai.models.base_model import BaseVLMAdapter
from ai.models.gemini_adapter import gemini_adapter
from ai.models.custom_rs_vlm_adapter import custom_rs_vlm_adapter

logger = logging.getLogger("satquery.ai.adapters")


class ModelAdapterFactory:
    """
    Factory that dynamically resolves the active Vision-Language Model provider.
    Allows 1-line configuration switching between Google Gemini cloud baseline
    and local sovereign fine-tuned checkpoints (Qwen3-VL / GeoChat / BigEarthNet).
    """

    @staticmethod
    def get_active_vlm() -> BaseVLMAdapter:
        provider = os.getenv("ACTIVE_VLM_PROVIDER", "gemini").lower().strip()

        if provider in {"custom", "custom_rs_vlm", "qwen", "qwen3_vl", "geochat", "local"}:
            logger.debug("ModelAdapterFactory: Active VLM provider set to CustomRSVLMAdapter")
            return custom_rs_vlm_adapter

        logger.debug("ModelAdapterFactory: Active VLM provider set to GeminiAdapter")
        return gemini_adapter


model_adapter_factory = ModelAdapterFactory()

def get_active_vlm_adapter() -> BaseVLMAdapter:
    return model_adapter_factory.get_active_vlm()
