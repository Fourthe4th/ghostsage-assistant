from typing import List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # new session if not provided


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: List[Message]
