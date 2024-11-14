import os

import httpx
import pytest

BASE = os.getenv("WEB_BASE_URL")
pytestmark = pytest.mark.skipif(not BASE, reason="requires running React/Nginx Docker Compose stack")


def test_react_console_and_api_proxy_are_reachable():
    with httpx.Client(base_url=BASE, timeout=30, follow_redirects=True) as client:
        page = client.get("/")
        page.raise_for_status()
        assert '<div id="root"></div>' in page.text
        assert "Agasthya" in page.text

