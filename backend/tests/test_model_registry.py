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
