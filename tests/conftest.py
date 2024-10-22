import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["TEMPORAL_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
