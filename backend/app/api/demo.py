from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.demo.service import DemoService
from app.experiments.source_selection_ppo import run_shadow_experiment
from app.core.config import get_settings
from app.workflows.client import execute_temporal_workflow

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/inventory-race")
def inventory_race(tenant_id: str = "tenant-a", stock: int = 5, attempts: int = 100, db: Session = Depends(get_db)):
    return DemoService(db).inventory_race(tenant_id, max(1, min(stock, 100)), max(1, min(attempts, 500)))

@router.post("/state-conflict")
def state_conflict(tenant_id: str = "tenant-a", operations: int = 100, db: Session = Depends(get_db)):
    return DemoService(db).state_conflict(tenant_id, max(1, min(operations, 500)))

@router.post("/external-failure")
async def external_failure(tenant_id: str = "tenant-a", query: str = "SKU-DEMO", scenario: str = "timeout", db: Session = Depends(get_db)):
    if get_settings().temporal_enabled:
        return await execute_temporal_workflow("research", {"tenant_id": tenant_id, "query": query, "scenario": scenario})
    return DemoService(db).external_failure(tenant_id, query, scenario)

@router.post("/recommendation")
def recommendation(tenant_id: str, customer_id: str, limit: int = 10, db: Session = Depends(get_db)):
    result = DemoService(db).recommendation(tenant_id, customer_id, limit)
    if result is None: raise HTTPException(404, "customer not found")
    return result

@router.post("/memory-prune")
def memory_prune(tenant_id: str = "tenant-a", db: Session = Depends(get_db)):
    return DemoService(db).memory_prune(tenant_id)

@router.get("/stats")
def stats(tenant_id: str = "tenant-a", db: Session = Depends(get_db)):
    return DemoService(db).stats(tenant_id)

@router.post("/ppo-shadow")
def ppo_shadow(seed: int = 42, iterations: int = 60):
    return run_shadow_experiment(seed=seed, iterations=max(1, min(iterations, 200)))
