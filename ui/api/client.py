from __future__ import annotations
import os
import httpx

class ApiClient:
    def __init__(self, base_url: str | None = None, client: httpx.Client | None = None):
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://api:8000")).rstrip("/")
        self.client = client or httpx.Client(base_url=self.base_url, timeout=60.0)

    def _safe(self, response: httpx.Response):
        if response.is_success:
