from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import SharedState, StateEvent
from app.schemas.events import EventEnvelope
from app.services.events.publisher import EventPublisher
from app.services.state.merge import merge_state, MERGEABLE_POLICIES

class StateService:
    def __init__(self, db: Session, publisher: EventPublisher | None = None):
        self.db = db
        self.publisher = publisher or EventPublisher()

    def _lookup(self, tenant_id: str, entity_type: str, entity_id: str, lock: bool = False) -> SharedState | None:
        stmt = select(SharedState).where(
            SharedState.tenant_id == tenant_id,
            SharedState.entity_type == entity_type,
            SharedState.entity_id == entity_id,
        )
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

