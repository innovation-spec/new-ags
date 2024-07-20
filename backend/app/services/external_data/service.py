from __future__ import annotations
import uuid
from sqlalchemy.orm import Session
from app.models.domain import ExternalResult, CredibilityScore
from app.services.external_data.providers import default_providers
from app.services.external_data.retry import execute_with_retry
from app.services.external_data.credibility import CredibilityResolver

class ExternalDataService:
    def __init__(self, db: Session, sleep=lambda _: None, jitter=lambda: 0.0):
        self.db = db
        self.sleep = sleep
        self.jitter = jitter
        self.resolver = CredibilityResolver()

    def resolve(self, tenant_id: str, query: str, scenario: str = "normal", internal_value: dict | None = None) -> dict:
