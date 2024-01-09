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
