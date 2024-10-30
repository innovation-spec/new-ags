from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_compose_bootstrap_runs_migration_seed_and_model_registration_before_api():
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "bootstrap:" in compose
    assert "alembic upgrade head" in compose
    assert "seed_demo.py" in compose
    assert "train_ranker.py" in compose
    assert "condition: service_completed_successfully" in compose

