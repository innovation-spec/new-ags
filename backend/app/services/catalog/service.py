from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Product

class CatalogService:
    def __init__(self, db: Session): self.db = db
    def list_products(self, tenant_id: str, limit: int = 100, category: str | None = None) -> list[Product]:
