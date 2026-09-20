# Phase 3: Multimodel VQA, Captioning, and Inference Foundation

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 3 Complete — Multimodel VQA Inference Foundation Implemented & Fully Verified  

---

## 1. Architecture & Design Principles

Phase 3 establishes a standardized, modular VQA and scene-captioning inference foundation for **SatQuery AI**:

```
                       ┌──────────────────────────────────────────────┐
                       │    API Route / Specialist Agent Invocation   │
                       │           (VQAAgent / /api/analyze)          │
                       └──────────────────────┬───────────────────────┘
                                              │
                                  ┌───────────▼───────────┐
                                  │ run_vqa_inference()   │
                                  │ run_caption_inference│
                                  └───────────┬───────────┘
                                              │
                      ┌───────────────────────┼───────────────────────┐
                      ▼                       ▼                       ▼
          ┌───────────────────────┐   ┌───────────────┐   ┌───────────────────────┐
          │  Input Validation &   │   │  Prompts &    │   │  Scientific Evidence  │
          │  Adapter Resolution   │   │  Domain Maps  │   │     Integration       │
          └───────────┬───────────┘   └───────┬───────┘   └───────────┬───────────┘
                      │                       │                       │
                      └───────────────────────┼───────────────────────┘
                                              │
                                  ┌───────────▼───────────┐
                                  │  BaseVLMAdapter Call  │
                                  │ (Gemini / Custom VLM) │
                                  └───────────┬───────────┘
                                              │
                                  ┌───────────▼───────────┐
                                  │normalize_vqa_response │
                                  └───────────────────────┘
```

### Core Design Guarantees
1. **Gemini Remains Default**: Google Gemini Flash remains the default operational cloud baseline provider (`ACTIVE_VLM_PROVIDER=gemini`). Zero breaking changes to existing routes.
2. **Provider Agnostic**: Provider selection is dynamically resolved via `ModelAdapterFactory` and `get_active_vlm_adapter()`, allowing 1-line switching via `.env` configuration.
3. **Standardized Response Structure**: All VQA and captioning inferences normalize return dictionaries into a uniform schema (`answer`, `model`, `model_version`, `provider`, `confidence`, `evidence`, `warnings`, `is_error`, `error_code`).
4. **Scientific Evidence Integration**: Integrates Lane A measurement facts (NDVI, NDWI, SAR dB backscatter) into visual reasoning prompts without overriding ground-truth facts. Synthetic test fixtures are explicitly flagged (`is_synthetic=True`).

---

## 2. Standardized VQA & Captioning Response Schemas

All inference outputs follow this standardized dictionary contract:

```json
{
  "answer": "Discontinuous urban fabric and agricultural pastures identified.",
  "model": "Gemini Multimodal VLM (Baseline)",
  "model_version": "1.5-flash",
  "provider": "google-gemini",
  "confidence": 92.0,
  "evidence": ["High NDVI reflectance", "Urban structure contours"],
  "warnings": ["[NOTE: Synthetic scientific fixture data for testing]"],
  "is_error": false,
  "error_code": null,
  "model_used": "Gemini Multimodal VLM (Baseline)"
}
```

---

## 3. Modular Prompt Templates (`backend/ai/prompts.py`)

- **`GENERAL_VQA_PROMPT`**: Direct, factual open-domain visual question answering.
- **`REMOTE_SENSING_VQA_PROMPT`**: Specialized remote-sensing prompt incorporating land-cover categories, built-up urban fabric, canopy cover, and coastal features.
- **`SCENE_CAPTIONING_PROMPT`**: Comprehensive scene description prompt generating structured land-use summaries.
- **`EVIDENCE_AWARE_VQA_PROMPT`**: Synthesizes Lane A scientific measurement facts with VLM visual reasoning.
- **`UNCERTAINTY_AWARE_PROMPT`**: Explicitly instructs the VLM to acknowledge spatial resolution limits or visual ambiguities.

---

## 4. Model Capabilities Catalog (`MODEL_REGISTRY`)

The updated model registry catalog ([`backend/orchestration/model_registry.py`](file:///e:/SatQuery%20AI/backend/orchestration/model_registry.py)) defines:

| Model ID | Provider | Category | Status | Execution Type | Hardware Req. | License |
| --- | --- | --- | --- | --- | --- | --- |
| `gemini-vlm` | `google-gemini` | Conversational VLM | `temporary_baseline` | `cloud_api` | 0 GB (Cloud API) | Proprietary Commercial API |
| `qwen2.5-vl-7b` | `qwen` | Conversational VLM | `candidate` | `local_server` | ~16 GB (FP16) / ~7.5-8 GB (4-bit AWQ est.) | Apache 2.0 |
| `geochat-7b` | `geochat` | Remote-Sensing VLM | `candidate` | `local_weights` | ~16 GB (FP16) / ~7 GB (4-bit est.) | Non-Commercial |
| `bigearthnet-resnet50` | `bigearthnet` | Multispectral Classifier | `planned` | `local_weights` | ~2-4 GB (Inference Est.) | CDLA-Permissive-1.0 / CC BY 4.0 |
| `changeformer` | `changeformer` | Change-Detection Model | `candidate` | `local_weights` | ~4-6 GB (Inference Est.) | Apache 2.0 |
| `skysense-remoteclip` | `remoteclip` | Embedding/Retrieval Model | `candidate` | `local_weights` | ~4-8 GB (Inference Est.) | Apache 2.0 / CC BY-NC |

---

## 5. Summary of Tested vs. Configured Models

- **Executed & Tested Models**:
  - `gemini-vlm` (Google Gemini 1.5 Flash): Fully operational and tested across unit test suites.
- **Prepared & Configured Models (Stubs)**:
  - `qwen2.5-vl-7b`, `geochat-7b`, `custom-rs-vlm`: Configured in registry and adapter architecture (`CustomRSVLMAdapter`). Returns structured graceful fallback responses (`is_error=True`, `error_code="VLM_ENDPOINT_UNCONFIGURED"`) when local endpoints are unconfigured.

---

## 6. Automated Unit Test Verification

Executed full backend unit test suite:
```cmd
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"; pytest backend/tests/ -v
```
- **Test Results**: **53 passed, 4 warnings in 71.40s**.
- **New Test Files Added**:
  - `backend/tests/test_vqa_inference.py` (8 unit tests)
  - `backend/tests/test_evaluation_foundation.py` (4 unit tests)
  - `backend/tests/test_bigearthnet_dataset.py` (5 unit tests)
