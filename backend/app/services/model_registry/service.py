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
        return self.db.scalar(select(MLModel).where(MLModel.name == name))

    def register(self, model_name: str, version: str, algorithm: str, artifact: bytes, metrics: dict, activate: bool = False) -> dict:
        model = self._model(model_name)
        if model is None:
            model = MLModel(id=str(uuid.uuid4()), name=model_name, description=f"{model_name} model")
            self.db.add(model); self.db.flush()
        existing = self.db.scalar(select(ModelVersion).where(ModelVersion.model_id == model.id, ModelVersion.version == version))
        if existing is not None:
            self.store.put_bytes(self.BUCKET, existing.object_path, artifact)
            existing.algorithm = algorithm; existing.metrics = metrics
            if activate: self.activate(model_name, version)
            else: self.db.commit()
            return self._serialize(model, existing)
        key = f"{model_name}/{version}/model.bin"
        self.store.put_bytes(self.BUCKET, key, artifact)
        row = ModelVersion(
            id=str(uuid.uuid4()), model_id=model.id, version=version,
            algorithm=algorithm, object_path=key, metrics=metrics, active=False,
        )
        self.db.add(row); self.db.commit()
