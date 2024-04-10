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


def test_internal_authority_preserves_existing_verified_value():
    merged = merge_state({"price": 99.0}, {"price": 120.0, "description": "new"}, "internal_authority")
    assert merged == {"price": 99.0, "description": "new"}


def test_stale_nonmergeable_patch_is_recorded_and_rejected(db_session):
    db_session.add(Tenant(id="tenant-a", name="A"))
    db_session.commit()
    svc = StateService(db_session)
    first = svc.submit_patch("tenant-a", "customer", "c1", "agent-a", "op-1", 0, {"intent": "running"}, "replace")
    stale = svc.submit_patch("tenant-a", "customer", "c1", "agent-b", "op-2", 0, {"intent": "hiking"}, "replace")
    state = svc.get_state("tenant-a", "customer", "c1")
    assert first["status"] == "APPLIED"
    assert stale["status"] == "REJECTED_CONFLICT"
    assert state["version"] == 1
    assert state["state"]["intent"] == "running"
    assert len(svc.list_events("tenant-a", "customer", "c1")) == 2


def test_stale_additive_patch_merges_and_increments_version(db_session):
    db_session.add(Tenant(id="tenant-a", name="A"))
    db_session.commit()
    svc = StateService(db_session)
    svc.submit_patch("tenant-a", "customer", "c1", "agent-a", "op-1", 0, {"views": 1}, "additive")
    merged = svc.submit_patch("tenant-a", "customer", "c1", "agent-b", "op-2", 0, {"views": 2}, "additive")
    state = svc.get_state("tenant-a", "customer", "c1")
    assert merged["status"] == "MERGED"
    assert state == {"id": state["id"], "version": 2, "state": {"views": 3}}


def test_operation_id_is_idempotent(db_session):
    db_session.add(Tenant(id="tenant-a", name="A"))
    db_session.commit()
    svc = StateService(db_session)
    a = svc.submit_patch("tenant-a", "customer", "c1", "agent-a", "same-op", 0, {"views": 1}, "additive")
    b = svc.submit_patch("tenant-a", "customer", "c1", "agent-a", "same-op", 0, {"views": 1}, "additive")
    assert a["event_id"] == b["event_id"]
    assert svc.get_state("tenant-a", "customer", "c1")["version"] == 1


def test_default_state_service_publishes_redis_stream_event(db_session, monkeypatch):
    from app.services.events import publisher as publisher_module
