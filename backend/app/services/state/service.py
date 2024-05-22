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

    def _get_or_create_locked(self, tenant_id: str, entity_type: str, entity_id: str) -> SharedState:
        state = self._lookup(tenant_id, entity_type, entity_id, lock=True)
        if state is not None:
            return state
        state = SharedState(
            id=str(uuid.uuid4()), tenant_id=tenant_id, entity_type=entity_type,
            entity_id=entity_id, version=0, state_json={},
        )
        self.db.add(state)
        self.db.flush()
        return state

    def get_state(self, tenant_id: str, entity_type: str, entity_id: str) -> dict | None:
        state = self._lookup(tenant_id, entity_type, entity_id)
        if state is None:
            return None
        return {"id": state.id, "version": state.version, "state": dict(state.state_json or {})}

    def list_events(self, tenant_id: str, entity_type: str, entity_id: str) -> list[dict]:
        state = self._lookup(tenant_id, entity_type, entity_id)
        if state is None:
            return []
        rows = self.db.scalars(select(StateEvent).where(
            StateEvent.tenant_id == tenant_id, StateEvent.state_id == state.id
        ).order_by(StateEvent.created_at, StateEvent.id)).all()
        return [{
            "id": row.id, "operation_id": row.operation_id, "base_version": row.base_version,
            "resulting_version": row.resulting_version, "status": row.status,
            "merge_policy": row.merge_policy, "patch": row.patch,
        } for row in rows]

    def submit_patch(
        self, tenant_id: str, entity_type: str, entity_id: str, agent_id: str,
        operation_id: str, base_version: int, patch: dict, merge_policy: str,
    ) -> dict:
        replay = self.db.scalar(select(StateEvent).where(
            StateEvent.tenant_id == tenant_id, StateEvent.operation_id == operation_id
        ))
        if replay is not None:
            return {
                "event_id": replay.id, "status": replay.status,
                "resulting_version": replay.resulting_version, "replayed": True,
            }

        state = self._get_or_create_locked(tenant_id, entity_type, entity_id)
        stale = base_version != state.version
        if stale and merge_policy not in MERGEABLE_POLICIES:
            status = "REJECTED_CONFLICT"
            resulting_version = state.version
        else:
            state.state_json = merge_state(dict(state.state_json or {}), patch, merge_policy)
            state.version += 1
            resulting_version = state.version
            status = "MERGED" if stale else "APPLIED"
        event = StateEvent(
            id=str(uuid.uuid4()), state_id=state.id, tenant_id=tenant_id,
            agent_id=agent_id, operation_id=operation_id, base_version=base_version,
            resulting_version=resulting_version, patch=patch, merge_policy=merge_policy,
            status=status,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        if status != "REJECTED_CONFLICT":
            self.publisher.publish("stream:state-events", EventEnvelope(
                event_type="state.updated", tenant_id=tenant_id,
                payload={
                    "state_id": state.id, "entity_type": entity_type, "entity_id": entity_id,
                    "operation_id": operation_id, "version": resulting_version, "status": status,
                },
            ))
        return {"event_id": event.id, "status": status, "resulting_version": resulting_version, "replayed": False}
