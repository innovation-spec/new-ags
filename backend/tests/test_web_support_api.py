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
