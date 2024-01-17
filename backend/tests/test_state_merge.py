from app.models.domain import Tenant
from app.services.state.merge import merge_state
from app.services.state.service import StateService


def test_additive_merge_adds_counters():
    merged = merge_state({"views": 10}, {"views": 3}, "additive")
    assert merged == {"views": 13}


def test_append_merge_appends_unique_and_nonunique_events_in_order():
    merged = merge_state({"events": ["a"]}, {"events": ["b", "c"]}, "append")
    assert merged == {"events": ["a", "b", "c"]}


def test_weighted_union_keeps_highest_weight_per_interest():
    merged = merge_state(
        {"interests": {"running": 0.7, "hiking": 0.8}},
        {"interests": {"running": 0.9, "fitness": 0.6}},
        "weighted_union",
    )
    assert merged["interests"] == {"running": 0.9, "hiking": 0.8, "fitness": 0.6}
