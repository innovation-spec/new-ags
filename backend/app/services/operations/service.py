from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.domain import AgentRun, Inventory, StateEvent
from app.services.demo.service import DemoService


class OperationsService:
    """Application-level daily reporting for the local demo."""

    def __init__(self, db: Session):
        self.db = db

    def daily_report(self, tenant_id: str) -> dict:
        now = datetime.now(timezone.utc)
