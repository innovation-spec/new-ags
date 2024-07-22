from app.models.domain import Tenant
from app.services.external_data.service import ExternalDataService
from app.services.external_data.credibility import CredibilityResolver


def setup_tenant(db):
    db.add(Tenant(id="tenant-a", name="A")); db.commit()


def test_timeout_retries_then_falls_back(db_session):
    setup_tenant(db_session)
    result = ExternalDataService(db_session, sleep=lambda _: None, jitter=lambda: 0).resolve("tenant-a", "SKU-1", "timeout")
    assert result["selected"]["source"] == "provider-b"
