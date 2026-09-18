from typing import Tuple, List, Optional, Dict, Any


class SemanticVerifier:
    """
    Cross-checks Lane B VLM qualitative text claims against Lane A deterministic metrics
    to detect hallucinations and unsupported assertions.
    """
    @staticmethod
    def cross_check_claims(
        vlm_answer: str,
        task: str,
        lane_a_metrics: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], float]:
        warnings: List[str] = []
        penalty = 0.0
        ans_lower = vlm_answer.lower()
        metrics = lane_a_metrics or {}

        # 1. Check Change Claims vs Change Percentage
        change_pct = metrics.get("change_percentage")
        if change_pct is not None:
            claims_major_change = any(w in ans_lower for w in ["massive expansion", "widespread destruction", "severe flooding", "major change", "large-scale"])
            if claims_major_change and change_pct < 0.5:
                warnings.append(f"VLM asserted major surface change, but deterministic Lane A pixel differencing measured only {change_pct}%.")
                penalty += 15.0

            claims_no_change = any(w in ans_lower for w in ["no change", "remained unchanged", "identical", "no visible difference"])
            if claims_no_change and change_pct > 25.0:
                warnings.append(f"VLM asserted no visible change, but deterministic Lane A pixel differencing measured {change_pct}% changed area.")
                penalty += 15.0

        # 2. Check Water Claims vs Water Estimation
        est_water_pct = metrics.get("estimated_water_pct")
        if est_water_pct is not None:
            claims_large_water = "large water body" in ans_lower or "vast lake" in ans_lower
            if claims_large_water and est_water_pct < 0.1:
                warnings.append("VLM claimed large water body presence, but spectral band index detected <0.1% water signature.")
                penalty += 10.0

        return len(warnings) == 0, warnings, penalty


semantic_verifier = SemanticVerifier()
