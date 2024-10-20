import math
import random
import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.base import Base
from app.models.domain import (
    Tenant,
    Customer,
    Product,
    ProductVariant,
    SKU,
    Warehouse,
    Inventory,
    CustomerEvent,
    CustomerFeature,
    CustomerSegment,
)

CATEGORIES = [
    "running",
    "fitness",
    "outdoor",
    "casual",
    "basketball",
    "soccer",
    "training",
    "walking",
]

BRANDS = [
    "Aero",
    "Stride",
    "NorthPeak",
    "Velocity",
    "Orbit",
    "Summit",
    "Nova",
    "TrailWorks",
]

EVENTS = [
    "view",
    "click",
    "save",
    "add_cart",
    "purchase",
]

def embedding(seed: int, dims: int = 8) -> list[float]:
    rng = random.Random(seed)
    values = [rng.uniform(-1, 1) for _ in range(dims)]
    norm = math.sqrt(sum(x * x for x in values)) or 1.0
    return [round(x / norm, 6) for x in values]

def seed(
    seed_value: int = 42,
    customers_per_tenant: int = 1000,
    products_per_tenant: int = 500,
    events_per_tenant: int = 10000,
):
    rng = random.Random(seed_value)

    engine = create_engine(get_settings().database_url)

    Base.metadata.create_all(engine)

    with Session(engine) as db:

        # ================================================================
        # CHECK WHETHER DATABASE IS ALREADY SEEDED
        # ================================================================
        if db.scalar(select(Tenant.id).limit(1)):
            print("Seed data already exists; skipping.")
            return

        tenant_definitions = [
            (0, "tenant-a", "Demo Retailer 1"),
            (1, "tenant-b", "Demo Retailer 2"),
        ]

        # ================================================================
        # 1. TENANTS
        # ================================================================
        for _, tenant_id, tenant_name in tenant_definitions:
            db.add(
                Tenant(
                    id=tenant_id,
                    name=tenant_name,
                )
            )

        db.flush()

        # ================================================================
        # 2. WAREHOUSES
        # ================================================================
        for _, tenant_id, _ in tenant_definitions:
            db.add(
                Warehouse(
