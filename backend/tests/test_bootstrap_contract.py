from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_compose_bootstrap_runs_migration_seed_and_model_registration_before_api():
    compose = (ROOT / "docker-compose.yml").read_text()
