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
        if activate:
            return self.activate(model_name, version)
        return self._serialize(model, row)

    def activate(self, model_name: str, version: str) -> dict:
        model = self._model(model_name)
        if model is None: raise ValueError("model not found")
        target = self.db.scalar(select(ModelVersion).where(ModelVersion.model_id == model.id, ModelVersion.version == version))
        if target is None: raise ValueError("model version not found")
        self.db.execute(update(ModelVersion).where(ModelVersion.model_id == model.id).values(active=False))
        target.active = True
        self.db.commit(); self.db.refresh(target)
        return self._serialize(model, target)

    def get_active(self, model_name: str) -> dict | None:
        model = self._model(model_name)
        if model is None: return None
        version = self.db.scalar(select(ModelVersion).where(ModelVersion.model_id == model.id, ModelVersion.active.is_(True)))
        return self._serialize(model, version) if version else None

    def list_versions(self, model_name: str) -> list[dict]:
        model = self._model(model_name)
        if model is None: return []
        rows = self.db.scalars(select(ModelVersion).where(ModelVersion.model_id == model.id).order_by(ModelVersion.version)).all()
        return [self._serialize(model, row) for row in rows]

    def list_models(self) -> list[dict]:
        models = self.db.scalars(select(MLModel).order_by(MLModel.name)).all()
        return [{"name": model.name, "versions": self.list_versions(model.name)} for model in models]

    def get_artifact(self, model_name: str, version: str) -> bytes | None:
        model = self._model(model_name)
        if model is None: return None
        row = self.db.scalar(select(ModelVersion).where(ModelVersion.model_id == model.id, ModelVersion.version == version))
        if row is None: return None
        return self.store.get_bytes(self.BUCKET, row.object_path)

    @staticmethod
    def _serialize(model: MLModel, row: ModelVersion) -> dict:
        return {
            "name": model.name, "version": row.version, "algorithm": row.algorithm,
            "object_path": row.object_path, "metrics": row.metrics or {}, "active": bool(row.active),
        }
