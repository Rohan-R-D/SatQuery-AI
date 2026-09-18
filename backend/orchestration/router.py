import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from schemas.tasks import TaskClassificationResult
from orchestration.task_classifier import task_classifier

logger = logging.getLogger("satquery.orchestration.router")


class RoutingDecision(BaseModel):
    task: str = Field(description="Routed task identifier")
    reason: str = Field(description="Explanation of routing decision")
    required_tools: List[str] = Field(default_factory=list, description="Tools needed for pipeline")
    workflow: Optional[str] = Field(default=None, description="Workflow identifier")
    required_agents: Optional[List[str]] = Field(default_factory=list, description="Agents to execute")
    confidence: Optional[float] = Field(default=1.0, description="Routing certainty")


class TaskRouter:
    @staticmethod
    def route_query(
        input_type: str,
        query: str,
        has_second_image: bool = False
    ) -> RoutingDecision:
        result: TaskClassificationResult = task_classifier.classify(
            input_type=input_type,
            query=query,
            has_second_image=has_second_image
        )
        logger.info(f"TaskRouter: task='{result.task}', workflow='{result.workflow}', tools={result.required_tools}")

        return RoutingDecision(
            task=result.task,
            reason=result.reason,
            required_tools=result.required_tools,
            workflow=result.workflow,
            required_agents=result.required_agents,
            confidence=result.confidence
        )


task_router = TaskRouter()
