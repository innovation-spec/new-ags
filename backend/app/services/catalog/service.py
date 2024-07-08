from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Product

class CatalogService:
    def __init__(self, db: Session): self.db = db
    def list_products(self, tenant_id: str, limit: int = 100, category: str | None = None) -> list[Product]:
        stmt = select(Product).where(Product.tenant_id == tenant_id)
        if category:
            stmt = stmt.where(Product.category == category)
        return list(self.db.scalars(stmt.order_by(Product.popularity.desc(), Product.id).limit(limit)))
    def get_product(self, tenant_id: str, product_id: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.tenant_id == tenant_id, Product.id == product_id))
