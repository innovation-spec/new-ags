from __future__ import annotations
from datetime import timedelta

def agent_step_names() -> list[str]:
    return ["create_run", "execute_tools", "validate_authoritative_state", "compose_response"]

try:
