from __future__ import annotations
from copy import deepcopy

MERGEABLE_POLICIES = {"additive", "append", "weighted_union", "internal_authority", "external_credibility"}

def merge_state(current: dict, patch: dict, policy: str) -> dict:
    out = deepcopy(current)
    if policy == "replace":
        out.update(deepcopy(patch))
        return out
    if policy == "additive":
        for key, value in patch.items():
            existing = out.get(key, 0)
