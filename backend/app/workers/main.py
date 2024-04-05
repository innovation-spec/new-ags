import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.core.config import get_settings
from app.workflows.recommendation import RecommendationWorkflow
from app.workflows.research import ResearchWorkflow
from app.workflows.agent import AgentWorkflow
from app.workflows.activities import recommendation_activity, research_activity, agent_chat_activity

async def connect_with_retry(address: str, attempts: int = 60):
    last = None
    for i in range(attempts):
        try:
            return await Client.connect(address)
        except Exception as exc:
            last = exc
            await asyncio.sleep(min(5, 1 + i * .2))
    raise RuntimeError(f"Could not connect to Temporal at {address}: {last}")

async def main():
    settings = get_settings()
    client = await connect_with_retry(settings.temporal_address)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
