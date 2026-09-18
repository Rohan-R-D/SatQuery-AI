import io
import asyncio
import base64
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image

from services.gemini_service import gemini_service
from scientific.preprocessing.alignment import coregistration_gate
from scientific.change_detection.opencv_baseline import opencv_change_detector
from scientific.geometry.georeferencing import regions_to_geojson_feature_collection
from agents.verification_agent import verification_agent

logger = logging.getLogger("satquery.agents.change")


class ChangeAgent:
    """
    Specialist Agent for Bi-Temporal Remote Sensing Change Detection & Explanatory Change VQA.
    Integrates sub-pixel SIFT/RANSAC co-registration, morphological change mapping,
    GeoJSON bounding vector generation, and Gemini multimodal temporal reasoning.
    """

    def __init__(self):
        self.name = "change_agent"
        self.description = "Performs SIFT/RANSAC co-registration, OpenCV change detection, and Gemini temporal change interpretation."

    def _sync_scientific_processing(
        self,
        before_bytes: bytes,
        after_bytes: bytes
    ) -> Dict[str, Any]:
        """Runs CPU-bound Lane A scientific alignment and change detection in worker thread."""
        pil_t1 = Image.open(io.BytesIO(before_bytes)).convert("RGB")
        pil_t2 = Image.open(io.BytesIO(after_bytes)).convert("RGB")

        np_t1 = np.array(pil_t1)
        np_t2 = np.array(pil_t2)

        h1, w1 = np_t1.shape[:2]
        h2, w2 = np_t2.shape[:2]

        # 1. Co-Registration Quality Gate (SIFT + RANSAC)
        aligned_t2, coreg_report = coregistration_gate.align_and_validate(np_t1, np_t2)
        rmse_val = coreg_report.get("rmse", 0.0)

        # 2. Deterministic Pixel Difference Mapping
        diff_res = opencv_change_detector.detect_changes(np_t1, aligned_t2, threshold_val=32, min_region_area=40)

        # 3. GeoJSON FeatureCollection Bounding Boxes
        geojson_fc = regions_to_geojson_feature_collection(
            regions=diff_res["regions"],
            image_width=w1,
            image_height=h1
        )

        return {
            "w1": w1,
            "h1": h1,
            "w2": w2,
            "h2": h2,
            "coreg_report": coreg_report,
            "rmse": rmse_val,
            "change_percentage": diff_res["change_percentage"],
            "changed_pixels": diff_res["changed_pixels"],
            "total_pixels": diff_res["total_pixels"],
            "regions": diff_res["regions"],
            "artifacts": diff_res["artifacts"],
            "geojson": geojson_fc
        }

    async def execute_change_detection(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        query: str,
        is_explanatory_vqa: bool = True
    ) -> Dict[str, Any]:
        """Execute complete bi-temporal pipeline combining non-blocking scientific lane and Gemini VLM reasoning."""
        logger.info(f"ChangeAgent: processing bi-temporal change (is_vqa={is_explanatory_vqa})")

        # 1. Lane A: Scientific Processing offloaded to threadpool (ISO-01)
        lane_a = await asyncio.to_thread(self._sync_scientific_processing, before_bytes, after_bytes)

        change_percentage = lane_a["change_percentage"]
        changed_pixels = lane_a["changed_pixels"]
        total_pixels = lane_a["total_pixels"]
        regions_list = lane_a["regions"]
        artifacts_list = lane_a["artifacts"]
        rmse_val = lane_a["rmse"]
        coreg_report = lane_a["coreg_report"]

        metrics_dict = {
            "Change Percentage": f"{change_percentage}%",
            "Changed Pixels": f"{changed_pixels:,}",
            "Total Pixels": f"{total_pixels:,}",
            "Connected Regions": f"{len(regions_list)}",
            "Alignment RMSE (px)": str(rmse_val) if rmse_val < 999.0 else "N/A"
        }

        overlay_data_url = artifacts_list[1]["url"] if len(artifacts_list) > 1 else ""
        if "," in overlay_data_url:
            overlay_bytes = base64.b64decode(overlay_data_url.split(",")[1])
        else:
            overlay_bytes = before_bytes

        # 2. Lane B: VLM Explanatory Analysis
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
                f"Quantitative Summary: {change_percentage}% pixel variation ({changed_pixels:,} / {total_pixels:,} pixels) across {len(regions_list)} region(s).\n"
                f"Co-registration Quality: {coreg_report.get('reason', 'Aligned')}"
            )
        else:
            answer = (
                f"Bi-temporal change detection detected {change_percentage}% surface variation ({changed_pixels:,} / {total_pixels:,} pixels) "
                f"across {len(regions_list)} significant spatial region(s). Alignment RMSE: {rmse_val}px."
            )

        # 3. Lane C: Verification Agent Evaluation
        verification_res = verification_agent.verify(
            task="change_vqa" if is_explanatory_vqa else "bi_temporal_change",
            input_type="bi_temporal",
            primary_dimensions=(lane_a["w1"], lane_a["h1"]),
            secondary_dimensions=(lane_a["w2"], lane_a["h2"]),
            rmse=rmse_val if rmse_val < 999.0 else None,
            bounding_boxes=regions_list,
            change_percentage=change_percentage,
            connected_regions_count=len(regions_list),
            total_pixels=total_pixels,
            vlm_answer=answer,
            lane_a_metrics={"change_percentage": change_percentage}
        )

        # Determine model description based on whether Gemini VLM was available
        model_name = (
            "OpenCV Difference Engine + SIFT Alignment + Gemini Multimodal VLM"
            if not is_error else
            "OpenCV Difference Engine + SIFT Alignment (Deterministic Baseline)"
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
            "geojson": lane_a["geojson"],
            "verification": verification_res,
            "alignment_rmse": rmse_val if rmse_val < 999.0 else None,
            "is_error": False,  # Lane A deterministic pipeline succeeded
            "error_code": error_code,
            "model_used": model_name
        }


change_agent = ChangeAgent()
