from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation.service import RecommendationService
from app.core.config import get_settings
from app.workflows.client import execute_temporal_workflow

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("/{customer_id}")
async def generate_recommendations(customer_id: str, request: RecommendationRequest, db: Session = Depends(get_db)):
    if get_settings().temporal_enabled:
        return await execute_temporal_workflow("recommendation", {
