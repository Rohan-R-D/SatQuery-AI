from typing import Dict, Any, Optional, List, Tuple
from verification import VerificationResult
from verification.geometry_verifier import geometry_verifier
from verification.temporal_verifier import temporal_verifier
from verification.statistical_verifier import statistical_verifier
from verification.semantic_verifier import semantic_verifier


class VerificationAgent:
    """
    Lane C - Verification Agent:
    Validates geometric consistency, temporal ordering, statistical validity,
    and semantic claims between Lane A (Deterministic) and Lane B (VLM).
    """
    def verify(
        self,
        task: str,
        input_type: str,
        primary_dimensions: Tuple[int, int],
        secondary_dimensions: Optional[Tuple[int, int]] = None,
        rmse: Optional[float] = None,
        bounding_boxes: Optional[List[Dict[str, Any]]] = None,
        change_percentage: Optional[float] = None,
        connected_regions_count: int = 0,
        total_pixels: int = 0,
        vlm_answer: str = "",
        lane_a_metrics: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        checks: Dict[str, bool] = {}
        warnings: List[str] = []
        total_penalty = 0.0

        # 1. Geometry Check
        dim_ok, dim_warn = geometry_verifier.verify_dimensions(primary_dimensions, secondary_dimensions)
        checks["dimensions_valid"] = dim_ok
        if dim_warn:
            warnings.append(dim_warn)
            total_penalty += 10.0

        if bounding_boxes:
            box_ok, box_warns = geometry_verifier.verify_bounding_boxes(
                bounding_boxes, primary_dimensions[0], primary_dimensions[1]
            )
            checks["bounding_boxes_valid"] = box_ok
            warnings.extend(box_warns)

        coreg_ok, coreg_warn, coreg_penalty = geometry_verifier.verify_coregistration(rmse)
        checks["coregistration_pass"] = coreg_ok
        if coreg_warn:
            warnings.append(coreg_warn)
        total_penalty += coreg_penalty

        # 2. Temporal Check
        temp_ok, temp_warn = temporal_verifier.verify_temporal_pair(
            has_second_image=secondary_dimensions is not None,
            input_type=input_type
        )
        checks["temporal_pairing_valid"] = temp_ok
        if temp_warn:
            warnings.append(temp_warn)
            total_penalty += 15.0

        # 3. Statistical Check
        stat_ok, stat_warns, stat_penalty = statistical_verifier.verify_change_mask(
            change_percentage=change_percentage,
            connected_regions_count=connected_regions_count,
            total_pixels=total_pixels
        )
        checks["statistical_plausibility"] = stat_ok
        warnings.extend(stat_warns)
        total_penalty += stat_penalty

        # 4. Semantic Cross-Check
        if vlm_answer:
            sem_ok, sem_warns, sem_penalty = semantic_verifier.cross_check_claims(
                vlm_answer=vlm_answer,
                task=task,
                lane_a_metrics=lane_a_metrics
            )
            checks["semantic_consistency"] = sem_ok
            warnings.extend(sem_warns)
            total_penalty += sem_penalty

        passed = len(warnings) == 0

        return VerificationResult(
            passed=passed,
            checks=checks,
            warnings=warnings,
            confidence_penalty=min(40.0, total_penalty),
            details={
                "checks_run_count": len(checks),
                "warnings_count": len(warnings),
                "confidence_penalty": round(total_penalty, 1)
            }
        )


verification_agent = VerificationAgent()
