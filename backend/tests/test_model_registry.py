from app.services.model_registry.service import ModelRegistry, InMemoryObjectStore
from app.models.domain import Tenant, Customer, Product, SKU, Warehouse, Inventory
from app.services.recommendation.service import RecommendationService


def test_register_and_load_artifact(db_session):
    store = InMemoryObjectStore()
    registry = ModelRegistry(db_session, store)
    out = registry.register("recommendation-ranker", "v1", "sklearn-gbr", b"model-bytes", {"ndcg": 0.81})
    assert out["version"] == "v1"
    assert store.get_bytes("agasthya-models", "recommendation-ranker/v1/model.bin") == b"model-bytes"
    assert registry.get_artifact("recommendation-ranker", "v1") == b"model-bytes"


def test_only_one_model_version_is_active(db_session):
    store = InMemoryObjectStore(); registry = ModelRegistry(db_session, store)
    registry.register("recommendation-ranker", "v1", "baseline", b"one", {}, activate=True)
    registry.register("recommendation-ranker", "v2", "baseline", b"two", {})
    registry.activate("recommendation-ranker", "v2")
    active = registry.get_active("recommendation-ranker")
    versions = registry.list_versions("recommendation-ranker")
    assert active["version"] == "v2"
    assert [(x["version"], x["active"]) for x in versions] == [("v1", False), ("v2", True)]


def test_missing_artifact_returns_none(db_session):
    registry = ModelRegistry(db_session, InMemoryObjectStore())
    assert registry.get_artifact("missing", "v1") is None


def test_active_registry_version_is_reflected_by_recommendation(db_session):
    db_session.add(Tenant(id="tenant-a", name="A"))
    db_session.add(Customer(id="c1", tenant_id="tenant-a", name="A", preferences={}))
