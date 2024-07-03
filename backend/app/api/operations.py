from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.operations.service import OperationsService

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("/daily-report")
def daily_report(tenant_id: str, db: Session = Depends(get_db)):
    return OperationsService(db).daily_report(tenant_id)
