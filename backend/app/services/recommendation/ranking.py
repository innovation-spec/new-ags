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
