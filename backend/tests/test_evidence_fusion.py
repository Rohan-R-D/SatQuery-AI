"""
Unit tests for Scientific Evidence Interface & Evidence Fusion (backend/ai/evidence_interface.py).
"""

import pytest
from backend.ai.evidence_interface import ScientificEvidence, format_evidence_for_prompt, create_synthetic_evidence_fixture


def test_scientific_evidence_default():
    evidence = ScientificEvidence()
    assert evidence.land_cover_predictions == {}
    assert evidence.is_synthetic is False


def test_scientific_evidence_with_land_cover():
    evidence = ScientificEvidence(
        land_cover_predictions={"labels": ["Discontinuous urban fabric", "Industrial or commercial units"]}
    )
    formatted = format_evidence_for_prompt(evidence)
    assert "Discontinuous urban fabric" in formatted
    assert "Industrial or commercial units" in formatted


def test_create_synthetic_evidence_fixture():
    evidence = create_synthetic_evidence_fixture(ndvi=0.72)
    assert evidence.is_synthetic is True
    assert evidence.spectral_indices["NDVI"] == 0.72
    formatted = format_evidence_for_prompt(evidence)
    assert "[NOTE: Synthetic scientific fixture data for testing]" in formatted


def test_scientific_evidence_from_dict():
    evidence_dict = {
        "change_percentage": 14.5,
        "spectral_indices": {"NDVI": 0.65},
        "land_cover_predictions": {"labels": ["Coniferous forest"]},
        "is_synthetic": True,
    }
    obj = ScientificEvidence.from_dict(evidence_dict)
    assert obj.change_percentage == 14.5
    assert obj.land_cover_predictions["labels"] == ["Coniferous forest"]
    assert obj.is_synthetic is True

