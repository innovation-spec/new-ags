from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.tenants import router as tenants_router
from app.api.catalog import router as catalog_router
from app.api.inventory import router as inventory_router
from app.api.state import router as state_router
from app.api.recommendations import router as recommendations_router
from app.api.models import router as models_router
from app.api.demo import router as demo_router
from app.api.memory import router as memory_router
from app.api.agents import router as agents_router
from app.api.operations import router as operations_router
from app.api.system import router as system_router
from app.core.request_logging import StructuredRequestLoggingMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="Agasthya Multi-tenant Recommendation Demo", version="0.1.0")
    app.add_middleware(StructuredRequestLoggingMiddleware)
    for router in (health_router, tenants_router, catalog_router, inventory_router, state_router, recommendations_router, models_router, demo_router, memory_router, agents_router, operations_router, system_router):
        app.include_router(router)
    return app

app = create_app()
