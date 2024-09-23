import pytest
from app.models.domain import Tenant, Product, SKU, Warehouse, Inventory
from app.services.inventory.service import InventoryService, InsufficientInventory


def seed_inventory(db, tenant="tenant-a", sku="sku-a", stock=5):
    db.add(Tenant(id=tenant, name=tenant))
    db.add(Product(id=f"{tenant}-p", tenant_id=tenant, name="Shoe", category="running", brand="A", price=100))
    db.add(SKU(id=sku, tenant_id=tenant, product_id=f"{tenant}-p", code=sku))
    db.add(Warehouse(id=f"{tenant}-wh", tenant_id=tenant, name="Main"))
    db.add(Inventory(id=f"{sku}-inv", tenant_id=tenant, sku_id=sku, warehouse_id=f"{tenant}-wh", on_hand=stock, reserved=0, version=0))
    db.commit()


def test_inventory_available_is_on_hand_minus_reserved(db_session):
    seed_inventory(db_session, stock=5)
    svc = InventoryService(db_session)
    first = svc.reserve("tenant-a", "sku-a", 2, "order-1")
    stock = svc.get_stock("tenant-a", "sku-a")
    assert first.quantity == 2
    assert stock["on_hand"] == 5
    assert stock["reserved"] == 2
    assert stock["available"] == 3


def test_idempotency_replay_returns_original_reservation(db_session):
    seed_inventory(db_session, stock=5)
    svc = InventoryService(db_session)
    first = svc.reserve("tenant-a", "sku-a", 2, "order-1")
    second = svc.reserve("tenant-a", "sku-a", 2, "order-1")
    assert second.id == first.id
    assert svc.get_stock("tenant-a", "sku-a")["reserved"] == 2
