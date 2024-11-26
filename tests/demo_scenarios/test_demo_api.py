import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.models.domain import Tenant, Customer, Product, SKU, Warehouse, Inventory


def seed_demo(db):
    db.add(Tenant(id="tenant-a", name="Demo A"))
    db.add(Customer(id="c1", tenant_id="tenant-a", name="Alice", preferences={"favorite_category":"running","max_price":150}))
    db.add(Product(id="p1", tenant_id="tenant-a", name="Runner", category="running", brand="Stride", price=100, popularity=.8))
    db.add(SKU(id="s1", tenant_id="tenant-a", product_id="p1", code="S1"))
    db.add(Warehouse(id="w1", tenant_id="tenant-a", name="Main"))
    db.add(Inventory(id="i1", tenant_id="tenant-a", sku_id="s1", warehouse_id="w1", on_hand=5, reserved=0, version=0))
    db.commit()


def test_inventory_race_demo(client, db_session):
    seed_demo(db_session)
    response = client.post("/demo/inventory-race", params={"tenant_id":"tenant-a","stock":3,"attempts":10})
    assert response.status_code == 200
    data = response.json()
    assert data["successful"] == 3
    assert data["rejected"] == 7
    assert data["final_stock"]["available"] == 0


def test_state_conflict_demo(client, db_session):
    seed_demo(db_session)
    response = client.post("/demo/state-conflict", params={"tenant_id":"tenant-a","operations":10})
    assert response.status_code == 200
    data = response.json()
    assert data["final_state"]["state"]["count"] == 10
    assert data["final_state"]["version"] == 11
    assert data["event_count"] == 11


def test_external_failure_demo(client, db_session):
    seed_demo(db_session)
    response = client.post("/demo/external-failure", params={"tenant_id":"tenant-a","query":"sku","scenario":"timeout"})
    assert response.status_code == 200
    assert response.json()["selected"]["source"] == "provider-b"


def test_recommendation_demo(client, db_session):
    seed_demo(db_session)
    response = client.post("/demo/recommendation", params={"tenant_id":"tenant-a","customer_id":"c1"})
    assert response.status_code == 200
    assert response.json()["items"][0]["product_id"] == "p1"


def test_memory_prune_and_stats_demo(client, db_session):
    seed_demo(db_session)
    pruned = client.post("/demo/memory-prune", params={"tenant_id":"tenant-a"})
    assert pruned.status_code == 200
    assert pruned.json()["deleted"] >= 1
    stats = client.get("/demo/stats", params={"tenant_id":"tenant-a"})
    assert stats.status_code == 200
    assert stats.json()["customers"] == 1
    assert stats.json()["products"] >= 1
