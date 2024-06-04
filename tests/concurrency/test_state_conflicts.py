import os, uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="requires local Postgres")


def test_100_stale_additive_patches_have_no_lost_updates():
    from app.models.domain import Tenant
    from app.services.state.service import StateService
    url = os.environ["POSTGRES_TEST_URL"]
    engine = create_engine(url, pool_size=20, max_overflow=20)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    suffix = uuid.uuid4().hex[:8]
    tenant = f"state-{suffix}"
    with Session() as db:
        db.add(Tenant(id=tenant, name="State Tenant")); db.commit()
        StateService(db).submit_patch(tenant, "counter", "shared", "seed", f"seed-{suffix}", 0, {"count": 0}, "additive")

    def patch(i):
        with Session() as db:
            return StateService(db).submit_patch(tenant, "counter", "shared", f"agent-{i}", f"op-{suffix}-{i}", 1, {"count": 1}, "additive")

    with ThreadPoolExecutor(max_workers=25) as pool:
        results = list(pool.map(patch, range(100)))
    with Session() as db:
        svc = StateService(db)
        state = svc.get_state(tenant, "counter", "shared")
        events = svc.list_events(tenant, "counter", "shared")
    assert state["state"]["count"] == 100
    assert state["version"] == 101
    assert len(events) == 101
    assert sum(r["status"] in {"APPLIED", "MERGED"} for r in results) == 100
