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
        db.flush()

        # ================================================================
        # 6. INVENTORY
        # ================================================================
        for _, tenant_id, _ in tenant_definitions:

            warehouse_id = f"{tenant_id}-wh-main"

            for i, product_id in enumerate(
                tenant_product_ids[tenant_id]
            ):

                sku_id = f"{product_id}-sku"

                db.add(
                    Inventory(
                        id=f"{sku_id}-inv",
                        tenant_id=tenant_id,
                        sku_id=sku_id,
                        warehouse_id=warehouse_id,
                        on_hand=3 + (i % 25),
                        reserved=0,
                        version=0,
                    )
                )

        db.flush()

        # ================================================================
        # 7. CUSTOMERS
        # ================================================================
        tenant_customer_ids = {}

        for tenant_idx, tenant_id, _ in tenant_definitions:

            customer_ids = []

            for i in range(customers_per_tenant):

                customer_id = f"{tenant_id}-c-{i:04d}"

                favorite_category = CATEGORIES[
                    (i + tenant_idx) % len(CATEGORIES)
                ]

                favorite_brand = BRANDS[
                    (i * 2 + tenant_idx) % len(BRANDS)
                ]

                segment = [
                    "new",
                    "high_value",
                    "frequent",
                    "discount_sensitive",
                ][i % 4]

                preferences = {
                    "favorite_category": favorite_category,
                    "favorite_brand": favorite_brand,
                    "max_price": 80 + (i % 120),
                }

                db.add(
                    Customer(
                        id=customer_id,
                        tenant_id=tenant_id,
                        name=f"Customer {i}",
                        segment=segment,
                        preferences=preferences,
                    )
                )

                customer_ids.append(customer_id)

            tenant_customer_ids[tenant_id] = customer_ids

        # Customers must exist before customer features/segments.
        db.flush()

        # ================================================================
        # 8. CUSTOMER FEATURES
        # ================================================================
        for tenant_idx, tenant_id, _ in tenant_definitions:

            for i, customer_id in enumerate(
                tenant_customer_ids[tenant_id]
            ):

                favorite_category = CATEGORIES[
                    (i + tenant_idx) % len(CATEGORIES)
                ]

                favorite_brand = BRANDS[
                    (i * 2 + tenant_idx) % len(BRANDS)
                ]

                db.add(
                    CustomerFeature(
                        id=f"{customer_id}-feat",
                        tenant_id=tenant_id,
                        customer_id=customer_id,
                        features={
                            "category_affinity": {
                                favorite_category: 0.9
                            },
                            "brand_affinity": {
                                favorite_brand: 0.8
                            },
                        },
                    )
                )

        db.flush()

        # ================================================================
        # 9. CUSTOMER SEGMENTS
        # ================================================================
        for _, tenant_id, _ in tenant_definitions:

            for i, customer_id in enumerate(
                tenant_customer_ids[tenant_id]
            ):

                segment = [
                    "new",
                    "high_value",
                    "frequent",
                    "discount_sensitive",
                ][i % 4]

                db.add(
                    CustomerSegment(
                        id=f"{customer_id}-seg",
                        tenant_id=tenant_id,
                        customer_id=customer_id,
                        segment=segment,
                        score=0.8,
                    )
                )

        db.flush()

        # ================================================================
        # 10. CUSTOMER EVENTS
        # ================================================================
        for _, tenant_id, _ in tenant_definitions:

            customer_ids = tenant_customer_ids[tenant_id]
            product_ids = tenant_product_ids[tenant_id]

            for i in range(events_per_tenant):

                customer_id = customer_ids[
                    rng.randrange(
                        len(customer_ids)
                    )
                ]

                product_id = product_ids[
                    rng.randrange(
                        len(product_ids)
                    )
                ]

                event_type = rng.choices(
                    EVENTS,
                    weights=[
                        50,
                        25,
                        10,
                        10,
                        5,
                    ],
                    k=1,
                )[0]

                db.add(
                    CustomerEvent(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        customer_id=customer_id,
                        product_id=product_id,
                        event_type=event_type,
                        value=1.0,
                    )
                )

                if i and i % 2000 == 0:
                    db.flush()

        # ================================================================
        # 11. FINAL COMMIT
        # ================================================================
        db.commit()

        print(
            "Seeded 2 tenants, "
            "2,000 customers, "
            "1,000 products and "
            "20,000 interactions."
        )

if __name__ == "__main__":
    seed()
