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
        target=.26*vals[0]+.20*vals[1]+.20*vals[2]+.14*vals[3]+.10*vals[4]+.05*vals[5]+.05*vals[6]+rng.gauss(0,.03)
        x.append(vals); y.append(target)
    return np.asarray(x), np.asarray(y)

if __name__ == "__main__":
    x,y=build_training()
    model=GradientBoostingRegressor(random_state=42, n_estimators=80, max_depth=3)
    model.fit(x,y)
