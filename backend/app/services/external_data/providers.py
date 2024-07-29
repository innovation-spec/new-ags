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
