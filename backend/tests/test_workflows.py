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

    assert response.status_code == 200
    assert calls == [("agent", {"tenant_id":"tenant-a", "customer_id":"c1", "message":"hello"})]
    assert response.json()["run"]["id"] == "temporal-run"

@pytest.mark.asyncio
async def test_recommendation_api_dispatches_temporal_workflow_when_enabled(client, monkeypatch):
    import app.api.recommendations as recommendations_api

    calls = []

    async def fake_execute(workflow_name, payload):
        calls.append((workflow_name, payload))
        return {"recommendation_id":"r1", "items":[]}

    monkeypatch.setattr(recommendations_api, "get_settings", lambda: Settings(temporal_enabled=True))
    monkeypatch.setattr(recommendations_api, "execute_temporal_workflow", fake_execute)

    response = client.post("/recommendations/c1", json={"tenant_id":"tenant-a", "limit":5})

    assert response.status_code == 200
    assert calls == [("recommendation", {"tenant_id":"tenant-a", "customer_id":"c1", "limit":5})]

@pytest.mark.asyncio
async def test_external_demo_dispatches_research_workflow_when_enabled(client, monkeypatch):
    import app.api.demo as demo_api

    calls = []

    async def fake_execute(workflow_name, payload):
        calls.append((workflow_name, payload))
        return {"query": "SKU", "selected": {"source": "provider-a"}}

    monkeypatch.setattr(demo_api, "get_settings", lambda: Settings(temporal_enabled=True))
    monkeypatch.setattr(demo_api, "execute_temporal_workflow", fake_execute)

    response = client.post(
        "/demo/external-failure",
        params={"tenant_id": "tenant-a", "query": "SKU", "scenario": "timeout"},
    )

    assert response.status_code == 200
    assert calls == [("research", {"tenant_id": "tenant-a", "query": "SKU", "scenario": "timeout"})]
