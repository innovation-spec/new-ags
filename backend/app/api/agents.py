from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.llm.schemas import AgentChatRequest
from app.agents.service import AgentService
from app.core.config import get_settings
from app.workflows.client import execute_temporal_workflow

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/chat")
async def chat(request: AgentChatRequest, db: Session = Depends(get_db)):
    payload = request.model_dump()
    if get_settings().temporal_enabled:
        return await execute_temporal_workflow("agent", payload)
    return AgentService(db).chat(request.tenant_id, request.customer_id, request.message)

@router.get("/runs")
def list_runs(tenant_id: str, limit: int = 50, db: Session = Depends(get_db)):
    return AgentService(db).list_runs(tenant_id, limit)

@router.get("/runs/{run_id}")
def get_run(run_id: str, tenant_id: str, db: Session = Depends(get_db)):
    result = AgentService(db).get_run(tenant_id, run_id)
    if result is None: raise HTTPException(404, "run not found")
    return result
