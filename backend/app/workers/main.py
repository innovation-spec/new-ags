import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.core.config import get_settings
from app.workflows.recommendation import RecommendationWorkflow
from app.workflows.research import ResearchWorkflow
from app.workflows.agent import AgentWorkflow
from app.workflows.activities import recommendation_activity, research_activity, agent_chat_activity

