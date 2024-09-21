from pydantic import BaseModel

class ToolCallRecord(BaseModel):
    name: str
    arguments: dict
    output: dict
