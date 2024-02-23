from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Tenant, Customer

class TenantService:
    def __init__(self, db: Session): self.db = db
