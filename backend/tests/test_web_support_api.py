from datetime import datetime, timezone

from app.models.domain import (
    AgentRun,
    InventoryLedger,
    StateEvent,
    SharedState,
    Tenant,
)
from app.models.domain import Product, SKU, Warehouse, Inventory


def seed_inventory(db, tenant="tenant-a", sku="sku-a", stock=5):
    db.add(Tenant(id=tenant, name=tenant))
    db.add(Product(id=f"{tenant}-p", tenant_id=tenant, name="Shoe", category="running", brand="A", price=100))
    db.add(SKU(id=sku, tenant_id=tenant, product_id=f"{tenant}-p", code=sku))
    db.add(Warehouse(id=f"{tenant}-wh", tenant_id=tenant, name="Main"))
    db.add(Inventory(id=f"{sku}-inv", tenant_id=tenant, sku_id=sku, warehouse_id=f"{tenant}-wh", on_hand=stock, reserved=0, version=0))
    db.commit()


def test_inventory_browse_and_ledger_are_tenant_scoped(client, db_session):
    seed_inventory(db_session, tenant="tenant-a", sku="sku-a", stock=5)
    seed_inventory(db_session, tenant="tenant-b", sku="sku-b", stock=9)
    db_session.add(
        InventoryLedger(
            id="ledger-a",
            tenant_id="tenant-a",
            sku_id="sku-a",
            warehouse_id="tenant-a-wh",
            event_type="RECEIVED",
            quantity_delta=5,
            reference_id="seed",
        )
    )
    db_session.commit()

    response = client.get("/inventory", params={"tenant_id": "tenant-a"})
    assert response.status_code == 200
    rows = response.json()
    assert [row["sku_id"] for row in rows] == ["sku-a"]
    assert rows[0]["product_name"] == "Shoe"
    assert rows[0]["available"] == 5

    ledger = client.get("/inventory/sku-a/ledger", params={"tenant_id": "tenant-a"})
    assert ledger.status_code == 200
    assert [row["id"] for row in ledger.json()] == ["ledger-a"]

    cross_tenant = client.get("/inventory/sku-a/ledger", params={"tenant_id": "tenant-b"})
    assert cross_tenant.status_code == 200
    assert cross_tenant.json() == []


def test_daily_report_surfaces_agent_failures_and_state_conflicts(client, db_session):
    db_session.add(Tenant(id="tenant-a", name="Tenant A"))
    run = AgentRun(
        id="run-failed",
        tenant_id="tenant-a",
        status="FAILED",
        input_text="demo",
        created_at=datetime.now(timezone.utc),
    )
    state = SharedState(
        id="state-a",
        tenant_id="tenant-a",
        entity_type="customer",
        entity_id="customer-a",
        version=1,
        state_json={},
    )
    db_session.add_all([run, state])
    db_session.flush()
    db_session.add(
        StateEvent(
            id="state-event-a",
            state_id=state.id,
            tenant_id="tenant-a",
            agent_id="agent-a",
            operation_id="op-a",
            base_version=0,
            resulting_version=1,
            patch={"x": 1},
            merge_policy="replace",
            status="REJECTED_CONFLICT",
        )
    )
    db_session.commit()

    response = client.get("/operations/daily-report", params={"tenant_id": "tenant-a"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_status"]["FAILED"] == 1
    codes = {item["code"] for item in payload["anomalies"]}
    assert "AGENT_FAILURES" in codes
    assert "STATE_CONFLICTS" in codes


def test_schema_registry_exposes_versioned_contracts(client):
    response = client.get("/schemas")
    assert response.status_code == 200
    payload = response.json()
    assert payload["registry_version"] == "1.0"
    assert "ReservationRequest" in payload["schemas"]
    assert "StatePatchRequest" in payload["schemas"]
    assert payload["schemas"]["ReservationRequest"]["type"] == "object"


def test_system_status_always_reports_local_capabilities(client):
    response = client.get("/system/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["database"]["status"] == "ok"
    assert payload["openai"]["status"] in {"enabled", "disabled"}
    assert payload["redis"]["status"] in {"ok", "unavailable"}
    assert payload["minio"]["status"] in {"ok", "unavailable"}
    assert payload["temporal"]["status"] in {"enabled", "disabled"}
