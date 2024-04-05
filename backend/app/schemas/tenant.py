from pydantic import BaseModel, ConfigDict

class TenantOut(BaseModel):
    id: str
    name: str
