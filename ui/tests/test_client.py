import httpx
from api.client import ApiClient


def test_chat_forwards_tenant_customer_and_message():
    seen = {}
    def handler(request):
        seen["json"] = __import__("json").loads(request.content)
        return httpx.Response(200, json={"answer":"ok"})
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test")
    api = ApiClient("http://test", client=client)
    result = api.chat("tenant-a", "c1", "hello")
    assert result["answer"] == "ok"
    assert seen["json"] == {"tenant_id":"tenant-a","customer_id":"c1","message":"hello"}


def test_api_errors_are_returned_as_safe_payloads():
    def handler(request):
        return httpx.Response(409, json={"detail":"insufficient inventory"})
    api = ApiClient("http://test", client=httpx.Client(transport=httpx.MockTransport(handler), base_url="http://test"))
    result = api.post("/anything")
    assert result["ok"] is False
    assert result["status_code"] == 409
    assert "insufficient inventory" in result["error"]
