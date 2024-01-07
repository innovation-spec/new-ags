from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.state import StatePatchRequest
from app.services.state.service import StateService

router = APIRouter(prefix="/state", tags=["state"])
