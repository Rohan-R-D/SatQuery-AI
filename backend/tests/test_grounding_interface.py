"""
Unit tests for provider-independent spatial grounding interface (backend/ai/grounding_interface.py).
Tests schema validation, coordinate conversion/scaling, structured errors, and adapter fallbacks.
"""

import pytest
from backend.ai.grounding_interface import (
    GroundingBox,
    GroundingRequest,
    GroundingResponse,
    CoordinateConvention,
    BaseGroundingAdapter,
    validate_grounding_coordinates,
    scale_normalized_coordinates,
)


def test_grounding_box_validation_valid():
    box = GroundingBox(
        label="water body",
        box=[50.0, 100.0, 400.0, 300.0],
        confidence=0.92,
    )
    assert box.label == "water body"
    assert box.box == [50.0, 100.0, 400.0, 300.0]
    assert box.confidence == 0.92


def test_coordinate_validation_pixel():
    # Valid box
    is_valid, issues = validate_grounding_coordinates(
        box=[50.0, 100.0, 400.0, 300.0],
        image_width=500,
        image_height=500,
        convention=CoordinateConvention.PIXEL,
    )
    assert is_valid is True
    assert len(issues) == 0

    # Invalid degenerate box (x2 <= x1)
    is_valid_deg, issues_deg = validate_grounding_coordinates(
        box=[400.0, 100.0, 50.0, 300.0],
        image_width=500,
        image_height=500,
        convention=CoordinateConvention.PIXEL,
    )
    assert is_valid_deg is False
    assert any("Degenerate" in msg for msg in issues_deg)


def test_coordinate_scaling_normalized_1000_to_pixel():
    # Token order [y1, x1, y2, x2] = [100, 200, 500, 800]
    box_1000 = [100.0, 200.0, 500.0, 800.0]
    scaled = scale_normalized_coordinates(box_1000, image_width=1000, image_height=500)
    # y1 (10% of 500) = 50.0, x1 (20% of 1000) = 200.0, y2 (50% of 500) = 250.0, x2 (80% of 1000) = 800.0
    # Returns [px_x1, px_y1, px_x2, px_y2] = [200.0, 50.0, 800.0, 250.0]
    assert scaled == [200.0, 50.0, 800.0, 250.0]


def test_grounding_response_schema():
    box = GroundingBox(
        label="solar panel",
        box=[20.0, 10.0, 80.0, 50.0],
        confidence=0.88,
    )
    resp = GroundingResponse(
        answer="Detected 1 solar panel region.",
        bounding_boxes=[box],
        source_model="geochat-7b",
        provider="geochat",
        capability_supported=True,
    )

    assert resp.capability_supported is True
    assert len(resp.bounding_boxes) == 1
    assert resp.is_error is False
    assert resp.source_model == "geochat-7b"


def test_grounding_response_unsupported():
    resp = GroundingResponse(
        answer="Grounding capability not supported by model gemini-1.5-flash.",
        bounding_boxes=[],
        source_model="gemini-1.5-flash",
        provider="gemini",
        capability_supported=False,
        is_error=True,
        error_code="GROUNDING_UNSUPPORTED",
    )

    assert resp.capability_supported is False
    assert len(resp.bounding_boxes) == 0
    assert resp.is_error is True
    assert resp.error_code == "GROUNDING_UNSUPPORTED"


class DummyUnsupportedGroundingAdapter(BaseGroundingAdapter):
    def supports_grounding(self) -> bool:
        return False

    def locate_grounded_regions(self, request: GroundingRequest) -> GroundingResponse:
        return GroundingResponse(
            answer="Dummy adapter does not support grounding.",
            bounding_boxes=[],
            source_model="dummy",
            provider="dummy",
            capability_supported=False,
            is_error=True,
            error_code="GROUNDING_UNSUPPORTED",
        )


def test_base_grounding_adapter_fallback():
    adapter = DummyUnsupportedGroundingAdapter()
    assert adapter.supports_grounding() is False
    req = GroundingRequest(image_bytes=b"dummy", query="test")
    resp = adapter.locate_grounded_regions(req)
    assert resp.capability_supported is False
    assert resp.is_error is True
    assert resp.error_code == "GROUNDING_UNSUPPORTED"
