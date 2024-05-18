from pydantic import BaseModel, Field

class StatePatchRequest(BaseModel):
    tenant_id: str
    agent_id: str
    operation_id: str = Field(min_length=1)
    base_version: int = Field(ge=0)
    patch: dict
    merge_policy: str = "replace"
