# Phase 4 Preparation — Spatial Grounding & Extensible Model Architecture

**Author**: Member 3 (AI/ML Lead)  
**Date**: September 20, 2026  
**Status**: ARCHITECTURE PREPARED & TESTED  
**Repository Branch**: `feature/member3-ai-ml-training`

---

## 1. Grounding Architecture Overview

Phase 4 introduces spatial object grounding and region localization to SatQuery AI. To support disparate Vision-Language Models (such as GeoChat, Qwen2.5-VL, and future fine-tuned RS checkpoints) without hardcoding model-specific assumptions, a provider-independent grounding architecture has been established in `backend/ai/grounding_interface.py`.

```mermaid
flowchart TD
    subgraph Client/Agent Request
        REQ[GroundingRequest\nimage_bytes, query, coordinate_convention]
    end

    subgraph BaseGroundingAdapter Interface
        BA[BaseGroundingAdapter\nsupports_grounding(), locate_grounded_regions()]
    end

    subgraph Adapters (Phase 4 Candidates)
        GC[GeoChat Grounding Adapter\nRegion tokens -> BBoxes]
        QW[Qwen2.5-VL Grounding Adapter\nAbsolute pixels -> BBoxes]
        GM[Gemini Baseline Adapter\nUnsupported Fallback]
    end

    subgraph Coordinate Validation & Scaling
        VAL[validate_grounding_coordinates\nCheck degenerate bounds]
        SCL[scale_normalized_coordinates\nNormalize 1000/1 -> Pixel]
    end

    subgraph Standard Response
        RESP[GroundingResponse\nanswer, bounding_boxes, coordinate_convention, capability_supported]
    end

    REQ --> BA
    BA --> GC
    BA --> QW
    BA --> GM
    GC --> VAL
    QW --> VAL
    VAL --> SCL
    SCL --> RESP
    GM --> RESP
```

---

## 2. Core Grounding Schemas & Coordinate Conventions

Defined in `backend/ai/grounding_interface.py`:

### Supported Coordinate Conventions (`CoordinateConvention`):
1. **`PIXEL`**: Absolute pixel coordinates `[x1, y1, x2, y2]`.
2. **`NORMALIZED_1000`**: Integer range `[0, 1000]` used by legacy Qwen2-VL tokenizers `[y1, x1, y2, x2]`.
3. **`NORMALIZED_1`**: Floating point range `[0.0, 1.0]` `[x1, y1, x2, y2]`.
4. **`GEO_COORDINATE`**: WGS84 geographic bounding boxes `[min_lon, min_lat, max_lon, max_lat]`.

### Schemas:
- **`GroundingBox`**: `label: str`, `box: List[float]`, `confidence: Optional[float]`, `polygon: Optional[List[List[float]]]`, `attributes: Dict[str, Any]`.
- **`GroundingRequest`**: `image_bytes`, `query`, `image_width`, `image_height`, `target_labels`, `coordinate_convention`.
- **`GroundingResponse`**: `answer`, `bounding_boxes`, `source_model`, `provider`, `coordinate_convention`, `capability_supported`, `is_error`, `error_code`, `warnings`.

---

## 3. Strict Anti-Hallucination & Fake Coordinate Principles

To ensure scientific integrity:
1. **No Fake Bounding Boxes**: The architecture explicitly forbids inventing bounding box coordinates or converting plain-language text descriptions into fake spatial boxes.
2. **Unsupported Capability Handling**: When a model (e.g., Gemini 1.5 Flash baseline or unconfigured endpoint) does not support native spatial bounding box output, it returns `capability_supported=False` with `error_code="GROUNDING_UNSUPPORTED"`, rather than dummy coordinates.
3. **Validation Gates**: All predicted bounding box coordinates pass through `validate_grounding_coordinates()`. Degenerate boxes (`x2 <= x1` or `y2 <= y1`), negative coordinates, or out-of-bounds coordinates are flagged with warning messages.

---

## 4. Land-Cover Classifier Separation

Non-conversational multi-label land-cover classifiers (such as BigEarthNet ResNet-50 / ViT) have been strictly decoupled from text-generative VLMs.

- **Location**: `backend/ai/classifiers/`
- **Abstract Interface**: `BaseRSClassifier` in `backend/ai/classifiers/base_classifier.py`
- **Adapter**: `BigEarthNetClassifier` in `backend/ai/classifiers/bigearthnet_classifier.py`
- **Role**: Multi-label classifiers output structured 19-class CORINE probability vectors over Sentinel-1/2 multi-band rasters. Their outputs feed directly into the `ScientificEvidence` layer (`Lane A`), which is subsequently injected into VLM prompts (`Lane B`) for evidence-grounded VQA.

---

## 5. Verification & Unit Testing

All Phase 4 preparation interfaces have been thoroughly covered by unit tests:

- `backend/tests/test_grounding_interface.py`:
  - `test_grounding_box_validation_valid`
  - `test_coordinate_validation_pixel`
  - `test_coordinate_scaling_normalized_1000_to_pixel`
  - `test_grounding_response_schema`
  - `test_grounding_response_unsupported`
  - `test_base_grounding_adapter_fallback`
- `backend/tests/test_classifier_interface.py`:
  - `test_bigearthnet_classifier_unconfigured`
  - `test_bigearthnet_classifier_custom_threshold`

All tests pass cleanly in the backend test suite.
