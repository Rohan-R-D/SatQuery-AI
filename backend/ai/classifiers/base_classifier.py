"""
SatQuery AI - Remote Sensing Classifier Base Interface.

Separates non-conversational deep learning classifiers (e.g., BigEarthNet ResNet-50 / ViT)
from text-generative Vision-Language Models (BaseVLMAdapter).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np


class BaseRSClassifier(ABC):
    """
    Abstract interface for multi-label and single-label remote sensing classifiers.
    Produces structured probability vectors and land-cover class rankings without text generation.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if classifier checkpoint weights are loaded or configured."""
        pass

    @abstractmethod
    def get_classifier_name(self) -> str:
        """Returns human-readable name and version of the classifier backbone."""
        pass

    @abstractmethod
    def predict_land_cover(
        self, raster_tensor: np.ndarray, top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Executes land-cover classification on an input multi-band array tensor.
        
        Args:
            raster_tensor: Array of shape (C, H, W) or (H, W, C)
            top_k: Top K land-cover predictions to return
            
        Returns structured dictionary:
        {
            "predictions": [{"class_name": str, "probability": float, "class_idx": int}],
            "top_class": str,
            "top_probability": float,
            "classifier_name": str,
            "model_version": str,
            "is_available": bool,
            "is_error": bool,
            "error_code": Optional[str],
            "warnings": List[str]
        }
        """
        pass
