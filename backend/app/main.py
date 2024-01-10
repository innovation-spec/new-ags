from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.tenants import router as tenants_router
from app.api.catalog import router as catalog_router
from app.api.inventory import router as inventory_router
from app.api.state import router as state_router
