from __future__ import annotations
from io import BytesIO
from app.core.config import get_settings

REQUIRED_BUCKETS = (
    "agasthya-models",
    "agasthya-datasets",
    "agasthya-artifacts",
    "agasthya-reports",
    "agasthya-state-archives",
)

class MinioObjectStore:
    def __init__(self):
        settings = get_settings()
        from minio import Minio
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
