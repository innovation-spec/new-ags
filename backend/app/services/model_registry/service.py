from __future__ import annotations
import uuid
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.domain import MLModel, ModelVersion

class InMemoryObjectStore:
    def __init__(self): self.objects: dict[tuple[str, str], bytes] = {}
    def ensure_buckets(self) -> None: return None
    def put_bytes(self, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.objects[(bucket, key)] = bytes(data)
    def get_bytes(self, bucket: str, key: str) -> bytes | None:
        return self.objects.get((bucket, key))

class ModelRegistry:
    BUCKET = "agasthya-models"

    def __init__(self, db: Session, store):
        self.db = db
        self.store = store

    def _model(self, name: str) -> MLModel | None:
