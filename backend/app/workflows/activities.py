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
