from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.memory.service import MemoryService, RedisWorkingMemory
from app.core.minio import MinioObjectStore

router = APIRouter(prefix="/memory", tags=["memory"])

class MemoryCreate(BaseModel):
    tenant_id: str
    owner_type: str
    owner_id: str
    memory_type: str
    content: dict
    importance: float = Field(default=.5, ge=0, le=1)
    source: str = "user"
    ttl_seconds: int | None = Field(default=None, gt=0)


def service(db: Session) -> MemoryService:
    try: working = RedisWorkingMemory()
    except Exception: working = None
    return MemoryService(db, working_store=working, object_store=MinioObjectStore())

@router.post("")
def save_memory(request: MemoryCreate, db: Session = Depends(get_db)):
    return service(db).save(**request.model_dump())

@router.get("")
def list_memory(tenant_id: str, owner_type: str | None = None, owner_id: str | None = None, db: Session = Depends(get_db)):
    return service(db).list(tenant_id, owner_type, owner_id)

@router.post("/prune")
def prune_memory(tenant_id: str, db: Session = Depends(get_db)):
    return service(db).prune_expired(tenant_id)
