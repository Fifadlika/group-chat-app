from pydantic import BaseModel
from datetime import datetime

class MessagePayload(BaseModel):
    message: str

class MessageResponse(BaseModel):
    type: str
    username: str
    message: str
    timestamp: str

