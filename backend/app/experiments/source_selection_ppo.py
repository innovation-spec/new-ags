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

    def greedy_action(self, state: np.ndarray) -> int:
        return int(np.argmax(self.probabilities(state)[0]))


def _collect_batch(env: SourceSelectionEnv, policy: PPOPolicy, batch_size: int, rng: np.random.Generator) -> list[Step]:
    batch: list[Step] = []
    for _ in range(batch_size):
        scenario = env.sample_scenario(rng)
        state = env.encode(scenario)
        action, old_log_prob, value = policy.sample_action(state, rng)
        reward = env.reward(scenario, ACTIONS[action])
        batch.append(Step(state, scenario, action, reward, old_log_prob, value))
    return batch


def _ppo_update(
    policy: PPOPolicy,
    batch: list[Step],
    learning_rate: float,
    clip_epsilon: float,
    epochs: int,
    value_lr: float,
) -> dict:
    states = np.stack([step.state for step in batch])
    actions = np.asarray([step.action for step in batch], dtype=np.int64)
    rewards = np.asarray([step.reward for step in batch], dtype=np.float64)
    old_log_probs = np.asarray([step.old_log_prob for step in batch], dtype=np.float64)
    old_values = np.asarray([step.value for step in batch], dtype=np.float64)
    advantages = rewards - old_values
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    rows = np.arange(len(batch))
    for _ in range(epochs):
        probs = policy.probabilities(states)
        selected = np.clip(probs[rows, actions], 1e-12, 1.0)
        log_probs = np.log(selected)
        ratio = np.exp(log_probs - old_log_probs)

        # PPO clipped surrogate: when clipping owns the min() branch its
        # derivative is zero; otherwise optimize ratio * advantage.
        active = np.where(
            advantages >= 0,
            ratio <= (1.0 + clip_epsilon),
            ratio >= (1.0 - clip_epsilon),
        ).astype(np.float64)
        coeff = active * ratio * advantages
        one_hot = np.zeros_like(probs)
        one_hot[rows, actions] = 1.0
        grad_logits = coeff[:, None] * (one_hot - probs)
        policy.actor_w += learning_rate * (states.T @ grad_logits) / len(batch)
        policy.actor_b += learning_rate * grad_logits.mean(axis=0)

        values = policy.value(states)
        value_error = rewards - values
        policy.critic_w += value_lr * (states.T @ value_error) / len(batch)
        policy.critic_b += value_lr * float(value_error.mean())

    clipped_ratio = np.clip(ratio, 1.0 - clip_epsilon, 1.0 + clip_epsilon)
    objective = np.minimum(ratio * advantages, clipped_ratio * advantages)
    return {
        "mean_reward": float(rewards.mean()),
        "policy_objective": float(objective.mean()),
        "value_mse": float(np.mean((rewards - policy.value(states)) ** 2)),
    }


def train_ppo(
    env: SourceSelectionEnv,
    policy: PPOPolicy,
    *,
    iterations: int = 60,
    batch_size: int = 192,
    learning_rate: float = 0.08,
    clip_epsilon: float = 0.2,
    epochs: int = 4,
    value_lr: float = 0.05,
    seed: int = 42,
) -> list[dict]:
    rng = np.random.default_rng(seed)
    history = []
    for iteration in range(1, iterations + 1):
        batch = _collect_batch(env, policy, batch_size, rng)
        metrics = _ppo_update(policy, batch, learning_rate, clip_epsilon, epochs, value_lr)
        metrics["iteration"] = iteration
        history.append(metrics)
    return history


def evaluate_policy(
    env: SourceSelectionEnv,
    policy: PPOPolicy,
    *,
    episodes: int = 600,
    seed: int = 123,
) -> dict:
    rng = np.random.default_rng(seed)
    rewards: list[float] = []
    correct = 0
    counts = {action: 0 for action in ACTIONS}
    for _ in range(episodes):
        scenario = env.sample_scenario(rng)
        action = ACTIONS[policy.greedy_action(env.encode(scenario))]
        counts[action] += 1
        rewards.append(env.reward(scenario, action))
        correct += int(action == env.deterministic_action(scenario))
    return {
        "episodes": episodes,
        "average_reward": round(float(np.mean(rewards)), 6),
        "accuracy": round(correct / episodes, 6),
        "action_counts": counts,
    }


def run_shadow_experiment(seed: int = 42, iterations: int = 60) -> dict:
    env = SourceSelectionEnv(seed=seed)
    policy = PPOPolicy(len(SCENARIOS), len(ACTIONS), seed=seed)
    before = evaluate_policy(env, policy, episodes=600, seed=seed + 1000)
    history = train_ppo(env, policy, iterations=iterations, seed=seed)
    after = evaluate_policy(env, policy, episodes=600, seed=seed + 1000)
    decisions = [env.shadow_decision(scenario, policy) for scenario in SCENARIOS]
    return {
        "mode": "shadow",
        "authoritative_policy": "deterministic_credibility_rules",
        "actions": list(ACTIONS),
        "before": before,
        "after": after,
        "training": {
            "iterations": iterations,
            "final": history[-1] if history else None,
        },
        "decisions": decisions,
    }
