from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(50), default="user")

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(100), index=True)
    brand: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[float] = mapped_column(Float)
    popularity: Mapped[float] = mapped_column(Float, default=0.0)
    embedding: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), default="Default")

class SKU(Base):
    __tablename__ = "skus"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    variant_id: Mapped[str | None] = mapped_column(ForeignKey("product_variants.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(100))
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_sku_tenant_code"),)

class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))

class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"), index=True)
    on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("tenant_id", "sku_id", "warehouse_id", name="uq_inventory_scope"),)

class InventoryLedger(Base):
    __tablename__ = "inventory_ledger"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    quantity_delta: Mapped[int] = mapped_column(Integer)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    sku_id: Mapped[str] = mapped_column(ForeignKey("skus.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    idempotency_key: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="RESERVED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("tenant_id", "idempotency_key", name="uq_reservation_idempotency"),)

class CustomerEvent(Base):
    __tablename__ = "customer_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CustomerFeature(Base):
    __tablename__ = "customer_features"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    features: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    segment: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column(Float, default=0.0)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(100), default="baseline")
    model_version: Mapped[str] = mapped_column(String(50), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class RecommendationItem(Base):
    __tablename__ = "recommendation_items"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    recommendation_id: Mapped[str] = mapped_column(ForeignKey("recommendations.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    rank: Mapped[int] = mapped_column(Integer)
    reasons: Mapped[dict] = mapped_column(JSON, default=dict)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    recommendation_id: Mapped[str] = mapped_column(ForeignKey("recommendations.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    action: Mapped[str] = mapped_column(String(50))

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="CREATED")
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AgentTask(Base):
    __tablename__ = "agent_tasks"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="CREATED")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

class AgentEvent(Base):
    __tablename__ = "agent_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(100))
    event_type: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class SharedState(Base):
    __tablename__ = "shared_states"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[int] = mapped_column(Integer, default=0)
    state_json: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("tenant_id", "entity_type", "entity_id", name="uq_shared_state_entity"),)

class StateEvent(Base):
    __tablename__ = "state_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    state_id: Mapped[str] = mapped_column(ForeignKey("shared_states.id"), index=True)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    agent_id: Mapped[str] = mapped_column(String(100))
    operation_id: Mapped[str] = mapped_column(String(100))
    base_version: Mapped[int] = mapped_column(Integer)
