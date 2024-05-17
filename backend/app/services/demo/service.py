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

    def state_conflict(self, tenant_id: str, operations: int = 100) -> dict:
        entity_id = f"demo-shared-{uuid.uuid4().hex[:8]}"
        svc = StateService(self.db)
        seed = svc.submit_patch(tenant_id, "demo_counter", entity_id, "seed", f"seed-{entity_id}", 0, {"count": 0}, "additive")
        base_version = seed["resulting_version"]
        bind = self.db.get_bind(); is_sqlite = bind.dialect.name == "sqlite"

        def apply(session, i):
            return StateService(session).submit_patch(tenant_id, "demo_counter", entity_id, f"agent-{i}", f"op-{entity_id}-{i}", base_version, {"count": 1}, "additive")

        if is_sqlite:
            results = [apply(self.db, i) for i in range(operations)]
            mode = "sequential-test"
        else:
            SessionFactory = sessionmaker(bind=bind, expire_on_commit=False)
            def patch(i):
                with SessionFactory() as session: return apply(session, i)
            with ThreadPoolExecutor(max_workers=min(25, operations)) as pool:
                results = list(pool.map(patch, range(operations)))
            mode = "concurrent"
        self.db.expire_all()
        final_state = StateService(self.db).get_state(tenant_id, "demo_counter", entity_id)
        events = StateService(self.db).list_events(tenant_id, "demo_counter", entity_id)
        return {
            "mode": mode, "operations": operations, "applied": sum(r["status"] == "APPLIED" for r in results),
            "merged": sum(r["status"] == "MERGED" for r in results), "rejected": sum(r["status"] == "REJECTED_CONFLICT" for r in results),
            "final_state": final_state, "event_count": len(events), "entity_id": entity_id,
        }

    def recommendation(self, tenant_id: str, customer_id: str, limit: int = 10):
        return RecommendationService(self.db).generate(tenant_id, customer_id, limit)

    def external_failure(self, tenant_id: str, query: str, scenario: str):
        return ExternalDataService(self.db).resolve(tenant_id, query, scenario)

    def memory_prune(self, tenant_id: str) -> dict:
        svc = MemoryService(self.db, InMemoryWorkingMemory())
        svc.save(tenant_id, "demo", "prune", "working", {"temporary": True}, expires_at=datetime.now(timezone.utc)-timedelta(seconds=1))
        return svc.prune_expired(tenant_id)

    def stats(self, tenant_id: str) -> dict:
        def count(model):
            return int(self.db.scalar(select(func.count()).select_from(model).where(model.tenant_id == tenant_id)) or 0)
        return {
            "tenant_id": tenant_id,
            "customers": count(Customer), "products": count(Product), "inventory_rows": count(Inventory),
            "recommendations": count(Recommendation), "agent_runs": count(AgentRun),
            "state_events": count(StateEvent), "external_results": count(ExternalResult), "memory_entries": count(MemoryEntry),
        }
