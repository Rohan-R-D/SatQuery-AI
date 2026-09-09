import time
import base64
import logging
from fastapi import UploadFile

from schemas import AnalysisResponse, EvidenceItem
from router import task_router, RoutingDecision
from gemini_service import gemini_service
from change_detection import change_detection_engine
from optical_sar import optical_sar_engine
from evidence import evidence_extractor
from confidence import confidence_calculator
from report import report_generator
from services.file_service import file_service

logger = logging.getLogger("satquery.agent")

class AgentOrchestrator:
    async def run_pipeline(
        self,
        input_type: str,
        image: UploadFile,
        second_image: UploadFile | None,
        query: str
    ) -> AnalysisResponse:
        start_time = time.time()
        logger.info(f"Agent Orchestrator received request: input_type='{input_type}', filename='{image.filename}'")

        # 1. Read Image Bytes
        image_bytes = await file_service.read_file_bytes(image)
        second_bytes = await file_service.read_file_bytes(second_image) if second_image else None

        # 2. Query Routing & Task Classification
        decision: RoutingDecision = task_router.route_query(
            input_type=input_type,
            query=query,
            has_second_image=bool(second_bytes)
        )

        logger.info(f"Router Decision: task='{decision.task}', reason='{decision.reason}', tools={decision.required_tools}")

        task_name = decision.task
        tools_list = decision.required_tools

        change_percentage = None
        built_up_list = None
        water_list = None
        regions_list = None
        artifacts_list = None
        evidence_items: list[EvidenceItem] = []
        is_success = True
        error_code = None

        has_gemini = gemini_service._client is not None

        # 3. Tool Execution based on Router Task
        if decision.task in {"single_image_vqa", "image_captioning", "region_grounding"}:
            model_used_name = "Gemini Multimodal VLM"
            gemini_res = gemini_service.analyze_image(image_bytes, query)

            answer = gemini_res.get("answer", "")
            is_success = not gemini_res.get("is_error", False)
            error_code = gemini_res.get("error_code") if not is_success else None

            gemini_evidence_strings = gemini_res.get("evidence", [])
            evidence_items = evidence_extractor.extract_evidence(
                task_type=decision.task,
                query=query,
                gemini_evidence_strings=gemini_evidence_strings
            )

        elif decision.task in {"bi_temporal_change", "change_vqa"} and second_bytes:
            model_used_name = "Gemini Multimodal VLM"

            # 1. OpenCV Change Engine
            change_res = change_detection_engine.detect_changes(image_bytes, second_bytes)

            change_percentage = change_res["change_percentage"]
            changed_pixels = change_res["changed_pixels"]
            total_pixels = change_res["total_pixels"]
            regions_list = change_res["regions"]
            disclaimer = change_res["disclaimer"]

            artifacts_list = [
                {"name": "difference_map", "type": "image/png", "url": change_res["difference_map"]},
                {"name": "change_mask", "type": "image/png", "url": change_res["change_mask"]},
                {"name": "change_overlay", "type": "image/png", "url": change_res["change_overlay"]},
            ]

            overlay_data_url = change_res["change_overlay"]
            if "," in overlay_data_url:
                overlay_bytes = base64.b64decode(overlay_data_url.split(",")[1])
            else:
                overlay_bytes = image_bytes

            # 2. Gemini Multimodal 3-Image Interpretation
            gemini_res = gemini_service.analyze_change_images(
                before_bytes=image_bytes,
                after_bytes=second_bytes,
                overlay_bytes=overlay_bytes,
                query=query,
                change_percentage=change_percentage
            )

            vlm_answer = gemini_res.get("answer", "")
            is_success = not gemini_res.get("is_error", False)
            error_code = gemini_res.get("error_code") if not is_success else None

            answer = (
                f"{vlm_answer}\n\n"
                f"Quantitative OpenCV Summary: {change_percentage}% pixel variation ({changed_pixels:,} / {total_pixels:,} pixels) across {len(regions_list)} region(s).\n"
                f"Note: {disclaimer}"
            )

            gemini_evidence_strings = gemini_res.get("evidence", [])
            metrics_dict = {
                "Change Percentage": f"{change_percentage}%",
                "Changed Pixels": f"{changed_pixels:,}",
                "Total Pixels": f"{total_pixels:,}",
                "Connected Regions": f"{len(regions_list)}"
            }
            evidence_items = evidence_extractor.extract_evidence(
                task_type=decision.task,
                query=query,
                extra_metrics=metrics_dict,
                gemini_evidence_strings=gemini_evidence_strings
            )

        elif decision.task == "optical_sar_analysis" and second_bytes:
            model_used_name = "Gemini Multimodal VLM"

            gemini_sar_res = gemini_service.analyze_optical_sar(image_bytes, second_bytes, query)

            raw_answer = gemini_sar_res.get("answer", "")
            is_success = not gemini_sar_res.get("is_error", False)
            error_code = gemini_sar_res.get("error_code") if not is_success else None

            answer = (
                f"[Optical + SAR Multimodal Prototype]: {raw_answer}\n\n"
                f"Note: This is an Optical + SAR Multimodal Prototype leveraging dual-sensor visual reasoning."
            )

            built_up_raw = gemini_sar_res.get("built_up_regions", [])
            water_raw = gemini_sar_res.get("water_regions", [])

            built_up_list = [{"description": b} for b in built_up_raw]
            water_list = [{"description": w} for w in water_raw]

            gemini_evidence_strings = gemini_sar_res.get("evidence", [])
            evidence_items = evidence_extractor.extract_evidence(
                task_type=decision.task,
                query=query,
                gemini_evidence_strings=gemini_evidence_strings
            )

        else:
            model_used_name = "Gemini Multimodal VLM"
            answer = f"Analysis pipeline completed for query: '{query}'."
            evidence_items = evidence_extractor.extract_evidence(input_type, query)

        # 4. Transparent Deterministic Confidence Score Calculation
        confidence_score, confidence_exp = confidence_calculator.calculate_confidence(
            task_type=decision.task,
            is_success=is_success,
            evidence_count=len(evidence_items),
            change_percentage=change_percentage,
            has_gemini=has_gemini,
            error_code=error_code
        )

        # 5. Measure Execution Duration & Build Trace Timeline
        elapsed_time = round(time.time() - start_time, 3)

        trace_steps = report_generator.generate_execution_trace(
            task=task_name,
            reason=decision.reason,
            tools=tools_list,
            execution_time_sec=elapsed_time,
            evidence_count=len(evidence_items),
            confidence_score=confidence_score
        )

        logger.info(f"Agent finished orchestrating task='{task_name}' in {elapsed_time}s with confidence={confidence_score}%")

        return AnalysisResponse(
            success=is_success,
            task=task_name,
            input_type=input_type,
            answer=answer,
            confidence=confidence_score,
            confidence_explanation=confidence_exp,
            model_used=model_used_name,
            evidence=evidence_items,
            execution_trace=trace_steps,
            processing_time=elapsed_time,
            change_percentage=change_percentage,
            built_up_regions=built_up_list,
            water_regions=water_list,
            regions=regions_list,
            artifacts=artifacts_list
        )

agent_orchestrator = AgentOrchestrator()
