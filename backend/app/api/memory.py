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
