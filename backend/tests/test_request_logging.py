import json
import logging
from fastapi.testclient import TestClient

from app.main import create_app


def test_requests_emit_structured_log_with_request_and_tenant_context(caplog):
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="agasthya.request"):
        response = client.get(
            "/health?tenant_id=tenant-a",
            headers={"X-Request-ID": "req-demo-123"},
        )

    assert response.status_code == 200
    records = [r for r in caplog.records if r.name == "agasthya.request"]
    assert records
    payload = json.loads(records[-1].getMessage())
