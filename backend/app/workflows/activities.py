from __future__ import annotations
from app.db.session import get_session_factory
from app.services.recommendation.service import RecommendationService
from app.services.external_data.service import ExternalDataService
from app.agents.service import AgentService

try:
    from temporalio import activity
except ImportError:  # local unit tests can run without Temporal SDK installed
    class _Activity:
        def defn(self, fn): return fn
    activity = _Activity()

@activity.defn
async def recommendation_activity(payload: dict) -> dict:
    with get_session_factory()() as db:
        result = RecommendationService(db).generate(payload["tenant_id"], payload["customer_id"], payload.get("limit", 10))
        if result is None:
            raise ValueError("customer not found")
        return result

@activity.defn
async def research_activity(payload: dict) -> dict:
    with get_session_factory()() as db:
        return ExternalDataService(db).resolve(payload["tenant_id"], payload["query"], payload.get("scenario", "normal"), payload.get("internal_value"))

@activity.defn
async def agent_chat_activity(payload: dict) -> dict:
    with get_session_factory()() as db:
        return AgentService(db).chat(payload["tenant_id"], payload["customer_id"], payload["message"])
