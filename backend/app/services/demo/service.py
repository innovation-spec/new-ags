from __future__ import annotations
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session, sessionmaker
from app.models.domain import (
    Product, SKU, Warehouse, Inventory, Customer, Recommendation, AgentRun,
    StateEvent, ExternalResult, MemoryEntry,
)
from app.services.inventory.service import InventoryService, InsufficientInventory
from app.services.state.service import StateService
from app.services.recommendation.service import RecommendationService
from app.services.external_data.service import ExternalDataService
from app.services.memory.service import MemoryService, InMemoryWorkingMemory

class DemoService:
    def __init__(self, db: Session): self.db = db

    def inventory_race(self, tenant_id: str, stock: int = 5, attempts: int = 100) -> dict:
        suffix = uuid.uuid4().hex[:8]
        pid, sku, wid = f"demo-p-{suffix}", f"demo-sku-{suffix}", f"demo-wh-{suffix}"
        self.db.add(Product(id=pid, tenant_id=tenant_id, name="Concurrency Demo SKU", category="demo", brand="Agasthya", price=1, popularity=0))
        self.db.add(SKU(id=sku, tenant_id=tenant_id, product_id=pid, code=sku))
        self.db.add(Warehouse(id=wid, tenant_id=tenant_id, name="Concurrency Demo Warehouse"))
