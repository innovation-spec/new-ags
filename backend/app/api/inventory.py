from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.inventory import ReservationRequest, ReservationOut
from app.services.inventory.service import InventoryService, InsufficientInventory, InventoryNotFound, InvalidReservation

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("")
def list_inventory(tenant_id: str, limit: int = 100, search: str | None = None, category: str | None = None, db: Session = Depends(get_db)):
    return InventoryService(db).list_inventory(tenant_id, limit, search, category)

@router.get("/{sku_id}/ledger")
def get_ledger(sku_id: str, tenant_id: str, limit: int = 100, db: Session = Depends(get_db)):
    return InventoryService(db).ledger(tenant_id, sku_id, limit)

@router.get("/{sku_id}")
def get_inventory(sku_id: str, tenant_id: str, db: Session = Depends(get_db)):
