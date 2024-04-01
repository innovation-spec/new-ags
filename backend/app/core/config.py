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
    temporal_enabled: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    random_seed: int = 42
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
