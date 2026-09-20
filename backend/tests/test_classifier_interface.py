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
    classifier = BigEarthNetClassifier(checkpoint_path="non_existent_weights_dir")

    assert classifier.get_classifier_name() == "BIFOLD BigEarthNet v2.0 ResNet-50 S2 [BIFOLD-BigEarthNetv2-0/resnet50-s2-v0.2.0]"

    # Availability check should return False if weights file does not exist
    assert classifier.is_available() is False

    # Predict should return structured dictionary with error details when unavailable
    dummy_tensor = np.zeros((10, 120, 120), dtype=np.float32)
    res = classifier.predict_land_cover(dummy_tensor)

    assert res["is_available"] is False
    assert res["is_error"] is True
    assert res["error_code"] == "CLASSIFIER_WEIGHTS_UNCONFIGURED"
    assert len(res["top_predictions"]) == 0


def test_bigearthnet_classifier_configured():
    classifier = BigEarthNetClassifier()

    # When checkpoint files exist, is_available() should return True
    assert classifier.is_available() is True

    dummy_tensor = np.zeros((10, 120, 120), dtype=np.float32)
    res = classifier.predict_land_cover(dummy_tensor)

    assert res["is_available"] is True
    assert res["is_error"] is False
    assert len(res["top_predictions"]) > 0


def test_bigearthnet_classifier_custom_threshold():
    classifier = BigEarthNetClassifier(threshold=0.6)
    assert classifier.threshold == 0.6


def test_bigearthnet_classifier_preprocessing():
    classifier = BigEarthNetClassifier()
    dummy_raw = np.ones((10, 120, 120), dtype=np.float32) * 1000.0
    processed = classifier.preprocess_raster_patch(dummy_raw)
    assert processed.shape == (10, 120, 120)
    assert isinstance(processed, np.ndarray)


