# Database Documentation: SatQuery AI (SIH 2026, ISRO PS SIH26167)

## 1. Overview
SatQuery AI utilizes **SQLite with SQLAlchemy 2.0** for execution tracking, audit logging, and metric aggregation. The schema is designed for multi-worker safety, relational integrity, and seamless future migration to PostgreSQL.

## 2. Relational Schema & ERD

```
+--------------------------------------------------------------------+
|                         EXECUTIONS                                 |
+------------------------------------+-------------------------------+
| id (PK)                            | VARCHAR(36) / UUID            |
| task                               | VARCHAR(50)                   |
| input_type                         | VARCHAR(30)                   |
| query                              | TEXT                          |
| status                             | VARCHAR(20)                   |
| answer                             | TEXT                          |
| confidence                         | FLOAT                         |
| confidence_explanation             | TEXT                          |
| model_used                         | VARCHAR(100)                  |
| change_percentage                  | FLOAT (NULLABLE)              |
| processing_time                    | FLOAT                         |
| started_at                         | DATETIME                      |
| completed_at                       | DATETIME (NULLABLE)           |
| created_at                         | DATETIME                      |
+------------------------------------+-------------------------------+
               | 1
               |
               | N (ON DELETE CASCADE)
               v
+--------------------------------------------------------------------+
|                         TRACE_STEPS                                |
+------------------------------------+-------------------------------+
| id (PK)                            | INTEGER AUTOINCREMENT         |
| execution_id (FK)                  | VARCHAR(36) -> executions(id) |
| step_number                        | INTEGER                       |
| title                              | VARCHAR(100)                  |
| description                        | TEXT                          |
| status                             | VARCHAR(20)                   |
| timestamp                          | DATETIME (NULLABLE)           |
+------------------------------------+-------------------------------+
               | 1
               |
               | N (ON DELETE CASCADE)
               v
+--------------------------------------------------------------------+
|                         EVIDENCE_ITEMS                             |
+------------------------------------+-------------------------------+
| id (PK)                            | VARCHAR(50)                   |
| execution_id (FK)                  | VARCHAR(36) -> executions(id) |
| title                              | VARCHAR(200)                  |
| description                        | TEXT                          |
| type                               | VARCHAR(30)                   |
| source                             | VARCHAR(100) (NULLABLE)       |
| limitations                        | JSON (List of strings)        |
| url                                | TEXT (NULLABLE)               |
| metrics                            | JSON (Key-value pairs)        |
| created_at                         | DATETIME                      |
+------------------------------------+-------------------------------+
```

## 3. Detailed Entity Specifications

### 3.1 `executions`
Stores the lifecycle and top-level summary of every analysis execution.
- `id` (VARCHAR(36), PK): UUID string.
- `task` (VARCHAR(50), NOT NULL): One of `single_image_vqa`, `captioning`, `grounding`, `bi_temporal_change`, `change_vqa`, `optical_sar_fusion`.
- `input_type` (VARCHAR(30), NOT NULL): `single`, `bi_temporal`, or `optical_sar`.
- `query` (TEXT, NOT NULL): Raw user prompt.
- `status` (VARCHAR(20), NOT NULL): `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.
- `answer` (TEXT, NULLABLE): Generated analytical response.
- `confidence` (FLOAT, NULLABLE): Calibrated score [0.0 - 100.0].
- `confidence_explanation` (TEXT, NULLABLE): Confidence breakdown rationale.
- `model_used` (VARCHAR(100), NULLABLE): Identifiers of model/tools executed.
- `change_percentage` (FLOAT, NULLABLE): Quantitative surface change metric.
- `processing_time` (FLOAT, DEFAULT 0.0): Total pipeline duration in seconds.
- `started_at` (DATETIME, NOT NULL): Start timestamp (UTC).
- `completed_at` (DATETIME, NULLABLE): Completion timestamp (UTC).
- `created_at` (DATETIME, DEFAULT utcnow).

### 3.2 `trace_steps`
Stores detailed progress steps for the 8-step agent execution timeline.
- `id` (INTEGER, PK, AUTOINCREMENT).
- `execution_id` (VARCHAR(36), FK -> `executions.id` ON DELETE CASCADE, NOT NULL).
- `step_number` (INTEGER, NOT NULL): Sequence index (1 to 8).
- `title` (VARCHAR(100), NOT NULL): Stage name (e.g., "Input Validation").
- `description` (TEXT, NOT NULL): Operational details.
- `status` (VARCHAR(20), NOT NULL): `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `SKIPPED`.
- `timestamp` (DATETIME, NULLABLE): Timestamp of step execution.

### 3.3 `evidence_items`
Stores visual artifacts, bounding boxes, and quantitative indices generated during inference.
- `id` (VARCHAR(50), PK): Unique evidence identifier (e.g., `ev-diff-01`).
- `execution_id` (VARCHAR(36), FK -> `executions.id` ON DELETE CASCADE, NOT NULL).
- `title` (VARCHAR(200), NOT NULL): Human-readable observation title.
- `description` (TEXT, NOT NULL): Detailed finding.
- `type` (VARCHAR(30), NOT NULL): `image`, `bbox`, `mask`, `metrics`, `geojson`.
- `source` (VARCHAR(100), NULLABLE): Generating component (`Lane-A`, `Lane-B`).
- `limitations` (JSON, DEFAULT '[]'): List of technical caveats.
- `url` (TEXT, NULLABLE): Base64 URI or static URL to visual artifact.
- `metrics` (JSON, NULLABLE): Key-value metrics dictionary.
- `created_at` (DATETIME, DEFAULT utcnow).

## 4. Database Indexing Strategy (DB-02)
To guarantee rapid retrieval and audit analytics without full-table scans:
1. `ix_executions_created_at`: Index on `executions(created_at DESC)` for the newest-first audit overview.
2. `ix_executions_task`: Index on `executions(task)` for task-filtered analytics.
3. `ix_trace_steps_exec_step`: Composite unique index on `trace_steps(execution_id, step_number)` for fast timeline lookup.
4. `ix_evidence_execution_id`: Index on `evidence_items(execution_id)` for retrieving artifacts by execution.

## 5. Concurrency & Multi-Worker Safety (DB-01, DB-03)
- **SQLite WAL Mode**: Configured with `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` to enable concurrent reads during active writes.
- **SQLAlchemy 2.0 Async Session**: Uses `async_sessionmaker` with `scoped_session` semantics to isolate worker transactions.
- **Atomic Step Updates**: Step status transitions execute within isolated transactions with explicit commit/rollback guards to avoid partial state corruption.
