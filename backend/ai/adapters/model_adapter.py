"""
SatQuery AI - Dynamic Model Adapter Factory.

Dynamically resolves the active Vision-Language Model provider adapter based on environment variable
ACTIVE_VLM_PROVIDER (defaulting to Gemini cloud baseline) or explicit runtime provider overrides.
"""

import os
import logging
from ..models.base_model import BaseVLMAdapter
from ..models.gemini_adapter import gemini_adapter
from ..models.custom_rs_vlm_adapter import custom_rs_vlm_adapter
from ..models.geochat_adapter import geochat_adapter
from ..models.qwen_adapter import qwen_adapter

logger = logging.getLogger("satquery.ai.adapters")


class ModelAdapterFactory:
    """
    Factory that dynamically resolves the active Vision-Language Model provider.
    Allows 1-line configuration switching between Google Gemini cloud baseline,
    GeoChat 7B RS-VLM, Qwen3-VL 2B Multimodal VLM, and local sovereign fine-tuned checkpoints.
    """

    @staticmethod
    def get_active_vlm() -> BaseVLMAdapter:
        provider = os.getenv("ACTIVE_VLM_PROVIDER", "gemini").lower().strip()

        if provider in {"geochat", "geochat-7b", "geochat_7b"}:
            logger.debug("ModelAdapterFactory: Active VLM provider set to GeoChatAdapter")
            return geochat_adapter

        if provider in {"qwen", "qwen-vl", "qwen3-vl", "qwen3_vl_2b"}:
            logger.debug("ModelAdapterFactory: Active VLM provider set to QwenAdapter")
            return qwen_adapter

        if provider in {"custom", "custom_rs_vlm", "local"}:
            logger.debug("ModelAdapterFactory: Active VLM provider set to CustomRSVLMAdapter")
            return custom_rs_vlm_adapter

        logger.debug("ModelAdapterFactory: Active VLM provider set to GeminiAdapter (Baseline)")
        return gemini_adapter


model_adapter_factory = ModelAdapterFactory()


def get_active_vlm_adapter() -> BaseVLMAdapter:
    return model_adapter_factory.get_active_vlm()
