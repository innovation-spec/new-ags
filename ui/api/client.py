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
        try: return self._safe(self.client.get(path, params=params or None))
        except Exception as exc: return {"ok": False, "status_code": 0, "error": str(exc)}

    def post(self, path: str, json: dict | None = None, **params):
        try: return self._safe(self.client.post(path, json=json, params=params or None))
        except Exception as exc: return {"ok": False, "status_code": 0, "error": str(exc)}

    def health(self): return self.get("/health")
    def tenants(self): return self.get("/tenants")
    def customers(self, tenant_id: str, limit: int = 100): return self.get(f"/tenants/{tenant_id}/customers", limit=limit)
    def chat(self, tenant_id: str, customer_id: str, message: str):
        return self.post("/agents/chat", json={"tenant_id": tenant_id, "customer_id": customer_id, "message": message})
    def recommend(self, tenant_id: str, customer_id: str, limit: int = 10):
        return self.post(f"/recommendations/{customer_id}", json={"tenant_id": tenant_id, "limit": limit})
    def latest_recommendation(self, tenant_id: str, customer_id: str):
        return self.get(f"/recommendations/{customer_id}/latest", tenant_id=tenant_id)
    def runs(self, tenant_id: str, limit: int = 50): return self.get("/agents/runs", tenant_id=tenant_id, limit=limit)
    def run(self, tenant_id: str, run_id: str): return self.get(f"/agents/runs/{run_id}", tenant_id=tenant_id)
    def models(self): return self.get("/models")
    def demo(self, scenario: str, **params): return self.post(f"/demo/{scenario}", **params)
    def stats(self, tenant_id: str): return self.get("/demo/stats", tenant_id=tenant_id)
