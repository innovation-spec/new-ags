from app.core.config import Settings
from app.llm.client import LLMClient, LLMResult
from app.llm.tools import APPROVED_TOOL_NAMES, build_tool_registry
from app.agents.service import AgentService
from app.models.domain import Tenant, Customer, Product, SKU, Warehouse, Inventory


def seed_agent_data(db):
    db.add(Tenant(id="tenant-a", name="A"))
    db.add(Customer(id="c1", tenant_id="tenant-a", name="Alice", preferences={"favorite_category":"running","max_price":150}))
    db.add(Product(id="p1", tenant_id="tenant-a", name="Runner", category="running", brand="Stride", price=100, popularity=.8))
    db.add(SKU(id="s1", tenant_id="tenant-a", product_id="p1", code="S1"))
    db.add(Warehouse(id="w1", tenant_id="tenant-a", name="Main"))
    db.add(Inventory(id="i1", tenant_id="tenant-a", sku_id="s1", warehouse_id="w1", on_hand=5, reserved=0, version=0))
