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
    assert result["candidates"][0]["value"]["price"] != result["candidates"][1]["value"]["price"]
    assert result["selected"]["source"] == "provider-a"


def test_internal_authority_always_wins_over_external_confidence():
    resolver = CredibilityResolver()
    selected = resolver.resolve([
        {"source": "provider-a", "value": {"price": 109}, "authority": 80, "reliability": .99, "freshness": 1, "corroboration": 1, "historical_quality": .99},
    ], internal_value={"price": 99})
    assert selected["source"] == "internal"
    assert selected["value"] == {"price": 99}
    assert selected["authority_override"] is True
