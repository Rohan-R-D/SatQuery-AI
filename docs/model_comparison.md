# Phase 1: Research and Model Selection Report

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 1 Complete — Research & Model Selection Finalized  

---

## 1. Executive Summary & Model Comparison

This report presents a systematic evaluation of Vision-Language Models (VLMs) and deep remote-sensing foundation backbones for integration into the **SatQuery AI** Two-Lane Architecture.

The evaluation covers cloud baselines, domain-adapted remote sensing VLMs, general open-weights multimodal models, and specialized deep learning feature extractors across 6 primary operational tasks:
1. Remote-Sensing Visual Question Answering (RS-VQA)
2. Remote-Sensing Scene Captioning & Land-Cover Summarization
3. Spatial Grounding & Target Localization (Bounding Box Coordinate Prediction)
4. BigEarthNet Multispectral (12-Band Sentinel-2 + 2-Band Sentinel-1 SAR) Land-Cover Adaptation
5. Bi-Temporal Change-VQA & Explanatory Modification Reasoning
6. Optical-SAR Cross-Modal Joint Interpretation

### Evaluation Matrix Summary

| Model ID | Model Name & Version | Primary Classification | Modality Support | VRAM Req. (FP16 / INT4) | License | Inference Engine | `BaseVLMAdapter` Compatibility | Recommended Role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gemini-vlm` | Google Gemini 1.5/2.0 Flash | Existing Gemini baseline | RGB (3-Channel) | 0 GB (Cloud API) | Proprietary Commercial API | `google-genai` SDK | Native ([gemini_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/gemini_adapter.py)) | Active Cloud Baseline |
| `qwen2.5-vl-7b` | Qwen2.5-VL-7B-Instruct | Candidate pretrained model | RGB (Dynamic Native Res) | 16 GB / 8 GB (AWQ) | Apache 2.0 | HuggingFace / vLLM / Ollama | Native ([custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py)) | **Primary Open-Weights VLM Candidate** |
| `geochat-7b` | GeoChat-7B (CVPR 2024) | Candidate pretrained model | RGB (Satellite & Aerial) | 16 GB / 7 GB (4-bit) | Non-Commercial (Vicuna base) | HuggingFace / LLaVA Codebase | Native ([custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py)) | Alternative RS-Specific Candidate |
| `bigearthnet-resnet50` | BigEarthNet Multi-Label Net | Model requiring fine-tuning / adaptation | 12-Band S2 + 2-Band S1 SAR | 2–4 GB | MIT / CC BY 4.0 | PyTorch (`timm` / `torchvision`) | Indirect (Lane A Scientific Feature Scorer) | Scientific Classifier / Feature Extractor |
| `changeformer` | ChangeFormer Bi-Temporal Net | Model requiring fine-tuning / adaptation | Bi-Temporal RGB / S2 | 4–6 GB | Apache 2.0 | PyTorch Model Forward | Indirect (Lane A Change Mask Generator) | Pixel-Dense Change Mask Engine |
| `skysense-remoteclip` | RemoteCLIP / SkySense | Candidate pretrained model | RGB & Multispectral | 4–8 GB | Apache 2.0 / CC BY-NC | HuggingFace / OpenCLIP | Indirect (Embedding Scorer) | Zero-Shot Embedding & Feature Scorer |
| `qwen2.5-vl-72b` | Qwen2.5-VL-72B-Instruct | Model unsuitable for hardware / project reqs | RGB (Dynamic Resolution) | >80 GB VRAM | Apache 2.0 | vLLM (Multi-GPU Cluster) | Native ([custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py)) | Unsuitable (Prohibitive VRAM Hardware Req) |

*The complete CSV dataset is archived at [experiments/model_selection.csv](file:///e:/SatQuery%20AI/experiments/model_selection.csv).*

---

## 2. Existing Baseline Analysis: Google Gemini Multimodal VLM

The existing cloud baseline uses Google Gemini 1.5/2.0 Flash via the `google-genai` SDK ([services/gemini_service.py](file:///e:/SatQuery%20AI/backend/services/gemini_service.py)).

### Capabilities & Strengths
- **Zero Local Hardware Requirement**: Runs via HTTPS calls to Google Cloud API, requiring 0 GB local GPU VRAM.
- **Multimodal Visual Reasoning**: Handles single-image VQA, multi-image bi-temporal change explanations (Image 1 = Before, Image 2 = After, Image 3 = Difference Overlay), and joint Optical + SAR cross-modal prompts.
- **Structured JSON Schema Enforcement**: Uses Pydantic `GenerateContentConfig` schemas (`GeminiVQAOutput`, `GeminiGroundingOutput`, `GeminiOpticalSarOutput`) to enforce strict return JSON types.
- **Spatial Grounding**: Returns pixel bounding boxes `{"x", "y", "width", "height", "label"}`.

### Limitations & Risks
- **External Network & API Key Dependency**: Fails gracefully with `MISSING_API_KEY` or `API_ERROR` if offline or unconfigured.
- **Privacy & Air-Gap Constraint**: Cannot be deployed in offline or high-security air-gapped sovereign environments.
- **RGB Input Constraint**: Standard API accepts 3-channel RGB imagery (`bytes`). Raw 12-band Sentinel-2 GeoTIFFs or complex polarimetric SAR arrays must be rendered into 3-channel RGB composites before invocation.

---

## 3. Recommended Candidate Model: Qwen2.5-VL-7B-Instruct

### Justification & Key Metrics
**Qwen2.5-VL-7B-Instruct** (released by Alibaba Cloud / Qwen Team in 2025) is selected as the **Primary Open-Weights VLM Candidate** for SatQuery AI.

1. **Native Spatial Grounding**: Out-of-the-box support for fine-grained target grounding. Outputs normalized coordinates `<|box_start|>(y1,x1),(y2,x2)<|box_end|>` mapped to an explicit $[0, 1000]$ coordinate grid, enabling sub-pixel feature bounding.
2. **Dynamic Resolution Visual Encoder**: Adapts dynamically to high-resolution satellite imagery without aggressive downsampling, preserving small remote sensing objects (e.g., individual structures, small water bodies, vessels, runways).
3. **Multi-Image Temporal Reasoning**: Supports arbitrary multi-image context sequences natively, making it directly compatible with `ChangeAgent` bi-temporal pairs and `FusionAgent` Optical + SAR multi-sensor pairs.
4. **Permissive Open License (Apache 2.0)**: Fully open for commercial deployment, redistribution, and hackathon presentation without restrictive non-commercial terms.
5. **Flexible Hardware Footprint**: 
   - Full FP16 precision: ~16 GB VRAM.
   - 4-bit AWQ / INT4 quantized precision: **~7.5–8 GB VRAM**, allowing single-GPU deployment on consumer GPUs (NVIDIA RTX 3090, 4090, or cloud T4 instances).

---

## 4. Alternative Candidate Models

### 4.1 GeoChat-7B (CVPR 2024)
- **Description**: Developed by MBZUAI, GeoChat is built on Vicuna-7B / LLaVA-1.5 and fine-tuned on 318k remote-sensing instruction pairs (RSVQA, RSICD, RSSCN7, PatternNet).
- **Strengths**: Domain-specific fine-tuning on aerial and satellite imagery; understands remote-sensing terminology natively (e.g., "apron", "runway", "canopy density", "built-up urban").
- **Limitations**: Restricted by Vicuna non-commercial license; fixed-resolution CLIP vision backbone (336x336 / 448x448 px) causes spatial details to blur on large rasters; lacks native 12-band input tensor support.

### 4.2 BigEarthNet Multi-Label Classifier (ResNet-50 / ViT)
- **Description**: Trained on the BigEarthNet dataset (590k Sentinel-2 12-band patches and Sentinel-1 SAR patches across 19 CORINE land-cover classes).
- **Role**: Serves as a **Lane A Scientific Feature Scorer** rather than a conversational VLM.
- **Integration**: Can be loaded as a local PyTorch module in `scientific/datasets/bigearthnet.py` to extract quantitative land-cover class probability vectors (e.g., `Urban Fabric: 78%`, `Coniferous Forest: 12%`) that feed into Lane C fact-checking verification.

---

## 5. Hardware & Deployment Requirements

| Model Configuration | VRAM Requirement | Minimum GPU Hardware | Quantization Strategy | Inference Server Option |
| --- | --- | --- | --- | --- |
| **Gemini 1.5 Flash (Baseline)** | 0 GB | None (Cloud API) | N/A (Hosted) | Google GenAI API Client |
| **Qwen2.5-VL-7B (FP16)** | ~16 GB | NVIDIA RTX 3090 / A10G / T4 (x2) | FP16 / BF16 | vLLM (v0.7+) / HuggingFace `transformers` |
| **Qwen2.5-VL-7B (AWQ / 4-bit)** | **~7.5 GB** | **NVIDIA RTX 3060 (12GB) / RTX 4070 / T4** | **AWQ / GPTQ / GGUF** | **vLLM / Ollama (`ollama run qwen2.5-vl`)** |
| **GeoChat-7B (4-bit)** | ~7.0 GB | NVIDIA RTX 3060 (12GB) / T4 | 4-bit BitsAndBytes / AWQ | HuggingFace `transformers` + LLaVA |
| **BigEarthNet ResNet-50** | ~2.5 GB | Any CUDA GPU or CPU | FP32 / FP16 | PyTorch (`torchvision` / `timm`) |

---

## 6. Repository Integration Architecture

The shortlisted open-weights model (Qwen2.5-VL-7B) integrates cleanly into SatQuery AI's existing architecture via [custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py) without altering API schemas or breaking existing endpoints:

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
                                                              (Qwen2.5-VL-7B-Instruct)
```

### Integration Workflow
1. **Adapter Resolution**: `get_active_vlm_adapter()` in [model_adapter.py](file:///e:/SatQuery%20AI/backend/ai/adapters/model_adapter.py) reads `ACTIVE_VLM_PROVIDER`. If set to `custom`, `qwen`, or `local`, it returns `custom_rs_vlm_adapter`.
2. **Specialist Agents**: All specialist agents ([vqa_agent.py](file:///e:/SatQuery%20AI/backend/agents/vqa_agent.py), [grounding_agent.py](file:///e:/SatQuery%20AI/backend/agents/grounding_agent.py), [change_agent.py](file:///e:/SatQuery%20AI/backend/agents/change_agent.py), [fusion_agent.py](file:///e:/SatQuery%20AI/backend/agents/fusion_agent.py)) execute against `get_active_vlm_adapter()`.
3. **Endpoint Client**: `CustomRSVLMAdapter` implements `BaseVLMAdapter` methods by issuing HTTP requests to an internal vLLM or Ollama inference endpoint (`http://localhost:11434/api/generate` or `http://localhost:8000/v1/chat/completions`).
4. **Coordinate Regex Parsing**: Grounding response string `<|box_start|>(y1,x1),(y2,x2)<|box_end|>` is parsed via regular expressions and converted into standard pixel bounding box dictionaries `{"x", "y", "width", "height", "label"}`.

---

## 7. Task Compatibility Analysis

| Operational Task | Gemini Baseline Compatibility | Qwen2.5-VL-7B Compatibility | BigEarthNet Classifier Role | Technical Handling |
| --- | --- | --- | --- | --- |
| **Single-Image VQA** | Native | Native | N/A | Prompt passed with image bytes; returns text answer & evidence list. |
| **Scene Captioning** | Native | Native | Provides 19-class probability vector | Generates land-cover summary and canopy density breakdown. |
| **Spatial Grounding** | Native (JSON boxes) | Native (Normalized $[0-1000]$ tokens) | N/A | Coordinate regex parser converts model tokens into pixel $[x, y, w, h]$. |
| **BigEarthNet Adaptation** | N/A (3-band RGB only) | RGB Composite rendering | Native (12-Band S2 + 2-Band S1) | PyTorch `Dataset` loader extracts 12-band arrays for scientific classification. |
| **Change-VQA** | Native (Multi-Image) | Native (Multi-Image) | N/A | Passes T1, T2, and difference overlay bytes; explains surface change. |
| **Optical-SAR Fusion** | Native (Multi-Image) | Native (Multi-Image) | Native dual-pol SAR support | Combines Sentinel-2 optical reflectance with Refined Lee filtered SAR backscatter. |

---

## 8. Technical Risks & Mitigation Strategies

1. **Coordinate Token Scaling Mismatch**:
   - *Risk*: Qwen2.5-VL outputs normalized $[0, 1000]$ coordinates, whereas the UI requires absolute pixel coordinates $(w, h)$.
   - *Mitigation*: Implement a coordinate scaling parser in `CustomRSVLMAdapter` that multiplies normalized values by $(w/1000, h/1000)$.
2. **Local Model Startup & Memory Overhead**:
   - *Risk*: Loading 7B model weights directly inside FastAPI process causes out-of-memory (OOM) crashes and blocks HTTP worker threads.
   - *Mitigation*: Decouple model serving into a standalone vLLM / Ollama container or process; `CustomRSVLMAdapter` communicates via lightweight async HTTP calls (`httpx`).
3. **Multispectral (12-Band) vs RGB Compatibility**:
   - *Risk*: Open VLMs accept 3-channel RGB inputs, losing infrared / SWIR spectral channels.
   - *Mitigation*: Lane A (`raster_loader.py` & `normalization.py`) generates calibrated 3-channel RGB composites (e.g. False-Color Infrared Band 8-4-3 or SAR VV-VH-Ratio composite) before sending image bytes to the VLM.

---

## 9. Research References & Links

1. **Qwen2.5-VL Technical Report & Repository**:
   - Repository: [github.com/QwenLM/Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL)
   - License: Apache 2.0
2. **GeoChat: Grounded Large Vision-Language Model for Remote Sensing**:
   - Paper: CVPR 2024 ([arxiv.org/abs/2311.15826](https://arxiv.org/abs/2311.15826))
   - Code: [github.com/MBZUAI-ORF/GeoChat](https://github.com/MBZUAI-ORF/GeoChat)
3. **BigEarthNet Large-Scale Remote Sensing Benchmark**:
   - Paper: EuroSIPP / TU Berlin ([bigearth.net](https://bigearth.net/))
   - Code & Archive: [github.com/kuzand/BigEarthNet-S2-tools](https://github.com/kuzand/BigEarthNet-S2-tools)
4. **ChangeFormer: A Transformer-Based Siamese Network for Change Detection**:
   - Paper: IEEE TGRS 2022 ([arxiv.org/abs/2201.01293](https://arxiv.org/abs/2201.01293))
5. **Google Gemini API Documentation**:
   - SDK: [github.com/googleapis/python-genai](https://github.com/googleapis/python-genai)

---

## 10. Exact Next Step for Phase 2

**Phase 2 Task**: **Implement the `CustomRSVLMAdapter` HTTP Endpoint Client & Grounding Token Parser**.

- **Goal**: Write the vLLM / Ollama API client inside `CustomRSVLMAdapter` in [custom_rs_vlm_adapter.py](file:///e:/SatQuery%20AI/backend/ai/models/custom_rs_vlm_adapter.py) to enable live open-weights inference against local endpoints (`ACTIVE_VLM_PROVIDER=custom`), and add the regex coordinate parser for target grounding.
