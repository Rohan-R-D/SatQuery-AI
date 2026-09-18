from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class VerificationResult:
    passed: bool
    checks: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    confidence_penalty: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
