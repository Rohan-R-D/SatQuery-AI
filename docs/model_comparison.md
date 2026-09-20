# Phase 1: Research and Model Selection Report

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 1 Complete — Final Cleanup & Research Qualification  

---

## 1. Executive Summary & Categorized Model Evaluation

This report presents a systematic evaluation of Vision-Language Models (VLMs), multispectral classification backbones, bi-temporal change detection architectures, and embedding models for potential integration into the **SatQuery AI** Two-Lane Architecture.

### Model Taxonomy & 6-Category Classification

To maintain strict architectural boundaries and avoid confusing scientific components with conversational engines, models are organized into 6 distinct categories:

1. **Conversational VLMs**: General auto-regressive multimodal vision-language models capable of open-domain VQA, scene captioning, multi-image temporal reasoning, and spatial grounding (e.g., Gemini 1.5 Flash, Qwen2.5-VL-7B).
2. **Remote-Sensing VLMs**: Specialized vision-language models fine-tuned on satellite and aerial instruction datasets for remote-sensing specific VQA and region captioning (e.g., GeoChat-7B).
3. **Multispectral Classification Models**: Deep convolutional or vision transformer backbones trained on multi-band satellite rasters for quantitative land-cover multi-label classification (e.g., ResNet-50 / ViT backbones on BigEarthNet; non-conversational).
4. **Change-Detection Models**: Siamese neural networks designed specifically for generating pixel-dense binary change masks from temporal image pairs (e.g., ChangeFormer; non-conversational).
5. **Embedding and Retrieval Models**: Contrastive vision-language encoders (CLIP-style) used for cross-modal similarity scoring, feature extraction, and zero-shot retrieval (e.g., RemoteCLIP / SkySense).
6. **Scientific Processing Components**: Deterministic computer vision algorithms (SIFT, RANSAC, OpenCV morphological difference, Refined Lee SAR speckle filtering, spectral index calculators).

---

### Evaluation Matrix Summary

| Model ID | Model Name & Version | Model Category | Integration Status (Research / Arch. / Planned / Impl. / Tested) | Modality Support | VRAM Req. (Inference / FT Est.) | Dataset License | Checkpoint License | Code License | Inference Engine | Evidence Level | Recommended Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gemini-vlm` | Google Gemini 1.5/2.0 Flash | Conversational VLM | High / Compatible / Active Baseline / Implemented / Unit Tested (41 passed, 4 warnings) | RGB (3-Channel) | 0 GB / N/A (Cloud API) | Proprietary | Hosted Cloud API | Google GenAI SDK | `google-genai` SDK | Verified from official source & Backend Unit Tested | Active Cloud Baseline |
| `qwen2.5-vl-7b` | Qwen2.5-VL-7B-Instruct | Conversational VLM | High / Compatible / Planned Candidate / Stub Only / Not Tested | RGB (Dynamic Res) | ~16 GB (FP16) / ~7.5–8 GB (4-bit AWQ est.) [FT: ~16-24GB QLoRA] | N/A (Model Card) | Apache 2.0 (Official Model Card) | Apache 2.0 (QwenLM Code) | HuggingFace / vLLM / Ollama | Verified from official source & Estimated | **Primary Open-Weights VLM Candidate** |
| `geochat-7b` | GeoChat-7B (CVPR 2024) | Remote-Sensing VLM | Moderate / Compatible / Alternative Candidate / Not Implemented / Not Tested | RGB (Aerial & Satellite) | ~16 GB (FP16) / ~7 GB (4-bit est.) [FT: ~16-24GB QLoRA] | N/A (Model Weight) | Non-Commercial (Vicuna base) | Apache 2.0 / LLaVA codebase | HuggingFace / LLaVA engine | Reported by research paper | Alternative RS-Specific Candidate |
| `bigearthnet-resnet50` | BigEarthNet Multi-Label Backbone | Multispectral Classification Model | High / Compatible / Planned Candidate / Not Implemented / Not Tested | 12-Band S2 + 2-Band S1 SAR | ~2–4 GB (Inference Est.) [FT: ~8-12GB Full FT] | CDLA-Permissive-1.0 (v1.0) / CC BY 4.0 (v2.0 reBEN) | Requires verification (Pending Phase 2) | MIT / Apache 2.0 (TU Berlin) | PyTorch (`timm` / `torchvision`) | Reported by research paper | Scientific Classifier / Feature Scorer |
| `changeformer` | ChangeFormer Bi-Temporal Net | Change-Detection Model | High / Compatible / Planned Candidate / Not Implemented / Not Tested | Bi-Temporal RGB / S2 | ~4–6 GB (Inference Est.) [FT: ~12-16GB Full FT] | N/A (Paper Architecture) | Apache 2.0 (GitHub weights) | Apache 2.0 | PyTorch model forward | Reported by research paper | Pixel-Dense Change Mask Engine |
| `skysense-remoteclip` | RemoteCLIP / SkySense | Embedding/Retrieval Model | Moderate / Compatible / Planned Candidate / Not Implemented / Not Tested | RGB & Multispectral | ~4–8 GB (Inference Est.) [FT: ~12-16GB Full FT] | N/A (Pretrained Encoder) | Apache 2.0 / CC BY-NC | Apache 2.0 / OpenCLIP | HuggingFace / OpenCLIP | Reported by research paper | Zero-Shot Feature & Embedding Scorer |
| `qwen2.5-vl-72b` | Qwen2.5-VL-72B-Instruct | Conversational VLM | Unsuitable / Incompatible / Not Planned / Not Implemented / Not Tested | RGB (Dynamic Res) | >80 GB VRAM (Inference Est.) | N/A (Model Card) | Qwen Research License Agreement | Apache 2.0 (QwenLM Code) | vLLM (Multi-GPU Cluster) | Verified from official source | Unsuitable (Excessive VRAM Hardware Req) |

*The complete CSV dataset is archived at [`experiments/model_selection.csv`](file:///e:/SatQuery%20AI/experiments/model_selection.csv).*

---

## 2. Existing Baseline Analysis: Google Gemini Multimodal VLM

- **Category**: Conversational VLM
- **Integration Status**: `Implemented (Active Baseline)`
- **Evidence Level**: `Verified from official source` & `Backend Adapter Unit Tested`

### Verified Test Results & Qualifications
Backend verification results executed during repository audits are reported as follows:
- **Backend Unit Tests Executed**: **41 tests passed, 4 warnings** (pytest plugin autoload was disabled via `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"` to bypass broken third-party entrypoints).
- **Warnings Overview**: 1 Starlette `python_multipart` pending deprecation warning, 3 PIL `DecompressionBombWarning` alerts on oversized image upload security tests.
- **Backend Adapter Scope**: Unit tests verify `BaseVLMAdapter` interface compliance, `GeminiAdapter` initialization, `CustomRSVLMAdapter` unconfigured fallback dictionary responses (`is_error=True`, `confidence=0`), schema validation, and task routing.
- **Live Gemini API Inference**: Supported via external Cloud API HTTPS calls (`google-genai` SDK). Tested manually during development, but live cloud API latency, token costs, and real-world network reliability are unmeasured in automated unit test suites.
- **Task-Level Evaluation**: Formal dataset-level VQA accuracy metrics on benchmarks like RSVQA, RSICD, or BigEarthNet have **not been tested yet** (scheduled for Phase 5 Evaluation).

---

## 3. Open-Weights Candidate Models

### 3.1 Qwen2.5-VL-7B-Instruct
- **Category**: Conversational VLM
- **Integration Status**: `Architecturally Compatible (Planned Candidate)` *(Not implemented or tested with live weights in this repository yet)*
- **Evidence Level**: `Verified from official source` & `Estimated` (Hardware memory metrics).

#### Exact License Verification
- **Model Checkpoint License**: **Apache 2.0** (Confirmed via official HuggingFace model card [`Qwen/Qwen2.5-VL-7B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)).
- **Official License Terms**: Subject to standard Apache 2.0 license terms (preservation of copyright notices, disclaimer of warranty, and limitation of liability).
- **Distinction from 72B Variant**: `Qwen2.5-VL-72B-Instruct` is governed by the separate **Qwen Research License Agreement** (free commercial use up to 100M monthly active users; requires license application above 100M MAU).

#### Grounding Format & Required Phase 4 Validation
- **Grounding Output Format**: Official Qwen2.5-VL documentation indicates support for absolute pixel coordinates `{"bbox_2d": [x1, y1, x2, y2]}` based on native image resolution, whereas legacy Qwen2-VL used normalized `[0, 1000]` token coordinates `<|box_start|>(y1,x1),(y2,x2)<|box_end|>`.
- **Validation Status**: **Requires Phase 4 Live Model Endpoint Validation**. The exact string token format, coordinate scaling, and bounding-box conventions must be empirically validated against live vLLM / Ollama outputs before implementing the regex parser in `CustomRSVLMAdapter`. *(No grounding parser was implemented in Phase 1)*.

---

### 3.2 GeoChat-7B (CVPR 2024)
- **Category**: Remote-Sensing VLM
- **Integration Status**: `Architecturally Compatible (Alternative Candidate)` *(Not implemented or tested in this repository yet)*
- **Evidence Level**: `Reported by research paper` (MBZUAI CVPR 2024; https://arxiv.org/abs/2311.15826).

#### Technical Specifications & License
1. **Model Checkpoint License**: **Non-Commercial** (Dependent on Vicuna-1.5 LLM base weights).
2. **Domain Fine-Tuning**: Fine-tuned on 318k remote-sensing instruction pairs (RSVQA, RSICD, RSSCN7, PatternNet). Understands specialized remote sensing terminology natively (e.g., "apron", "runway", "canopy cover", "built-up urban").

---

## 4. Multispectral & Specialized Models

### 4.1 BigEarthNet Multi-Label Classification Backbone (ResNet-50 / ViT)
- **Category**: Multispectral Classification Model *(NOT a conversational VLM or grounding model)*
- **Integration Status**: `Model Requiring Adaptation (Planned Candidate)`
- **Evidence Level**: `Reported by research paper` (TU Berlin / DLR; https://bigearth.net/).

#### Disambiguation: Dataset vs. Model vs. Pretrained Checkpoint
To avoid confusion, BigEarthNet components are clearly separated:
1. **BigEarthNet Dataset**: Benchmark land-cover dataset containing Sentinel-2 multispectral and Sentinel-1 SAR patch pairs.
2. **Model Architecture**: Deep convolutional (ResNet-50) or vision transformer (ViT) backbones configured for multi-label classification across CORINE land-cover classes.
3. **Pretrained Checkpoint**: **No specific pretrained checkpoint selected yet; checkpoint selection is pending during Phase 2.**
4. **Future Adaptation Experiment**: Planned adaptation as a **Lane A Scientific Feature Scorer** in `scientific/datasets/bigearthnet.py` to produce quantitative land-cover probability vectors for Lane C verification.

#### Disambiguated License Terms
- **Dataset License**: **BigEarthNet-MM v1.0** dataset is licensed under **Community Data License Agreement - Permissive - Version 1.0 (CDLA-Permissive-1.0)**. **BigEarthNet v2.0 (reBEN)** dataset is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Model Checkpoint License**: **Requires verification** (depends on specific pretrained checkpoint repository selected in Phase 2).
- **Code License**: **MIT License / Apache 2.0** (Official TU Berlin pipeline repository `rsim-tu-berlin/bigearthnet-pipeline`).

---

### 4.2 ChangeFormer (Siamese Transformer for Change Detection)
- **Category**: Change-Detection Model *(NOT a conversational VLM)*
- **Integration Status**: `Model Requiring Adaptation (Planned Candidate)`
- **Evidence Level**: `Reported by research paper` (IEEE TGRS 2022; https://arxiv.org/abs/2201.01293).

#### Technical Specifications & Role
1. **Primary Function**: Siamese Transformer network that inputs bi-temporal satellite image pairs (T1, T2) and outputs pixel-dense binary change masks.
2. **Repository Role**: Planned integration as an advanced Lane A change detection engine alongside the existing `OpenCVChangeDetector`.

---

## 5. Hardware & Deployment Requirements Matrix

### Hardware & VRAM Metric Qualifications
Hardware metrics are categorized strictly as **Estimations** vs. **Actual Measurements**:
- **VRAM Requirements**: All memory figures are *estimates based on model parameters and standard quantization benchmarks*. No local GPU hardware measurements have been conducted in this repository yet.
- **Inference vs. Fine-Tuning Memory**:
  - *Inference*: Assumes single-batch evaluation (e.g., ~7.5–8 GB VRAM for 4-bit Qwen2.5-VL-7B).
  - *Fine-Tuning*: Assumes gradient storage, optimizer states (AdamW), and activation memory (e.g., ~16–24 GB VRAM for QLoRA fine-tuning; >40 GB for full fine-tuning).
- **Quantization Assumptions**: 4-bit estimates assume AWQ, GPTQ, or BitsAndBytes 4-bit normal float (NF4) quantization.

| Model Configuration | Model Category | VRAM Requirement (Inference Est.) | VRAM Requirement (Fine-Tuning Est.) | Quantization Strategy | Inference Engine Option | Evidence Level |
| --- | --- | --- | --- | --- | --- | --- |
| **Gemini 1.5 Flash (Baseline)** | Conversational VLM | 0 GB | N/A (Hosted) | Hosted Cloud | Google GenAI API Client | Verified from official source |
| **Qwen2.5-VL-7B (FP16)** | Conversational VLM | ~16 GB | >40 GB (Full FT) | FP16 / BF16 | vLLM (v0.7+) / HuggingFace | Estimated |
| **Qwen2.5-VL-7B (AWQ / 4-bit)** | Conversational VLM | **~7.5–8 GB** | **~16–24 GB (QLoRA)** | **AWQ / GPTQ / GGUF** | **vLLM / Ollama (`ollama run qwen2.5-vl`)** | **Estimated** |
| **GeoChat-7B (4-bit)** | Conversational VLM | ~7.0 GB | ~16–24 GB (QLoRA) | 4-bit BitsAndBytes / AWQ | HuggingFace `transformers` + LLaVA | Reported by research paper |
| **BigEarthNet ResNet-50** | Multispectral Classification Model | ~2.5 GB | ~8–12 GB (Full FT) | FP32 / FP16 | PyTorch (`torchvision` / `timm`) | Estimated |

---

## 6. Repository Integration Architecture

The existing backend architecture enforces dynamic model resolution via `BaseVLMAdapter` (`base_model.py`) and `get_active_vlm_adapter()` (`model_adapter.py`):

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
- **Planned Endpoint Integration**: In future VLM integration phases (Phase 4), `CustomRSVLMAdapter` will make async HTTP requests (`httpx`) to a local vLLM / Ollama inference server (`http://localhost:11434/api/generate`) and parse Qwen2.5-VL grounding tokens into standard pixel bounding box dictionaries `{"x", "y", "width", "height", "label"}`.

---

## 7. Technical Risks & Mitigation Strategies

1. **Grounding Coordinate Format Scaling**:
   - *Risk*: Open-weights VLMs (e.g. Qwen2.5-VL) output string tokens that may be normalized [0, 1000] or absolute pixel coordinates depending on model version and prompt format.
   - *Mitigation*: Validate live endpoint outputs in Phase 4 and implement a regex scaling parser inside `CustomRSVLMAdapter`.
2. **Local Model Startup & Memory Overhead**:
   - *Risk*: Loading a 7B model directly inside the FastAPI Python process causes out-of-memory (OOM) crashes and blocks worker threads.
   - *Mitigation*: Decouple model serving into a standalone vLLM or Ollama process/container. `CustomRSVLMAdapter` communicates via lightweight async HTTP calls (`httpx`).
3. **Multispectral (12-Band) vs. RGB Channel Mapping**:
   - *Risk*: Open VLMs accept 3-channel RGB inputs, ignoring SWIR/Infrared bands.
   - *Mitigation*: Lane A (`raster_loader.py` & `normalization.py`) synthesizes calibrated 3-channel RGB composites (e.g., False-Color Infrared Band 8-4-3 or SAR VV-VH-Ratio composite) prior to VLM ingestion, while feeding raw 12-band tensors to the BigEarthNet scientific classifier.

---

## 8. Research References & Source Links

1. **Qwen2.5-VL Technical Report & Model Card**:
   - Official Model Card: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct (Verified: Apache 2.0 License).
   - 72B Model Card: https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct (Verified: Qwen Research License Agreement).
2. **GeoChat: Grounded Large Vision-Language Model for Remote Sensing**:
   - Research Paper: CVPR 2024 (https://arxiv.org/abs/2311.15826).
3. **BigEarthNet Benchmark Datasets**:
   - BigEarthNet-MM v1.0 (CDLA-Permissive-1.0) & BigEarthNet v2.0 reBEN (CC BY 4.0): TU Berlin RSiM / DIMA (http://bigearth.net/; Clasen et al., 2024).
4. **ChangeFormer: A Transformer-Based Siamese Network for Change Detection**:
   - Research Paper: IEEE TGRS 2022 (https://arxiv.org/abs/2201.01293).
5. **Google Gemini API Documentation**:
   - Official SDK: https://github.com/googleapis/python-genai.

---

## 9. Phase 2 Recommendation — Dataset Preparation and BigEarthNet Groundwork

In accordance with the official Work Distribution document, the next phase for Member 3 is **Phase 2 — Dataset Preparation and BigEarthNet Groundwork**. *(Do not recommend grounding parser implementation as Phase 2)*.

### 9.1 Dataset Version Selection & Evaluation Strategy
The project evaluates two versions of the BigEarthNet benchmark:

| Specification | BigEarthNet-MM v1.0 | BigEarthNet v2.0 (reBEN) |
| --- | --- | --- |
| **Release Year** | 2021 (Sumbul et al.) | 2024 (Clasen et al., TU Berlin) |
| **Total Patch Count** | 590,326 patch pairs | 549,488 patch pairs |
| **Sentinel-2 Tiles** | 125 tiles (6 countries) | 115 tiles (10 countries) |
| **Sentinel-1 Scenes** | 325 scenes | 312 scenes (close temporal alignment) |
| **Atmospheric Correction** | Sen2Cor original | Sen2Cor v2.11 (Refined) |
| **Land Cover Labels** | CORINE CLC 2018 (v2018_u1) | CORINE CLC 2018 (v2020_u1, reduced noise) |
| **Dataset License** | CDLA-Permissive-1.0 | CC BY 4.0 |

**Version Selection Status**: **Decision pending in Phase 2 based on subset evaluation.** Both versions will be evaluated on small 1,000-patch test subsets during Phase 2 to determine data cleanliness and preprocessing speed before committing to full archive downloads.

### 9.2 Data Archive Directory Structure
Data archives will be structured in directory hierarchies:
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

### 9.3 Sentinel-2 and Sentinel-1 Data Considerations
- **Sentinel-2 Multi-Resolution Bands**: 10m spatial resolution (B02, B03, B04, B08), 20m spatial resolution (B05, B06, B07, B8A, B11, B12), and 60m spatial resolution (B01, B09, B10). Preprocessing must resample 20m and 60m channels to a uniform 10m grid (120x120 pixels per patch).
- **Sentinel-1 SAR Dual-Pol Channels**: Co-polarized VV and cross-polarized VH backscatter intensity. Preprocessing converts linear intensity to decibel scale (\(\sigma^0\text{ dB}\)) using Refined Lee speckle filtering (`scientific/sar/calibration.py`).

### 9.4 Preprocessing & RGB Composite Requirements
- **Radiometric Stretches**: Min-max and 2%–98% linear percentile reflectance normalization.
- **Nodata & Invalid Pixel Filtering**: Filtering patches with cloud cover or incomplete coverage using dataset valid masks.
- **VLM Preview Synthesis**: Generating 3-channel RGB composites (Natural Color Band 4-3-2 and False-Color Infrared Band 8-4-3) to allow VLM vision encoders to process multi-spectral scenes.

### 9.5 Dataset Loader Architecture Planning
- **Module Path**: `scientific/datasets/bigearthnet.py`
- **Class Design**: PyTorch `Dataset` and `DataLoader` abstractions (`BigEarthNetDataset`) implementing:
  - Multi-band tensor extraction `(12, H, W)` for Sentinel-2.
  - Dual-channel SAR tensor extraction `(2, H, W)` for Sentinel-1.
  - CORINE 19-class multi-label target vector mapping `(19,)`.

### 9.6 Proposed Small-Subset Experiment
- **Planned Experiment Scope**: Extracting a 1,000-patch validation subset (`data/bigearthnet_subset/`) for fast local verification without downloading 100+ GB archives.
- **Validation Mandate**: Sampling strategy, label distribution balance across CORINE 19 classes, and dual-modality (S1+S2) tensor integrity validation will be performed during Phase 2 execution.

### 9.7 Reproducible Configuration
- **Configuration Variables**: Configure `BIGEARTHNET_DIR`, `BIGEARTHNET_NUM_CLASSES=19`, and `BIGEARTHNET_SAMPLE_SIZE=1000` in `config.py` and `.env.example`.

### 9.8 Expected Next Implementation Steps (Phase 2 Roadmap)
1. Define dataset path variables in `config.py`.
2. Construct the 1,000-patch validation subset archive structure.
3. Perform sampling, label distribution, and modality validation.
4. Implement `scientific/datasets/bigearthnet.py` PyTorch `Dataset` & `DataLoader`.
5. Implement band resampling (20m/60m to 10m grid) and percentile normalization helpers.
6. Add automated unit tests in `tests/test_bigearthnet_dataset.py` verifying tensor shapes `(12, 120, 120)` and 19-class label encoding.
