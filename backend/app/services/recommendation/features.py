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
        if not product: continue
        weight = EVENT_WEIGHTS.get(event.event_type, 1.0) * float(event.value or 1)
        category_scores[product.category] += weight
        brand_scores[product.brand] += weight
        product_scores[product.id] += weight
        if product.embedding: vectors.append([float(x) for x in product.embedding])
    if vectors:
        dims = len(vectors[0])
        vector = [sum(v[i] for v in vectors if len(v) == dims)/len(vectors) for i in range(dims)]
    else:
        vector = []
    return {
        "favorite_category": prefs.get("favorite_category"),
        "favorite_brand": prefs.get("favorite_brand"),
        "max_price": float(prefs.get("max_price", 0) or 0),
        "category_scores": dict(category_scores),
        "brand_scores": dict(brand_scores),
        "product_scores": dict(product_scores),
        "behavior_vector": vector,
    }
