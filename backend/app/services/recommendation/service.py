from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import Customer, Product, CustomerEvent, Recommendation, RecommendationItem, MLModel, ModelVersion
from app.services.recommendation.candidate import inventory_aware_candidates
from app.services.recommendation.features import build_customer_profile
from app.services.recommendation.ranking import score_candidate
from app.schemas.events import EventEnvelope
from app.services.events.publisher import EventPublisher

class RecommendationService:
    def __init__(self, db: Session, publisher: EventPublisher | None = None):
        self.db = db
        self.publisher = publisher or EventPublisher()

    def generate(self, tenant_id: str, customer_id: str, limit: int = 10) -> dict | None:
        customer = self.db.scalar(select(Customer).where(Customer.tenant_id == tenant_id, Customer.id == customer_id))
        if customer is None: return None
        products = list(self.db.scalars(select(Product).where(Product.tenant_id == tenant_id)))
