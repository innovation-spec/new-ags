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
            if not isinstance(existing, (int, float)) or not isinstance(value, (int, float)):
                raise ValueError(f"additive policy requires numeric values for {key}")
            out[key] = existing + value
        return out
    if policy == "append":
        for key, value in patch.items():
            existing = out.get(key, [])
            if not isinstance(existing, list) or not isinstance(value, list):
                raise ValueError(f"append policy requires list values for {key}")
            out[key] = [*existing, *deepcopy(value)]
        return out
    if policy == "weighted_union":
        for key, value in patch.items():
            existing = dict(out.get(key, {}))
            if not isinstance(value, dict):
                raise ValueError(f"weighted_union requires object values for {key}")
            for item, weight in value.items():
                old = float(existing.get(item, 0.0))
                existing[item] = max(old, float(weight))
            out[key] = existing
        return out
    if policy == "internal_authority":
        for key, value in patch.items():
            if key not in out or out[key] is None:
                out[key] = deepcopy(value)
        return out
