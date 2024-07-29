from __future__ import annotations
from app.services.external_data.providers import ProviderTimeout, ProviderRateLimit, MalformedProviderResponse

RETRYABLE = (ProviderTimeout, ProviderRateLimit, MalformedProviderResponse)

def execute_with_retry(provider, query: str, scenario: str, max_attempts: int = 3, base_delay: float = 0.05, sleep=lambda _: None, jitter=lambda: 0.0):
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            value = provider.fetch(query, scenario)
            attempts.append({"source": provider.name, "attempt": attempt, "status": "success"})
            return value, attempts
        except ProviderTimeout as exc:
