import os
os.environ.setdefault("OPENAI_API_KEY", "")
from fastapi.testclient import TestClient
from app.main import create_app

def test_health_reports_openai_disabled_without_key():
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
