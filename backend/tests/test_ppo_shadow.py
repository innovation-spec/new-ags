from app.experiments.source_selection_ppo import (
    ACTIONS,
    SCENARIOS,
    SourceSelectionEnv,
    PPOPolicy,
    train_ppo,
    evaluate_policy,
)


def test_ppo_training_improves_source_selection_reward():
