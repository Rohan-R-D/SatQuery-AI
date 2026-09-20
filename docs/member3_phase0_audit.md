# Phase 0 Audit & AI/ML Architecture Guide (Member 3)

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 0 Complete — Verified & Audited  

---

## 1. Current Architecture Overview

SatQuery AI is engineered as a **Modular FastAPI Monolith** that orchestrates an advanced **Two-Lane + Fact-Checking Verification Engine**:

```
                          ┌──────────────────────────────────────────────┐
                          │               FastAPI API Routes             │
                          │   /api/analyze, /api/models, /api/upload     │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                     ┌───────────▼───────────┐
                                     │    SupervisorAgent    │
                                     └───────────┬───────────┘
                                                 │
                ┌────────────────────────────────┼────────────────────────────────┐
                ▼                                ▼                                ▼
        ┌───────────────┐                ┌───────────────┐                ┌───────────────┐
        │    Lane A     │                │    Lane B     │                │    Lane C     │
        │ Deterministic │                │    VLM / AI   │                │ Verification  │
        │ Scientific ML │                │ Semantic VQA  │                │ Fact-Checker  │
        └───────┬───────┘                └───────┬───────┘                └───────┬───────┘
                │                                │                                │
     OpenCV / SIFT / RANSAC              Gemini Service /                4-Factor Consistency Check
     Refined Lee SAR Filter             Custom RS-VLM Adapter            5-Factor Confidence Score
     NDVI / NDWI / NDBI                 (BaseVLMAdapter)
```

1. **Lane A (Deterministic Scientific Processing)**: Executed concurrently or via `asyncio.to_thread` worker threads. Handles sub-pixel co-registration (SIFT + RANSAC homography, $RMSE \le 0.8\text{px}$), morphological change detection, Refined Lee speckle filtering, decibel scale ($\sigma^0\text{ dB}$) SAR calibration, spectral index generation (NDVI, NDWI, NDBI), and GeoJSON bounding feature export.
2. **Lane B (Semantic VLM Reasoning)**: Qualitative multimodal interpretation driven by Vision-Language Models. Cloud baseline uses Google Gemini VLM (`google-genai` SDK); local/custom sovereign models switch dynamically to `CustomRSVLMAdapter`.
3. **Lane C (Fact-Checking Verification & Confidence Scoring)**: Cross-validates Lane B VLM outputs against Lane A's deterministic math across 4 factors (Geometry, Temporal, Statistical, Semantic) and computes an empirical 5-factor confidence score to suppress hallucinations.

---

## 2. File and Module Responsibilities

| File Path | Role & Primary Responsibility |
| --- | --- |
| [base_model.py](file:///e:/SatQuery%20AI/backend/ai/models/base_model.py) | Abstract base class `BaseVLMAdapter` defining the standard VLM contract. |
| [gemini_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/gemini_adapter.py) | Concrete adapter for Google Gemini Multimodal VLM (`google-genai` SDK). |
| [custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py) | Concrete adapter stub for fine-tuned checkpoints (Qwen3-VL / GeoChat / BigEarthNet). |
| [model_adapter.py](file:///e:/SatQuery%20AI/backend/ai/adapters/model_adapter.py) | Factory (`ModelAdapterFactory`) and `get_active_vlm_adapter()` resolver (`ACTIVE_VLM_PROVIDER`). |
| [model_registry.py](file:///e:/SatQuery%20AI/backend/orchestration/model_registry.py) | In-memory catalog (`MODEL_REGISTRY`) listing operational and candidate model capabilities. |
| [task_classifier.py](file:///e:/SatQuery%20AI/backend/orchestration/task_classifier.py) | Rule-based query & modality classifier mapping inputs to workflows and required tools. |
| [vqa_agent.py](file:///e:/SatQuery%20AI/backend/agents/vqa_agent.py) | Specialist Agent executing single-image VQA and scene captioning via active VLM adapter. |
| [grounding_agent.py](file:///e:/SatQuery%20AI/backend/agents/grounding_agent.py) | Specialist Agent executing spatial feature localization & bounding box overlay generation. |
| [change_agent.py](file:///e:/SatQuery%20AI/backend/agents/change_agent.py) | Specialist Agent orchestrating SIFT/RANSAC alignment, OpenCV change detection, and VLM Change-VQA. |
| [fusion_agent.py](file:///e:/SatQuery%20AI/backend/agents/fusion_agent.py) | Specialist Agent executing joint Sentinel-1 SAR and Sentinel-2 Optical cross-modal reasoning. |
| [supervisor_agent.py](file:///e:/SatQuery%20AI/backend/agents/supervisor_agent.py) | Central Orchestrator managing 10-step lifecycle, task routing, DB persistence, and response synthesis. |

---

## 3. VLM Adapter Method Compatibility Table

Both `GeminiAdapter` and `CustomRSVLMAdapter` implement `BaseVLMAdapter` and return compatible dictionary payloads:

| Interface Method | Argument Signature | Expected Return Keys | GeminiAdapter Status | CustomRSVLMAdapter Status |
| --- | --- | --- | --- | --- |
| `is_available()` | `() -> bool` | `bool` | Functional (`GEMINI_API_KEY` check) | Operational (`CUSTOM_VLM_ENDPOINT` / `LOCAL_WEIGHTS_PATH` check) |
| `get_provider_name()` | `() -> str` | `str` | `"Gemini Multimodal VLM (Baseline)"` | `"{model_name} (Sovereign RS-VLM)"` |
| `generate_vqa()` | `(image_bytes: bytes, query: str)` | `answer`, `evidence`, `confidence`, `is_error`, `error_code` | Functional (Gemini API call) | Stub (Fallback dictionary structure) |
| `generate_caption()` | `(image_bytes: bytes)` | `caption` / `answer`, `scene_features`, `evidence`, `confidence`, `is_error`, `error_code` | Functional (Gemini API call) | Stub (Fallback dictionary structure) |
| `generate_change_explanation()` | `(before_bytes: bytes, after_bytes: bytes, overlay_bytes: bytes, query: str, change_percentage: float)` | `answer`, `evidence`, `confidence`, `is_error`, `error_code` | Functional (Gemini API call) | Stub (Fallback dictionary structure) |
| `generate_optical_sar()` | `(optical_bytes: bytes, sar_bytes: bytes, query: str)` | `answer`, `built_up_regions`, `water_regions`, `evidence`, `confidence`, `is_error`, `error_code` | Functional (Gemini API call) | Stub (Fallback dictionary structure) |
| `locate_regions()` | `(image_bytes: bytes, query: str)` | `answer`, `bounding_boxes`, `evidence`, `confidence`, `is_error`, `error_code` | Functional (Gemini API call) | Stub (Fallback dictionary structure) |

---

## 4. Specialist Agent Workflow Analysis

All four specialist agents dynamically resolve the active adapter via `get_active_vlm_adapter()`:

1. **VQAAgent** ([vqa_agent.py](file:///e:/SatQuery%20AI/backend/agents/vqa_agent.py)):
   - **Input**: `image_bytes`, `query`.
   - **Adapter Call**: `adapter.generate_vqa()` or `adapter.generate_caption()`.
   - **Output**: Structured payload containing `answer`, `evidence`, `confidence`, `is_error`, `model_used`.
   - **Scientific Dependency**: None. Direct visual spectrum processing.

2. **GroundingAgent** ([grounding_agent.py](file:///e:/SatQuery%20AI/backend/agents/grounding_agent.py)):
   - **Input**: `image_bytes`, `query`.
   - **Adapter Call**: `adapter.locate_regions()`.
   - **Output**: Bounding box coordinates $[x, y, w, h]$, base64 bounding box overlay artifact, `answer`, `evidence`, `model_used`.
   - **Scientific Dependency**: OpenCV `cv2.rectangle` bounding box overlay renderer.

3. **ChangeAgent** ([change_agent.py](file:///e:/SatQuery%20AI/backend/agents/change_agent.py)):
   - **Input**: `before_bytes`, `after_bytes`, `query`, `is_explanatory_vqa`.
   - **Adapter Call**: `adapter.generate_change_explanation()`.
   - **Output**: Bi-temporal change percentage, changed pixel count, difference raster base64 artifact, overlay artifact, GeoJSON feature collection, `answer`, `verification`, `model_used`.
   - **Scientific Dependency**: SIFT/ORB + RANSAC homography alignment gate (`CoregistrationQualityGate`) and OpenCV morphological change detector (`OpenCVChangeDetector`).

4. **FusionAgent** ([fusion_agent.py](file:///e:/SatQuery%20AI/backend/agents/fusion_agent.py)):
   - **Input**: `optical_bytes`, `sar_bytes`, `query`.
   - **Adapter Call**: `adapter.generate_optical_sar()`.
   - **Output**: Calibrated VV mean backscatter ($\text{dB}$), optical vegetation/water index summaries, built-up region list, water region list, `answer`, `verification`, `model_used`.
   - **Scientific Dependency**: SAR Refined Lee speckle filter, $\sigma^0\text{ dB}$ radiometric converter (`SARPreprocessor`), and optical spectral index engine (`compute_spectral_summary`).

---

## 5. Current AI/ML Implementation Status

| Component | Status | Description |
| --- | --- | --- |
| **Gemini Multimodal VLM Baseline** | `Implemented` | Live cloud VLM inference via `google-genai` SDK with fallback models. |
| **VLM Adapter Routing (`ModelAdapterFactory`)** | `Implemented` | Dynamic env-based resolution (`ACTIVE_VLM_PROVIDER`) across all specialist agents. |
| **Lane A Scientific Preprocessing Engine** | `Implemented` | SIFT/RANSAC co-registration, OpenCV change detection, Refined Lee SAR filter, NDVI/NDWI/NDBI, GeoJSON export. |
| **Lane C Verification & Fact-Checking** | `Implemented` | 4-Factor verifiers (Geometry, Temporal, Stats, Semantics) & empirical 5-factor confidence scorer. |
| **CustomRSVLMAdapter Execution Engine** | `Stub` | Structurally compatible fallback dicts; actual PyTorch / vLLM / Ollama forward calls not yet implemented. |
| **BigEarthNet Dataset Adaptation** | `Missing` | PyTorch `Dataset` / `DataLoader` for Sentinel-2 12-band rasters & 19/43 land-cover label mapper missing. |
| **Open-Source VLM Bounding Box Token Parser** | `Missing` | Token parser for Qwen3-VL / GeoChat coordinate tokens (`[x1, y1, x2, y2]`) missing. |
| **Offline Model Evaluation Pipeline** | `Missing` | Automated benchmark scripts for VQA Accuracy, BLEU, CIDEr, and Geo-IoU missing. |
| **LoRA / PEFT Fine-Tuning Pipeline** | `Missing` | Parameter-efficient fine-tuning scripts for local Qwen3-VL / GeoChat domain adaptation missing. |

---

## 6. Technical Risks & Gaps

1. **Local Inference Latency & VRAM Limitations**: Loading 7B/8B local VLMs (e.g., Qwen3-VL 8B or GeoChat 7B) requires 16GB+ VRAM or quantized GGUF/AWQ checkpoints. Running PyTorch forwards inside FastAPI routes will block the GIL unless wrapped with `asyncio.to_thread` or executed via an async API server (e.g., vLLM / Ollama).
2. **Coordinate Token Scale Differences**: Gemini returns relative or absolute pixel boxes (`x, y, width, height`). Open-weights VLMs (Qwen3-VL, GeoChat) return normalized `[0, 1000]` or `<box>(x1,y1),(x2,y2)</box>` string tokens. A regex/parser wrapper is required in `CustomRSVLMAdapter`.
3. **Multispectral (12-Band) vs. RGB (3-Band) Band Mapping**: PyTorch models trained on BigEarthNet expect 12 Sentinel-2 bands, whereas standard web APIs receive PNG/JPEG RGB bytes. The dataset loader and preprocessing engine must support both 12-band GeoTIFF and 3-band RGB arrays cleanly.

---

## 7. Recommended Member 3 Implementation Roadmap

### Phase 1: Local / Endpoint VLM Inference Engine
- Implement internal vLLM / Ollama / PyTorch HTTP runner inside `CustomRSVLMAdapter.generate_vqa()` and `generate_caption()`.
- Add coordinate token regex parser to convert Qwen3-VL / GeoChat string coordinates into pixel `bounding_boxes`.

### Phase 2: BigEarthNet Dataset & Preprocessing Pipeline
- Build `scientific/datasets/bigearthnet.py` PyTorch `Dataset` and `DataLoader` supporting Sentinel-2 12-band GeoTIFF rasters and 19-class CORINE land-cover mapping.
- Implement zero-shot and classification feature extractor adapters for remote sensing land-cover analysis.

### Phase 3: Change-VQA & Optical-SAR Deep Model Integration
- Integrate deep bi-temporal change models (e.g., ChangeFormer) into `ChangeAgent`.
- Wire cross-modal deep feature fusion networks (e.g., GRAMA) into `FusionAgent`.

### Phase 4: Model Evaluation & LoRA Fine-Tuning Suite
- Create offline evaluation scripts in `backend/tests/eval/` measuring VQA Accuracy, Geo-IoU, and BLEU.
- Set up PEFT/LoRA fine-tuning scripts for Qwen3-VL on domain-specific satellite datasets.

---

## 8. Dependencies & Team Coordination

- **Member 1 (Architect / Supervisor)**: Coordinate on multi-agent routing rules in `task_classifier.py` when adding new specialized models.
- **Member 2 (Security & DB Reviewer)**: Coordinate on constant-time API key verification, file validation, rate limiting, and persistent audit logging.
- **Member 4 (Frontend / Presentation Lead)**: Coordinate on visual artifact schemas (`image/png` base64 data URLs) and GeoJSON feature collections displayed on the UI map.

---

## 9. Testing & Empirical Verification

Ran full backend test suite (`pytest backend/tests/ -v`):

```text
======================= 41 passed, 4 warnings in 50.63s =======================
```

- **Passed Tests**: 41/41 (100% pass rate).
- **Failed Tests**: 0.
- **Warnings**: 4 (Deprecation warnings for `python-multipart` import and PIL `DecompressionBombWarning` on oversized image test).
- **Audit Verification**: All specialist agents (`VQAAgent`, `GroundingAgent`, `ChangeAgent`, `FusionAgent`) and adapter factories (`ModelAdapterFactory`, `get_active_vlm_adapter()`) are fully verified.

---

## 10. Phase 0 Completion Checklist

- [x] Full read-only audit of existing backend architecture and Two-Lane engine complete.
- [x] Documented `BaseVLMAdapter` interface, `GeminiAdapter`, and `CustomRSVLMAdapter`.
- [x] Verified specialist agent adapter routing (`get_active_vlm_adapter()`).
- [x] Constructed VLM adapter method compatibility table.
- [x] Traced input/output workflows for VQA, Grounding, Change, and Fusion agents.
- [x] Classified AI/ML component statuses (`Implemented`, `Stub`, `Missing`).
- [x] Identified technical risks (VRAM, coordinate tokens, multispectral bands).
- [x] Formulated Member 3 roadmap for Phase 1 through Phase 4.
- [x] Executed backend test suite (41/41 passed).
