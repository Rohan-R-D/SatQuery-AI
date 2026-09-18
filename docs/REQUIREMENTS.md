# Requirements: SatQuery AI (SIH 2026, ISRO PS SIH26167)

## 1. System Overview
SatQuery AI is an agentic vision-language remote-sensing analysis platform designed for complex satellite imagery interpretation, spatial reasoning, change analysis, and multimodal optical-SAR fusion.

## 2. Core Functional Tasks
The system must support six primary remote-sensing analysis tasks:

1. **`single_image_vqa` (Single Image Visual Question Answering)**
   - Answers natural language questions regarding terrain, features, infrastructure, and environmental conditions on single satellite scenes.
2. **`captioning` / `image_captioning` (Scene Captioning)**
   - Synthesizes comprehensive, grammatically sound descriptions of satellite scene compositions, land cover, and dominant geographical entities.
3. **`grounding` / `region_grounding` (Spatial Grounding)**
   - Localizes requested entities, facilities, or geographical features with bounding box coordinates `[x, y, width, height]`.
4. **`bi_temporal_change` (Bi-Temporal Change Detection)**
   - Computes quantitative surface changes, pixel change percentage, and localized bounding regions between pre-event (T1) and post-event (T2) scenes.
5. **`change_vqa` (Bi-Temporal Change VQA)**
   - Performs comparative visual question answering across temporal scene pairs, explaining the nature, severity, and context of physical modifications.
6. **`optical_sar_fusion` (Optical + SAR Cross-Modal Analysis)**
   - Fuses multi-sensor inputs (optical spectral bands + Synthetic Aperture Radar polarizations) for penetrating cloud cover, identifying surface roughness, and assessing all-weather conditions.

## 3. Two-Lane Intelligence Architecture Requirements
- **Lane A (Deterministic Scientific Engine)**:
  - Responsible for all quantitative calculations, spectral index derivations (NDVI, NDWI, MNDWI), SIFT/RANSAC feature co-registration, Lee speckle filtering for SAR, and structural difference computations.
  - Lane A must hold exclusive authority over mathematical and numerical metrics.
- **Lane B (Vision-Language Model Interpretation)**:
  - Interprets visual features, parses user query context, and translates semantic visual cues into conversational answers.
  - Lane B must never unilaterally invent or estimate quantitative metrics (e.g., exact change percentages or spatial areas).
- **Lane C (Verification & Alignment Layer)**:
  - Cross-checks Lane B assertions against Lane A empirical metrics.
  - Detects semantic-vs-quantitative hallucinations (e.g., VLM claiming severe flood expansion when Lane A computes 0.02% water index change).
  - Penalizes confidence scores and appends transparent limitations to output evidence.

## 4. Scientific Gating & Precision Constraints
- **Co-Registration Quality Gate**:
  - Pre-alignment between bi-temporal scenes or optical-SAR pairs must achieve Root Mean Square Error (RMSE) **<= 0.8 pixels** before proceeding to change detection.
  - If RMSE > 0.8 px, the system must trigger a co-registration warning, apply a severe confidence penalty, or reject unaligned comparison.
- **Speckle Suppression**:
  - SAR intensity rasters must undergo spatial despeckling (e.g., Refined Lee filter) prior to feature matching and amplitude thresholding.
- **Spectral Index Validation**:
  - Ratios must be clamped to the valid scientific range `[-1.0, 1.0]`, handling invalid/nodata values gracefully via masks.

## 5. Model Registry & Pipeline Hierarchy
- **`gemini-vlm`**: Active `temporary_baseline` multimodal foundation model (Gemini 2.5 Flash / 2.0 Flash fallback).
- **`opencv-change`**: Active `baseline` deterministic image processing pipeline.
- **Candidate Models (Future Integrations)**:
  - `geochat-rs`: Domain-adapted 7B remote sensing VLM candidate for specialized geospatial QA.
  - `qwen3-vl-rs`: High-resolution vision-language model candidate for dense grounding.
  - `changeformer`: Siamese transformer candidate for deep bi-temporal change detection.
  - `grama-fusion`: Cross-modal attention network candidate for optical-SAR joint representation.

## 6. Supported File Formats & Ingestion Constraints
- Supported input formats: **GeoTIFF / TIFF (`.tif`, `.tiff`)**, **PNG (`.png`)**, **JPEG (`.jpg`, `.jpeg`)**.
- Image size limit: Hard threshold of **50,000,000 pixels (50 MP)** (`MAX_FILE_SIZE_MB = 50 MB`).
- Images exceeding thresholds or failing header validation must be rejected with HTTP 413 or HTTP 400.

## 7. Confidence Calibration & Evidence Rules
- **Multi-Factor Confidence Assessment**:
  - Confidence (0-100%) computed via 5 weighted factors:
    1. Input Image Quality & Resolution
    2. Co-registration Alignment Precision (RMSE penalty)
    3. Tool / Model Agreement (Lane A vs Lane B)
    4. Mask & Spatial Evidence Density
    5. Prompt / Query Relevance and Coverage
- **Evidence Integrity**:
  - Every `evidence` item returned to the client must declare:
    - `source` (e.g., `"Lane-A: OpenCV Differencing"`, `"Lane-B: Gemini-VLM"`, `"Lane-A: SIFT Co-registration"`)
    - `limitations` (array of strings, e.g., `["Uncalibrated optical lighting", "RMSE: 0.65 px"]`)
    - `type` (`image`, `bbox`, `mask`, `metrics`, `geojson`)

## 8. Non-Functional Requirements
- **Performance & Latency**: API endpoints must respond within 90s (client timeout threshold). CPU-heavy processing must execute asynchronously off the main event loop.
- **Compatibility**: The backend MUST preserve compatibility with existing React frontend payloads (`frontend/src/services/api.ts`).
- **Reliability & Multi-Worker Safety**: Execution records and audit logs must persist in SQLite/SQLAlchemy to survive server restarts.
- **Security**: CORS must be locked down to trusted domains; endpoints must be rate-limited and protected against denial of service and decompression bombs.
