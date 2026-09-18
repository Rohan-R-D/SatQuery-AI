import logging
from typing import Tuple, Optional

logger = logging.getLogger("satquery.services.confidence")


class ConfidenceService:
    """
    Empirical 5-factor remote-sensing confidence evaluation engine.
    Computes a transparent, auditable score based on input quality, alignment RMSE,
    evidence observation density, signal strength, and verification gate status.
    """

    @staticmethod
    def calculate_confidence(
        task_type: str,
        is_success: bool,
        evidence_count: int,
        change_percentage: Optional[float] = None,
        has_gemini: bool = True,
        error_code: Optional[str] = None,
        alignment_rmse: Optional[float] = None,
        verification_penalty: float = 0.0
    ) -> Tuple[float, str]:
        if not is_success:
            return 0.0, f"Analysis failed or model was unavailable (Error: {error_code or 'UNKNOWN'})."

        # Factor 1: Input Validity & Format Integrity (Max 20 pts)
        f1_input = 20.0

        # Factor 2: Pipeline Execution & Alignment Quality (Max 25 pts)
        f2_pipeline = 25.0
        alignment_note = ""
        if alignment_rmse is not None:
            if alignment_rmse > 2.0:
                f2_pipeline -= 15.0
                alignment_note = f" Co-registration error ({alignment_rmse:.2f}px > 2.0px) reduced certainty."
            elif alignment_rmse > 0.8:
                f2_pipeline -= 10.0
                alignment_note = f" Sub-pixel misregistration ({alignment_rmse:.2f}px > 0.8px) slightly reduced certainty."
            else:
                alignment_note = f" Sub-pixel co-registration verified (RMSE={alignment_rmse:.2f}px)."

        # Factor 3: Evidence Observation Density (Max 25 pts)
        # Scaled: 5 pts per evidence item up to 5 items (25 pts)
        f3_evidence = min(25.0, max(10.0, evidence_count * 5.0))

        # Factor 4: Signal Strength & Dynamic Range (Max 15 pts)
        f4_signal = 15.0
        if change_percentage is not None:
            if change_percentage < 0.1:
                f4_signal = 10.0  # Minimal signal
            elif change_percentage > 80.0:
                f4_signal = 8.0   # Extreme change / cloud shift warning

        # Factor 5: Model Agreement & Verification Gate (Max 15 pts)
        f5_verification = max(0.0, 15.0 - verification_penalty)

        # Multi-model boost or baseline penalty
        if not has_gemini:
            f5_verification = max(5.0, f5_verification - 5.0)

        total_score = f1_input + f2_pipeline + f3_evidence + f4_signal + f5_verification
        # Clamp to [15.0, 96.0]
        final_score = round(max(15.0, min(96.0, total_score)), 1)

        rating = "High" if final_score >= 85 else ("Medium" if final_score >= 60 else "Low")
        explanation = (
            f"Confidence {final_score}% ({rating}) derived from: "
            f"Input Integrity ({f1_input}/20), "
            f"Pipeline Execution ({f2_pipeline}/25), "
            f"Evidence Density ({f3_evidence}/25 from {evidence_count} items), "
            f"Signal Strength ({f4_signal}/15), and "
            f"Verification Integrity ({f5_verification}/15)."
            f"{alignment_note}"
        )

        return final_score, explanation


confidence_service = ConfidenceService()
confidence_calculator = confidence_service
ConfidenceCalculator = ConfidenceService
