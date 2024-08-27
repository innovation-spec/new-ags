from __future__ import annotations
from app.services.recommendation.features import cosine_similarity

def score_candidate(profile: dict, product, available: int) -> tuple[float, dict]:
    fav_category = profile.get("favorite_category")
    fav_brand = profile.get("favorite_brand")
    category_match = 1.0 if fav_category and product.category == fav_category else 0.0
    brand_match = 1.0 if fav_brand and product.brand == fav_brand else 0.0
    category_behavior = float(profile.get("category_scores", {}).get(product.category, 0))
    brand_behavior = float(profile.get("brand_scores", {}).get(product.brand, 0))
    direct_behavior = float(profile.get("product_scores", {}).get(product.id, 0))
    behavior_raw = category_behavior + 0.5 * brand_behavior + direct_behavior
    behavior = behavior_raw / (behavior_raw + 5.0) if behavior_raw > 0 else 0.0
    semantic_raw = cosine_similarity(profile.get("behavior_vector", []), [float(x) for x in (product.embedding or [])])
    semantic = (semantic_raw + 1.0) / 2.0 if profile.get("behavior_vector") else 0.0
    max_price = float(profile.get("max_price", 0) or 0)
    if max_price <= 0:
        price_fit = 0.5
    elif product.price <= max_price:
        price_fit = 1.0 - min(0.5, abs(max_price - product.price) / max_price * 0.25)
    else:
        price_fit = max(0.0, 1.0 - (product.price - max_price) / max_price)
