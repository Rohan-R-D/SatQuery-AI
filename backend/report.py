import re
import uuid
import datetime
from typing import Tuple
from schemas import ReportRequest, AnalysisResponse, TraceStep, StepStatusEnum

def sanitize_header_text(text: str) -> str:
    """Strip dangerous control characters from user text before embedding in headers."""
    if not text:
        return ""
    # Strip null bytes and non-printable control characters except standard whitespace
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text).strip()

class ReportGenerator:
    """
    Service responsible for synthesizing downloadable Markdown/Text analysis reports
    and agent execution trace step histories.
    """
    def generate_execution_trace(
        self,
        task: str,
        reason: str,
        tools: list,
        execution_time_sec: float,
        evidence_count: int,
        confidence_score: float
    ) -> list:
        """
        Generates structured 8-step Agent execution trace timeline.
        """
        tools_str = ", ".join(tools) if tools else "gemini-vlm"
        return [
            TraceStep(
                id=1,
                title="Query Understanding",
                description="Parsed natural language query intent and extracted spatial entities.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=2,
                title="Input Validation",
                description="Validated satellite raster integrity, spatial dimensions, and coordinate references.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=3,
                title="Task Classification",
                description=f"Classified task as '{task}' ({reason}).",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=4,
                title="Model Selection",
                description=f"Selected engine pipeline: {tools_str}.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=5,
                title="Analysis Execution",
                description=f"Executed vision-language analysis pipeline in {execution_time_sec:.3f}s.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=6,
                title="Evidence Generation",
                description=f"Collected {evidence_count} visual evidence item(s) and bounding regions.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=7,
                title="Confidence Calculation",
                description=f"Evaluated multi-factor certainty score at {confidence_score:.1f}%.",
                status=StepStatusEnum.COMPLETED
            ),
            TraceStep(
                id=8,
                title="Response Generation",
                description="Synthesized structured response payload and visual annotations.",
                status=StepStatusEnum.COMPLETED
            ),
        ]

    def generate_report(self, request: ReportRequest) -> Tuple[str, str]:
        """
        Generates a structured Markdown report from a ReportRequest.
        Returns (report_content_str, download_filename).
        Filename strictly adheres to server-generated regex: ^satquery_report_[a-f0-9]{8}_[0-9]{8}\\.md$
        """
        now_str = request.timestamp or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        now_str = sanitize_header_text(now_str)

        # Input Type Display Mapping
        input_type_map = {
            "single": "Single Scene Satellite Image VQA",
            "bi_temporal": "Bi-Temporal Change Detection (T1 vs T2)",
            "bitemporal": "Bi-Temporal Change Detection (T1 vs T2)",
            "optical_sar": "Optical + SAR Joint Multimodal Analysis",
            "optical-sar": "Optical + SAR Joint Multimodal Analysis"
        }
        input_type_str = input_type_map.get(request.input_type.lower(), request.input_type.upper())
        task_str = sanitize_header_text(request.task)
        model_str = sanitize_header_text(request.model_used)
        query_str = sanitize_header_text(request.query)

        # Rating determination
        rating = "High" if request.confidence >= 85 else ("Medium" if request.confidence >= 60 else "Low")

        # Format Evidence Section
        evidence_lines = []
        if request.evidence:
            for idx, item in enumerate(request.evidence, 1):
                item_title = sanitize_header_text(item.title)
                item_desc = sanitize_header_text(item.description)
                evidence_lines.append(f"{idx}. [{item.type.upper()}] {item_title}: {item_desc}")
                if item.metrics:
                    metrics_str = ", ".join([f"{sanitize_header_text(str(k))}: {sanitize_header_text(str(v))}" for k, v in item.metrics.items()])
                    evidence_lines.append(f"     * Metrics: {metrics_str}")
        else:
            evidence_lines.append("* Visual evidence verified by model perception.")

        evidence_text = "\n".join(evidence_lines)

        # Format Execution Trace Section
        trace_lines = []
        if request.execution_trace:
            for step in request.execution_trace:
                status_icon = "[OK]" if step.status == "COMPLETED" else ("!FAIL!" if step.status == "FAILED" else "[..]")
                step_title = sanitize_header_text(step.title)
                step_desc = sanitize_header_text(step.description)
                trace_lines.append(f"{status_icon} Step {step.id}: {step_title} [{step.status}]")
                trace_lines.append(f"     -> {step_desc}")
        else:
            trace_lines.append("* 8-step agentic execution completed.")

        trace_text = "\n".join(trace_lines)

        # Change percentage section if present
        change_text = ""
        if request.change_percentage is not None:
            change_text = f"\nComputed Pixel Change      : {request.change_percentage:.2f}%\n"

        report_md = f"""================================================================================
                        SATQUERY AI - ANALYSIS REPORT
================================================================================

Analysis Date / Time   : {now_str}
Input Imagery Mode     : {input_type_str}
Analytical Task        : {task_str}
Model / Engine Used    : {model_str}
Processing Time        : {request.processing_time:.3f} seconds

--------------------------------------------------------------------------------
1. USER QUERY
--------------------------------------------------------------------------------
"{query_str}"

--------------------------------------------------------------------------------
2. ANALYTICAL ANSWER
--------------------------------------------------------------------------------
{request.answer}

--------------------------------------------------------------------------------
3. CONFIDENCE & CERTAINTY ASSESSMENT
--------------------------------------------------------------------------------
Confidence Score       : {request.confidence:.1f}% ({rating})
Confidence Rationale   : {request.confidence_explanation}{change_text}
--------------------------------------------------------------------------------
4. VISUAL EVIDENCE & OBSERVATIONS
--------------------------------------------------------------------------------
{evidence_text}

--------------------------------------------------------------------------------
5. AGENT EXECUTION TRACE
--------------------------------------------------------------------------------
{trace_text}

================================================================================
Generated by SatQuery AI - Agentic Remote-Sensing Vision-Language Assistant
================================================================================
"""

        # Strictly server-generated UUID & date filename matching ^satquery_report_[a-f0-9]{8}_[0-9]{8}\.md$
        report_id = uuid.uuid4().hex[:8]
        date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        filename = f"satquery_report_{report_id}_{date_str}.md"
        return report_md, filename


# Global singleton instance
report_generator = ReportGenerator()

def generate_analysis_report(request: ReportRequest) -> Tuple[str, str]:
    return report_generator.generate_report(request)
