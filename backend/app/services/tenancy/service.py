from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Tenant, Customer

class TenantService:
    def __init__(self, db: Session): self.db = db
    def list_tenants(self) -> list[Tenant]:
        return list(self.db.scalars(select(Tenant).order_by(Tenant.id)))
    def get(self, tenant_id: str) -> Tenant | None:
        return self.db.scalar(select(Tenant).where(Tenant.id == tenant_id))
    def customers(self, tenant_id: str, limit: int = 100) -> list[Customer]:
        return list(self.db.scalars(select(Customer).where(Customer.tenant_id == tenant_id).order_by(Customer.id).limit(limit)))
