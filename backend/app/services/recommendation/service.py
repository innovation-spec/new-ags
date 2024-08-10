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
        products_by_id = {p.id: p for p in products}
        events = list(self.db.scalars(select(CustomerEvent).where(CustomerEvent.tenant_id == tenant_id, CustomerEvent.customer_id == customer_id)))
        profile = build_customer_profile(customer, events, products_by_id)
        candidates = inventory_aware_candidates(self.db, tenant_id)
        ranked = []
        for candidate in candidates:
            product = candidate["product"]
            score, reasons = score_candidate(profile, product, candidate["available"])
            ranked.append((score, product, candidate["available"], candidate["sku_ids"], reasons))
        ranked.sort(key=lambda row: (-row[0], row[1].id))
        ranked = ranked[:max(1, min(limit, 100))]

        active = self.db.execute(
            select(MLModel.name, ModelVersion.version)
            .join(ModelVersion, ModelVersion.model_id == MLModel.id)
            .where(MLModel.name == "recommendation-ranker", ModelVersion.active.is_(True))
        ).first()
        model_name, model_version = active if active else ("baseline-weighted", "v1")
        rec = Recommendation(id=str(uuid.uuid4()), tenant_id=tenant_id, customer_id=customer_id, model_name=model_name, model_version=model_version)
        self.db.add(rec); self.db.flush()
        items = []
        for rank, (score, product, available, sku_ids, reasons) in enumerate(ranked, start=1):
            item = RecommendationItem(
                id=str(uuid.uuid4()), tenant_id=tenant_id, recommendation_id=rec.id,
                product_id=product.id, score=score, rank=rank, reasons=reasons,
            )
            self.db.add(item)
            items.append({
                "product_id": product.id, "name": product.name, "category": product.category,
                "brand": product.brand, "price": product.price, "score": score, "rank": rank,
                "available": available, "sku_ids": sku_ids, "reasons": reasons,
            })
        self.db.commit()
        self.publisher.publish("stream:recommendation-events", EventEnvelope(
            event_type="recommendation.generated", tenant_id=tenant_id,
            payload={"recommendation_id": rec.id, "customer_id": customer_id, "item_count": len(items), "model_name": rec.model_name, "model_version": rec.model_version},
        ))
        return {
