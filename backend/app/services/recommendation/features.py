from __future__ import annotations
import math
from collections import Counter

EVENT_WEIGHTS = {"view": 1.0, "click": 2.0, "save": 3.0, "add_cart": 4.0, "purchase": 5.0}

def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0: return 0.0
    return max(-1.0, min(1.0, dot/(na*nb)))

def build_customer_profile(customer, events, products_by_id: dict) -> dict:
    prefs = dict(customer.preferences or {})
    category_scores = Counter()
    brand_scores = Counter()
    product_scores = Counter()
    vectors: list[list[float]] = []
    for event in events:
        product = products_by_id.get(event.product_id)
