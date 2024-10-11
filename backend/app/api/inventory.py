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
    stock = InventoryService(db).get_stock(tenant_id, sku_id)
    if stock is None: raise HTTPException(404, "inventory not found")
    return stock

@router.post("/reserve", response_model=ReservationOut)
def reserve(request: ReservationRequest, db: Session = Depends(get_db)):
    try:
        item = InventoryService(db).reserve(request.tenant_id, request.sku_id, request.quantity, request.idempotency_key)
    except InventoryNotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except InsufficientInventory as exc:
        raise HTTPException(409, str(exc)) from exc
    except InvalidReservation as exc:
        raise HTTPException(422, str(exc)) from exc
    return ReservationOut(
        reservation_id=item.id, tenant_id=item.tenant_id, sku_id=item.sku_id,
        quantity=item.quantity, status=item.status,
    )
