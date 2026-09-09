# SatQuery AI 🛰️🤖

> **"Ask Satellite Images. Get Real Answers."**

An Agentic Vision-Language Assistant for Remote-Sensing & Geospatial Analysis. Built for **Smart India Hackathon 2026**.

---

## 🌟 Key Objectives & Capabilities

- **Single Image Analysis**: Visual Question Answering (VQA), scene classification, optical/multispectral & SAR interpretation.
- **Bi-Temporal Analysis**: Change detection, change explanation, and temporal VQA across T1 (Before) and T2 (After) images.
- **Optical + SAR Fusion**: Joint multimodal interpretation leveraging complementary optical and synthetic aperture radar imagery.
- **Agentic Orchestration**: Autonomous intent recognition, task classification, tool selection, evidence collection, confidence scoring, and execution trace generation.

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: React, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **AI & Remote Sensing**: Gemini Multimodal VLM, OpenCV, NumPy, Pillow, Rasterio
- **Future Models**: Hugging Face / PyTorch Remote Sensing backbones (BigEarthNet, RSVQA, CDVQA)

---

## 📁 Repository Structure

```
satquery-ai/
├── frontend/             # Vite + React + TypeScript web application
├── backend/              # Python FastAPI REST API
├── demo-data/            # Sample satellite datasets
│   ├── single/           # Single scene optical/SAR images
│   ├── temporal/         # Bi-temporal change detection pairs
│   │   ├── before/
│   │   └── after/
│   └── optical-sar/      # Co-registered optical and SAR pairs
│       ├── optical/
│       └── sar/
├── docs/                 # Architectural documentation & API spec
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
└── README.md             # Project documentation
```

---

## 🚀 Quick Start (Phase 1)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Verify backend health check:
```bash
curl http://localhost:8000/api/health
```

Expected Response:
```json
{
  "status": "ok",
  "service": "SatQuery AI Backend"
}
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📜 Development Roadmap

- [x] **Phase 1**: Project Initialization & Core Architecture Skeleton
- [x] **Phase 2**: Frontend UI Layout & Modern Design System (Glassmorphism Dark Theme)
- [x] **Phase 3**: Backend FastAPI Structure & Data Schemas
- [x] **Phase 4**: Real Multipart Image Ingestion & Frontend/Backend API Service
- [x] **Phase 5**: Gemini Multimodal VLM Integration (`google-genai` SDK)
- [x] **Phase 6**: SatQuery AI Agent & Deterministic Task Router
- [x] **Phase 7**: OpenCV Bi-Temporal Change Detection & Baseline Change Maps
- [x] **Phase 8**: Joint Optical + SAR Multimodal Analysis Engine
- [x] **Phase 9**: Visual Evidence Extractor & Deterministic Confidence Evaluation
- [x] **Phase 10**: Complete Frontend-Backend Integration & Animated Execution Trace
- [x] **Phase 11**: Presentation Demo Mode with 1-Click Presets & Sample Rasters
- [x] **Phase 12**: Automated Geospatial Report Generation & Download (.md)
