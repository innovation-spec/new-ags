from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.inventory import ReservationRequest, ReservationOut
from app.services.inventory.service import InventoryService, InsufficientInventory, InventoryNotFound, InvalidReservation

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("")
