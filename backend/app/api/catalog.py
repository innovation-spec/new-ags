from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.catalog.service import CatalogService
from app.schemas.catalog import ProductOut

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/products", response_model=list[ProductOut])
def list_products(tenant_id: str, limit: int = 100, category: str | None = None, db: Session = Depends(get_db)):
    return CatalogService(db).list_products(tenant_id, limit, category)

@router.get("/products/{product_id}", response_model=ProductOut)
