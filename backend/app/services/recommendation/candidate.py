from __future__ import annotations
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Product, SKU, Inventory

def inventory_aware_candidates(db: Session, tenant_id: str) -> list[dict]:
    rows = db.execute(
        select(Product, SKU, Inventory)
        .join(SKU, SKU.product_id == Product.id)
        .join(Inventory, Inventory.sku_id == SKU.id)
        .where(Product.tenant_id == tenant_id, SKU.tenant_id == tenant_id, Inventory.tenant_id == tenant_id)
    ).all()
    grouped: dict[str, dict] = {}
    for product, sku, inv in rows:
        available = max(0, inv.on_hand - inv.reserved)
