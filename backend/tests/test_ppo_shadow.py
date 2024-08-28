from app.experiments.source_selection_ppo import (
    ACTIONS,
    SCENARIOS,
    SourceSelectionEnv,
    PPOPolicy,
    train_ppo,
    evaluate_policy,
)


def test_ppo_training_improves_source_selection_reward():
    env = SourceSelectionEnv(seed=11)
    policy = PPOPolicy(state_dim=len(SCENARIOS), action_dim=len(ACTIONS), seed=11)
    before = evaluate_policy(env, policy, episodes=600, seed=101)
    history = train_ppo(env, policy, iterations=80, batch_size=192, learning_rate=0.08, seed=11)
    after = evaluate_policy(env, policy, episodes=600, seed=101)

    assert history
    assert after["average_reward"] > before["average_reward"] + 0.35
    assert after["accuracy"] >= 0.90


