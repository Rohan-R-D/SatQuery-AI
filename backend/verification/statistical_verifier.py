from typing import Tuple, List, Optional, Dict, Any


class StatisticalVerifier:
    """Verifies change detection statistics, mask plausibility, and anomaly thresholds."""

    @staticmethod
    def verify_change_mask(
        change_percentage: Optional[float],
        connected_regions_count: int,
        total_pixels: int
    ) -> Tuple[bool, List[str], float]:
        warnings: List[str] = []
        penalty = 0.0

        if change_percentage is None:
            return True, warnings, 0.0

        if change_percentage < 0.0 or change_percentage > 100.0:
            warnings.append(f"Invalid change percentage: {change_percentage}%. Must be in range [0, 100].")
            return False, warnings, 25.0

        # Anomaly check: >95% changed area typically indicates illumination blowout or complete cloud cover
        if change_percentage > 95.0:
            warnings.append(f"Extreme change detected ({change_percentage}%). Likely caused by severe cloud cover or illumination shift.")
            penalty += 15.0

        return len(warnings) == 0, warnings, penalty


statistical_verifier = StatisticalVerifier()
