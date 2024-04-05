from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Tenant, Customer

class TenantService:
    def __init__(self, db: Session): self.db = db
    def list_tenants(self) -> list[Tenant]:
        return list(self.db.scalars(select(Tenant).order_by(Tenant.id)))
    def get(self, tenant_id: str) -> Tenant | None:
