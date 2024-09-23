from __future__ import annotations
import uuid
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.domain import Inventory, InventoryLedger, InventoryReservation, Product, SKU, Warehouse
from app.schemas.events import EventEnvelope
from app.services.events.publisher import EventPublisher

class InsufficientInventory(Exception):
    pass

class InventoryNotFound(Exception):
    pass

class InvalidReservation(Exception):
    pass

class InventoryEventHook:
    def __init__(self, publisher: EventPublisher | None = None):
        self.publisher = publisher or EventPublisher()

    def publish(self, event_type: str, payload: dict) -> None:
        self.publisher.publish(
            "stream:inventory-events",
            EventEnvelope(
                event_type=event_type,
                tenant_id=str(payload.get("tenant_id", "")),
                payload=payload,
            ),
        )

class InventoryService:
    def __init__(self, db: Session, event_hook: InventoryEventHook | None = None):
        self.db = db
        self.event_hook = event_hook or InventoryEventHook()

    def get_stock(self, tenant_id: str, sku_id: str) -> dict | None:
        row = self.db.scalar(select(Inventory).where(Inventory.tenant_id == tenant_id, Inventory.sku_id == sku_id))
        if row is None:
            return None
        return {
            "inventory_id": row.id,
            "sku_id": row.sku_id,
            "warehouse_id": row.warehouse_id,
            "on_hand": row.on_hand,
            "reserved": row.reserved,
            "available": row.on_hand - row.reserved,
            "version": row.version,
        }

    def list_inventory(self, tenant_id: str, limit: int = 100, search: str | None = None, category: str | None = None) -> list[dict]:
        query = (
            select(Inventory, SKU, Product, Warehouse)
            .join(SKU, SKU.id == Inventory.sku_id)
            .join(Product, Product.id == SKU.product_id)
            .join(Warehouse, Warehouse.id == Inventory.warehouse_id)
            .where(Inventory.tenant_id == tenant_id, SKU.tenant_id == tenant_id, Product.tenant_id == tenant_id, Warehouse.tenant_id == tenant_id)
            .order_by(Product.name, SKU.code)
            .limit(max(1, min(limit, 500)))
        )
        if category:
            query = query.where(Product.category == category)
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                func.lower(Product.name).like(term)
                | func.lower(Product.brand).like(term)
                | func.lower(SKU.code).like(term)
            )
        rows = self.db.execute(query).all()
        return [
            {
                "inventory_id": inventory.id,
                "sku_id": sku.id,
                "sku_code": sku.code,
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category,
                "brand": product.brand,
                "price": product.price,
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "on_hand": inventory.on_hand,
                "reserved": inventory.reserved,
