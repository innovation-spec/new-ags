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
