from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    tenant_id: str
    limit: int = Field(default=10, ge=1, le=100)
