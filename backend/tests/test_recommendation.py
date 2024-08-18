from app.models.domain import Tenant, Customer, Product, SKU, Warehouse, Inventory, CustomerEvent
from app.services.recommendation.service import RecommendationService


def seed_recommendation_data(db):
    db.add_all([Tenant(id="tenant-a", name="A"), Tenant(id="tenant-b", name="B")])
    db.add(Customer(id="c-a", tenant_id="tenant-a", name="Alice", segment="runner", preferences={"favorite_category": "running", "favorite_brand": "Stride", "max_price": 150}))
    db.add(Customer(id="c-b", tenant_id="tenant-b", name="Bob", preferences={}))
    db.add_all([
        Product(id="p-best", tenant_id="tenant-a", name="Stride Runner", category="running", brand="Stride", price=120, popularity=0.9, embedding=[1,0]),
        Product(id="p-oos", tenant_id="tenant-a", name="Stride Pro", category="running", brand="Stride", price=130, popularity=1.0, embedding=[1,0]),
        Product(id="p-casual", tenant_id="tenant-a", name="Orbit Casual", category="casual", brand="Orbit", price=80, popularity=0.5, embedding=[0,1]),
        Product(id="p-b", tenant_id="tenant-b", name="Tenant B Runner", category="running", brand="Stride", price=50, popularity=1.0, embedding=[1,0]),
    ])
    db.add_all([
        SKU(id="s-best", tenant_id="tenant-a", product_id="p-best", code="S-BEST"),
        SKU(id="s-oos", tenant_id="tenant-a", product_id="p-oos", code="S-OOS"),
        SKU(id="s-casual", tenant_id="tenant-a", product_id="p-casual", code="S-CAS"),
        SKU(id="s-b", tenant_id="tenant-b", product_id="p-b", code="S-B"),
        Warehouse(id="wa", tenant_id="tenant-a", name="A Main"),
        Warehouse(id="wb", tenant_id="tenant-b", name="B Main"),
    ])
    db.add_all([
        Inventory(id="i-best", tenant_id="tenant-a", sku_id="s-best", warehouse_id="wa", on_hand=10, reserved=0, version=0),
        Inventory(id="i-oos", tenant_id="tenant-a", sku_id="s-oos", warehouse_id="wa", on_hand=0, reserved=0, version=0),
        Inventory(id="i-casual", tenant_id="tenant-a", sku_id="s-casual", warehouse_id="wa", on_hand=10, reserved=0, version=0),
        Inventory(id="i-b", tenant_id="tenant-b", sku_id="s-b", warehouse_id="wb", on_hand=10, reserved=0, version=0),
        CustomerEvent(id="e1", tenant_id="tenant-a", customer_id="c-a", product_id="p-best", event_type="view", value=1),
        CustomerEvent(id="e2", tenant_id="tenant-a", customer_id="c-a", product_id="p-best", event_type="purchase", value=1),
    ])
    db.commit()


def test_recommendations_exclude_unavailable_and_cross_tenant_products(db_session):
    seed_recommendation_data(db_session)
    result = RecommendationService(db_session).generate("tenant-a", "c-a", limit=10)
    ids = [item["product_id"] for item in result["items"]]
    assert "p-oos" not in ids
    assert "p-b" not in ids
    assert set(ids) == {"p-best", "p-casual"}


def test_preference_and_behavior_make_matching_product_rank_first(db_session):
    seed_recommendation_data(db_session)
    result = RecommendationService(db_session).generate("tenant-a", "c-a", limit=10)
    assert result["items"][0]["product_id"] == "p-best"
    assert result["items"][0]["score"] > result["items"][1]["score"]
    assert "favorite_category" in result["items"][0]["reasons"]


def test_recommendation_scores_are_deterministic(db_session):
    seed_recommendation_data(db_session)
    svc = RecommendationService(db_session)
    a = svc.generate("tenant-a", "c-a", limit=2)
    b = svc.generate("tenant-a", "c-a", limit=2)
    assert [(x["product_id"], x["score"]) for x in a["items"]] == [(x["product_id"], x["score"]) for x in b["items"]]


def test_unknown_customer_returns_none(db_session):
    db_session.add(Tenant(id="tenant-a", name="A")); db_session.commit()
    assert RecommendationService(db_session).generate("tenant-a", "missing", limit=10) is None


def test_recommendation_generation_publishes_stream_event(db_session, monkeypatch):
    from app.services.events import publisher as publisher_module

    class FakeRedis:
        def __init__(self): self.calls = []
        def xadd(self, stream, fields):
            self.calls.append((stream, fields)); return "1-0"

    fake = FakeRedis()
    monkeypatch.setattr(publisher_module, "get_redis_client", lambda: fake)
    seed_recommendation_data(db_session)

    result = RecommendationService(db_session).generate("tenant-a", "c-a", limit=2)

    assert fake.calls[0][0] == "stream:recommendation-events"
    assert fake.calls[0][1]["event_type"] == "recommendation.generated"
    assert result["recommendation_id"]
