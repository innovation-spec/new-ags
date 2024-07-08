from datetime import datetime, timedelta, timezone
from app.models.domain import Tenant, SharedState, StateEvent
from app.services.memory.service import MemoryService, InMemoryWorkingMemory
from app.services.model_registry.service import InMemoryObjectStore


def seed_tenants(db):
    db.add_all([Tenant(id="tenant-a", name="A"), Tenant(id="tenant-b", name="B")]); db.commit()


def test_memory_list_is_tenant_scoped(db_session):
    seed_tenants(db_session)
