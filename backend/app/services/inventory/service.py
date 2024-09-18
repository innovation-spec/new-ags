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
