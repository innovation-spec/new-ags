import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["TEMPORAL_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
