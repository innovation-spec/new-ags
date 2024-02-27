from app.models.domain import Tenant, Product

def test_catalog_is_tenant_scoped(client, db_session):
    db_session.add_all([
        Tenant(id="tenant-a", name="Tenant A"),
        Tenant(id="tenant-b", name="Tenant B"),
        Product(id="pa", tenant_id="tenant-a", name="A Shoe", category="running", brand="A", price=100),
        Product(id="pb", tenant_id="tenant-b", name="B Shoe", category="running", brand="B", price=110),
    ])
    db_session.commit()

    response = client.get("/catalog/products", params={"tenant_id": "tenant-a"})
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()}
