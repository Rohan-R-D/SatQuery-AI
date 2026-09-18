# Implementation Plan: SatQuery AI (SIH 2026, ISRO PS SIH26167)

This plan outlines the sequential, atomic tasks required to remediate technical debt and build the full SatQuery AI backend. Each task must be executed and validated in order.

---

### Task 1: BACKEND-SEC-01 - Restrict CORS Configuration & Remove Wildcard with Credentials
- **Goal**: Ensure CORS allowlist explicitly enumerates trusted client origins without wildcard `*` when credentials are permitted.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/config.py`
  - `backend/main.py`
- **Acceptance Criteria**:
  - `CORS_ORIGINS` defaults to a discrete list (`["https://sat-query-ai-six.vercel.app", "http://localhost:5173", "http://127.0.0.1:5173"]`).
  - Wildcard `"*"` is rejected when `allow_credentials=True`.
  - Preflight OPTIONS requests from localhost and Vercel succeed; unauthorized origins receive standard CORS block.
- **Tests**:
  - Unit test checking CORS headers on simulated requests with authorized vs unauthorized `Origin` headers.
- **Security Considerations**: Eliminates cross-origin credential leaking and unauthorized script interaction.

---

### Task 2: BACKEND-SEC-03 - Decompression Bomb Defense & Pixel Limit Enforcement
- **Goal**: Protect server against memory exhaustion attacks by enforcing strict pixel limits and pre-decoding header inspection.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/utils/image_utils.py`
  - `backend/utils/validation.py`
  - `backend/services/file_service.py`
  - `backend/scientific/raster_loader.py`
- **Acceptance Criteria**:
  - Application initializes with `Image.MAX_IMAGE_PIXELS = 50_000_000`.
  - `verify_image_readability` and `load_raster` inspect image dimensions before full memory allocation.
  - Any image exceeding 50 MP (50,000,000 pixels) is rejected with HTTP 413 Payload Too Large.
- **Tests**:
  - Test upload with synthetic oversized image header asserting HTTP 413 rejection.
  - Test valid 4K satellite scene asserting successful ingestion.
- **Security Considerations**: Prevents Denial of Service via memory exhaustion (OOM).

---

### Task 3: BACKEND-SEC-06 - Sanitize Global Exception Handler & API Error Outputs
- **Goal**: Prevent internal stack trace and server environment leakage to external clients.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/main.py`
- **Acceptance Criteria**:
  - Global 500 exception handler logs full exception trace internally with `logger.error(..., exc_info=True)`.
  - HTTP 500 response payload returns generic `{"detail": "An internal server error occurred."}` without exposing `str(exc)`.
- **Tests**:
  - Trigger simulated unhandled exception on test route; verify JSON response does not contain Python class names, tracebacks, or file paths.
- **Security Considerations**: Mitigates Information Disclosure vulnerability.

---

### Task 4: BACKEND-SEC-05 - Secure Report File Generation & Content-Disposition
- **Goal**: Prevent HTTP Header Injection and directory traversal in report generation endpoints.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/report.py`
  - `backend/api/routes/reports.py`
- **Acceptance Criteria**:
  - Downloaded report filename strictly adheres to server-generated regex: `^satquery_report_[a-f0-9]{8}_[0-9]{8}\.md$`.
  - User-provided parameters are sanitized before embedding into Markdown headers.
- **Tests**:
  - Invoke `POST /api/report` with malicious query containing CRLF (`\r\n`) and assert clean `Content-Disposition` header output.
- **Security Considerations**: Eliminates HTTP response splitting and header injection vectors.

---

### Task 5: BACKEND-SEC-04 - Rate Limiting on Inference & Ingestion Endpoints
- **Goal**: Prevent API quota starvation and CPU exhaustion on `/api/analyze` and `/api/upload`.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/api/routes/analysis.py`
  - `backend/api/routes/upload.py`
  - `backend/config.py`
- **Acceptance Criteria**:
  - Rate limiting middleware / dependency caps IP requests to 10 requests per minute on `/api/analyze`.
  - Exceeded rate limits return HTTP 429 Too Many Requests with `Retry-After` header.
- **Tests**:
  - Send 12 rapid requests to `/api/analyze` in test harness and assert 11th and 12th return HTTP 429.
- **Security Considerations**: Protects Gemini API credits and backend CPU resources against DoS.

---

### Task 6: BACKEND-DB-01 - SQLite + SQLAlchemy 2.0 Persistence Layer
- **Goal**: Replace volatile in-memory storage with persistent relational SQLite storage for executions and audit logs.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/database/` (models, session, connection)
  - `backend/orchestration/execution_manager.py`
  - `backend/services/audit_service.py`
  - `backend/schemas/execution.py`
- **Acceptance Criteria**:
  - SQLAlchemy 2.0 declarative models created for `ExecutionModel`, `TraceStepModel`, `EvidenceItemModel`.
  - Foreign key cascading deletes (`ON DELETE CASCADE`) configured for child tables.
  - Composite index `(execution_id, step_number)` applied.
  - State persists across FastAPI server restarts.
- **Tests**:
  - Create execution, restart backend instance, and verify execution record and trace steps are retrievable via `GET /api/executions/{id}`.
- **Security Considerations**: Multi-worker persistence, transaction isolation, and audit trail retention.

---

### Task 7: BACKEND-001 - Concrete Lane A Scientific Suite
- **Goal**: Implement deterministic remote-sensing algorithms replacing stubs (SIFT/RANSAC alignment, SAR despeckling, spectral indices).
- **Dependencies**: None.
- **Files Affected**:
  - `backend/scientific/alignment/coregistration.py`
  - `backend/scientific/sar/despeckle.py`
  - `backend/scientific/indices/spectral.py`
  - `backend/scientific/differencing/pixel_diff.py`
- **Acceptance Criteria**:
  - `coregistration.py` computes SIFT keypoints, matches with FLANN/RANSAC, computes RMSE, and warps second image. Enforces RMSE <= 0.8 px threshold.
  - `despeckle.py` implements Refined Lee filter on SAR intensity rasters.
  - `spectral.py` computes NDVI, NDWI, MNDWI with floating-point safety masks.
- **Tests**:
  - Unit tests with synthetic bi-temporal shifts verifying RMSE computation and correct warping.
  - Unit tests verifying NDVI output matches ground-truth formula within 1e-5.
- **Security Considerations**: All algorithms operate strictly in-memory without invoking shell commands.

---

### Task 8: BACKEND-002 - Lane C Multi-Factor Verification & Confidence Scoring
- **Goal**: Implement deterministic verification engine checking Lane B textual claims against Lane A metrics.
- **Dependencies**: Task 7 (BACKEND-001).
- **Files Affected**:
  - `backend/services/confidence_service.py`
  - `backend/services/evidence_service.py`
  - `backend/agents/verification_agent.py`
- **Acceptance Criteria**:
  - 5-factor confidence calculation implemented with dynamic weighting.
  - Penalizes confidence if Lane B claims change when Lane A calculates < 1% change.
  - Populates `source` and `limitations` for all evidence items.
- **Tests**:
  - Test case where VLM claims major flooding but Lane A NDWI delta is 0; assert confidence is penalized and limitation is recorded.
- **Security Considerations**: Transparent validation preventing hallucinated quantitative metrics.

---

### Task 9: BACKEND-003 - Supervisor Two-Lane Wiring & Event Loop Isolation (ISO-01)
- **Goal**: Integrate Lane A, Lane B, and Lane C into `SupervisorAgent` with CPU thread-offloading (`asyncio.to_thread`).
- **Dependencies**: Task 7 (BACKEND-001), Task 8 (BACKEND-002).
- **Files Affected**:
  - `backend/agents/supervisor_agent.py`
  - `backend/agents/change_agent.py`
  - `backend/agents/fusion_agent.py`
- **Acceptance Criteria**:
  - Supervisor orchestrates: Validation -> SIFT Alignment (to_thread) -> Lane A Metrics (to_thread) -> Lane B VLM (async) -> Lane C Verification -> Persistence.
  - No CPU-bound OpenCV/NumPy routine executes synchronously on main event loop.
- **Tests**:
  - Execute concurrent `/api/analyze` calls; assert event loop does not block health checks during heavy SIFT alignment.
- **Security Considerations**: Prevents server lockup under concurrent computational load.

---

### Task 10: BACKEND-004 - Model Adapter Interface & Candidate Pipeline Abstraction
- **Goal**: Standardize interface for foundation models to enable plug-and-play addition of GeoChat, Qwen3-VL, ChangeFormer, and GRAMA.
- **Dependencies**: None.
- **Files Affected**:
  - `backend/models/base_adapter.py`
  - `backend/models/gemini_adapter.py`
  - `backend/orchestration/model_registry.py`
- **Acceptance Criteria**:
  - Generic `BaseVLMAdapter` interface with async `generate_response(images, prompt)` method.
  - `GeminiAdapter` implements fallback logic and clean error translation.
  - Registry exposes candidate models with metadata.
- **Tests**:
  - Mock adapter unit test verifying standardized response structure.
- **Security Considerations**: Isolates external API dependencies behind uniform error boundaries.

---

### Task 11: BACKEND-SEC-02 - API Key Authentication on Audit and Execution Endpoints
- **Goal**: Protect `/api/audit` and `/api/executions/{id}` with API key authorization.
- **Dependencies**: Task 6 (BACKEND-DB-01).
- **Files Affected**:
  - `backend/api/routes/audit.py`
  - `backend/api/deps.py`
  - `backend/config.py`
- **Acceptance Criteria**:
  - Requests without valid `X-API-Key` or `Authorization: Bearer` return HTTP 401 Unauthorized.
  - Key validation uses constant-time string comparison (`secrets.compare_digest`).
- **Tests**:
  - Send request to `/api/audit` without key -> assert 401.
  - Send request with valid key -> assert 200 OK.
- **Security Considerations**: Prevents unauthorized reconnaissance and data exposure.
