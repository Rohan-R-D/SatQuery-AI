from schemas.evidence import EvidenceItem


class EvidenceService:
    @staticmethod
    def extract_evidence(task_type, query, extra_metrics=None, gemini_evidence_strings=None, regions=None, artifacts=None):
        evidence = []
        for index, text in enumerate(gemini_evidence_strings or []):
            if isinstance(text, str) and text.strip():
                evidence.append(EvidenceItem(
                    id=f"ev-observation-{index}", title="Model observation",
                    description=text, type="metrics", source="semantic_model",
                    limitations=["Model interpretation; not an independently verified measurement"],
                ))
        if extra_metrics:
            evidence.append(EvidenceItem(
                id="ev-measurements", title="Processing measurements", type="metrics",
                description="Values returned by the processing tool.",
                metrics=extra_metrics, source="processing_tool",
            ))
        for index, region in enumerate(regions or []):
            evidence.append(EvidenceItem(
                id=f"ev-region-{index}", title="Reported region", type="bbox",
                description="Pixel-space region returned by the selected tool.",
                metrics=region, source="specialist_tool",
                limitations=["Pixel coordinates are not geographic coordinates"],
            ))
        for index, artifact in enumerate(artifacts or []):
            if artifact.get("url"):
                evidence.append(EvidenceItem(
                    id=f"ev-artifact-{index}", title=artifact.get("name", "Artifact"),
                    description=artifact.get("description") or "Generated processing artifact",
                    type="image", url=artifact["url"], source="specialist_tool",
                ))
        return evidence


evidence_service = EvidenceService()
evidence_extractor = evidence_service
