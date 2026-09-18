import pytest
from verification.geometry_verifier import geometry_verifier
from verification.statistical_verifier import statistical_verifier
from verification.semantic_verifier import semantic_verifier
from agents.verification_agent import verification_agent


def test_geometry_verifier_dimensions():
    # Identical aspect ratio
    ok, warn = geometry_verifier.verify_dimensions((500, 500), (500, 500))
    assert ok is True
    assert warn is None

    # Mismatched aspect ratio
    ok, warn = geometry_verifier.verify_dimensions((800, 200), (400, 400))
    assert ok is False
    assert "Aspect ratio mismatch" in warn


def test_geometry_verifier_coregistration_rmse():
    # Valid sub-pixel alignment
    ok, warn, penalty = geometry_verifier.verify_coregistration(0.45)
    assert ok is True
    assert warn is None
    assert penalty == 0.0

    # Misregistration > 0.8px
    ok, warn, penalty = geometry_verifier.verify_coregistration(1.25)
    assert ok is False
    assert "exceeds sub-pixel threshold" in warn
    assert penalty > 0.0


def test_statistical_verifier():
    # Valid change percentage
    ok, warns, penalty = statistical_verifier.verify_change_mask(4.5, 3, 100000)
    assert ok is True
    assert len(warns) == 0

    # Extreme change anomaly > 95%
    ok, warns, penalty = statistical_verifier.verify_change_mask(98.5, 1, 100000)
    assert ok is False
    assert any("Extreme change" in w for w in warns)
    assert penalty > 0.0


def test_semantic_verifier_hallucination_detection():
    # VLM claims massive change but Lane A measured 0.1%
    ok, warns, penalty = semantic_verifier.cross_check_claims(
        vlm_answer="There is massive expansion and severe flooding across the entire sector.",
        task="change_vqa",
        lane_a_metrics={"change_percentage": 0.05}
    )
    assert ok is False
    assert any("VLM asserted major surface change" in w for w in warns)
    assert penalty > 0.0


def test_verification_agent_full_pass():
    result = verification_agent.verify(
        task="bi_temporal_change",
        input_type="bi_temporal",
        primary_dimensions=(400, 400),
        secondary_dimensions=(400, 400),
        rmse=0.35,
        change_percentage=3.5,
        connected_regions_count=2,
        total_pixels=160000,
        vlm_answer="Minor commercial construction detected on the eastern perimeter.",
        lane_a_metrics={"change_percentage": 3.5}
    )
    assert result.passed is True
    assert len(result.warnings) == 0
    assert result.confidence_penalty == 0.0
