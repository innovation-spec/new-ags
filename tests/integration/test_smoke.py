import os
import pytest
import httpx

BASE = os.getenv("SMOKE_BASE_URL")
pytestmark = pytest.mark.skipif(not BASE, reason="requires running Docker Compose stack")

def test_running_stack_smoke():
