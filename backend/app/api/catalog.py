from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.catalog.service import CatalogService
from app.schemas.catalog import ProductOut

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/products", response_model=list[ProductOut])
