import logging
from typing import Dict, Any, List
from services.gemini_service import gemini_service

logger = logging.getLogger("satquery.agents.fusion")


class FusionAgent:
    """
    Specialist Agent for Joint Optical Reflectance and SAR Synthetic Aperture Radar Multimodal Reasoning.
    """

    def __init__(self):
        self.name = "fusion_agent"
        self.description = "Performs cross-modal reasoning integrating Sentinel-1 SAR backscatter with Sentinel-2 Optical reflectance."

    def execute_fusion(
        self,
        optical_bytes: bytes,
        sar_bytes: bytes,
        query: str
    ) -> Dict[str, Any]:
        """Execute joint Optical + SAR multimodal reasoning pipeline."""
        logger.info(f"FusionAgent: executing Optical + SAR joint analysis for query='{query}'")

        gemini_sar_res = gemini_service.analyze_optical_sar(optical_bytes, sar_bytes, query)

        raw_answer = gemini_sar_res.get("answer", "")
        is_error = gemini_sar_res.get("is_error", False)
        error_code = gemini_sar_res.get("error_code")
        evidence_strings = gemini_sar_res.get("evidence", [])

        built_up_raw = gemini_sar_res.get("built_up_regions", [])
        water_raw = gemini_sar_res.get("water_regions", [])

        built_up_list = [{"description": b} for b in built_up_raw] if not is_error else []
        water_list = [{"description": w} for w in water_raw] if not is_error else []
        evidence_strings = evidence_strings if not is_error else []
        metrics_dict = {}

        answer = (
            f"[Optical + SAR Multimodal Analysis]: {raw_answer}\n\n"
            f"Cross-Modal Fusion Context: Integrated Sentinel-2 optical spectral bands with Sentinel-1 SAR synthetic aperture radar channels."
        )

        return {
            "answer": answer,
            "built_up_regions": built_up_list,
            "water_regions": water_list,
            "evidence": evidence_strings,
            "metrics": metrics_dict,
            "artifacts": [],
            "is_error": is_error,
            "error_code": error_code,
            "model_used": "Gemini Multimodal VLM + Optical-SAR Engine"
        }


fusion_agent = FusionAgent()
