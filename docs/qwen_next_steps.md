# Qwen3-VL Integration Guide — SatQuery AI

**Author**: Member 3 (AI/ML Lead)  
**Date**: September 20, 2026  
**Status**: REMOTE-ONLY ADAPTER IMPLEMENTED & TESTED  
**Repository Branch**: `feature/member3-ai-ml-training`

---

## 1. Overview & Model Selection

Qwen3-VL (`Qwen/Qwen3-VL-2B-Instruct`) is integrated into SatQuery AI as a lightweight, high-performance generalist multimodal Vision-Language Model.

In SatQuery AI, Qwen3-VL operates **STRICTLY AS A REMOTE-ONLY PROVIDER**:
- Zero local weights downloaded.
- Zero local GPU / CUDA requirements.
- OpenAI-compatible multimodal `/v1/chat/completions` API interface.

| Specification | Details |
| :--- | :--- |
| **Model Repository** | `Qwen/Qwen3-VL-2B-Instruct` |
| **Provider Type** | Remote HTTP Multimodal API |
| **Primary Tasks** | High-resolution VQA, Scene Captioning, Optional Spatial Grounding |
| **Local Dependencies** | None (Remote-only) |
| **Payload Structure** | JSON Base64 Data URL Image format |

---

## 2. Configuration Parameters

Qwen3-VL behavior is configurable via environment variables:

```env
# Enable Qwen Model Integration
SATQUERY_QWEN_ENABLED=true

# Remote Endpoint URL (vLLM / Ollama / OpenAI-compatible endpoint)
SATQUERY_QWEN_ENDPOINT_URL=http://localhost:8000/v1/chat/completions

# Model ID
SATQUERY_QWEN_MODEL_ID=Qwen/Qwen3-VL-2B-Instruct

# Optional Grounding Support Flag
SATQUERY_QWEN_GROUNDING_ENABLED=true

# Active VLM Provider Routing Override
ACTIVE_VLM_PROVIDER=qwen
```

---

## 3. Adapter Implementation Details

Implemented in `backend/ai/models/qwen_adapter.py`:

- **Class**: `QwenAdapter(BaseVLMAdapter, BaseGroundingAdapter)`
- **Remote HTTP Integration**: Uses `RemoteVLMHttpClient.query_openai_multimodal_endpoint`.
- **Grounding Validation**: Validates bounding boxes if `SATQUERY_QWEN_GROUNDING_ENABLED=true` and remote API returns structured boxes.
- **Unconfigured Error Handling**: Returns structured error responses (`QWEN_ENDPOINT_UNCONFIGURED`) when disabled or unconfigured.

---

## 4. Test Suite & Verification

- **Unit Tests**: `backend/tests/test_qwen_adapter.py` (Passed).
- **Remote Architecture Verified**: Confirmed zero local weights required.
- **Provider Resolution**: `run_vqa_inference(..., provider_override="qwen")` routes to `QwenAdapter`.
