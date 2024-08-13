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
            "tenant_id": request.tenant_id,
            "customer_id": customer_id,
            "limit": request.limit,
        })
    result = RecommendationService(db).generate(request.tenant_id, customer_id, request.limit)
    if result is None: raise HTTPException(404, "customer not found")
    return result

@router.get("/{customer_id}/latest")
def latest_recommendation(customer_id: str, tenant_id: str, db: Session = Depends(get_db)):
    result = RecommendationService(db).latest(tenant_id, customer_id)
    if result is None: raise HTTPException(404, "recommendation not found")
    return result
