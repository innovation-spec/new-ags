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

