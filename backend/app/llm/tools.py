from __future__ import annotations

import json
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.domain import Customer, CustomerEvent
from app.services.catalog.service import CatalogService
from app.services.inventory.service import InventoryService
from app.services.recommendation.service import RecommendationService
from app.services.state.service import StateService
from app.services.external_data.service import ExternalDataService
from app.services.memory.service import MemoryService, InMemoryWorkingMemory


APPROVED_TOOL_NAMES = {
    "get_customer_profile",
    "get_customer_history",
    "search_products",
    "get_recommendations",
    "check_inventory",
    "get_shared_state",
    "submit_state_patch",
    "search_external_data",
    "save_memory",
}


def build_tool_registry(
    db: Session,
    tenant_id: str,
    customer_id: str,
) -> dict[str, Callable]:
    def get_customer_profile():
        customer = db.scalar(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.id == customer_id,
            )
        )

        if not customer:
            return {"found": False}

        return {
            "found": True,
            "id": customer.id,
            "name": customer.name,
            "segment": customer.segment,
            "preferences": customer.preferences,
        }

    def get_customer_history(limit: int = 20):
        rows = db.scalars(
            select(CustomerEvent)
            .where(
                CustomerEvent.tenant_id == tenant_id,
                CustomerEvent.customer_id == customer_id,
            )
            .order_by(CustomerEvent.created_at.desc())
            .limit(max(1, min(limit, 100)))
        ).all()

        return [
            {
                "event_type": row.event_type,
                "product_id": row.product_id,
                "value": row.value,
            }
            for row in rows
        ]

    def search_products(
        query: str = "",
        category: str | None = None,
        max_price: float | None = None,
        limit: int = 20,
    ):
        rows = CatalogService(db).list_products(
            tenant_id,
            limit=100,
            category=category,
        )

        query_text = query.lower().strip()
        output = []

        for product in rows:
            searchable = (
                f"{product.name} "
                f"{product.category} "
                f"{product.brand}"
            ).lower()

            if query_text and query_text not in searchable:
                continue

            if max_price is not None and product.price > max_price:
                continue

            output.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "brand": product.brand,
                    "price": product.price,
                }
            )
