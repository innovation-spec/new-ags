from __future__ import annotations

from dataclasses import dataclass
import numpy as np

ACTIONS = (
    "use_internal_only",
    "query_provider_a",
    "query_provider_b",
    "query_both",
    "fallback",
    "abstain",
)

SCENARIOS = (
    "internal_authoritative",
    "provider_a_preferred",
    "provider_b_preferred",
    "provider_conflict",
    "preferred_failed",
    "all_unreliable",
)

BEST_ACTION = {
    "internal_authoritative": "use_internal_only",
    "provider_a_preferred": "query_provider_a",
    "provider_b_preferred": "query_provider_b",
    "provider_conflict": "query_both",
    "preferred_failed": "fallback",
    "all_unreliable": "abstain",
}

# Reward shaping keeps the experiment interpretable: correct source selection is
# strongly positive, safe abstention/fallback gets partial credit where sensible,
# and unnecessary external calls receive a small cost.
_REWARD = {
    scenario: {action: -0.25 for action in ACTIONS}
    for scenario in SCENARIOS
}
for _scenario, _action in BEST_ACTION.items():
    _REWARD[_scenario][_action] = 1.0
_REWARD["provider_conflict"]["abstain"] = 0.25
_REWARD["preferred_failed"]["abstain"] = 0.35
_REWARD["all_unreliable"]["fallback"] = 0.10
_REWARD["internal_authoritative"]["query_both"] = -0.50


@dataclass(frozen=True)
class Step:
    state: np.ndarray
    scenario: str
    action: int
    reward: float
    old_log_prob: float
    value: float


class SourceSelectionEnv:
    """One-step source-selection environment used only for PPO shadow evaluation."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def encode(scenario: str) -> np.ndarray:
        if scenario not in SCENARIOS:
            raise ValueError(f"unknown scenario: {scenario}")
