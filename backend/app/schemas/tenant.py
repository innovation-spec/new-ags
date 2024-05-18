from pydantic import BaseModel, ConfigDict

class TenantOut(BaseModel):
    id: str
    name: str
    model_config = ConfigDict(from_attributes=True)
