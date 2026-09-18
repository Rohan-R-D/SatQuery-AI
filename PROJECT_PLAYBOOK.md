# Project Playbook: SatQuery AI (SIH 2026, ISRO PS SIH26167)

This document serves as the technical memory and development coordinator for the project.

## Architecture Decisions
| Decision | Description | Status |
| --- | --- | --- |
| Modular FastAPI Monolith | Single backend service to simplify hackathon deployment; microservices/Kafka/K8s are over-engineered for this phase. | ACCEPTED |
| Two-Lane Intelligence | Lane A explores scientific metrics (NumPy/OpenCV); Lane B leverages VLM qualitative interpretation; Lane C verifies Lane B against Lane A. | ACCEPTED |
| Lightweight Raster Processing | Lane A relies on NumPy, OpenCV, and optionally Rasterio. Avoid hard dependencies on GDAL C++ binaries to maintain multi-platform agility. | ACCEPTED |
| SQLite + SQLAlchemy 2.0 | Used for persistence of execution logic, trace steps, and audits during hackathon (PostgreSQL optional for scaling later). | ACCEPTED |
| API Key Authentication | Initial auth strategy for /api/audit and /api/executions/{id}. | ACCEPTED |

## Technology Choices
- **Frontend Framework**: React, Vite, TypeScript
- **Backend Framework**: FastAPI, Pydantic, Python 3.12+
- **Database Engine**: SQLite with SQLAlchemy 2.0
- **Scientific Models**: Gemini (temporary baseline), OpenCV (baseline), ChangeFormer, GeoChat, Qwen3-VL, GRAMA (candidates)
- **Image Processing**: NumPy, OpenCV, PIL, Rasterio

## Conventions
- **Coding conventions**: Use descriptive variable names; favor structured logging; scientific image filters (SIFT/RANSAC) should use syncio.to_thread.
- **Database conventions**: Use FK ON DELETE CASCADE; employ composite indexes where required; concurrent writes need atomic updates or transaction locks.
- **API conventions**: Strict preservation of existing REST endpoints and JSON payloads to avoid breaking React frontend (rontend/src/services/api.ts). Use explicit CORS allowlists.
- **Security requirements**: Address findings SEC-01 to SEC-06 and DB-01 to DB-03 stringently before production. Do not expose str(exc) in 500 errors. No wildcard credentials. No unthrottled external inferences.

## Task Management

### Current Tasks
| ID | Description | Status | Dependencies | Files | Acceptance Criteria | Tests |
| --- | --- | --- | --- | --- | --- | --- |
| BACKEND-SEC-01 | Restrict CORS wildcard | DONE | None | config.py, main.py | CORS config specifies discrete allowed origins; allow_credentials=True used without * origins. | test_cors.py |
| BACKEND-SEC-03 | Impose pixel limits | DONE | None | utils/image_utils.py, utils/validation.py, services/file_service.py, scientific/raster_loader.py | Pillow Image.MAX_IMAGE_PIXELS set to 50M; reject limits with 413. | test_pixel_limits.py |
| BACKEND-SEC-06 | Sanitize errors | DONE | None | main.py | Global exception handler logs exc but returns generic 500 cleanly to client. | test_error_sanitization.py |
| BACKEND-SEC-05 | Report filenames | DONE | None | report.py, api/routes/reports.py | Securely generated UUID/hash filenames for Content-Disposition in report routes. | test_report_security.py |
| BACKEND-SEC-04 | Rate limit /api/analyze | TODO | None | api/routes/analysis.py | Throttle API calls to Gemini and CPU-intensive routes. | Perform burst load |
| BACKEND-DB-01 | Persist executions | TODO | None | orchestration/execution_manager.py, services/audit_service.py | Replace in-memory dicts with SQLAlchemy models to survive restarts. | Verify after restart |
| BACKEND-001 | Scientific suite | IN_PROGRESS | None | scientific/* | Stubs replaced with concrete metrics for alignment, SAR indices, etc. | Unit tests |
| BACKEND-002 | Verification layer | TODO | BACKEND-001 | verification/* | Ground truth discrepancy engine for Lane C logic. | Unit tests |
| BACKEND-003 | Supervisor wiring | TODO | BACKEND-002 | agents/supervisor_agent.py | Coordinate two-lane data flow effectively. | Integration tests |
| BACKEND-004 | Model adapter abstraction | TODO | None | ai/models/*, ai/adapters/* | Common abstraction over local OpenCV vs hosted Gemini vs open weights. | Interface tests |
| BACKEND-SEC-02 | Auth on audit/executions | TODO | None | api/routes/audit.py | API Key validation wrapper ensuring internal routes are protected. | Test invalid key |

### Known Technical Debt (BLOCKING)
- **SEC-02 CRITICAL**: /api/audit and /api/executions/{id} currently have zero auth.
- **SEC-04 HIGH**: /api/analyze is unthrottled, creating vulnerability for CPU starvation and API quota abuse.
- **DB-01 HIGH**: ExecutionManager and AuditService are volatile in-memory dicts.
- **DB-02 MEDIUM**: Proposed SQL schema requires FK ON DELETE CASCADE and composite indexing.
- **DB-03 MEDIUM**: Lack of atomic writes on concurrent trace step updates.
- **ISO-01 HIGH**: CPU-bound scientific logic (SIFT/RANSAC/Lee filters) executes synchronously on main event loop.

### Important Assumptions
- Scientific packages (Lane A/B/C) remain stubs. Do NOT mark Lane A/B/C full implementation as DONE yet. The current implementation only has 
aster_loader + 
ormalization. Alignment, SAR manipulation, and verification agents do not exist.
- Required integration limits RMSE co-registration to <= 0.8px natively before passing to analytical steps.
