from __future__ import annotations
from datetime import timedelta

def recommendation_step_names() -> list[str]:
    return [
        "load_customer", "load_shared_state", "generate_candidates",
        "check_inventory", "rank_and_persist", "optional_llm_explanation",
    ]
