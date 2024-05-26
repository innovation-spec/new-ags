from __future__ import annotations

import uuid

from app.core.config import get_settings
from app.workflows.agent import AgentWorkflow
from app.workflows.recommendation import RecommendationWorkflow
from app.workflows.research import ResearchWorkflow

_WORKFLOWS = {
    "agent": AgentWorkflow,
    "recommendation": RecommendationWorkflow,
    "research": ResearchWorkflow,
}


async def execute_temporal_workflow(workflow_name: str, payload: dict) -> dict:
    try:
        workflow = _WORKFLOWS[workflow_name]
    except KeyError as exc:
        raise ValueError(f"unknown workflow: {workflow_name}") from exc
    from temporalio.client import Client
    settings = get_settings()
    client = await Client.connect(settings.temporal_address)
    return await client.execute_workflow(
        workflow.run,
        payload,
        id=f"agasthya-{workflow_name}-{uuid.uuid4()}",
        task_queue=settings.temporal_task_queue,
    )
