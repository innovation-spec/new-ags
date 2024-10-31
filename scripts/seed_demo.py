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
                    id=f"{tenant_id}-wh-main",
                    tenant_id=tenant_id,
                    name="Main Warehouse",
                )
            )

        db.flush()

        # ================================================================
        # 3. PRODUCTS
        # ================================================================
        tenant_product_ids = {}

        for tenant_idx, tenant_id, _ in tenant_definitions:

            product_ids = []

            for i in range(products_per_tenant):

                product_id = f"{tenant_id}-p-{i:04d}"

                category = CATEGORIES[
                    i % len(CATEGORIES)
                ]

                brand = BRANDS[
                    (i * 3 + tenant_idx) % len(BRANDS)
                ]

                price = round(
                    39
                    + (i % 180) * 1.35
                    + tenant_idx * 2,
                    2,
                )

                db.add(
                    Product(
                        id=product_id,
                        tenant_id=tenant_id,
                        name=f"{brand} {category.title()} {i}",
                        category=category,
                        brand=brand,
                        price=price,
                        popularity=round(
                            rng.random(),
                            4,
                        ),
                        embedding=embedding(
                            i + tenant_idx * 10000
                        ),
                    )
                )

                product_ids.append(product_id)

            tenant_product_ids[tenant_id] = product_ids

        # Product must exist before variants/SKUs.
        db.flush()

        # ================================================================
        # 4. PRODUCT VARIANTS
        # ================================================================
        for _, tenant_id, _ in tenant_definitions:

            for product_id in tenant_product_ids[tenant_id]:

                db.add(
                    ProductVariant(
                        id=f"{product_id}-v",
                        tenant_id=tenant_id,
                        product_id=product_id,
                        name="Default",
                    )
                )

        # Variants must exist before SKUs.
        db.flush()

        # ================================================================
        # 5. SKUs
        # ================================================================
        for tenant_idx, tenant_id, _ in tenant_definitions:

            for i, product_id in enumerate(
                tenant_product_ids[tenant_id]
            ):

                db.add(
                    SKU(
                        id=f"{product_id}-sku",
                        tenant_id=tenant_id,
                        product_id=product_id,
                        variant_id=f"{product_id}-v",
                        code=f"SKU-{tenant_idx}-{i:04d}",
                    )
                )

        # IMPORTANT:
        # Inventory references SKU through inventory.sku_id.
        # Therefore SKUs must be committed to the current transaction
        # before Inventory is flushed.
