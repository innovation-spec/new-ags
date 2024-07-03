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
        since = now - timedelta(hours=24)
        stats = DemoService(self.db).stats(tenant_id)
        agent_rows = self.db.execute(
            select(AgentRun.status, func.count())
            .where(AgentRun.tenant_id == tenant_id, AgentRun.created_at >= since)
            .group_by(AgentRun.status)
        ).all()
        agent_status = {str(status): int(count) for status, count in agent_rows}
        rejected_conflicts = int(self.db.scalar(
            select(func.count()).select_from(StateEvent).where(
                StateEvent.tenant_id == tenant_id,
                StateEvent.created_at >= since,
                StateEvent.status == "REJECTED_CONFLICT",
            )
        ) or 0)
        merged_conflicts = int(self.db.scalar(
            select(func.count()).select_from(StateEvent).where(
                StateEvent.tenant_id == tenant_id,
                StateEvent.created_at >= since,
                StateEvent.status == "MERGED",
            )
        ) or 0)
        low_inventory = int(self.db.scalar(
            select(func.count()).select_from(Inventory).where(
                Inventory.tenant_id == tenant_id,
                (Inventory.on_hand - Inventory.reserved) <= 2,
            )
        ) or 0)

        anomalies: list[dict] = []
        failed = agent_status.get("FAILED", 0)
        if failed:
            anomalies.append({"code": "AGENT_FAILURES", "severity": "high", "value": failed,
                              "message": f"{failed} agent run(s) failed in the last 24 hours."})
        if rejected_conflicts:
