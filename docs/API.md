# API Contract: SatQuery AI (SIH 2026, ISRO PS SIH26167)

## 1. Overview
SatQuery AI exposes a RESTful HTTP API. This specification defines all public endpoints and guarantees strict compatibility with the existing React frontend client (`frontend/src/services/api.ts`).

## 2. Authentication & Authorization (SEC-02)
- Public Endpoints: `/api/health`, `/health`, `/api/upload`, `/api/analyze*`, `/api/models`, `/api/report`.
- Protected Administrative Endpoints: `/api/audit`, `/api/executions/{execution_id}`.
- Authentication Header:
  - Header: `X-API-Key: <SATQUERY_ADMIN_API_KEY>` or `Authorization: Bearer <SATQUERY_ADMIN_API_KEY>`
  - Failure response: HTTP 401 Unauthorized (`{"detail": "Invalid or missing API key"}`).

## 3. Endpoints Specification

---

### 3.1 System Health
- **Route**: `GET /api/health` and `GET /health`
- **Description**: Returns operational status of the service.
- **Response** `200 OK`:
```json
{
  "status": "healthy",
  "service": "satquery-backend",
  "version": "0.1.0"
}
```

---

### 3.2 Raster Image Ingestion & Validation
- **Route**: `POST /api/upload`
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `file` (UploadFile, required): Satellite raster image (TIFF, PNG, JPEG).
- **Validation Constraints**:
  - Maximum file size: 50 MB.
  - Maximum pixel count: 50,000,000 pixels.
- **Response** `200 OK` (Schema: `UploadResponse`):
```json
{
  "success": true,
  "filename": "sentinel2_scene.tif",
  "size_bytes": 14205840,
  "format": "TIFF",
  "dimensions": [4096, 4096],
  "preview_url": null,
  "message": "Raster successfully validated (4096x4096 px, TIFF)."
}
```
- **Error Responses**:
  - `400 Bad Request`: Unsupported format or unreadable image.
  - `413 Payload Too Large`: File or pixel dimensions exceed limits.

---

### 3.3 Multimodal Analysis Endpoints
- **Routes**:
  - `POST /api/analyze` (Unified endpoint)
  - `POST /api/analyze/single` (Dedicated single scene)
  - `POST /api/analyze/change` (Dedicated bi-temporal pair)
  - `POST /api/analyze/optical-sar` (Dedicated optical + SAR pair)
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `image` (UploadFile, required): Primary raster image.
  - `second_image` (UploadFile, optional/required for pair tasks): Temporal T2 or SAR raster.
  - `input_type` (string, optional, default: `single`): `single`, `bi_temporal`, or `optical_sar`.
  - `query` (string, required): Natural language question or analytical prompt.
- **Response** `200 OK` (Schema: `AnalysisResponse`):
```json
{
  "success": true,
  "task": "bi_temporal_change",
  "input_type": "bi_temporal",
  "answer": "Significant urban construction detected in the western quadrant (+14.2% surface modification). Water body boundaries remained stable.",
  "confidence": 88.5,
  "confidence_explanation": "Evaluated across 5 criteria: High raster resolution (0.95), co-registration RMSE 0.42 px (0.92), Lane A/B cross-agreement (0.85), dense morphological change masks (0.88), complete prompt coverage (0.82).",
  "model_used": "OpenCV Difference Engine + Gemini 2.5 Flash",
  "evidence": [
    {
      "id": "ev-diff-001",
      "title": "Morphological Change Mask",
      "description": "Pixel intensity deviation exceeding dynamic Otsu threshold across band delta.",
      "type": "mask",
      "source": "Lane-A: OpenCV Differencing",
      "limitations": ["Sensitive to illumination angle variance"],
      "url": "data:image/png;base64,iVBORw0KGgo...",
      "metrics": {
        "changed_pixels": 245100,
        "change_percentage": 14.2,
        "co_registration_rmse_px": 0.42
      }
    }
  ],
  "execution_trace": [
    {
      "id": 1,
      "title": "Query Understanding",
      "description": "Parsed natural language query intent and extracted spatial entities.",
      "status": "COMPLETED",
      "timestamp": "2026-09-18T16:00:00Z"
    },
    {
      "id": 2,
      "title": "Input Validation",
      "description": "Validated satellite raster integrity, spatial dimensions, and coordinate references.",
      "status": "COMPLETED",
      "timestamp": "2026-09-18T16:00:01Z"
    }
  ],
  "processing_time": 4.125,
  "change_percentage": 14.2,
  "regions": [
    {
      "x": 120,
      "y": 450,
      "width": 300,
      "height": 280,
      "area": 84000,
      "label": "Built-up Construction",
      "confidence": 0.89
    }
  ],
  "artifacts": [],
  "built_up_regions": [{"description": "Commercial building expansion in grid W-4"}],
  "water_regions": []
}
```

---

### 3.4 Model Registry
- **Route**: `GET /api/models`
- **Query Parameters**:
  - `task` (string, optional): Filter by task ID.
  - `status` (string, optional): Filter by status (`available`, `baseline`, `temporary_baseline`, `candidate`, `planned`).
- **Response** `200 OK` (Schema: `ModelListResponse`):
```json
{
  "models": [
    {
      "id": "gemini-vlm",
      "name": "Gemini Multimodal VLM",
      "type": "vision-language",
      "tasks": ["single_image_vqa", "captioning", "grounding", "change_vqa", "optical_sar_fusion"],
      "status": "temporary_baseline",
      "description": "Active multimodal vision-language foundation model for remote sensing visual reasoning."
    },
    {
      "id": "opencv-change",
      "name": "OpenCV Difference Engine",
      "type": "image-processing",
      "tasks": ["bi_temporal_change", "change_vqa"],
      "status": "baseline",
      "description": "Deterministic pixel-difference, morphological filtering, and contour region change detection pipeline."
    }
  ]
}
```

---

### 3.5 Markdown Report Generation
- **Route**: `POST /api/report`
- **Content-Type**: `application/json`
- **Request Body** (Schema: `ReportRequest`):
```json
{
  "query": "Identify urban expansion between 2024 and 2026",
  "input_type": "bi_temporal",
  "task": "bi_temporal_change",
  "answer": "Detected 14.2% surface modification...",
  "confidence": 88.5,
  "confidence_explanation": "5-factor evaluation...",
  "model_used": "OpenCV Difference Engine + Gemini 2.5 Flash",
  "evidence": [],
  "execution_trace": [],
  "processing_time": 4.125,
  "change_percentage": 14.2,
  "timestamp": "2026-09-18T16:00:00Z"
}
```
- **Response** `200 OK`:
  - `Content-Type`: `text/markdown`
  - `Content-Disposition`: `attachment; filename=satquery_report_<UUID>.md`

---

### 3.6 Execution Lifecycle Retrieval
- **Route**: `GET /api/executions/{execution_id}`
- **Security**: Requires `X-API-Key`
- **Response** `200 OK` (Schema: `ExecutionRecord`):
```json
{
  "execution_id": "exec-9f8e7d6c5b4a",
  "task": "bi_temporal_change",
  "status": "COMPLETED",
  "query": "Identify urban expansion",
  "input_type": "bi_temporal",
  "started_at": "2026-09-18T16:00:00Z",
  "completed_at": "2026-09-18T16:00:04Z",
  "duration_sec": 4.125,
  "trace_steps": [],
  "result": {
    "task": "bi_temporal_change",
    "confidence": 88.5,
    "answer_summary": "Detected 14.2% surface modification..."
  }
}
```

---

### 3.7 Audit Log & Metrics Overview
- **Route**: `GET /api/audit`
- **Security**: Requires `X-API-Key`
- **Query Parameters**:
  - `limit` (integer, default: 50, max: 200).
  - `task` (string, optional).
- **Response** `200 OK`:
```json
{
  "metrics": {
    "total_queries": 142,
    "avg_duration_sec": 3.82,
    "success_rate_pct": 98.6,
    "task_distribution": {
      "single_image_vqa": 60,
      "bi_temporal_change": 45,
      "optical_sar_fusion": 25,
      "grounding": 12
    }
  },
  "total_returned": 50,
  "records": []
}
```
