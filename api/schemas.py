# api/schemas.py

from typing import Literal

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    history: list[HistoryMessage] = []


class UrlRequest(BaseModel):
    url: str
