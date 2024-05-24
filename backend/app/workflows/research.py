from __future__ import annotations
from datetime import timedelta

def research_step_names() -> list[str]:
    return [
        "query_preferred", "retry_with_backoff", "fallback_secondary",
        "normalize", "credibility_resolve", "persist_provenance",
    ]

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
    with workflow.unsafe.imports_passed_through():
        from app.workflows.activities import research_activity

    @workflow.defn
    class ResearchWorkflow:
        @workflow.run
        async def run(self, payload: dict) -> dict:
            return await workflow.execute_activity(
                research_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3, initial_interval=timedelta(milliseconds=250), backoff_coefficient=2.0),
            )
except ImportError:
    class ResearchWorkflow:
        async def run(self, payload: dict) -> dict:
            raise RuntimeError("Temporal SDK is not installed")
