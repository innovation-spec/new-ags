from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.tenancy.service import TenantService
from app.schemas.tenant import TenantOut

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("", response_model=list[TenantOut])
