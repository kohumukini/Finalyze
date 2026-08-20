from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentItem(BaseModel):
    id: int | None = None
    timestamp: datetime | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentCreateRequest(BaseModel):
    document_name: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkItem(BaseModel):
    chunk_id: int | None = None
    vector: list[float] = Field(
        default_factory=list,
        description="The dense vector representation of a chunk that interprets the semantic meaning of the text",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str
    previous_conversation: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str