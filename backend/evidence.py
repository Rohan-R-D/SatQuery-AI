"""
Backward compatibility layer for Evidence Extractor.
All evidence logic has moved to `services/evidence_service.py`.
"""
from services.evidence_service import evidence_service, evidence_extractor, EvidenceService

# Alias for backwards compatibility
EvidenceExtractor = EvidenceService

__all__ = [
    "evidence_service",
    "evidence_extractor",
    "EvidenceService",
    "EvidenceExtractor"
]
