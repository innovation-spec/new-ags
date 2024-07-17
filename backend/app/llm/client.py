from __future__ import annotations
from dataclasses import dataclass, field
import json
from app.core.config import Settings, get_settings

@dataclass
class LLMResult:
    enabled: bool
    text: str
    tool_calls: list[dict] = field(default_factory=list)
    response_id: str | None = None
    error: str | None = None

class LLMClient:
    def __init__(self, settings: Settings | None = None, client=None):
        self.settings = settings or get_settings()
        self._client = client

    @property
