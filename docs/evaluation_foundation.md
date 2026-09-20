# Evaluation Foundation Guide — SatQuery AI

**Author**: Member 3 (AI/ML Lead)  
**Date**: September 20, 2026  
**Status**: ENGINE IMPLEMENTED & TESTED WITH EXPLICIT MOCK/REAL SEPARATION  
**Repository Branch**: `feature/member3-ai-ml-training`

---

## 1. Overview & Policy

SatQuery AI includes an Evaluation Engine (`backend/ai/evaluation.py`) for logging VQA predictions, computing exact match, token similarity, and evidence consistency metrics, and generating benchmark summary statistics.

### Mandatory Evaluation Policy
1. **Offline / Mock Evaluation (`eval_mode="MOCK_OFFLINE"`)**:
   - Used for unit tests, synthetic dataset fixtures, and offline mock endpoint runs.
   - Flagged with `is_mock=True` and `is_synthetic=True`.
   - Explicitly identified in summary statistics so mock runs are never misrepresented as real model benchmark results.

2. **Real Model Evaluation (`eval_mode="REAL_BENCHMARK"`)**:
   - Reported ONLY when actual remote model endpoints (Qwen, GeoChat) or real local checkpoints (BigEarthNet) successfully respond.
   - Flagged with `is_mock=False`.

---

## 2. Metrics & Engine Structure

- **Exact Match (`exact_match`)**: Normalized string equivalence ratio.
- **Token Similarity (`token_similarity`)**: Jaccard word token overlap ratio.
- **Evidence Consistency (`evidence_consistency`)**: Ratio of scientific evidence terms cited in VLM responses.
- **`EvaluationRecord`**: Structured dataclass capturing `record_id`, `model_id`, `provider`, `dataset_name`, `metrics`, `is_synthetic`, `is_mock`, and runtime.
- **`EvaluationEngine`**: Aggregates records and computes summary statistics with explicit `mock_records`, `real_records`, and `eval_mode` counts.

---

## 3. Test Suite & Verification

- **Unit Tests**: `backend/tests/test_evaluation_foundation.py` (Passed).
- **Mock vs Real Separation Verified**: Engine accurately flags `MOCK_OFFLINE` when mock records are processed and `REAL_BENCHMARK` when real endpoints respond.
