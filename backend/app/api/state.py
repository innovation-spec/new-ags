from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.state import StatePatchRequest
from app.services.state.service import StateService

router = APIRouter(prefix="/state", tags=["state"])

@router.get("/{entity_type}/{entity_id}")
def get_state(entity_type: str, entity_id: str, tenant_id: str, db: Session = Depends(get_db)):
    value = StateService(db).get_state(tenant_id, entity_type, entity_id)
    if value is None: raise HTTPException(404, "state not found")
    return value

@router.get("/{entity_type}/{entity_id}/events")
def get_events(entity_type: str, entity_id: str, tenant_id: str, db: Session = Depends(get_db)):
    return StateService(db).list_events(tenant_id, entity_type, entity_id)

@router.post("/{entity_type}/{entity_id}/patch")
def patch_state(entity_type: str, entity_id: str, request: StatePatchRequest, db: Session = Depends(get_db)):
    try:
