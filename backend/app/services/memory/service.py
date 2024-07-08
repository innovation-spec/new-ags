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
