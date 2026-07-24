from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentItem(BaseModel):
    document_id: int | None = None
    document_name: str
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


class ChatResponse(BaseModel):
    response: str