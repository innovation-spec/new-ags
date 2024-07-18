from __future__ import annotations
from copy import deepcopy

class CredibilityResolver:
    def score(self, candidate: dict) -> float:
        authority = min(1.0, max(0.0, float(candidate.get("authority", 0)) / 100.0))
        reliability = min(1.0, max(0.0, float(candidate.get("reliability", 0))))
