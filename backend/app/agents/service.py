from __future__ import annotations
import json, uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import AgentRun, AgentEvent
from app.llm.client import LLMClient
from app.llm.tools import build_tool_registry, dispatch_tool, openai_tool_specs
from app.services.recommendation.service import RecommendationService

class AgentService:
    def __init__(self, db: Session, llm_client=None):
        self.db = db
        self.llm_client = llm_client or LLMClient()

    def _event(self, run: AgentRun, event_type: str, payload: dict | None = None, agent_name: str = "Supervisor Agent"):
        self.db.add(AgentEvent(
            id=str(uuid.uuid4()), tenant_id=run.tenant_id, run_id=run.id,
            agent_name=agent_name, event_type=event_type, payload=payload or {},
        ))
