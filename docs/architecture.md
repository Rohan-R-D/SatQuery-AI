# SatQuery AI - System Architecture Document

## 🛰️ Overview

SatQuery AI is designed as an agentic Remote-Sensing Vision-Language Assistant. It accepts high-resolution satellite imagery (optical, multispectral, SAR) and natural-language queries to return analytical reports, visual evidence, change maps, and task execution traces.

---

## 🏛️ System Architecture

```
                                +-------------------+
                                |   User Interface  |
                                |  React + Vite TS  |
                                +---------+---------+
                                          |
                                    REST / JSON
                                          |
                                          v
                                +-------------------+
                                |  FastAPI Gateway  |
                                |   (backend/app)   |
                                +---------+---------+
                                          |
                                          v
                                +-------------------+
                                |  Agent Router     |
                                | (Task Classifier) |
                                +----+----+----+----+
                                     |    |    |
           +-------------------------+    |    +-------------------------+
           |                              |                              |
           v                              v                              v
+--------------------+        +--------------------+        +--------------------+
| Single Image VQA   |        | Bi-Temporal Change |        | Optical + SAR      |
| Engine             |        | Detection Engine   |        | Fusion Engine      |
+----------+---------+        +----------+---------+        +----------+---------+
           |                             |                             |
           +-----------------------------+-----------------------------+
                                         |
                                         v
                               +-------------------+
                               | Gemini VLM &      |
                               | Remote Sensing    |
                               | Toolkit           |
                               +-------------------+
```

---

## 🔒 Engineering & Architectural Principles

1. **Complete Decoupling**: Frontend and Backend interact strictly via RESTful APIs.
2. **Key Security**: API keys are handled strictly in backend environment variables and never exposed to the client side.
3. **Modularity**: Model services, image utilities, and agent tools are structured cleanly in separate Python packages.
4. **Authenticity**: Responses reflect real model inferences; mock or fallback data is strictly restricted to explicitly designated "DEMO MODE" toggles.
5. **Explainability**: Execution traces and confidence scores accompany all agent decisions.
