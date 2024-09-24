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
