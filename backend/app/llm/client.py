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
    def enabled(self) -> bool:
        return self.settings.openai_enabled

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    @staticmethod
    def _field(item, name, default=None):
        if isinstance(item, dict): return item.get(name, default)
        return getattr(item, name, default)

    def chat(self, message: str, tool_specs: list[dict], dispatch, instructions: str | None = None) -> LLMResult:
        if not self.enabled:
            return LLMResult(enabled=False, text="OpenAI integration is disabled. Add OPENAI_API_KEY to enable LLM explanations and tool orchestration.")
        try:
            client = self._get_client()
