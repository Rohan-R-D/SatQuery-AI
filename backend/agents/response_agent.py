import logging
from typing import Dict, Any, List, Optional
from schemas.responses import AnalysisResponse
from schemas.evidence import EvidenceItem
from schemas.execution import TraceStep
from services.evidence_service import evidence_service
from services.confidence_service import confidence_service

logger = logging.getLogger("satquery.agents.response")


class ResponseAgent:
    """
    Specialist Agent for Response Synthesis, Evidence Consolidation, and Quality Assurance.
    """

    def __init__(self):
        self.name = "response_agent"
        self.description = "Synthesizes final verified analysis responses, compiles evidence, and evaluates empirical confidence."

    def synthesize(
        self,
        task: str,
        input_type: str,
        query: str,
        agent_output: Dict[str, Any],
        trace_steps: List[TraceStep],
        processing_time: float,
        has_gemini: bool = True
    ) -> AnalysisResponse:
        """Synthesize verified, schema-compliant AnalysisResponse."""
        logger.info(f"ResponseAgent: synthesizing final response for task='{task}'")

        is_error = agent_output.get("is_error", False)
        error_code = agent_output.get("error_code")
        answer = agent_output.get("answer", "Analysis completed.")
        model_used = agent_output.get("model_used", "Gemini Multimodal VLM")
        change_percentage = agent_output.get("change_percentage")
        regions = agent_output.get("regions")
        artifacts = agent_output.get("artifacts")
        built_up_regions = agent_output.get("built_up_regions")
        water_regions = agent_output.get("water_regions")
        extra_metrics = agent_output.get("metrics")
        gemini_evidence_strings = agent_output.get("evidence", [])

        # 1. Evidence Extraction
        evidence_items = evidence_service.extract_evidence(
            task_type=task,
            query=query,
            extra_metrics=extra_metrics,
            gemini_evidence_strings=gemini_evidence_strings,
            regions=regions,
            artifacts=artifacts
        )

        # 2. Transparent Deterministic Confidence Evaluation
        confidence_score, confidence_exp = confidence_service.calculate_confidence(
            task_type=task,
            is_success=not is_error,
            evidence_count=len(evidence_items),
            change_percentage=change_percentage,
            has_gemini=has_gemini,
            error_code=error_code
        )

        is_success = not is_error

        return AnalysisResponse(
            success=is_success,
            task=task,
            input_type=input_type,
            answer=answer,
            confidence=confidence_score,
            confidence_explanation=confidence_exp,
            model_used=model_used,
            evidence=evidence_items,
            execution_trace=trace_steps,
            processing_time=round(processing_time, 3),
            change_percentage=change_percentage,
            built_up_regions=built_up_regions,
            water_regions=water_regions,
            regions=regions,
            artifacts=artifacts
        )


response_agent = ResponseAgent()
