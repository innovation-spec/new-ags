from datetime import datetime, timedelta, timezone
from app.models.domain import Tenant, SharedState, StateEvent
from app.services.memory.service import MemoryService, InMemoryWorkingMemory
from app.services.model_registry.service import InMemoryObjectStore


def seed_tenants(db):
    db.add_all([Tenant(id="tenant-a", name="A"), Tenant(id="tenant-b", name="B")]); db.commit()


def test_memory_list_is_tenant_scoped(db_session):
    seed_tenants(db_session)
    svc = MemoryService(db_session, InMemoryWorkingMemory(), InMemoryObjectStore())
    svc.save("tenant-a", "customer", "c1", "episodic", {"note": "A"})
    svc.save("tenant-b", "customer", "c1", "episodic", {"note": "B"})
    assert [m["content"]["note"] for m in svc.list("tenant-a", "customer", "c1")] == ["A"]


def test_prune_expired_removes_only_expired_memory(db_session):
    seed_tenants(db_session)
    svc = MemoryService(db_session, InMemoryWorkingMemory(), InMemoryObjectStore())
    now = datetime.now(timezone.utc)
    expired = svc.save("tenant-a", "customer", "c1", "working", {"x": 1}, expires_at=now - timedelta(seconds=1))
    keep = svc.save("tenant-a", "customer", "c1", "episodic", {"x": 2})
    result = svc.prune_expired("tenant-a", now=now)
    ids = {m["id"] for m in svc.list("tenant-a", "customer", "c1")}
    assert result["deleted"] == 1
    assert expired["id"] not in ids
    assert keep["id"] in ids


def test_working_memory_ttl_is_mirrored_to_working_store(db_session):
    seed_tenants(db_session)
    working = InMemoryWorkingMemory(); svc = MemoryService(db_session, working, InMemoryObjectStore())
    saved = svc.save("tenant-a", "agent", "a1", "working", {"task": "rank"}, ttl_seconds=60)
    assert working.get(saved["working_key"]) == {"task": "rank"}


def test_archive_state_events_writes_json_artifact(db_session):
    seed_tenants(db_session)
    state = SharedState(id="state-1", tenant_id="tenant-a", entity_type="customer", entity_id="c1", version=1, state_json={"x":1})
    event = StateEvent(id="event-1", state_id="state-1", tenant_id="tenant-a", agent_id="a", operation_id="op", base_version=0, resulting_version=1, patch={"x":1}, merge_policy="replace", status="APPLIED")
    db_session.add_all([state, event]); db_session.commit()
    store = InMemoryObjectStore(); svc = MemoryService(db_session, InMemoryWorkingMemory(), store)
    manifest = svc.archive_state_events("tenant-a", "state-1")
    assert manifest["event_count"] == 1
    data = store.get_bytes("agasthya-state-archives", manifest["object_key"])
    assert b'"operation_id":"op"' in data
