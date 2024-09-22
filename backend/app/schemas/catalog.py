from pydantic import BaseModel, ConfigDict

class ProductOut(BaseModel):
    id: str
    tenant_id: str
    name: str
