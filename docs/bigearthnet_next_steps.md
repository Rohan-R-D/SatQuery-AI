# BIFOLD BigEarthNet v2.0 Classifier Guide — SatQuery AI

**Author**: Member 3 (AI/ML Lead)  
**Date**: September 20, 2026  
**Status**: LOCAL CLASSIFIER IMPLEMENTED & TESTED  
**Repository Branch**: `feature/member3-ai-ml-training`

---

## 1. Model & Checkpoint Specifications

SatQuery AI uses the official BIFOLD BigEarthNet v2.0 ResNet-50 Sentinel-2 pretrained checkpoint (`BIFOLD-BigEarthNetv2-0/resnet50-s2-v0.2.0`).

BigEarthNet operates **STRICTLY LOCALLY**:
- Pretrained weights loaded from `backend/scientific/weights/resnet50-s2-v0.2.0`.
- Format: `model.safetensors` PyTorch state dict.
- Input Patch Size: **120 x 120** spatial grid.
- Input Channels: **10 Sentinel-2 bands** (`B02, B03, B04, B05, B06, B07, B08, B8A, B11, B12` — 60m B01 & B09 excluded).
- Output: 19-class CORINE multi-label land-cover probabilities.

| Specification | Details |
| :--- | :--- |
| **Model Checkpoint** | `BIFOLD-BigEarthNetv2-0/resnet50-s2-v0.2.0` |
| **Checkpoint Path** | `backend/scientific/weights/resnet50-s2-v0.2.0` |
| **Input Shape** | `(10, 120, 120)` float32 tensor |
| **Normalization** | ReBEN Channel Mean & Std: `(X - Mean) / Std` |
| **Target Classes** | 19 CORINE land-cover classes |

---

## 2. Channel Normalization Statistics

Official BIFOLD reBEN 10-band Sentinel-2 statistics:
- **Mean**: `[1348.6, 1222.8, 1238.4, 1374.0, 1756.2, 2404.9, 2636.5, 2772.3, 2736.6, 1928.3]`
- **Std**: `[897.6, 843.2, 989.4, 911.8, 977.8, 1162.7, 1269.4, 1290.4, 1228.3, 1079.8]`

---

## 3. Classifier Implementation & Evidence Fusion

Implemented in `backend/ai/classifiers/bigearthnet_classifier.py`:

- **Class**: `BigEarthNetClassifier(BaseRSClassifier)`
- **Lazy Loading**: `safetensors.torch.load_file` or `torch.load` reads `model.safetensors` on first inference call.
- **Evidence Fusion**: Land-cover predictions (`land_cover_predictions`) are injected into `ScientificEvidence` and formatted for VLM prompts in `format_evidence_for_prompt()`.

---

## 4. Test Suite & Verification

- **Unit Tests**: `backend/tests/test_classifier_interface.py` & `backend/tests/test_evidence_fusion.py` (Passed).
- **Preprocessing Validation**: Verified 10-band $120 \times 120$ patch resizing and channel normalization.
- **Unconfigured Error Handling**: Returns structured error `CLASSIFIER_WEIGHTS_UNCONFIGURED` when weights are missing.
