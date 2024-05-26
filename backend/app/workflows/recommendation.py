from __future__ import annotations
from datetime import timedelta

def recommendation_step_names() -> list[str]:
    return [
        "load_customer", "load_shared_state", "generate_candidates",
        "check_inventory", "rank_and_persist", "optional_llm_explanation",
    ]

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
    with workflow.unsafe.imports_passed_through():
        from app.workflows.activities import recommendation_activity

    @workflow.defn
    class RecommendationWorkflow:
        @workflow.run
        async def run(self, payload: dict) -> dict:
            return await workflow.execute_activity(
                recommendation_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
except ImportError:
    class RecommendationWorkflow:
        async def run(self, payload: dict) -> dict:
            raise RuntimeError("Temporal SDK is not installed")
