"""Postgres-only concurrency proof; run after Docker Compose starts.

POSTGRES_TEST_URL=postgresql+psycopg://agasthya:agasthya@localhost:5432/agasthya \
  PYTHONPATH=backend pytest tests/concurrency/test_inventory_race.py -q
"""
import os, uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="requires local Postgres")
