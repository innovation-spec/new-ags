from app.workflows.recommendation import recommendation_step_names
from app.workflows.research import research_step_names
from app.workflows.agent import agent_step_names


def test_recommendation_workflow_orders_authoritative_steps_before_explanation():
    assert recommendation_step_names() == [
        "load_customer", "load_shared_state", "generate_candidates",
        "check_inventory", "rank_and_persist", "optional_llm_explanation",
    ]


def test_research_workflow_orders_retry_fallback_normalize_and_credibility():
    assert research_step_names() == [
        "query_preferred", "retry_with_backoff", "fallback_secondary",
        "normalize", "credibility_resolve", "persist_provenance",
    ]


def test_agent_workflow_keeps_tool_execution_before_final_composition():
    assert agent_step_names() == ["create_run", "execute_tools", "validate_authoritative_state", "compose_response"]

import pytest
from app.core.config import Settings


def test_temporal_is_disabled_by_default_for_unit_execution():
    assert Settings().temporal_enabled is False


@pytest.mark.asyncio
async def test_agent_api_dispatches_temporal_workflow_when_enabled(client, monkeypatch):
    import app.api.agents as agents_api

    calls = []

    async def fake_execute(workflow_name, payload):
        calls.append((workflow_name, payload))
        return {"run": {"id": "temporal-run", "status": "COMPLETED"}, "answer": "ok", "recommendations": []}

    monkeypatch.setattr(agents_api, "get_settings", lambda: Settings(temporal_enabled=True))
    monkeypatch.setattr(agents_api, "execute_temporal_workflow", fake_execute)

    response = client.post("/agents/chat", json={"tenant_id":"tenant-a", "customer_id":"c1", "message":"hello"})
