import io
import base64
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image

from services.gemini_service import gemini_service

logger = logging.getLogger("satquery.agents.change")


class ChangeAgent:
    """
    Specialist Agent for Bi-Temporal Remote Sensing Change Detection & Explanatory Change VQA.
    """

    def __init__(self):
        self.name = "change_agent"
        self.description = "Performs OpenCV pixel-difference change detection and Gemini multimodal temporal change interpretation."

    @staticmethod
    def _to_base64_data_url(cv_img: np.ndarray) -> str:
        """Helper to convert OpenCV image array into base64 PNG data URL."""
        success, buffer = cv2.imencode(".png", cv_img)
        if not success:
            return ""
        b64_str = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/png;base64,{b64_str}"

    def compute_opencv_change(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        threshold_val: int = 35,
        min_region_area: int = 50
    ) -> Dict[str, Any]:
        """Compute pixel differences, morphological mask, contour bounding boxes, and visual overlay."""
        pil_t1 = Image.open(io.BytesIO(before_bytes)).convert("RGB")
        pil_t2 = Image.open(io.BytesIO(after_bytes)).convert("RGB")

        img1_bgr = cv2.cvtColor(np.array(pil_t1), cv2.COLOR_RGB2BGR)
        img2_bgr = cv2.cvtColor(np.array(pil_t2), cv2.COLOR_RGB2BGR)

        h1, w1 = img1_bgr.shape[:2]
        h2, w2 = img2_bgr.shape[:2]

        if (h1, w1) != (h2, w2):
            logger.info(f"Resizing T2 image from {w2}x{h2} to match T1 {w1}x{h1}")
            img2_bgr = cv2.resize(img2_bgr, (w1, h1), interpolation=cv2.INTER_LINEAR)

        gray1 = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_bgr, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(gray1, gray2)
        _, binary_thresh = cv2.threshold(diff, threshold_val, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morphed = cv2.morphologyEx(binary_thresh, cv2.MORPH_OPEN, kernel)
        morphed = cv2.morphologyEx(morphed, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        clean_mask = np.zeros_like(morphed)
        regions = []

        for cnt in contours:
            area = int(cv2.contourArea(cnt))
            if area >= min_region_area:
                cv2.drawContours(clean_mask, [cnt], -1, 255, thickness=cv2.FILLED)
                x, y, w, h = cv2.boundingRect(cnt)
                regions.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": area,
                    "label": "changed_area"
                })

        regions.sort(key=lambda r: r["area"], reverse=True)

        changed_pixels = int(np.sum(clean_mask > 0))
        total_pixels = int(w1 * h1)
        change_percentage = round((changed_pixels / total_pixels) * 100, 2)

        overlay_bgr = img2_bgr.copy()
        red_mask = np.zeros_like(img2_bgr)
        red_mask[clean_mask > 0] = [0, 0, 255]

        cv2.addWeighted(red_mask, 0.45, overlay_bgr, 1.0, 0, overlay_bgr)
        cv2.drawContours(overlay_bgr, contours, -1, (0, 255, 255), 1)

        diff_map_url = self._to_base64_data_url(diff)
        change_mask_url = self._to_base64_data_url(clean_mask)
        overlay_url = self._to_base64_data_url(overlay_bgr)

        return {
            "change_percentage": change_percentage,
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "regions": regions[:15],
            "difference_map": diff_map_url,
            "change_mask": change_mask_url,
            "change_overlay": overlay_url,
            "overlay_bgr": overlay_bgr
        }

    def execute_change_detection(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        query: str,
        is_explanatory_vqa: bool = True
    ) -> Dict[str, Any]:
        """Execute complete bi-temporal pipeline combining OpenCV difference engine and Gemini VLM reasoning."""
        logger.info(f"ChangeAgent: processing bi-temporal change (is_vqa={is_explanatory_vqa})")

        # 1. OpenCV Change Analysis
        change_res = self.compute_opencv_change(before_bytes, after_bytes)
        change_percentage = change_res["change_percentage"]
        changed_pixels = change_res["changed_pixels"]
        total_pixels = change_res["total_pixels"]
        regions_list = change_res["regions"]

        artifacts_list = [
            {"name": "difference_map", "type": "image/png", "url": change_res["difference_map"], "description": "Absolute spectral difference raster"},
            {"name": "change_mask", "type": "image/png", "url": change_res["change_mask"], "description": "Binary filtered change mask"},
            {"name": "change_overlay", "type": "image/png", "url": change_res["change_overlay"], "description": "Colorized spatial change overlay on T2"},
        ]

        metrics_dict = {
            "Change Percentage": f"{change_percentage}%",
            "Changed Pixels": f"{changed_pixels:,}",
            "Total Pixels": f"{total_pixels:,}",
            "Connected Regions": f"{len(regions_list)}"
        }

        overlay_data_url = change_res["change_overlay"]
        if "," in overlay_data_url:
            overlay_bytes = base64.b64decode(overlay_data_url.split(",")[1])
        else:
            overlay_bytes = before_bytes

        # 2. VLM Explanatory Analysis
        is_error = False
        error_code = None
        evidence_strings = []

        if is_explanatory_vqa:
            gemini_res = gemini_service.analyze_change_images(
                before_bytes=before_bytes,
                after_bytes=after_bytes,
                overlay_bytes=overlay_bytes,
                query=query,
                change_percentage=change_percentage
            )
            vlm_answer = gemini_res.get("answer", "")
            is_error = gemini_res.get("is_error", False)
            error_code = gemini_res.get("error_code")
            evidence_strings = gemini_res.get("evidence", [])

            answer = (
                f"{vlm_answer}\n\n"
                f"Quantitative OpenCV Summary: {change_percentage}% pixel variation ({changed_pixels:,} / {total_pixels:,} pixels) across {len(regions_list)} region(s).\n"
                f"Note: Scientific baseline uses OpenCV pixel-difference thresholding engine."
            )
        else:
            answer = (
                f"Bi-temporal change detection detected {change_percentage}% surface variation ({changed_pixels:,} / {total_pixels:,} pixels) "
                f"across {len(regions_list)} significant spatial region(s)."
            )

        return {
            "answer": answer,
            "change_percentage": change_percentage,
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "regions": regions_list,
            "artifacts": artifacts_list,
            "metrics": metrics_dict,
            "evidence": evidence_strings,
            "is_error": is_error,
            "error_code": error_code,
            "model_used": "OpenCV Difference Engine + Gemini Multimodal VLM"
        }


change_agent = ChangeAgent()
