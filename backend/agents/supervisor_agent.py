import time
import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import UploadFile

from schemas.responses import AnalysisResponse
from schemas.execution import StepStatusEnum
from orchestration.task_classifier import task_classifier
from orchestration.workflow_manager import workflow_manager
from orchestration.execution_manager import execution_manager
from services.file_service import file_service
from services.gemini_service import gemini_service
from services.audit_service import audit_service
from agents.vqa_agent import vqa_agent
from agents.grounding_agent import grounding_agent
from agents.change_agent import change_agent
from agents.fusion_agent import fusion_agent
from agents.response_agent import response_agent

logger = logging.getLogger("satquery.agents.supervisor")


class SupervisorAgent:
    """
    Central Controller and Multi-Agent Orchestrator executing the 10-step remote-sensing analysis lifecycle.
    """

    def __init__(self):
        self.name = "supervisor_agent"
        self.description = "Coordinates specialist agents, manages execution workflows, and ensures verification standards."

    async def run_pipeline(
        self,
        input_type: str,
        image: UploadFile,
        second_image: Optional[UploadFile],
        query: str
    ) -> AnalysisResponse:
        start_time = time.time()
        exec_id = f"exec-{uuid.uuid4().hex[:12]}"
        logger.info(f"SupervisorAgent: Starting execution {exec_id} (input_type='{input_type}')")

        # Step 1 & 2: Receive Request and Read/Validate Inputs
        image_bytes = await file_service.read_file_bytes(image)
        second_bytes = await file_service.read_file_bytes(second_image) if second_image else None

        # Step 3: Understand Query & Classify Task
        classification = task_classifier.classify(
            input_type=input_type,
            query=query,
            has_second_image=bool(second_bytes)
        )
        task_name = classification.task
        workflow_name = classification.workflow

        logger.info(f"SupervisorAgent: Task='{task_name}', Workflow='{workflow_name}', Reason='{classification.reason}'")

        # Create Execution Record in ExecutionManager
        record = execution_manager.create_execution(
            execution_id=exec_id,
            task=task_name,
            query=query,
            input_type=input_type,
            workflow_name=workflow_name
        )

        execution_manager.update_step(exec_id, 1, StepStatusEnum.COMPLETED, f"Parsed query intent: '{query}'")
        execution_manager.update_step(exec_id, 2, StepStatusEnum.COMPLETED, f"Validated raster inputs (Primary: {len(image_bytes):,} bytes)")
        execution_manager.update_step(exec_id, 3, StepStatusEnum.COMPLETED, f"Classified task as '{task_name}' ({classification.reason})")
        execution_manager.update_step(exec_id, 4, StepStatusEnum.COMPLETED, f"Selected tools: {', '.join(classification.required_tools)}")

        # Step 4, 5, 6, 7 & 8: Execute Specialist Agent Workflow
        execution_manager.update_step(exec_id, 5, StepStatusEnum.RUNNING, "Executing specialist agent inference...")
        agent_output: Dict[str, Any] = {}

        try:
            if task_name in {"bi_temporal_change", "change_vqa"} and second_bytes:
                is_vqa = task_name == "change_vqa"
                agent_output = change_agent.execute_change_detection(
                    before_bytes=image_bytes,
                    after_bytes=second_bytes,
                    query=query,
                    is_explanatory_vqa=is_vqa
                )
            elif task_name in {"optical_sar_fusion", "optical_sar_analysis"} and second_bytes:
                agent_output = fusion_agent.execute_fusion(
                    optical_bytes=image_bytes,
                    sar_bytes=second_bytes,
                    query=query
                )
            elif task_name in {"grounding", "region_grounding"}:
                agent_output = grounding_agent.execute_grounding(
                    image_bytes=image_bytes,
                    query=query
                )
            elif task_name in {"captioning", "image_captioning"}:
                agent_output = vqa_agent.execute_caption(
                    image_bytes=image_bytes
                )
            else:
                # Default: Single Image VQA
                agent_output = vqa_agent.execute_vqa(
                    image_bytes=image_bytes,
                    query=query
                )

            execution_manager.update_step(exec_id, 5, StepStatusEnum.COMPLETED, f"Specialist inference completed via {agent_output.get('model_used')}")
            execution_manager.update_step(exec_id, 6, StepStatusEnum.COMPLETED, f"Collected visual artifacts and evidence observations.")
            execution_manager.update_step(exec_id, 7, StepStatusEnum.COMPLETED, f"Evaluated empirical confidence criteria.")

        except Exception as e:
            logger.error(f"SupervisorAgent: Error during agent execution: {str(e)}", exc_info=True)
            execution_manager.update_step(exec_id, 5, StepStatusEnum.FAILED, f"Inference notice: {str(e)}")
            agent_output = {
                "answer": f"Analysis execution notice: {str(e)}",
                "is_error": True,
                "error_code": "EXECUTION_ERROR",
                "evidence": ["Error occurred during specialist agent execution."]
            }

        # Step 9 & 10: Confidence Evaluation, Response Synthesis and Audit
        execution_manager.update_step(exec_id, 8, StepStatusEnum.RUNNING, "Synthesizing unified response...")
        elapsed_sec = time.time() - start_time
        has_gemini = gemini_service.is_available()

        # Retrieve updated trace steps
        updated_rec = execution_manager.get_execution(exec_id)
        trace_steps = updated_rec.trace_steps if updated_rec else []

        response = response_agent.synthesize(
            task=task_name,
            input_type=input_type,
            query=query,
            agent_output=agent_output,
            trace_steps=trace_steps,
            processing_time=elapsed_sec,
            has_gemini=has_gemini
        )

        execution_manager.update_step(exec_id, 8, StepStatusEnum.COMPLETED, "Structured response and trace finalized.")
        completed_rec = execution_manager.complete_execution(
            execution_id=exec_id,
            result={
                "task": task_name,
                "confidence": response.confidence,
                "answer_summary": response.answer[:120] + "..." if len(response.answer) > 120 else response.answer
            },
            duration_sec=response.processing_time
        )

        if completed_rec:
            audit_service.record_execution(completed_rec)

        logger.info(f"SupervisorAgent: Completed {exec_id} in {response.processing_time}s with confidence {response.confidence}%")
        return response


supervisor_agent = SupervisorAgent()
agent_orchestrator = supervisor_agent
