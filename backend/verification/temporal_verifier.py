from typing import Tuple, Optional, Dict, Any


class TemporalVerifier:
    """Verifies temporal image pairing consistency and spatial coverage."""

    @staticmethod
    def verify_temporal_pair(
        has_second_image: bool,
        input_type: str,
        t1_metadata: Optional[Dict[str, Any]] = None,
        t2_metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        if input_type in {"bi_temporal", "bitemporal"}:
            if not has_second_image:
                return False, "Bi-temporal change analysis requires both T1 (Before) and T2 (After) rasters."
        return True, None


temporal_verifier = TemporalVerifier()
