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
        providers = default_providers()
        attempts: list[dict] = []
        candidates: list[dict] = []
        fallback_used = False

        first, first_attempts = execute_with_retry(providers[0], query, scenario, sleep=self.sleep, jitter=self.jitter)
        attempts.extend(first_attempts)
        if first is not None:
            first["provenance"] = {"source": first["source"], "query": query, "scenario": scenario, "attempt": first_attempts[-1]["attempt"]}
            candidates.append(first)

        need_fallback = first is None or scenario == "conflict"
        if need_fallback:
            fallback_used = first is None
            second, second_attempts = execute_with_retry(providers[1], query, "conflict" if scenario == "conflict" else "normal", max_attempts=1, sleep=self.sleep, jitter=self.jitter)
            attempts.extend(second_attempts)
            if second is not None:
                second["provenance"] = {"source": second["source"], "query": query, "scenario": scenario, "attempt": second_attempts[-1]["attempt"]}
                candidates.append(second)

        selected = self.resolver.resolve(candidates, internal_value=internal_value)
        persisted_ids = []
        for candidate in candidates:
            result = ExternalResult(
                id=str(uuid.uuid4()), tenant_id=tenant_id, source_name=candidate["source"], query=query,
                value=candidate["value"], provenance=candidate.get("provenance", {}),
            )
            self.db.add(result); self.db.flush()
            score = self.resolver.score(candidate)
            self.db.add(CredibilityScore(
                id=str(uuid.uuid4()), tenant_id=tenant_id, external_result_id=result.id,
                score=score, factors={
                    "authority": candidate.get("authority"), "reliability": candidate.get("reliability"),
                    "freshness": candidate.get("freshness"), "corroboration": candidate.get("corroboration"),
                    "historical_quality": candidate.get("historical_quality"),
                },
            ))
            persisted_ids.append(result.id)
        self.db.commit()
        if selected and selected.get("source") != "internal":
            selected.setdefault("provenance", {"source": selected["source"], "query": query, "scenario": scenario})
        return {
            "query": query, "scenario": scenario, "selected": selected,
            "candidates": candidates, "attempts": attempts, "fallback_used": fallback_used,
            "persisted_result_ids": persisted_ids,
        }
