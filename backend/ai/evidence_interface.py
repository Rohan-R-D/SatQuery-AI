"""
SatQuery AI - Scientific Evidence Interface & Evidence Fusion.

Defines the contract and helper functions for incorporating Lane A deterministic
scientific measurements (spectral indices, BigEarthNet land-cover predictions, SAR backscatter, bounding boxes)
into Lane B Vision-Language Model reasoning contexts and Lane C fact-checking verification.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ScientificEvidence:
    """
    Standardized dataclass representing Lane A scientific measurement and classification outputs.
    """
    detected_regions: List[Dict[str, Any]] = field(default_factory=list)
    bounding_boxes: List[Dict[str, Any]] = field(default_factory=list)
    land_cover_predictions: Dict[str, Any] = field(default_factory=dict)  # BigEarthNet predictions
    change_percentage: Optional[float] = None
    spectral_indices: Dict[str, float] = field(default_factory=dict)
    sar_statistics: Dict[str, Any] = field(default_factory=dict)
    optical_sar_comparison: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    is_synthetic: bool = False  # MUST be True if using synthetic test fixtures

    def to_dict(self) -> Dict[str, Any]:
        """Converts evidence dataclass to dictionary payload."""
        return {
            "detected_regions": self.detected_regions,
            "bounding_boxes": self.bounding_boxes,
            "land_cover_predictions": self.land_cover_predictions,
            "change_percentage": self.change_percentage,
            "spectral_indices": self.spectral_indices,
            "sar_statistics": self.sar_statistics,
            "optical_sar_comparison": self.optical_sar_comparison,
            "confidence": self.confidence,
            "warnings": self.warnings,
            "processing_metadata": self.processing_metadata,
            "is_synthetic": self.is_synthetic,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScientificEvidence":
        """Instantiates evidence dataclass from dictionary payload."""
        if not data:
            return cls()
        return cls(
            detected_regions=data.get("detected_regions", []),
            bounding_boxes=data.get("bounding_boxes", []),
            land_cover_predictions=data.get("land_cover_predictions", {}),
            change_percentage=data.get("change_percentage"),
            spectral_indices=data.get("spectral_indices", {}),
            sar_statistics=data.get("sar_statistics", {}),
            optical_sar_comparison=data.get("optical_sar_comparison", {}),
            confidence=data.get("confidence"),
            warnings=data.get("warnings", []),
            processing_metadata=data.get("processing_metadata", {}),
            is_synthetic=data.get("is_synthetic", False),
        )


def format_evidence_for_prompt(evidence: Optional[ScientificEvidence]) -> str:
    """
    Formats scientific evidence into a clean, structured string block for VLM prompting.
    Injects physical measurements and BigEarthNet land-cover predictions into VLM prompt contexts.
    """
    if not evidence:
        return "No scientific evidence attached."

    lines = []
    if evidence.is_synthetic:
        lines.append("[NOTE: Synthetic scientific fixture data for testing]")

    # 1. BigEarthNet Local Land-Cover Predictions
    if evidence.land_cover_predictions:
        top_preds = evidence.land_cover_predictions.get("top_predictions", [])
        if top_preds:
            formatted_preds = [f"{p['class_name']} ({p['probability']*100:.1f}%)" for p in top_preds[:3] if isinstance(p, dict)]
            lines.append(f"- Measured Land Cover (BIFOLD BigEarthNet v2.0): {', '.join(formatted_preds)}")
        elif "labels" in evidence.land_cover_predictions:
            labels = evidence.land_cover_predictions.get("labels", [])
            lines.append(f"- Measured Land Cover (BIFOLD BigEarthNet v2.0): {', '.join(labels)}")

    # 2. Measured Spectral Indices
    if evidence.spectral_indices:
        indices_str = ", ".join(f"{k}={v:.3f}" for k, v in evidence.spectral_indices.items())
        lines.append(f"- Measured Spectral Indices: {indices_str}")

    # 3. SAR Backscatter Statistics
    if evidence.sar_statistics:
        sar_str = ", ".join(f"{k}={v}" for k, v in evidence.sar_statistics.items())
        lines.append(f"- Measured SAR Backscatter: {sar_str}")

    # 4. Bi-Temporal Change Percentage
    if evidence.change_percentage is not None:
        lines.append(f"- Measured Surface Change: {evidence.change_percentage:.2f}%")

    # 5. Feature Bounding Boxes / Detected Regions
    if evidence.detected_regions:
        lines.append(f"- Detected Feature Regions: {len(evidence.detected_regions)} regions identified")

    if evidence.warnings:
        lines.append(f"- Scientific Measurement Warnings: {'; '.join(evidence.warnings)}")

    if not lines:
        return "General scientific metadata attached."

    lines.append("\nCRITICAL INSTRUCTION: Your visual reasoning MUST strictly align with the physical measurements above. Do NOT contradict the measured land-cover classes or spectral index values.")
    return "\n".join(lines)


def create_synthetic_evidence_fixture(
    ndvi: float = 0.65,
    ndwi: float = -0.15,
    sar_vv_mean_db: float = -12.4,
    change_pct: Optional[float] = None,
    num_regions: int = 2,
    land_cover_classes: Optional[List[str]] = None
) -> ScientificEvidence:
    """
    Generates a synthetic scientific evidence fixture for testing.
    Clearly flags `is_synthetic=True` to prevent presenting synthetic fixtures as real data.
    """
    regions = [
        {"id": i, "label": f"synthetic_region_{i}", "bbox": [10 * i, 20 * i, 50, 50]}
        for i in range(num_regions)
    ]
    lc_classes = land_cover_classes or ["Coniferous forest", "Discontinuous urban fabric"]
    lc_preds = {
        "labels": lc_classes,
        "probabilities": {cls: 0.85 for cls in lc_classes},
        "top_predictions": [{"class_name": cls, "probability": 0.85} for cls in lc_classes],
        "model_id": "BIFOLD-BigEarthNetv2-0/resnet50-s2-v0.2.0 (Synthetic)",
    }
    return ScientificEvidence(
        detected_regions=regions,
        bounding_boxes=[r["bbox"] for r in regions],
        land_cover_predictions=lc_preds,
        change_percentage=change_pct,
        spectral_indices={"NDVI": ndvi, "NDWI": ndwi},
        sar_statistics={"vv_mean_db": sar_vv_mean_db, "vh_mean_db": sar_vv_mean_db - 6.0},
        confidence=90.0,
        warnings=["Synthetic test fixture - not real satellite measurements"],
        processing_metadata={"pipeline": "synthetic_fixture_generator", "version": "0.2"},
        is_synthetic=True
    )
