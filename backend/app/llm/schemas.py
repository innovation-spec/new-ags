from pydantic import BaseModel

class ToolCallRecord(BaseModel):
    name: str
    arguments: dict
    output: dict

class AgentChatRequest(BaseModel):
    tenant_id: str
    customer_id: str
    message: str
