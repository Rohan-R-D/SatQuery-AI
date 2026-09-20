"""
SatQuery AI - Multimodel VQA and Image Captioning Inference Engine.

Provides standardized, modular inference functions for single-image VQA,
scene captioning, evidence integration, and structured output normalization.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from backend.ai.adapters.model_adapter import ModelAdapterFactory, get_active_vlm_adapter
from backend.ai.evidence_interface import ScientificEvidence, format_evidence_for_prompt
from backend.ai.models.base_model import BaseVLMAdapter
from backend.ai.prompts import (
    EVIDENCE_AWARE_VQA_PROMPT,
    GENERAL_VQA_PROMPT,
    REMOTE_SENSING_VQA_PROMPT,
    SCENE_CAPTIONING_PROMPT,
)

logger = logging.getLogger("satquery.ai.inference")


def normalize_vqa_response(
    raw_response: Dict[str, Any],
    provider: str,
    model: str = "",
    model_version: str = "",
    warnings: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Normalizes any raw adapter dictionary response into the standardized VQA structure.
    
    Standard Payload Schema:
    {
        "answer": str,
        "model": str,
        "model_version": str,
        "provider": str,
        "confidence": Optional[float],
        "evidence": List[Any],
        "warnings": List[str],
        "is_error": bool,
        "error_code": Optional[str]
    }
    """
    warn_list = warnings if warnings is not None else []
    raw_warnings = raw_response.get("warnings", [])
    if isinstance(raw_warnings, list):
        warn_list.extend(raw_warnings)

    answer_str = raw_response.get("answer", raw_response.get("caption", ""))
    evidence_list = raw_response.get("evidence", [])
    if not isinstance(evidence_list, list):
        evidence_list = [str(evidence_list)]

    is_err = raw_response.get("is_error", False)
    err_code = raw_response.get("error_code")

    if not answer_str and not is_err:
        is_err = True
        err_code = "MALFORMED_MODEL_RESPONSE"
        answer_str = f"[{provider}]: Model returned an empty response."

    conf = raw_response.get("confidence")
    if conf is not None:
        try:
            conf = float(conf)
        except (ValueError, TypeError):
            conf = None

    return {
        "answer": answer_str,
        "model": model or provider,
        "model_version": model_version or "default",
        "provider": provider,
        "confidence": conf,
        "evidence": evidence_list,
        "warnings": warn_list,
        "is_error": is_err,
        "error_code": err_code,
        "model_used": provider,  # Backward compatibility key for existing agents
    }


def resolve_adapter(provider_override: Optional[str] = None) -> BaseVLMAdapter:
    """
    Resolves the VLM adapter instance (either active environment default or explicit override).
    """
    if provider_override:
        provider_key = provider_override.lower().strip()
        if provider_key in {"gemini", "gemini-vlm"}:
            from backend.ai.models.gemini_adapter import gemini_adapter
            return gemini_adapter
        elif provider_key in {"custom", "custom_rs_vlm", "qwen", "geochat", "local"}:
            from backend.ai.models.custom_rs_vlm_adapter import custom_rs_vlm_adapter
            return custom_rs_vlm_adapter

    return get_active_vlm_adapter()


def run_vqa_inference(
    image_bytes: bytes,
    query: str,
    scientific_evidence: Optional[Union[Dict[str, Any], ScientificEvidence]] = None,
    provider_override: Optional[str] = None,
    domain_adapted: bool = True
) -> Dict[str, Any]:
    """
    Executes standardized VQA inference using the resolved VLM adapter.
    
    Supports:
    - Input validation (missing bytes or query)
    - Domain prompt selection
    - Scientific evidence integration
    - Standardized output normalization
    """
    warnings: List[str] = []

    # 1. Input Validation
    if not image_bytes:
        return normalize_vqa_response(
            raw_response={
                "answer": "Error: Missing or empty image input bytes.",
                "evidence": [],
                "confidence": 0,
                "is_error": True,
                "error_code": "INVALID_INPUT"
            },
            provider="system",
            warnings=["Input image payload was zero bytes."]
        )

    if not query or not query.strip():
        return normalize_vqa_response(
            raw_response={
                "answer": "Error: Query string cannot be empty.",
                "evidence": [],
                "confidence": 0,
                "is_error": True,
                "error_code": "INVALID_INPUT"
            },
            provider="system",
            warnings=["VQA query parameter was empty."]
        )

    # 2. Resolve Adapter
    adapter = resolve_adapter(provider_override)
    provider_name = adapter.get_provider_name()

    if not adapter.is_available():
        warnings.append(f"Provider '{provider_name}' is currently unconfigured or unavailable.")

    # 3. Scientific Evidence Context Formatting
    evidence_obj: Optional[ScientificEvidence] = None
    if isinstance(scientific_evidence, ScientificEvidence):
        evidence_obj = scientific_evidence
    elif isinstance(scientific_evidence, dict) and scientific_evidence:
        evidence_obj = ScientificEvidence.from_dict(scientific_evidence)

    if evidence_obj and evidence_obj.is_synthetic:
        warnings.append("Scientific evidence provided is a synthetic test fixture.")

    # 4. Construct Prompt
    if evidence_obj:
        evidence_text = format_evidence_for_prompt(evidence_obj)
        prompt_str = EVIDENCE_AWARE_VQA_PROMPT.format(
            query=query, scientific_evidence_text=evidence_text
        )
    elif domain_adapted:
        prompt_str = REMOTE_SENSING_VQA_PROMPT.format(query=query)
    else:
        prompt_str = GENERAL_VQA_PROMPT.format(query=query)

    # 5. Execute Adapter Call
    try:
        raw_res = adapter.generate_vqa(image_bytes, prompt_str)
    except Exception as e:
        logger.error(f"VQAInference: Adapter '{provider_name}' execution failed: {e}")
        raw_res = {
            "answer": f"[{provider_name}]: Execution failed due to unexpected error: {str(e)}",
            "evidence": [],
            "confidence": 0,
            "is_error": True,
            "error_code": "PROVIDER_EXECUTION_FAILURE"
        }

    # 6. Normalize Response
    return normalize_vqa_response(
        raw_response=raw_res,
        provider=provider_name,
        warnings=warnings
    )


def run_caption_inference(
    image_bytes: bytes,
    scientific_evidence: Optional[Union[Dict[str, Any], ScientificEvidence]] = None,
    provider_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes standardized scene captioning inference using the resolved VLM adapter.
    """
    warnings: List[str] = []

    if not image_bytes:
        return normalize_vqa_response(
            raw_response={
                "answer": "Error: Missing or empty image input bytes for captioning.",
                "evidence": [],
                "confidence": 0,
                "is_error": True,
                "error_code": "INVALID_INPUT"
            },
            provider="system",
            warnings=["Input image payload was zero bytes."]
        )

    adapter = resolve_adapter(provider_override)
    provider_name = adapter.get_provider_name()

    if not adapter.is_available():
        warnings.append(f"Provider '{provider_name}' is currently unconfigured or unavailable.")

    try:
        raw_res = adapter.generate_caption(image_bytes)
    except Exception as e:
        logger.error(f"CaptionInference: Adapter '{provider_name}' execution failed: {e}")
        raw_res = {
            "caption": f"[{provider_name}]: Scene captioning failed due to unexpected error: {str(e)}",
            "evidence": [],
            "confidence": 0,
            "is_error": True,
            "error_code": "PROVIDER_EXECUTION_FAILURE"
        }

    return normalize_vqa_response(
        raw_response=raw_res,
        provider=provider_name,
        warnings=warnings
    )
