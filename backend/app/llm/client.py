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
            response = client.responses.create(
                model=self.settings.openai_model,
                instructions=instructions or "Use only the supplied tools for authoritative data. Never invent product IDs, prices, inventory, or state.",
                input=message,
                tools=tool_specs,
                parallel_tool_calls=True,
            )
            call_log: list[dict] = []
            for _ in range(8):
                calls = [item for item in (response.output or []) if self._field(item, "type") == "function_call"]
                if not calls:
                    return LLMResult(enabled=True, text=response.output_text or "", tool_calls=call_log, response_id=response.id)
                outputs = []
                for call in calls:
                    name = self._field(call, "name")
                    call_id = self._field(call, "call_id")
                    raw_args = self._field(call, "arguments", "{}") or "{}"
                    args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
                    try:
