from app.models.domain import Tenant, Product

def test_catalog_is_tenant_scoped(client, db_session):
    db_session.add_all([
        Tenant(id="tenant-a", name="Tenant A"),
        Tenant(id="tenant-b", name="Tenant B"),
        Product(id="pa", tenant_id="tenant-a", name="A Shoe", category="running", brand="A", price=100),
