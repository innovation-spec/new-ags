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
