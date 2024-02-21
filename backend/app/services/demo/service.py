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
        self.db.add(Inventory(id=f"demo-inv-{suffix}", tenant_id=tenant_id, sku_id=sku, warehouse_id=wid, on_hand=stock, reserved=0, version=0))
        self.db.commit()
        bind = self.db.get_bind()
        is_sqlite = bind.dialect.name == "sqlite"

        def run_with_session(session, i: int) -> bool:
            try:
                InventoryService(session).reserve(tenant_id, sku, 1, f"demo-race-{suffix}-{i}")
                return True
            except InsufficientInventory:
                return False

        if is_sqlite:
            results = [run_with_session(self.db, i) for i in range(attempts)]
            mode = "sequential-test"
        else:
            SessionFactory = sessionmaker(bind=bind, expire_on_commit=False)
            def attempt(i):
                with SessionFactory() as session: return run_with_session(session, i)
            with ThreadPoolExecutor(max_workers=min(25, attempts)) as pool:
                results = list(pool.map(attempt, range(attempts)))
            mode = "concurrent"
        self.db.expire_all()
        final_stock = InventoryService(self.db).get_stock(tenant_id, sku)
        return {"mode": mode, "attempts": attempts, "initial_stock": stock, "successful": sum(results), "rejected": attempts-sum(results), "final_stock": final_stock, "sku_id": sku}
