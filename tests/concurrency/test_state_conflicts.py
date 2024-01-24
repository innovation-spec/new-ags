import os, uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

pytestmark = pytest.mark.skipif(not os.getenv("POSTGRES_TEST_URL"), reason="requires local Postgres")


