"""
Backward compatibility layer for Model Registry.
All model registry definitions have moved to `orchestration/model_registry.py`.
"""
from orchestration.model_registry import model_registry, ModelRegistry, MODEL_REGISTRY

__all__ = [
    "model_registry",
    "ModelRegistry",
    "MODEL_REGISTRY"
]
