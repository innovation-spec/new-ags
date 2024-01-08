from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Agasthya Demo API"
    environment: str = "local"
    database_url: str = "sqlite+pysqlite:///./agasthya.db"
