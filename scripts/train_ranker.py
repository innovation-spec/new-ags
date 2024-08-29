import io, json, pickle, random
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.minio import MinioObjectStore
from app.services.model_registry.service import ModelRegistry

FEATURES = ["category_affinity", "brand_affinity", "behavior", "popularity", "price_fit", "semantic", "inventory"]

def build_training(seed: int = 42, rows: int = 5000):
    rng = random.Random(seed)
    x=[]; y=[]
    for _ in range(rows):
        vals=[rng.random() for _ in FEATURES]
