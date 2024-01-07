from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.minio import MinioObjectStore
from app.services.model_registry.service import ModelRegistry

