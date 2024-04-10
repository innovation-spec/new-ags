from __future__ import annotations
from datetime import timedelta

def agent_step_names() -> list[str]:
    return ["create_run", "execute_tools", "validate_authoritative_state", "compose_response"]

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
    with workflow.unsafe.imports_passed_through():
        from app.workflows.activities import agent_chat_activity

    @workflow.defn
    class AgentWorkflow:
        @workflow.run
        async def run(self, payload: dict) -> dict:
            return await workflow.execute_activity(
                agent_chat_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=90),
