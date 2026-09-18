"""
Backward compatibility layer for Confidence Calculator.
All confidence calculation logic has moved to `services/confidence_service.py`.
"""
from services.confidence_service import confidence_service, confidence_calculator, ConfidenceService

# Alias for backwards compatibility
ConfidenceCalculator = ConfidenceService

__all__ = [
    "confidence_service",
    "confidence_calculator",
    "ConfidenceService",
    "ConfidenceCalculator"
]
