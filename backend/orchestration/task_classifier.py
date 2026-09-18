import re
import logging
from typing import Set
from schemas.tasks import TaskClassificationResult, TaskEnum, InputTypeEnum

logger = logging.getLogger("satquery.orchestration.task_classifier")


class TaskClassifier:
    """
    Deterministic rule-based task classifier for remote-sensing queries and raster modalities.
    """

    @staticmethod
    def classify(
        input_type: str,
        query: str,
        has_second_image: bool = False
    ) -> TaskClassificationResult:
        query_clean = query.lower().strip()
        words: Set[str] = set(re.findall(r'\b\w+\b', query_clean))

        # 1. Optical + SAR Multimodal Fusion Rule
        optical_sar_keywords = {
            "optical", "sar", "radar", "sentinel-1", "sentinel-2", "multimodal",
            "backscatter", "dual-sensor", "cross-modal", "reflectance"
        }
        if input_type in {"optical_sar", "optical-sar"} or (has_second_image and bool(words & optical_sar_keywords)):
            return TaskClassificationResult(
                task=TaskEnum.OPTICAL_SAR_FUSION.value,
                workflow="optical_sar_fusion_workflow",
                required_agents=["fusion_agent", "response_agent"],
                required_artifacts=["cross_modal_metrics", "dual_sensor_evidence"],
                required_tools=["gemini-vlm", "optical-sar-engine"],
                confidence=0.98,
                reason="Optical reflectance and SAR synthetic aperture radar rasters provided for joint multi-sensor interpretation."
            )

        # 2. Bi-Temporal Change Detection & Change VQA Rules
        change_keywords = {
            "change", "changed", "before", "after", "increase", "decrease",
            "between", "dates", "variation", "growth", "difference", "expansion",
            "deforestation", "construction", "loss", "flood", "destroyed", "built"
        }
        is_temporal_request = (
            input_type in {"bi_temporal", "bitemporal"}
            or has_second_image
            or bool(words & change_keywords)
        )

        if is_temporal_request and has_second_image:
            question_words = {"what", "why", "how", "describe", "explain", "has", "is", "where", "which"}
            is_question = bool(words & question_words) or query_clean.endswith("?")

            if is_question:
                return TaskClassificationResult(
                    task=TaskEnum.CHANGE_VQA.value,
                    workflow="bi_temporal_change_vqa_workflow",
                    required_agents=["change_agent", "vqa_agent", "response_agent"],
                    required_artifacts=["difference_map", "change_mask", "change_overlay"],
                    required_tools=["opencv-change", "gemini-vlm"],
                    confidence=0.96,
                    reason="Bi-temporal image pair supplied with an explanatory analytical question regarding surface change."
                )
            else:
                return TaskClassificationResult(
                    task=TaskEnum.BI_TEMPORAL_CHANGE.value,
                    workflow="bi_temporal_change_workflow",
                    required_agents=["change_agent", "response_agent"],
                    required_artifacts=["difference_map", "change_mask", "change_overlay"],
                    required_tools=["opencv-change"],
                    confidence=0.95,
                    reason="Bi-temporal image pair supplied for quantitative land-cover difference mapping and mask generation."
                )

        # 3. Spatial Grounding & Localization Rule
        grounding_keywords = {
            "highlight", "where", "locate", "region", "show", "find",
            "bounding", "box", "localize", "coordinates", "detect", "pinpoint"
        }
        if bool(words & grounding_keywords):
            return TaskClassificationResult(
                task=TaskEnum.GROUNDING.value,
                workflow="spatial_grounding_workflow",
                required_agents=["grounding_agent", "response_agent"],
                required_artifacts=["bounding_boxes", "region_coordinates"],
                required_tools=["gemini-vlm", "opencv-grounding"],
                confidence=0.92,
                reason="Query explicitly requests spatial localization, bounding coordinates, or feature highlighting."
            )

        # 4. Scene Captioning & Land-Cover Description Rule
        caption_keywords = {
            "describe", "caption", "scene", "landcover", "overview",
            "summary", "explain this image", "what is shown"
        }
        if bool(words & caption_keywords) or "land cover" in query_clean or "major objects" in query_clean:
            return TaskClassificationResult(
                task=TaskEnum.CAPTIONING.value,
                workflow="scene_captioning_workflow",
                required_agents=["vqa_agent", "response_agent"],
                required_artifacts=["scene_summary", "land_cover_breakdown"],
                required_tools=["gemini-vlm"],
                confidence=0.94,
                reason="Query requests comprehensive satellite scene description, land-cover overview, or summary."
            )

        # 5. Single Image VQA (Default)
        return TaskClassificationResult(
            task=TaskEnum.SINGLE_IMAGE_VQA.value,
            workflow="single_image_vqa_workflow",
            required_agents=["vqa_agent", "response_agent"],
            required_artifacts=["vqa_evidence"],
            required_tools=["gemini-vlm"],
            confidence=0.95,
            reason="Single satellite image supplied for targeted visual question answering."
        )


task_classifier = TaskClassifier()
