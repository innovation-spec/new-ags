from __future__ import annotations
import os
import httpx

class ApiClient:
    def __init__(self, base_url: str | None = None, client: httpx.Client | None = None):
        self.base_url = (base_url or os.getenv("API_BASE_URL", "http://api:8000")).rstrip("/")
        self.client = client or httpx.Client(base_url=self.base_url, timeout=60.0)

    def _safe(self, response: httpx.Response):
        if response.is_success:
            try: return response.json()
            except Exception: return {"ok": True, "text": response.text}
        try:
            payload = response.json()
            error = payload.get("detail") or payload.get("error") or str(payload)
        except Exception:
            error = response.text or response.reason_phrase
        return {"ok": False, "status_code": response.status_code, "error": str(error)}

    def get(self, path: str, **params):
