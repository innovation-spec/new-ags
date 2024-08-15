from __future__ import annotations
from dataclasses import dataclass

class ProviderTimeout(Exception): pass
class ProviderRateLimit(Exception): pass
class MalformedProviderResponse(Exception): pass

@dataclass
class MockProvider:
    name: str
    authority: int
    reliability: float
    base_price: float

    def fetch(self, query: str, scenario: str = "normal") -> dict:
        if self.name == "provider-a":
            if scenario == "timeout": raise ProviderTimeout("provider-a timed out")
            if scenario == "rate_limit": raise ProviderRateLimit("provider-a returned 429")
            if scenario == "malformed": raise MalformedProviderResponse("provider-a malformed payload")
            price = self.base_price if scenario != "conflict" else self.base_price + 10
        else:
            price = self.base_price if scenario != "conflict" else self.base_price + 25
        return {
            "source": self.name,
            "value": {"query": query, "price": round(price, 2), "currency": "CAD"},
            "authority": self.authority,
            "reliability": self.reliability,
            "freshness": 0.95,
            "corroboration": 0.8 if scenario == "conflict" else 0.9,
            "historical_quality": self.reliability,
        }


def default_providers() -> list[MockProvider]:
    return [
        MockProvider("provider-a", authority=70, reliability=0.92, base_price=99.0),
        MockProvider("provider-b", authority=55, reliability=0.80, base_price=101.0),
    ]
