from pydantic import BaseModel, Field

class ReservationRequest(BaseModel):
    tenant_id: str
