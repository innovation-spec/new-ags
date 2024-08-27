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
        state = np.zeros(len(SCENARIOS), dtype=np.float64)
        state[SCENARIOS.index(scenario)] = 1.0
        return state

    def sample_scenario(self, rng: np.random.Generator | None = None) -> str:
        source = rng or self.rng
        return str(source.choice(SCENARIOS))

    @staticmethod
    def reward(scenario: str, action: str) -> float:
        if scenario not in _REWARD:
            raise ValueError(f"unknown scenario: {scenario}")
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action}")
        return float(_REWARD[scenario][action])

    @staticmethod
    def deterministic_action(scenario: str) -> str:
        try:
            return BEST_ACTION[scenario]
        except KeyError as exc:
            raise ValueError(f"unknown scenario: {scenario}") from exc

    def shadow_decision(self, scenario: str, policy: "PPOPolicy") -> dict:
        state = self.encode(scenario)
        ppo_action = ACTIONS[policy.greedy_action(state)]
        deterministic = self.deterministic_action(scenario)
        return {
            "scenario": scenario,
            "mode": "shadow",
            "ppo_action": ppo_action,
            "ppo_reward": self.reward(scenario, ppo_action),
            "deterministic_action": deterministic,
            "authoritative_action": deterministic,
            "authoritative_reward": self.reward(scenario, deterministic),
        }


class PPOPolicy:
    """Tiny linear actor/critic used to demonstrate clipped PPO without ML servers."""

    def __init__(self, state_dim: int, action_dim: int, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.actor_w = rng.normal(0.0, 0.01, size=(state_dim, action_dim))
        self.actor_b = np.zeros(action_dim, dtype=np.float64)
        self.critic_w = np.zeros(state_dim, dtype=np.float64)
        self.critic_b = 0.0

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        shifted = logits - np.max(logits, axis=-1, keepdims=True)
        exp = np.exp(shifted)
        return exp / np.sum(exp, axis=-1, keepdims=True)

    def probabilities(self, states: np.ndarray) -> np.ndarray:
        states = np.atleast_2d(states).astype(np.float64)
        return self._softmax(states @ self.actor_w + self.actor_b)

    def value(self, states: np.ndarray) -> np.ndarray:
        states = np.atleast_2d(states).astype(np.float64)
        return states @ self.critic_w + self.critic_b

    def sample_action(self, state: np.ndarray, rng: np.random.Generator) -> tuple[int, float, float]:
        probs = self.probabilities(state)[0]
        action = int(rng.choice(len(ACTIONS), p=probs))
        return action, float(np.log(probs[action] + 1e-12)), float(self.value(state)[0])
