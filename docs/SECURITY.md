# Security Assessment & Hardening Guide: SatQuery AI (SIH 2026, ISRO PS SIH26167)

## 1. Executive Verdict
**STATUS: CHANGES REQUIRED (BLOCKING BEFORE PRODUCTION CODE)**
A comprehensive security review of the prototype revealed several critical and high-severity technical vulnerabilities across CORS configurations, authentication, image decompression, rate limiting, and exception sanitization. These items must be remediated sequentially prior to deploying production inference capabilities.

---

## 2. Vulnerability Findings & Remediation Plan

### SEC-01 [CRITICAL]: Permissive CORS Configuration with Wildcard Credentials
- **Location**: `backend/config.py:30`, `backend/main.py:32`
- **Vulnerability**: The default configuration sets `allow_origins=["*"]` while simultaneously setting `allow_credentials=True`. This is invalid per CORS specifications and exposes the API to Cross-Origin Information Disclosure and CSRF exploits.
- **Remediation**:
  - Remove wildcard `*` from origin lists when credentials are enabled.
  - Require explicit environment configuration for trusted frontends (`https://sat-query-ai-six.vercel.app`, `http://localhost:5173`).
  - Implement dynamic regex checking only for known deployment domains.

---

### SEC-02 [CRITICAL]: Unauthenticated Audit and Execution Tracing Endpoints
- **Location**: `backend/api/routes/audit.py:12-39`
- **Vulnerability**: `/api/audit` and `/api/executions/{execution_id}` have zero access controls, allowing unauthenticated attackers to inspect all user queries, analytical answers, execution traces, and system performance metrics.
- **Remediation**:
  - Introduce an `X-API-Key` / Bearer token authentication dependency (`get_admin_api_key`) guarding administrative and audit routes.
  - Set `ADMIN_API_KEY` in environment variables with constant-time comparison (`secrets.compare_digest`).

---

### SEC-03 [HIGH]: Pillow Decompression Bomb Vulnerability
- **Location**: `backend/services/file_service.py`, `backend/utils/validation.py`, `backend/scientific/raster_loader.py`
- **Vulnerability**: Raster decoding processes image byte arrays using PIL/Pillow without configuring `Image.MAX_IMAGE_PIXELS` or inspecting image dimension headers prior to full decompression. An attacker uploading a maliciously crafted compression bomb (e.g., small file expanding to 10 gigapixels) causes instant server Out-Of-Memory (OOM) crashing.
- **Remediation**:
  - Explicitly set `Image.MAX_IMAGE_PIXELS = 50_000_000` at application startup.
  - Inspect image metadata headers (via `Image.open` without calling `.load()` or `.convert()`) and reject rasters exceeding 50 MP with HTTP 413.

---

### SEC-04 [HIGH]: Unthrottled Inference Endpoints (Denial of Service & Quota Abuse)
- **Location**: `backend/api/routes/analysis.py:14-89`
- **Vulnerability**: `/api/analyze` and sub-routes are unthrottled. A burst script can exhaust Google Gemini API rate limits or starve server CPU resources through parallel OpenCV computations.
- **Remediation**:
  - Implement IP/Token based rate limiting (e.g., using `slowapi` or an in-memory sliding window limiter) capping requests to 10 req/min per client IP.

---

### SEC-05 [MEDIUM]: Insecure Content-Disposition Filename in Report Generation
- **Location**: `backend/report.py:165`, `backend/api/routes/reports.py:20`
- **Vulnerability**: Generating filenames with non-sanitized timestamps or client input risks Header Injection if special characters or CRLF sequences are introduced into `Content-Disposition`.
- **Remediation**:
  - Restrict filenames strictly to server-generated UUIDs and safe timestamps matching `^[a-zA-Z0-9_-]+\.md$`.

---

### SEC-06 [MEDIUM]: Information Leakage in Global Exception Handler
- **Location**: `backend/main.py:60-65`
- **Vulnerability**: Global exception handler returns `{"detail": f"Internal server error: {str(exc)}"}` directly to API consumers. This leaks internal file paths, module structures, and third-party library error stacks.
- **Remediation**:
  - Capture full stack trace in server logs with `logger.error(..., exc_info=True)`.
  - Return a sanitized generic response: `{"detail": "An internal server error occurred. Please contact system administrator."}` with a correlation tracking UUID.

---

### ISO-01 [HIGH]: Event Loop Starvation from Synchronous Scientific Computations
- **Location**: `backend/scientific/`, `backend/change_detection.py`, `backend/optical_sar.py`
- **Vulnerability**: Heavy computational routines (SIFT feature matching, RANSAC homography estimation, Lee speckle filtering, morphological dilation) execute synchronously inside async route handlers, blocking the Python GIL and event loop for all concurrent requests.
- **Remediation**:
  - Wrap all CPU-bound OpenCV and NumPy functions with `await asyncio.to_thread(...)`.

---

### DB-01 / DB-02 / DB-03 [HIGH/MEDIUM]: Database Relational Integrity & Concurrency
- **Location**: `backend/orchestration/execution_manager.py`, `backend/services/audit_service.py`
- **Vulnerabilities**: Volatile in-memory dictionaries lose all state on restart and fail across multi-process workers. Missing FK cascading deletes and lack of atomic updates risk data corruption.
- **Remediation**:
  - Migrate state management to SQLite with SQLAlchemy 2.0.
  - Enforce `FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE`.
  - Wrap trace step updates in atomic transactions.

---

## 3. Environment Variable Security & Key Handling
- `GEMINI_API_KEY`: Must be loaded strictly from environment variables or `.env` files; never committed to source control or logged in cleartext.
- `ADMIN_API_KEY`: Enforced minimum 32-character high-entropy secret for audit endpoint authorization.
