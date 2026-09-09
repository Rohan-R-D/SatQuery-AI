import re
import logging
from pydantic import BaseModel
from typing import List

logger = logging.getLogger("satquery.router")

class RoutingDecision(BaseModel):
    task: str
    reason: str
    required_tools: List[str]

class TaskRouter:
    @staticmethod
    def route_query(
        input_type: str,
        query: str,
        has_second_image: bool = False
    ) -> RoutingDecision:
        query_lower = query.lower().strip()
        words = set(re.findall(r'\b\w+\b', query_lower))

        # 1. Optical + SAR Multimodal Analysis Rule
        optical_sar_keywords = {"optical", "sar", "radar", "sentinel-1", "sentinel-2", "multimodal", "backscatter"}
        if input_type == "optical_sar" or (has_second_image and bool(words & optical_sar_keywords)):
            return RoutingDecision(
                task="optical_sar_analysis",
                reason="Optical and SAR inputs provided for joint radar and reflectance interpretation.",
                required_tools=["gemini-vlm", "opencv-change"]
            )

        # 2. Bi-Temporal Change Detection & Change-VQA Rules
        change_keywords = {"change", "changed", "before", "after", "increase", "decrease", "between", "dates", "variation", "growth"}
        is_temporal_request = input_type == "bi_temporal" or has_second_image or bool(words & change_keywords)

        if is_temporal_request:
            question_words = {"what", "why", "how", "describe", "explain", "has", "is"}
            is_question = bool(words & question_words) or query_lower.endswith("?")
            
            if is_question:
                return RoutingDecision(
                    task="change_vqa",
                    reason="Bi-temporal image pair supplied with a query requesting an explanatory change assessment.",
                    required_tools=["opencv-change", "gemini-vlm"]
                )
            else:
                return RoutingDecision(
                    task="bi_temporal_change",
                    reason="Bi-temporal image pair supplied for land-use difference mapping.",
                    required_tools=["opencv-change"]
                )

        # 3. Region Grounding Rule
        grounding_keywords = {"highlight", "where", "locate", "region", "show", "find", "bounding"}
        if bool(words & grounding_keywords):
            return RoutingDecision(
                task="region_grounding",
                reason="Query requests spatial localization and bounding region identification.",
                required_tools=["gemini-vlm"]
            )

        # 4. Image Captioning Rule
        caption_keywords = {"describe", "caption", "scene", "landcover", "objects", "overview", "summary"}
        if bool(words & caption_keywords) or "land cover" in query_lower or "major objects" in query_lower:
            return RoutingDecision(
                task="image_captioning",
                reason="Query requests full scene description or land-cover overview.",
                required_tools=["gemini-vlm"]
            )

        # 5. Single Image VQA (Default)
        return RoutingDecision(
            task="single_image_vqa",
            reason="One image was supplied and the query asks a visual question.",
            required_tools=["gemini-vlm"]
        )

task_router = TaskRouter()
