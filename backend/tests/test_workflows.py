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

