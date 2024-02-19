from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Agasthya Demo API"
    environment: str = "local"
    database_url: str = "sqlite+pysqlite:///./agasthya.db"
    redis_url: str = "redis://redis:6379/0"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "agasthya"
    minio_secret_key: str = "agasthya-demo-secret"
    minio_secure: bool = False
    temporal_address: str = "temporal:7233"
    temporal_task_queue: str = "agasthya-demo"
