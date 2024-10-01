from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    tenant_id: str
