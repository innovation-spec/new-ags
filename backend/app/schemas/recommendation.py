from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    tenant_id: str
