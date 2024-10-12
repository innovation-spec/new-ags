"""Postgres-only concurrency proof; run after Docker Compose starts.

POSTGRES_TEST_URL=postgresql+psycopg://agasthya:agasthya@localhost:5432/agasthya \
  PYTHONPATH=backend pytest tests/concurrency/test_inventory_race.py -q
"""
import os, uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="requires local Postgres")


def test_100_attempts_only_reserve_seeded_stock():
    from app.models.domain import Tenant, Product, SKU, Warehouse, Inventory
    from app.services.inventory.service import InventoryService, InsufficientInventory
    url = os.environ["POSTGRES_TEST_URL"]
    engine = create_engine(url, pool_size=20, max_overflow=20)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    suffix = uuid.uuid4().hex[:8]
    tenant = f"race-{suffix}"
    sku = f"sku-{suffix}"
    with Session() as db:
        db.add(Tenant(id=tenant, name="Race Tenant"))
        db.add(Product(id=f"p-{suffix}", tenant_id=tenant, name="Race Shoe", category="running", brand="Race", price=99))
        db.add(SKU(id=sku, tenant_id=tenant, product_id=f"p-{suffix}", code=sku))
        db.add(Warehouse(id=f"wh-{suffix}", tenant_id=tenant, name="Main"))
        db.add(Inventory(id=f"inv-{suffix}", tenant_id=tenant, sku_id=sku, warehouse_id=f"wh-{suffix}", on_hand=5, reserved=0, version=0))
        db.commit()

    def attempt(i):
        with Session() as db:
            try:
                InventoryService(db).reserve(tenant, sku, 1, f"race-{suffix}-{i}")
                return True
            except InsufficientInventory:
                return False

    with ThreadPoolExecutor(max_workers=25) as pool:
        results = list(pool.map(attempt, range(100)))
    assert sum(results) == 5
    with Session() as db:
        stock = InventoryService(db).get_stock(tenant, sku)
        assert stock["reserved"] == 5
        assert stock["available"] == 0
