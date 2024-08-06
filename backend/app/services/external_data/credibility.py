from __future__ import annotations
from copy import deepcopy

class CredibilityResolver:
    def score(self, candidate: dict) -> float:
        authority = min(1.0, max(0.0, float(candidate.get("authority", 0)) / 100.0))
        reliability = min(1.0, max(0.0, float(candidate.get("reliability", 0))))
        freshness = min(1.0, max(0.0, float(candidate.get("freshness", 0))))
        corroboration = min(1.0, max(0.0, float(candidate.get("corroboration", 0))))
        historical = min(1.0, max(0.0, float(candidate.get("historical_quality", 0))))
        return round(.30*authority + .25*reliability + .20*freshness + .15*corroboration + .10*historical, 6)

    def resolve(self, candidates: list[dict], internal_value: dict | None = None) -> dict | None:
        if internal_value is not None:
            return {
                "source": "internal", "value": deepcopy(internal_value), "credibility": 1.0,
                "authority_override": True,
                "provenance": {"source": "internal", "kind": "authoritative_transactional"},
            }
        if not candidates: return None
        scored = []
