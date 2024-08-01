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
