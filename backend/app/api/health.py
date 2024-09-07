from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])

