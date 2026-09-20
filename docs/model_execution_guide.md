# SatQuery AI Model Execution & Configuration Guide

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  

---

## 1. Overview

This guide explains how to configure, switch, and deploy Vision-Language Models (VLMs) and specialized remote sensing backbones in **SatQuery AI**.

The system enforces a **1-Model-at-a-Time Execution Strategy**. Models are resolved dynamically via `get_active_vlm_adapter()`, allowing seamless switching between external cloud APIs (Google Gemini) and local open-weights inference servers (vLLM / Ollama).

---

## 2. Environment Configuration & Provider Switching

VLM provider selection is managed via environment variables in `backend/.env`:

```env
# 1. Cloud Baseline (Default)
ACTIVE_VLM_PROVIDER=gemini
GEMINI_API_KEY=your_google_gemini_api_key_here

# 2. Sovereign Local VLM (Future Open-Weights Integration)
# ACTIVE_VLM_PROVIDER=custom
# CUSTOM_VLM_ENDPOINT=http://localhost:11434/api/generate
# CUSTOM_VLM_NAME=Qwen2.5-VL-7B-Instruct
# LOCAL_WEIGHTS_PATH=/path/to/checkpoints/qwen2.5-vl-7b/
```

### Provider Resolution Logic (`ModelAdapterFactory`)

| `ACTIVE_VLM_PROVIDER` Value | Active Adapter Instance | Execution Mode | Requirements |
| --- | --- | --- | --- |
| `gemini` (default) | `GeminiAdapter` | External Cloud API | Valid `GEMINI_API_KEY` in `.env` |
| `custom` / `qwen` / `geochat` | `CustomRSVLMAdapter` | Local Server / Endpoint | Local vLLM / Ollama endpoint |

---

## 3. Hardware Requirements & Quantization Matrix

| Model | Provider | Execution Type | FP16 VRAM (Est.) | 4-Bit Quantized VRAM (Est.) | Recommended GPU Hardware |
| --- | --- | --- | --- | --- | --- |
| **Gemini 1.5 Flash** | `google-gemini` | Cloud API | 0 GB | N/A (Hosted) | None (Runs on Cloud API) |
| **Qwen2.5-VL-7B** | `qwen` | Local Server (vLLM / Ollama) | ~16 GB | **~7.5–8 GB (AWQ)** | NVIDIA RTX 3060 (12GB) / RTX 4070 / T4 |
| **GeoChat-7B** | `geochat` | Local Weights (LLaVA) | ~16 GB | **~7.0 GB (4-bit)** | NVIDIA RTX 3060 (12GB) / T4 |
| **BigEarthNet ResNet-50** | `bigearthnet` | Local PyTorch | ~2.5 GB | N/A (FP32/FP16) | CPU or Any CUDA GPU |
| **ChangeFormer** | `changeformer` | Local PyTorch | ~4.5 GB | N/A (FP32/FP16) | CPU or Any CUDA GPU |

---

## 4. Serving Open-Weights Models (Future Phase 4 Deployment)

To deploy an open-weights model locally without downloading large checkpoints inside the FastAPI process:

### Option A: vLLM Inference Server (Recommended for High Throughput)
```bash
# Launch Qwen2.5-VL-7B server on port 8000
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-7B-Instruct \
    --quantization awq \
    --port 11434
```

### Option B: Ollama Local Server (Recommended for Single-GPU Dev)
```bash
# Pull and serve Qwen2.5-VL via Ollama
ollama run qwen2.5-vl:7b
```

Once the local server is operational, update `backend/.env`:
```env
ACTIVE_VLM_PROVIDER=custom
CUSTOM_VLM_ENDPOINT=http://localhost:11434/api/generate
```

---

## 5. Fallback Behavior & Safety Guarantees

- **Unconfigured Provider**: If `ACTIVE_VLM_PROVIDER=custom` is selected but `CUSTOM_VLM_ENDPOINT` is unconfigured or unreachable, `CustomRSVLMAdapter` returns a structured error payload:
  ```json
  {
    "answer": "[Qwen3-VL-RS-Adapted]: Model checkpoint or endpoint not configured in backend environment.",
    "evidence": ["Custom VLM endpoint unconfigured."],
    "confidence": 0,
    "is_error": true,
    "error_code": "VLM_ENDPOINT_UNCONFIGURED"
  }
  ```
- **Gemini Fallback Models**: If the primary Gemini model experiences quota limits, `GeminiAdapter` automatically retries across fallback models (`gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`).
