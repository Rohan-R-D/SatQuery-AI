import io
import unittest
from PIL import Image
from fastapi.testclient import TestClient

from main import app
from orchestration.task_classifier import task_classifier
from orchestration.router import task_router
from orchestration.model_registry import model_registry
from orchestration.workflow_manager import workflow_manager
from orchestration.execution_manager import execution_manager
from schemas.tasks import TaskEnum
from schemas.responses import HealthResponse, ModelListResponse, AnalysisResponse


def create_dummy_image_bytes(color=(100, 150, 200), size=(100, 100)) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()


class BackendTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.img1_bytes = create_dummy_image_bytes(color=(100, 150, 200))
        cls.img2_bytes = create_dummy_image_bytes(color=(200, 50, 50))

    def test_health_endpoints(self):
        """Test both /api/health and root /health."""
        res1 = self.client.get("/api/health")
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertIn("status", data1)
        self.assertIn("service", data1)

        res2 = self.client.get("/health")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertIn("status", data2)

    def test_models_endpoint(self):
        """Test /api/models registry querying and filtering."""
        res = self.client.get("/api/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("models", data)
        self.assertGreater(len(data["models"]), 0)

        # Filter by task
        res_filtered = self.client.get("/api/models?task=bi_temporal_change")
        self.assertEqual(res_filtered.status_code, 200)
        filtered_data = res_filtered.json()
        self.assertTrue(any(m["id"] == "opencv-change" for m in filtered_data["models"]))

    def test_task_classification_and_routing(self):
        """Test task classifier for all 6 target workflows."""
        # 1. Single Image VQA
        r1 = task_classifier.classify("single", "Are there airplanes visible on the tarmac?")
        self.assertEqual(r1.task, TaskEnum.SINGLE_IMAGE_VQA.value)

        # 2. Scene Captioning
        r2 = task_classifier.classify("single", "Describe the land cover and scene overview.")
        self.assertEqual(r2.task, TaskEnum.CAPTIONING.value)

        # 3. Spatial Grounding
        r3 = task_classifier.classify("single", "Locate and highlight the runway bounding box.")
        self.assertEqual(r3.task, TaskEnum.GROUNDING.value)

        # 4. Bi-Temporal Change Detection
        r4 = task_classifier.classify("bi_temporal", "Compute change map between dates.", has_second_image=True)
        self.assertEqual(r4.task, TaskEnum.BI_TEMPORAL_CHANGE.value)

        # 5. Bi-Temporal Change VQA
        r5 = task_classifier.classify("bi_temporal", "What has changed between these two dates?", has_second_image=True)
        self.assertEqual(r5.task, TaskEnum.CHANGE_VQA.value)

        # 6. Optical + SAR Fusion
        r6 = task_classifier.classify("optical_sar", "Cross-validate radar backscatter with optical reflectance.", has_second_image=True)
        self.assertEqual(r6.task, TaskEnum.OPTICAL_SAR_FUSION.value)

    def test_upload_endpoint(self):
        """Test POST /api/upload with dummy image."""
        files = {
            "file": ("test_raster.png", self.img1_bytes, "image/png")
        }
        res = self.client.post("/api/upload", files=files)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["filename"], "test_raster.png")
        self.assertEqual(data["dimensions"], [100, 100])

    def test_analyze_single_image_endpoint(self):
        """Test POST /api/analyze for single image."""
        files = {
            "image": ("image1.png", self.img1_bytes, "image/png"),
        }
        data = {
            "input_type": "single",
            "query": "Is there water present in this satellite image?"
        }
        res = self.client.post("/api/analyze", files=files, data=data)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("answer", body)
        self.assertIn("confidence", body)
        self.assertIn("evidence", body)
        self.assertIn("execution_trace", body)
        self.assertGreaterEqual(body["confidence"], 0.0)

    def test_analyze_change_detection_endpoint(self):
        """Test POST /api/analyze/change with two temporal images."""
        files = {
            "image": ("before.png", self.img1_bytes, "image/png"),
            "second_image": ("after.png", self.img2_bytes, "image/png"),
        }
        data = {
            "query": "What changed between T1 and T2?"
        }
        res = self.client.post("/api/analyze/change", files=files, data=data)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["input_type"], "bi_temporal")
        self.assertIsNotNone(body["change_percentage"])
        self.assertIn("artifacts", body)
        self.assertTrue(any(a["name"] == "change_mask" for a in (body["artifacts"] or [])))

    def test_analyze_optical_sar_endpoint(self):
        """Test POST /api/analyze/optical-sar with Optical and SAR images."""
        files = {
            "image": ("optical.png", self.img1_bytes, "image/png"),
            "second_image": ("sar.png", self.img2_bytes, "image/png"),
        }
        data = {
            "query": "Examine radar backscatter and optical spectral features."
        }
        res = self.client.post("/api/analyze/optical-sar", files=files, data=data)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["input_type"], "optical_sar")
        self.assertIsNotNone(body["built_up_regions"])
        self.assertIsNotNone(body["water_regions"])

    def test_report_generation_endpoint(self):
        """Test POST /api/report for generating downloadable markdown."""
        payload = {
            "query": "Analyze water features",
            "input_type": "single",
            "task": "single_image_vqa",
            "answer": "Water bodies detected along eastern corridor.",
            "confidence": 88.5,
            "confidence_explanation": "High confidence based on spectral reflectance.",
            "model_used": "Gemini Multimodal VLM",
            "evidence": [
                {
                    "id": "ev-1",
                    "title": "Water Reflectance",
                    "description": "Distinct absorption in near-infrared.",
                    "type": "metrics"
                }
            ],
            "execution_trace": [
                {
                    "id": 1,
                    "title": "Query Understanding",
                    "description": "Parsed intent.",
                    "status": "COMPLETED"
                }
            ],
            "processing_time": 0.45
        }
        res = self.client.post("/api/report", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("attachment", res.headers.get("Content-Disposition", ""))
        self.assertIn("SATQUERY AI - ANALYSIS REPORT", res.text)

    def test_audit_endpoints(self):
        """Test GET /api/audit and GET /api/executions/{id}."""
        res = self.client.get("/api/audit")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("records", data)


if __name__ == "__main__":
    unittest.main()
