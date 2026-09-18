"""
Backward compatibility layer for Task Router.
All router logic has moved to `orchestration/router.py` and `orchestration/task_classifier.py`.
"""
from orchestration.router import task_router, TaskRouter, RoutingDecision
from orchestration.task_classifier import task_classifier, TaskClassifier

__all__ = [
    "task_router",
    "TaskRouter",
    "RoutingDecision",
    "task_classifier",
    "TaskClassifier"
]
