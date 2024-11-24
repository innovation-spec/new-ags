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
        rec = client.post(f"/recommendations/{customer_id}", json={"tenant_id":"tenant-a","limit":5}); rec.raise_for_status(); assert rec.json()["items"]
        race = client.post("/demo/inventory-race", params={"tenant_id":"tenant-a","stock":5,"attempts":20}); race.raise_for_status(); assert race.json()["successful"] == 5
        state = client.post("/demo/state-conflict", params={"tenant_id":"tenant-a","operations":20}); state.raise_for_status(); assert state.json()["final_state"]["state"]["count"] == 20
