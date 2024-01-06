from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.demo.service import DemoService
from app.experiments.source_selection_ppo import run_shadow_experiment
from app.core.config import get_settings
from app.workflows.client import execute_temporal_workflow

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/inventory-race")
