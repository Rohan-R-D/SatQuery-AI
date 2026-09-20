# Phase 5 Evaluation Foundation Specification

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  

---

## 1. Overview & Objectives

Phase 3 establishes the lightweight **Evaluation Foundation** to prepare SatQuery AI for systematic model benchmarking in **Phase 5 (Evaluation, Benchmarking, and Reporting)**.

The evaluation engine enables:
1. Standardized logging of VQA and captioning predictions into `EvaluationRecord` instances.
2. Extensible metric computation (Exact Match, Token Similarity, Evidence Consistency).
3. Summary statistic aggregation across test datasets.
4. Explicit flagging of synthetic test fixtures (`is_synthetic=True`) vs. real evaluation samples.

---

## 2. Evaluation Record Schema (`EvaluationRecord`)

Each evaluation sample prediction is logged as a structured JSON record:

```json
{
  "record_id": "8f3b2a1c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "model_id": "gemini-vlm",
  "model_version": "1.5-flash",
  "provider": "google-gemini",
  "dataset_name": "rsvqa_synthetic_test",
  "dataset_split": "test",
  "sample_id": "patch_042",
  "prompt": "Identify land cover categories.",
  "generated_answer": "Discontinuous urban fabric and agricultural pastures.",
  "reference_answer": "Discontinuous urban fabric and agricultural pastures.",
  "metrics": {
    "exact_match": 1.0,
    "token_similarity": 1.0,
    "evidence_consistency": 1.0
  },
  "runtime_ms": 142.5,
  "gpu_info": null,
  "is_error": false,
  "failure_reason": null,
  "timestamp": "2026-09-20T14:45:00Z",
  "is_synthetic": true
}
```

---

## 3. Evaluation Metrics Definition

1. **Exact Match (`exact_match`)**:
   - *Formula*: $1.0$ if normalized prediction string equals reference string; $0.0$ otherwise.
2. **Token Similarity (`token_similarity`)**:
   - *Formula*: Jaccard word token overlap between prediction and reference:
     $$\text{Similarity} = \frac{|T_{\text{pred}} \cap T_{\text{ref}}|}{|T_{\text{pred}} \cup T_{\text{ref}}|}$$
3. **Evidence Consistency (`evidence_consistency`)**:
   - *Formula*: Ratio of scientific evidence keywords referenced in the generated prediction text.
4. **Grounding IoU (`grounding_iou`)** *(Planned for Phase 5)*:
   - *Formula*: Intersection-over-Union between predicted bounding box $[x1, y1, x2, y2]$ and ground truth box.

---

## 4. Phase 5 Integration Roadmap

During Phase 5, the `EvaluationEngine` ([`backend/ai/evaluation.py`](file:///e:/SatQuery%20AI/backend/ai/evaluation.py)) will be integrated with full benchmark test splits:
- **RSVQA Benchmark**: Evaluating single-image remote sensing question answering accuracy.
- **BigEarthNet Test Split**: Evaluating multi-label classification accuracy (Precision, Recall, F1 score).
- **Bi-Temporal Change VQA**: Evaluating change detection explanation accuracy against OpenCV ground-truth masks.
