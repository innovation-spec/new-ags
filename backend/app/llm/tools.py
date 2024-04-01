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

            if len(output) >= max(1, min(limit, 50)):
                break

        return output

    def get_recommendations(limit: int = 10):
        return RecommendationService(db).generate(
            tenant_id,
            customer_id,
            max(1, min(limit, 25)),
        )

    def check_inventory(sku_id: str):
        return InventoryService(db).get_stock(
            tenant_id,
            sku_id,
        ) or {
            "found": False,
            "sku_id": sku_id,
        }

    def get_shared_state(
        entity_type: str,
        entity_id: str,
    ):
        return StateService(db).get_state(
            tenant_id,
            entity_type,
            entity_id,
        ) or {
            "version": 0,
            "state": {},
        }

    def submit_state_patch(
        entity_type: str,
        entity_id: str,
        operation_id: str,
        base_version: int,
        patch: str,
        merge_policy: str = "replace",
    ):
        try:
            parsed_patch = json.loads(patch)
        except (TypeError, json.JSONDecodeError) as exc:
            return {
                "ok": False,
                "error": f"patch must contain valid JSON object: {exc}",
            }

        if not isinstance(parsed_patch, dict):
            return {
                "ok": False,
                "error": "patch JSON must decode to an object",
            }

        return StateService(db).submit_patch(
            tenant_id,
            entity_type,
            entity_id,
            "supervisor-agent",
            operation_id,
            base_version,
            parsed_patch,
            merge_policy,
        )

    def search_external_data(
        query: str,
        scenario: str = "normal",
    ):
        return ExternalDataService(db).resolve(
            tenant_id,
            query,
            scenario,
        )

    def save_memory(
        memory_type: str,
        content: dict,
        ttl_seconds: int | None = None,
    ):
        return MemoryService(
            db,
            InMemoryWorkingMemory(),
        ).save(
            tenant_id,
            "customer",
            customer_id,
            memory_type,
            content,
            source="openai-agent",
            ttl_seconds=ttl_seconds,
        )

    registry = {
        "get_customer_profile": get_customer_profile,
        "get_customer_history": get_customer_history,
        "search_products": search_products,
        "get_recommendations": get_recommendations,
        "check_inventory": check_inventory,
        "get_shared_state": get_shared_state,
        "submit_state_patch": submit_state_patch,
        "search_external_data": search_external_data,
        "save_memory": save_memory,
    }

    assert set(registry) == APPROVED_TOOL_NAMES

    return registry


def dispatch_tool(
    registry: dict[str, Callable],
    name: str,
    args: dict,
):
    function = registry.get(name)

    if function is None:
        return {
            "ok": False,
            "error": f"tool {name!r} is not approved",
        }

    return function(**args)


def openai_tool_specs() -> list[dict]:
    def tool(
        name: str,
        description: str,
        properties: dict | None = None,
        required: list[str] | None = None,
    ) -> dict:
        return {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
            "strict": True,
        }

    return [
        tool(
            "get_customer_profile",
            "Read the selected customer's verified profile.",
        ),

        tool(
            "get_customer_history",
            "Read recent customer behavior.",
            {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            ["limit"],
        ),

        tool(
            "search_products",
            "Search this tenant's catalog only.",
            {
                "query": {
                    "type": "string",
                },
                "category": {
                    "type": ["string", "null"],
                },
                "max_price": {
                    "type": ["number", "null"],
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            [
                "query",
                "category",
                "max_price",
                "limit",
            ],
        ),

        tool(
            "get_recommendations",
            "Generate inventory-aware backend recommendations.",
            {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 25,
                },
            },
            ["limit"],
        ),

        tool(
            "check_inventory",
            "Read authoritative inventory for a tenant SKU.",
            {
                "sku_id": {
                    "type": "string",
                },
            },
            ["sku_id"],
        ),

        tool(
            "get_shared_state",
