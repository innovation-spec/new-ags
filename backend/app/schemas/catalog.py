from pydantic import BaseModel, ConfigDict

class ProductOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    category: str
    brand: str
    price: float
    popularity: float
    model_config = ConfigDict(from_attributes=True)
