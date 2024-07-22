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
