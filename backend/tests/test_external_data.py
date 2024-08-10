from app.models.domain import Tenant
from app.services.external_data.service import ExternalDataService
from app.services.external_data.credibility import CredibilityResolver


def setup_tenant(db):
    db.add(Tenant(id="tenant-a", name="A")); db.commit()


def test_timeout_retries_then_falls_back(db_session):
    setup_tenant(db_session)
    result = ExternalDataService(db_session, sleep=lambda _: None, jitter=lambda: 0).resolve("tenant-a", "SKU-1", "timeout")
    assert result["selected"]["source"] == "provider-b"
    assert [a["status"] for a in result["attempts"][:3]] == ["timeout", "timeout", "timeout"]
    assert result["attempts"][3]["source"] == "provider-b"
    assert result["fallback_used"] is True


def test_429_retries_then_falls_back(db_session):
    setup_tenant(db_session)
    result = ExternalDataService(db_session, sleep=lambda _: None, jitter=lambda: 0).resolve("tenant-a", "SKU-1", "rate_limit")
    assert result["selected"]["source"] == "provider-b"
    assert sum(a["status"] == "rate_limited" for a in result["attempts"]) == 3


def test_malformed_payload_falls_back_with_provenance(db_session):
    setup_tenant(db_session)
    result = ExternalDataService(db_session, sleep=lambda _: None, jitter=lambda: 0).resolve("tenant-a", "SKU-1", "malformed")
    assert result["selected"]["source"] == "provider-b"
    assert result["selected"]["provenance"]["query"] == "SKU-1"
    assert any(a["status"] == "malformed" for a in result["attempts"])


def test_conflicting_external_values_choose_more_credible_source(db_session):
    setup_tenant(db_session)
    result = ExternalDataService(db_session, sleep=lambda _: None, jitter=lambda: 0).resolve("tenant-a", "SKU-1", "conflict")
    assert len(result["candidates"]) == 2
