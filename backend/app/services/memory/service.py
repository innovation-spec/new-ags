from __future__ import annotations
import json, uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.domain import MemoryEntry, StateEvent

class InMemoryWorkingMemory:
    def __init__(self): self.values: dict[str, object] = {}
    def set(self, key: str, value: dict, ttl_seconds: int | None = None) -> None: self.values[key] = value
    def get(self, key: str): return self.values.get(key)
    def delete(self, key: str) -> None: self.values.pop(key, None)

class RedisWorkingMemory:
    def __init__(self, client=None):
        if client is None:
            from app.core.redis import get_redis_client
            client = get_redis_client()
        self.client = client
    def set(self, key: str, value: dict, ttl_seconds: int | None = None) -> None:
        payload = json.dumps(value, separators=(",", ":"))
        if ttl_seconds: self.client.set(key, payload, ex=ttl_seconds)
        else: self.client.set(key, payload)
    def get(self, key: str):
        raw = self.client.get(key)
        return json.loads(raw) if raw else None
    def delete(self, key: str) -> None: self.client.delete(key)

class MemoryService:
    def __init__(self, db: Session, working_store=None, object_store=None):
        self.db = db
        self.working_store = working_store or InMemoryWorkingMemory()
        self.object_store = object_store

    def save(
        self, tenant_id: str, owner_type: str, owner_id: str, memory_type: str,
        content: dict, importance: float = .5, source: str = "system",
        ttl_seconds: int | None = None, expires_at: datetime | None = None,
        reconstructible: bool = True, embedding: list | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc)
        if expires_at is None and ttl_seconds is not None:
            expires_at = now + timedelta(seconds=ttl_seconds)
        mid = str(uuid.uuid4())
        row = MemoryEntry(
            id=mid, tenant_id=tenant_id, owner_type=owner_type, owner_id=owner_id,
            memory_type=memory_type, content=content, importance=importance, source=source,
            embedding=embedding or [], expires_at=expires_at, reconstructible=reconstructible,
        )
        self.db.add(row); self.db.commit()
        key = None
        if memory_type == "working":
            key = f"memory:{tenant_id}:{owner_type}:{owner_id}:{mid}"
            self.working_store.set(key, content, ttl_seconds)
        return self._serialize(row, working_key=key)

    def list(self, tenant_id: str, owner_type: str | None = None, owner_id: str | None = None, limit: int = 100) -> list[dict]:
        stmt = select(MemoryEntry).where(MemoryEntry.tenant_id == tenant_id)
        if owner_type is not None: stmt = stmt.where(MemoryEntry.owner_type == owner_type)
        if owner_id is not None: stmt = stmt.where(MemoryEntry.owner_id == owner_id)
        rows = self.db.scalars(stmt.order_by(MemoryEntry.created_at, MemoryEntry.id).limit(limit)).all()
        return [self._serialize(row) for row in rows]

    def prune_expired(self, tenant_id: str, now: datetime | None = None) -> dict:
        now = now or datetime.now(timezone.utc)
        rows = self.db.scalars(select(MemoryEntry).where(
            MemoryEntry.tenant_id == tenant_id,
            MemoryEntry.expires_at.is_not(None),
            MemoryEntry.expires_at <= now,
        )).all()
        for row in rows:
            key = f"memory:{tenant_id}:{row.owner_type}:{row.owner_id}:{row.id}"
            self.working_store.delete(key)
            self.db.delete(row)
        self.db.commit()
        return {"tenant_id": tenant_id, "deleted": len(rows), "pruned_at": now.isoformat()}

    def archive_state_events(self, tenant_id: str, state_id: str, delete_after: bool = False) -> dict:
        if self.object_store is None:
            raise ValueError("object store is required for archiving")
        rows = self.db.scalars(select(StateEvent).where(
            StateEvent.tenant_id == tenant_id, StateEvent.state_id == state_id
        ).order_by(StateEvent.resulting_version, StateEvent.created_at)).all()
        payload = [{
            "id": r.id, "operation_id": r.operation_id, "agent_id": r.agent_id,
            "base_version": r.base_version, "resulting_version": r.resulting_version,
            "patch": r.patch, "merge_policy": r.merge_policy, "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        } for r in rows]
        object_key = f"{tenant_id}/{state_id}/{uuid.uuid4().hex}.json"
        data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        self.object_store.put_bytes("agasthya-state-archives", object_key, data, "application/json")
        if delete_after and rows:
            self.db.execute(delete(StateEvent).where(StateEvent.id.in_([r.id for r in rows])))
            self.db.commit()
        return {"tenant_id": tenant_id, "state_id": state_id, "event_count": len(rows), "object_key": object_key, "deleted": bool(delete_after and rows)}

    @staticmethod
    def _serialize(row: MemoryEntry, working_key: str | None = None) -> dict:
        return {
            "id": row.id, "tenant_id": row.tenant_id, "owner_type": row.owner_type,
            "owner_id": row.owner_id, "memory_type": row.memory_type, "content": row.content,
            "importance": row.importance, "source": row.source,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            "reconstructible": row.reconstructible, "working_key": working_key,
        }
