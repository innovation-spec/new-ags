import os
import pytest
import httpx

BASE = os.getenv("SMOKE_BASE_URL")
pytestmark = pytest.mark.skipif(not BASE, reason="requires running Docker Compose stack")

def test_running_stack_smoke():
    with httpx.Client(base_url=BASE, timeout=30) as client:
        health = client.get("/health"); health.raise_for_status(); assert health.json()["status"] == "ok"
        tenants = client.get("/tenants"); tenants.raise_for_status(); assert {t["id"] for t in tenants.json()} >= {"tenant-a", "tenant-b"}
        customers = client.get("/tenants/tenant-a/customers", params={"limit":1}); customers.raise_for_status(); customer_id = customers.json()[0]["id"]
