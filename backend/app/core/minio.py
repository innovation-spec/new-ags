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
        )

    def ensure_buckets(self) -> None:
        for bucket in REQUIRED_BUCKETS:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)

    def put_bytes(self, bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        self.ensure_buckets()
        self.client.put_object(bucket, key, BytesIO(data), len(data), content_type=content_type)
