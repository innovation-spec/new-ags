from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.minio import REQUIRED_BUCKETS
from app.db.session import get_db
from app.llm.schemas import AgentChatRequest
from app.schemas.events import EventEnvelope
from app.schemas.inventory import ReservationRequest
from app.schemas.recommendation import RecommendationRequest
from app.schemas.state import StatePatchRequest

router = APIRouter(tags=["system"])


@router.get("/schemas")
def schema_registry():
