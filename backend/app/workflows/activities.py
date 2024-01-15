from __future__ import annotations
from app.db.session import get_session_factory
from app.services.recommendation.service import RecommendationService
from app.services.external_data.service import ExternalDataService
from app.agents.service import AgentService

try:
    from temporalio import activity
