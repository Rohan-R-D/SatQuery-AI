# SatQuery AI - Backend Service

FastAPI service providing API routes for satellite image analysis, bi-temporal change detection, optical+SAR joint interpretation, and agentic orchestration.

## 🚀 Running the Server

1. Create and activate a Python 3.11+ virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Verify health endpoint:
   ```bash
   curl http://localhost:8000/api/health
   ```
