from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.memory.service import MemoryService, RedisWorkingMemory
from app.core.minio import MinioObjectStore

router = APIRouter(prefix="/memory", tags=["memory"])

