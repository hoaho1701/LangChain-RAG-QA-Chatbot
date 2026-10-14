from typing import List, Literal
from pydantic import BaseModel, Field

class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    history: List[HistoryMessage] = []

class UrlRequest(BaseModel):
    url: str
