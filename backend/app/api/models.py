from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.minio import MinioObjectStore
from app.services.model_registry.service import ModelRegistry

router = APIRouter(prefix="/models", tags=["models"])

def registry(db: Session) -> ModelRegistry:
    return ModelRegistry(db, MinioObjectStore())

@router.get("")
def list_models(db: Session = Depends(get_db)):
    return registry(db).list_models()

@router.post("/{model_name}/{version}/activate")
