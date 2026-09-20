"""
Unit tests for Remote Sensing Classifier interface and BigEarthNet classifier adapter.
(backend/ai/classifiers/base_classifier.py, backend/ai/classifiers/bigearthnet_classifier.py)
"""

import pytest
import numpy as np
from backend.ai.classifiers.base_classifier import BaseRSClassifier
from backend.ai.classifiers.bigearthnet_classifier import BigEarthNetClassifier
from backend.scientific.datasets.bigearthnet import CORINE_19_CLASSES


def test_bigearthnet_classifier_unconfigured():
    classifier = BigEarthNetClassifier()

    assert classifier.get_classifier_name() == "BigEarthNet-ResNet-50 (19-Class) (v2.0-reBEN)"

    # Availability check should return False if weights file does not exist
    assert classifier.is_available() is False

    # Predict should return structured dictionary with error details when unavailable
    dummy_tensor = np.zeros((12, 128, 128), dtype=np.float32)
    res = classifier.predict_land_cover(dummy_tensor)

    assert res["is_available"] is False
    assert res["is_error"] is True
    assert res["error_code"] == "CLASSIFIER_WEIGHTS_UNCONFIGURED"
    assert len(res["predictions"]) == 0


def test_bigearthnet_classifier_custom_threshold():
    classifier = BigEarthNetClassifier(threshold=0.6)
    assert classifier.threshold == 0.6
