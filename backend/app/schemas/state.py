from pydantic import BaseModel, Field

class StatePatchRequest(BaseModel):
    tenant_id: str
    agent_id: str
