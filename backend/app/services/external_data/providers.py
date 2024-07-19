from __future__ import annotations
from dataclasses import dataclass

class ProviderTimeout(Exception): pass
class ProviderRateLimit(Exception): pass
class MalformedProviderResponse(Exception): pass

@dataclass
class MockProvider:
    name: str
