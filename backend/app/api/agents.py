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
