from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health() -> dict[str, object]:
