# GeoChat Integration Guide — SatQuery AI

**Author**: Member 3 (AI/ML Lead)  
**Date**: September 20, 2026  
**Status**: REMOTE-ONLY ADAPTER IMPLEMENTED & TESTED  
**Repository Branch**: `feature/member3-ai-ml-training`

---

## 1. Overview & Architecture

GeoChat (7B, CVPR 2024 by MBZUAI) is domain-adapted for remote-sensing Visual Question Answering (VQA), Scene Captioning, and Spatial Grounding over satellite and aerial imagery.

In SatQuery AI, GeoChat operates **STRICTLY AS A REMOTE-ONLY MULTIMODAL PROVIDER**:
- Zero local weights downloaded.
- Zero local GPU / CUDA requirements.
- Queries routed via resilient HTTP API client to remote GeoChat servers.

| Specification | Details |
| :--- | :--- |
| **Model Repository** | `MBZUAI/geochat-7B` |
| **Provider Type** | Remote HTTP Multimodal API |
| **Primary Tasks** | Remote Sensing VQA, Scene Captioning, Region Grounding |
| **Local Dependencies** | None (Remote-only) |
| **Input Format** | Base64 encoded JPEG/PNG satellite imagery + text prompts |

---

## 2. Configuration Parameters

GeoChat behavior is configurable via environment variables:

```env
# Enable GeoChat Model Integration
SATQUERY_GEOCHAT_ENABLED=true

# Model ID
SATQUERY_GEOCHAT_MODEL_ID=MBZUAI/geochat-7B

# Remote Inference Endpoint URL
SATQUERY_GEOCHAT_ENDPOINT_URL=http://localhost:8000/v1/geochat

# Active VLM Provider Routing Override
ACTIVE_VLM_PROVIDER=geochat
```

---

## 3. Adapter Implementation Details

Implemented in `backend/ai/models/geochat_adapter.py`:

- **Class**: `GeoChatAdapter(BaseVLMAdapter, BaseGroundingAdapter)`
- **Remote HTTP Routing**: Leverages `RemoteVLMHttpClient` for non-blocking payload formatting and error sanitization.
- **Unconfigured Error Handling**: If `SATQUERY_GEOCHAT_ENABLED=false` or endpoint URL is missing, returns structured error responses (`GEOCHAT_UNCONFIGURED`) without throwing exceptions.
- **Gemini Baseline Isolation**: Default baseline remains `ACTIVE_VLM_PROVIDER=gemini`.

---

## 4. Test Suite & Verification

- **Unit Tests**: `backend/tests/test_geochat_adapter.py` (Passed).
- **Remote Architecture Verified**: Confirmed zero local weights required.
- **Dynamic Provider Routing**: `resolve_adapter(provider_override="geochat")` correctly resolves `GeoChatAdapter`.
