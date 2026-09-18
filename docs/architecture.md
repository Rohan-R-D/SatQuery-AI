# Architecture: SatQuery AI (SIH 2026, ISRO PS SIH26167)

## 1. High-Level System Overview
SatQuery AI employs a **Modular FastAPI Monolith** architecture designed for low-overhead hackathon velocity and deterministic satellite imagery interpretation. The system integrates a **Two-Lane Intelligence Model** that decouples quantitative remote-sensing calculations from generative vision-language understanding.

```
                     +----------------------------------+
                     |    React / Vite Web Frontend     |
                     |   (frontend/src/services/api.ts) |
                     +-----------------+----------------+
                                       | HTTP / REST (Multipart / JSON)
                                       v
                     +----------------------------------+
                     |     FastAPI Modular Monolith     |
                     |  - CORS & Rate Limiting Guard    |
                     |  - Input Validation & Image Sec  |
                     +-----------------+----------------+
                                       |
                     +-----------------v----------------+
                     |         Supervisor Agent         |
                     |  - Task Classifier & Router      |
                     |  - Execution Trace Dispatcher    |
                     +--------+----------------+--------+
                              |                |
             +----------------+                +----------------+
             |                                                  |
             v                                                  v
+-----------------------------+                    +-----------------------------+
|    LANE A: SCIENTIFIC       |                    |     LANE B: GENERATIVE      |
|    DETERMINISTIC ENGINE     |                    |     VLM FOUNDATION ADAPTER  |
| - SIFT / RANSAC Alignment   |                    | - Gemini 2.5/2.0 Flash VLM  |
|   (RMSE <= 0.8 px Gate)     |                    | - Prompt Engineering & CoT  |
| - Normalized Diff (NDVI)    |                    | - Candidate RS Models       |
| - Lee Despeckling for SAR   |                    |   (GeoChat, Qwen3-VL)       |
| - OpenCV Difference Engine  |                    | - Qualitative Descriptions  |
+--------------+--------------+                    +--------------+--------------+
               |                                                  |
               +----------------------+   +-----------------------+
                                      |   |
                                      v   v
                     +----------------------------------+
                     |     LANE C: VERIFICATION LAYER   |
                     | - Cross-Lane Semantic Check      |
                     | - Numerical Ground-Truth Enforce |
                     | - 5-Factor Confidence Evaluation |
                     | - Evidence & Limitation Tagging  |
                     +-----------------+----------------+
                                       |
                                       v
                     +----------------------------------+
                     |     Response Synthesizer         |
                     | - Persist in SQLite / DB Layer   |
                     | - Stream Execution Trace Steps   |
                     | - Export Markdown Reports        |
                     +------------------+---------------+
```

## 2. Major Components

### 2.1 API Ingestion & Security Gateway (`backend/api/`)
- Handles endpoint routing (`/api/analyze`, `/api/upload`, `/api/models`, `/api/report`, `/api/executions`, `/api/audit`).
- Validates file constraints, enforces `Image.MAX_IMAGE_PIXELS = 50_000_000`, checks MIME headers before decoding.
- Controls CORS with explicit domain allowlists and handles rate limiting.

### 2.2 Supervisor & Orchestration Layer (`backend/agents/supervisor_agent.py`, `backend/orchestration/`)
- **Task Classifier**: Uses rule-based heuristics and input modality inspection to classify requests into one of the 6 canonical tasks.
- **Execution Manager**: Generates deterministic execution traces with 8 structured lifecycle steps:
  1. Query Understanding
  2. Input Validation
  3. Task Classification
  4. Model Selection
  5. Analysis Execution
  6. Evidence Generation
  7. Confidence Calculation
  8. Response Generation

### 2.3 Lane A: Deterministic Scientific Engine (`backend/scientific/`)
- **Lightweight Dependencies**: Uses pure NumPy, OpenCV, and optional Rasterio. Avoids heavy C++ GDAL dependencies.
- **Image Co-Registration**: Implements SIFT feature detection and RANSAC homography estimation. Enforces an **RMSE <= 0.8 pixel** gate.
- **Spectral Index Engine**: Computes normalized difference indices (NDVI, NDWI, MNDWI) using floating-point safety masks.
- **SAR Preprocessing**: Implements Refined Lee speckle filtering and dual-polarization ratio computation.

### 2.4 Lane B: Vision-Language Model Adapters (`backend/services/gemini_service.py`, `backend/models/`)
- Wraps multimodal foundation models with exponential backoff and automatic model fallback (`gemini-2.5-flash` -> `gemini-2.0-flash` -> `gemini-1.5-flash`).
- Provides clean adapter interfaces for future open-weights model deployment (GeoChat, Qwen3-VL, ChangeFormer).

### 2.5 Lane C: Verification & Calibration Layer (`backend/services/confidence_service.py`, `backend/services/evidence_service.py`)
- Compares Lane B textual assertions with Lane A empirical numbers.
- Evaluates 5-factor confidence:
  - Quality of input image
  - Co-registration RMSE precision
  - Model cross-agreement
  - Evidence mask density
  - Prompt relevance
- Appends source provenance and technical limitations to every piece of evidence.

### 2.6 Persistence Layer (`backend/database/`, `backend/services/audit_service.py`)
- SQLite database backing via SQLAlchemy 2.0.
- Stores full execution lifecycle records, trace step state transitions, and audit analytics.

## 3. Data Flow & Two-Lane Execution Lifecycle

1. **Intake & Pre-Validation**: Client posts multipart form data with images and query.
2. **Asynchronous Image Ingestion**: Files read into memory, header validated against magic bytes, raster metadata extracted.
3. **Task Routing**: Router identifies task type and allocates specialist pipelines.
4. **Lane A Execution (Thread-Isolated)**:
   - SIFT/RANSAC co-registration executed inside `asyncio.to_thread`.
   - If bi-temporal or optical-SAR, alignment RMSE is calculated.
   - Deterministic difference masks and metric bounding boxes generated.
5. **Lane B Execution (Async I/O)**:
   - Formats query prompt with instructions and visual payload.
   - Calls VLM API asynchronously.
6. **Lane C Verification**:
   - Verification agent checks if VLM claims contradict Lane A masks or metrics.
   - Generates confidence score and evidence limitations.
7. **Trace Finalization & Persistence**:
   - Trace steps marked as `COMPLETED`.
   - SQLite atomic write of execution record.
8. **Client Response**: Returns payload matching `BackendAnalysisResponse` contract.

## 4. Async Processing & Event Loop Isolation (ISO-01)
To ensure the FastAPI asyncio event loop remains responsive under concurrent load:
- **Rule**: All CPU-intensive OpenCV operations (SIFT feature extraction, RANSAC matrix solving, morphological contour tracing, Lee SAR filtering) must be dispatched via `await asyncio.to_thread(func, *args)`.
- Network I/O (Gemini API calls, database writes) uses native async/await.

## 5. Failure Modes & Graceful Degradation
| Failure Scenario | System Handling / Degradation Behavior |
| --- | --- |
| **Gemini VLM Outage / 429 Quota** | Fall back down `GEMINI_FALLBACK_MODELS` list; if all fail, return deterministic Lane A OpenCV analysis with low confidence and limitation note. |
| **Co-Registration RMSE > 0.8 px** | Apply co-registration penalty (-25% confidence), emit warning evidence item, and proceed with unaligned caution. |
| **Invalid / Corrupted Raster** | Reject immediately at upload validation with HTTP 400 and clear error description without server trace. |
| **Pillow Decompression Bomb** | Intercept at header inspection; reject with HTTP 413 if dimensions exceed 50,000,000 pixels. |
| **Database Lock / Busy (SQLite)** | SQLAlchemy connection pool configured with timeout and WAL mode enabled (`PRAGMA journal_mode=WAL`). |
