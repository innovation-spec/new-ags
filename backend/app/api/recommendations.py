from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation.service import RecommendationService
from app.core.config import get_settings
from app.workflows.client import execute_temporal_workflow
