# Phase 1: Research and Model Selection Report

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 1 Complete — Research & Model Selection Finalized (Reviewed & Qualified)  

---

## 1. Executive Summary & Categorized Model Evaluation

This report presents a systematic evaluation of Vision-Language Models (VLMs), multispectral classification networks, bi-temporal change detection backbones, and embedding models for integration into the **SatQuery AI** Two-Lane Architecture.

### Model Taxonomy & Categorization

To maintain strict architectural boundaries, models are grouped into 5 distinct functional categories:

1. **Conversational VLMs**: Auto-regressive multimodal vision-language models capable of visual question answering (VQA), scene captioning, multi-image temporal reasoning, and spatial grounding.
2. **Multispectral Classification Models**: Deep convolutional / vision transformer backbones trained on multi-band satellite rasters for quantitative land-cover multi-label classification (non-conversational).
3. **Change-Detection Models**: Siamese neural networks designed specifically for generating pixel-dense binary change masks from temporal image pairs (non-conversational).
4. **Embedding and Retrieval Models**: Contrastive vision-language encoders (CLIP-style) used for cross-modal similarity scoring, feature extraction, and zero-shot retrieval.
5. **Scientific Processing Components**: Deterministic computer vision algorithms (SIFT, RANSAC, OpenCV morphological difference, Refined Lee SAR speckle filtering, spectral index calculators).

---

### Evaluation Matrix Summary

| Model ID | Model Name & Version | Model Category | Integration Status | Modality Support | VRAM Req. (FP16 / INT4) | License | Inference Engine | Evidence Level | Recommended Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gemini-vlm` | Google Gemini 1.5/2.0 Flash | Conversational VLM | Implemented (Active Baseline) | RGB (3-Channel) | 0 GB (Cloud API) | Proprietary Commercial API | `google-genai` SDK | Verified from official source | Active Cloud Baseline |
| `qwen2.5-vl-7b` | Qwen2.5-VL-7B-Instruct | Conversational VLM | Architecturally Compatible (Planned) | RGB (Dynamic Native Res) | 16 GB / 8 GB (AWQ est.) | Apache 2.0 | HuggingFace / vLLM / Ollama | Verified from official source & Estimated | **Primary Open-Weights VLM Candidate** |
| `geochat-7b` | GeoChat-7B (CVPR 2024) | Conversational VLM | Architecturally Compatible (Planned) | RGB (Aerial & Satellite) | 16 GB / 7 GB (4-bit est.) | Non-Commercial (Vicuna base) | HuggingFace / LLaVA codebase | Reported by research paper | Alternative RS-Specific Candidate |
| `bigearthnet-resnet50` | BigEarthNet Multi-Label Net | Multispectral Classifier | Model Requiring Adaptation (Planned) | 12-Band S2 + 2-Band S1 SAR | 2–4 GB (Estimated) | MIT / CC BY 4.0 | PyTorch (`timm` / `torchvision`) | Reported by research paper | Scientific Classifier / Feature Scorer |
| `changeformer` | ChangeFormer Bi-Temporal Net | Change-Detection Model | Model Requiring Adaptation (Planned) | Bi-Temporal RGB / S2 | 4–6 GB (Estimated) | Apache 2.0 | PyTorch model forward | Reported by research paper | Pixel-Dense Change Mask Engine |
| `skysense-remoteclip` | RemoteCLIP / SkySense | Embedding/Retrieval Model | Architecturally Compatible (Planned) | RGB & Multispectral | 4–8 GB (Estimated) | Apache 2.0 / CC BY-NC | HuggingFace / OpenCLIP | Reported by research paper | Zero-Shot Embedding & Feature Scorer |
| `qwen2.5-vl-72b` | Qwen2.5-VL-72B-Instruct | Conversational VLM | Unsuitable (Exceeds VRAM) | RGB (Dynamic Resolution) | >80 GB VRAM (Estimated) | Apache 2.0 | vLLM (Multi-GPU Cluster) | Verified from official source | Unsuitable (Excessive VRAM Hardware Req) |

*The complete CSV dataset is archived at [experiments/model_selection.csv](file:///e:/SatQuery%20AI/experiments/model_selection.csv).*

---

## 2. Existing Baseline Analysis: Google Gemini Multimodal VLM

- **Category**: Conversational VLM
- **Integration Status**: `Implemented (Active Baseline)`
- **Implementation Verification**: Active in repository via [services/gemini_service.py](file:///e:/SatQuery%20AI/backend/services/gemini_service.py) and [ai/models/gemini_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/gemini_adapter.py). Fully tested across backend test suites.

### Capabilities & Validated Performance
- **Zero Local Hardware Requirement**: Runs via HTTPS API calls to Google Cloud API, requiring 0 GB local GPU VRAM.
- **Multimodal Visual Reasoning**: Handles single-image VQA, multi-image bi-temporal change explanations (Image 1 = Before, Image 2 = After, Image 3 = Difference Overlay), and joint Optical + SAR cross-modal prompts.
- **Structured JSON Schema Enforcement**: Uses Pydantic `GenerateContentConfig` schemas (`GeminiVQAOutput`, `GeminiGroundingOutput`, `GeminiOpticalSarOutput`) to enforce strict return JSON types.
- **Spatial Grounding**: Returns pixel bounding boxes `{"x", "y", "width", "height", "label"}`.

### Limitations & Technical Risks
- **External Network Dependency**: Fails gracefully with `MISSING_API_KEY` or `API_ERROR` if offline or unconfigured.
- **Privacy & Air-Gap Constraint**: Cannot be deployed in offline or high-security air-gapped sovereign environments.
- **RGB Input Constraint**: Standard API accepts 3-channel RGB imagery (`bytes`). Raw 12-band Sentinel-2 GeoTIFFs or complex polarimetric SAR arrays must be rendered into 3-channel RGB composites before invocation.

---

## 3. Open-Weights Candidate Models

### 3.1 Qwen2.5-VL-7B-Instruct
- **Category**: Conversational VLM
- **Integration Status**: `Architecturally Compatible (Planned)` *(Not implemented or tested with live weights in this repository yet)*
- **Evidence Level**: `Verified from official source` (Repository: [github.com/QwenLM/Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL)) & `Estimated` (Hardware memory metrics).

#### Technical Specifications & Justification
1. **License**: Apache 2.0 (Fully open for commercial deployment and hackathon distribution).
2. **Native Spatial Grounding Format**: Predicts normalized coordinate tokens `<|box_start|>(y1,x1),(y2,x2)<|box_end|>` mapped to an explicit $[0, 1000]$ coordinate grid. *(Requires regex parser implementation in `CustomRSVLMAdapter` during future VLM integration phases)*.
3. **Dynamic Resolution Visual Encoder**: Adapts dynamically to native satellite raster resolutions without fixed square resizing, preserving small remote sensing features (e.g., individual structures, small water bodies, vessels, runways).
4. **Multi-Image Temporal Reasoning**: Native support for multi-image sequences, making it architecturally compatible with `ChangeAgent` bi-temporal pairs and `FusionAgent` Optical + SAR multi-sensor pairs.
5. **Hardware Footprint**:
   - Full FP16 precision: ~16 GB VRAM *(Estimated based on 7B parameters)*.
   - 4-bit AWQ / INT4 quantized precision: **~7.5–8 GB VRAM** *(Estimated)*, allowing single-GPU execution on consumer GPUs (NVIDIA RTX 3090, 4090, or cloud T4 instances).

---

### 3.2 GeoChat-7B (CVPR 2024)
- **Category**: Conversational VLM
- **Integration Status**: `Architecturally Compatible (Planned)` *(Not implemented or tested in this repository yet)*
- **Evidence Level**: `Reported by research paper` (MBZUAI CVPR 2024; [arxiv.org/abs/2311.15826](https://arxiv.org/abs/2311.15826)).

#### Technical Specifications
1. **License**: Non-Commercial (Dependent on Vicuna-1.5 LLM base weights).
2. **Domain Fine-Tuning**: Fine-tuned on 318k remote-sensing instruction pairs (RSVQA, RSICD, RSSCN7, PatternNet). Understands specialized remote sensing terminology natively (e.g., "apron", "runway", "canopy cover", "built-up urban").
3. **Limitations**: Fixed-resolution CLIP vision backbone (336x336 / 448x448 px) causes fine spatial details to blur on large rasters; lacks native 12-band input tensor support.

---

## 4. Multispectral & Specialized Models

### 4.1 BigEarthNet Multi-Label Classifier (ResNet-50 / ViT)
- **Category**: Multispectral Classification Model *(NOT a conversational VLM or grounding model)*
- **Integration Status**: `Model Requiring Adaptation (Planned)`
- **Evidence Level**: `Reported by research paper` (TU Berlin / DLR; [bigearth.net](https://bigearth.net/)).

#### Technical Specifications & Role
1. **Modality Support**: Native 12-Band Sentinel-2 L2A (10m, 20m, 60m bands) & 2-Band Sentinel-1 SAR (VV, VH backscatter).
2. **Primary Function**: Multi-label classification across 19 CORINE land-cover classes (e.g., *Urban Fabric, Arable Land, Permanent Crops, Pastures, Forests, Scrub, Open Spaces, Wetlands, Water Bodies*).
3. **Repository Role**: Planned integration as a **Lane A Scientific Feature Scorer** in `scientific/datasets/bigearthnet.py` to produce quantitative land-cover probability vectors that feed into Lane C fact-checking verification.

---

### 4.2 ChangeFormer (Siamese Transformer for Change Detection)
- **Category**: Change-Detection Model *(NOT a conversational VLM)*
- **Integration Status**: `Model Requiring Adaptation (Planned)`
- **Evidence Level**: `Reported by research paper` (IEEE TGRS 2022; [arxiv.org/abs/2201.01293](https://arxiv.org/abs/2201.01293)).

#### Technical Specifications & Role
1. **Primary Function**: Siamese Transformer network that inputs bi-temporal satellite image pairs (T1, T2) and outputs pixel-dense binary change masks.
2. **Repository Role**: Planned integration as an advanced Lane A change detection engine alongside the existing `OpenCVChangeDetector`.

---

## 5. Hardware & Deployment Requirements Matrix

| Model Configuration | Model Category | VRAM Requirement | Minimum GPU Hardware | Quantization Strategy | Inference Engine Option | Evidence Level |
| --- | --- | --- | --- | --- | --- | --- |
| **Gemini 1.5 Flash (Baseline)** | Conversational VLM | 0 GB | None (Cloud API) | N/A (Hosted) | Google GenAI API Client | Verified from official source |
| **Qwen2.5-VL-7B (FP16)** | Conversational VLM | ~16 GB | NVIDIA RTX 3090 / A10G / T4 (x2) | FP16 / BF16 | vLLM (v0.7+) / HuggingFace | Estimated |
| **Qwen2.5-VL-7B (AWQ / 4-bit)** | Conversational VLM | **~7.5 GB** | **NVIDIA RTX 3060 (12GB) / RTX 4070 / T4** | **AWQ / GPTQ / GGUF** | **vLLM / Ollama (`ollama run qwen2.5-vl`)** | **Estimated** |
| **GeoChat-7B (4-bit)** | Conversational VLM | ~7.0 GB | NVIDIA RTX 3060 (12GB) / T4 | 4-bit BitsAndBytes / AWQ | HuggingFace `transformers` + LLaVA | Reported by research paper |
| **BigEarthNet ResNet-50** | Multispectral Classifier | ~2.5 GB | Any CUDA GPU or CPU | FP32 / FP16 | PyTorch (`torchvision` / `timm`) | Estimated |

---

## 6. Repository Integration Architecture

The existing backend architecture enforces dynamic model resolution via `BaseVLMAdapter` ([base_model.py](file:///e:/SatQuery%20AI/backend/ai/models/base_model.py)) and `get_active_vlm_adapter()` ([model_adapter.py](file:///e:/SatQuery%20AI/backend/ai/adapters/model_adapter.py)):

```
                            ┌───────────────────────────────────┐
                            │    Environment Switch (.env)      │
                            │    ACTIVE_VLM_PROVIDER=custom     │
                            └─────────────────┬─────────────────┘
                                              │
                                  ┌───────────▼───────────┐
                                  │ get_active_vlm_adapter│
                                  └───────────┬───────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
          ┌───────────────────────┐                       ┌───────────────────────┐
          │     GeminiAdapter     │                       │  CustomRSVLMAdapter   │
          │ (ACTIVE_VLM_PROVIDER  │                       │ (ACTIVE_VLM_PROVIDER  │
          │       = gemini)       │                       │  = custom / qwen)     │
          └───────────┬───────────┘                       └───────────┬───────────┘
                      │                                               │
             Google Cloud API                                 vLLM / Ollama Local API
           (Implemented Baseline)                        (Structurally Compatible Stub)
```

### Current Status of `CustomRSVLMAdapter`
- **Implementation Status**: `Stub` (Structurally compatible adapter interface).
- **Current Behavior**: Implements all 5 `BaseVLMAdapter` methods. When `is_available()` returns `False` (unconfigured endpoint/weights), returns predictable fallback dictionaries containing `is_error=True`, `error_code="VLM_ENDPOINT_UNCONFIGURED"`, and `confidence=0`.
- **Planned Endpoint Integration**: In future VLM integration phases, `CustomRSVLMAdapter` will make async HTTP requests (`httpx`) to a local vLLM / Ollama inference server (`http://localhost:11434/api/generate`) and parse Qwen2.5-VL grounding tokens `<|box_start|>(y1,x1),(y2,x2)<|box_end|>` into standard pixel bounding box dictionaries `{"x", "y", "width", "height", "label"}`.

---

## 7. Technical Risks & Mitigation Strategies

1. **Grounding Coordinate Format Scaling**:
   - *Risk*: Open-weights VLMs (e.g. Qwen2.5-VL) output normalized $[0, 1000]$ string tokens, whereas the frontend UI expects absolute pixel coordinates $(w, h)$.
   - *Mitigation*: Implement a coordinate regex scaling parser inside `CustomRSVLMAdapter` during future VLM integration phases that multiplies normalized tokens by $(w/1000, h/1000)$.
2. **Local Model Startup & Memory Overhead**:
   - *Risk*: Loading a 7B model directly inside the FastAPI Python process causes out-of-memory (OOM) crashes and blocks worker threads.
   - *Mitigation*: Decouple model serving into a standalone vLLM or Ollama process/container. `CustomRSVLMAdapter` communicates via lightweight async HTTP calls (`httpx`).
3. **Multispectral (12-Band) vs. RGB Channel Mapping**:
   - *Risk*: Open VLMs accept 3-channel RGB inputs, ignoring SWIR/Infrared bands.
   - *Mitigation*: Lane A (`raster_loader.py` & `normalization.py`) synthesizes calibrated 3-channel RGB composites (e.g., False-Color Infrared Band 8-4-3 or SAR VV-VH-Ratio composite) prior to VLM ingestion, while feeding raw 12-band tensors to the BigEarthNet scientific classifier.

---

## 8. Research References & Source Links

1. **Qwen2.5-VL Technical Report & Repository**:
   - Official Repository: [github.com/QwenLM/Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL) (Verified: Apache 2.0 License).
2. **GeoChat: Grounded Large Vision-Language Model for Remote Sensing**:
   - Research Paper: CVPR 2024 ([arxiv.org/abs/2311.15826](https://arxiv.org/abs/2311.15826)).
3. **BigEarthNet Large-Scale Remote Sensing Benchmark**:
   - Benchmark & Documentation: TU Berlin / DLR ([bigearth.net](https://bigearth.net/)).
4. **ChangeFormer: A Transformer-Based Siamese Network for Change Detection**:
   - Research Paper: IEEE TGRS 2022 ([arxiv.org/abs/2201.01293](https://arxiv.org/abs/2201.01293)).
5. **Google Gemini API Documentation**:
   - Official SDK: [github.com/googleapis/python-genai](https://github.com/googleapis/python-genai).

---

## 9. Phase 2 Recommendation — Dataset Preparation and BigEarthNet Groundwork

In accordance with the official Work Distribution document, the immediate next phase for Member 3 is **Phase 2 — Dataset Preparation and BigEarthNet Groundwork**.

### 9.1 Dataset Selection & Archive Structure
- **Selected Benchmark Dataset**: **BigEarthNet-MM** (BigEarthNet Multispectral & SAR dataset by TU Berlin / DLR).
- **Data Archive Format**: 590,326 GeoTIFF patch pairs stored in structured directory hierarchies:
  ```text
  data/bigearthnet/
  ├── Sentinel-2/
  │   └── Patch_S2_X_Y/
  │       ├── Patch_S2_X_Y_B01.tif (60m)
  │       ├── Patch_S2_X_Y_B02.tif (10m Blue)
  │       ├── Patch_S2_X_Y_B03.tif (10m Green)
  │       ├── Patch_S2_X_Y_B04.tif (10m Red)
  │       ├── Patch_S2_X_Y_B08.tif (10m NIR)
  │       └── Patch_S2_X_Y_labels_metadata.json
  └── Sentinel-1/
      └── Patch_S1_X_Y/
          ├── Patch_S1_X_Y_VV.tif (10m SAR)
          └── Patch_S1_X_Y_VH.tif (10m SAR)
  ```

### 9.2 Sentinel-2 and Sentinel-1 Data Considerations
- **Sentinel-2 Multi-Resolution Bands**: 10m spatial resolution (B02, B03, B04, B08), 20m spatial resolution (B05, B06, B07, B8A, B11, B12), and 60m spatial resolution (B01, B09, B10). Preprocessing must resample 20m and 60m channels to a uniform 10m grid (120x120 pixels per patch).
- **Sentinel-1 SAR Dual-Pol Channels**: Co-polarized VV and cross-polarized VH backscatter intensity. Preprocessing converts linear intensity to decibel scale ($\sigma^0\text{ dB}$) using Refined Lee speckle filtering ([scientific/sar/calibration.py](file:///e:/SatQuery%20AI/backend/scientific/sar/calibration.py)).

### 9.3 Preprocessing & RGB Composite Requirements
- **Radiometric Stretches**: Min-max and 2%–98% linear percentile reflectance normalization.
- **Nodata & Invalid Pixel Filtering**: Filtering patches with cloud cover or incomplete coverage using dataset valid masks.
- **VLM Preview Synthesis**: Generating 3-channel RGB composites (Natural Color Band 4-3-2 and False-Color Infrared Band 8-4-3) to allow VLM vision encoders to process multi-spectral scenes.

### 9.4 Dataset Loader Architecture Planning
- **Module Path**: `scientific/datasets/bigearthnet.py`
- **Class Design**: PyTorch `Dataset` and `DataLoader` abstractions (`BigEarthNetDataset`) implementing:
  - Multi-band tensor extraction `(12, H, W)` for Sentinel-2.
  - Dual-channel SAR tensor extraction `(2, H, W)` for Sentinel-1.
  - CORINE 19-class multi-label target vector mapping `(19,)`.

### 9.5 Small-Subset Experiment Planning
- **Subset Scope**: Extracting a 1,000-patch reproducible validation subset (`data/bigearthnet_subset/`) containing balanced land-cover class samples for fast local verification without downloading 100+ GB archives.

### 9.6 Reproducible Configuration
- **Configuration Variables**: Configure `BIGEARTHNET_DIR`, `BIGEARTHNET_NUM_CLASSES=19`, and `BIGEARTHNET_SAMPLE_SIZE=1000` in `config.py` and `.env.example`.

### 9.7 Expected Next Implementation Steps (Phase 2 Roadmap)
1. Define dataset path variables in `config.py`.
2. Construct the 1,000-patch validation subset archive structure.
3. Implement `scientific/datasets/bigearthnet.py` PyTorch `Dataset` & `DataLoader`.
4. Implement band resampling (20m/60m to 10m grid) and percentile normalization helpers.
5. Add automated unit tests in `tests/test_bigearthnet_dataset.py` verifying tensor shapes `(12, 120, 120)` and 19-class label encoding.
