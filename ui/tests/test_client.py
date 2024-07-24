import httpx
from api.client import ApiClient


def test_chat_forwards_tenant_customer_and_message():
    seen = {}
