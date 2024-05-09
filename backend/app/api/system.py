from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.minio import REQUIRED_BUCKETS
from app.db.session import get_db
from app.llm.schemas import AgentChatRequest
from app.schemas.events import EventEnvelope
from app.schemas.inventory import ReservationRequest
from app.schemas.recommendation import RecommendationRequest
from app.schemas.state import StatePatchRequest

router = APIRouter(tags=["system"])


@router.get("/schemas")
def schema_registry():
    contracts = (ReservationRequest, RecommendationRequest, StatePatchRequest, AgentChatRequest, EventEnvelope)
    return {
        "registry_version": "1.0",
        "schemas": {model.__name__: model.model_json_schema() for model in contracts},
    }


@router.get("/system/status")
def system_status(db: Session = Depends(get_db)):
    settings = get_settings()
    components: dict[str, dict] = {}

    try:
        db.execute(text("SELECT 1"))
        components["database"] = {"status": "ok", "engine": db.get_bind().dialect.name}
    except Exception as exc:
        components["database"] = {"status": "unavailable", "error": type(exc).__name__}

    try:
        import redis
        client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=0.25,
            socket_timeout=0.25,
        )
        client.ping()
        components["redis"] = {"status": "ok"}
    except Exception as exc:
        components["redis"] = {"status": "unavailable", "error": type(exc).__name__}

    try:
        import urllib3
        from minio import Minio
        pool = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=0.25, read=0.25),
            retries=False,
        )
        minio = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
            http_client=pool,
        )
        present = [bucket for bucket in REQUIRED_BUCKETS if minio.bucket_exists(bucket)]
        components["minio"] = {"status": "ok" if present else "unavailable", "buckets": present}
    except Exception as exc:
        components["minio"] = {"status": "unavailable", "error": type(exc).__name__, "buckets": []}

    components["temporal"] = {
        "status": "enabled" if settings.temporal_enabled else "disabled",
        "address": settings.temporal_address,
    }
    components["openai"] = {
        "status": "enabled" if settings.openai_enabled else "disabled",
        "model": settings.openai_model,
    }
    return components
