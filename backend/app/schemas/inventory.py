from pydantic import BaseModel, Field

class ReservationRequest(BaseModel):
    tenant_id: str
    sku_id: str
    quantity: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1)

class ReservationOut(BaseModel):
    reservation_id: str
    tenant_id: str
    sku_id: str
    quantity: int
    status: str
