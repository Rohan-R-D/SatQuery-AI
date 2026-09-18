class ConfidenceService:
    @staticmethod
    def calculate_confidence(task_type, is_success, evidence_count, change_percentage=None, has_gemini=False, error_code=None):
        return (
            0.0,
            "Confidence is uncalibrated: the legacy numeric field is a placeholder, not a probability. "
            "Use confidence_assessment and verification for limitations."
            if is_success else
            "No confidence estimate is available because analysis failed or the provider is unavailable.",
        )


confidence_service = ConfidenceService()
confidence_calculator = confidence_service
