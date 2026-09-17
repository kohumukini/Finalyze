from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Metadata Declarations
# =============================================================================
class DocumentMetadata(BaseModel): 
    author: Optional[str] = None
    filepath: Optional[str]
    source_type: str = "text"
    extras: dict[str, Any] = Field(default_factory=dict)
    
class ChunkMetadata(BaseModel):
    source_name: Optional[str]
    chunk_index = int
    extras: dict[str, Any] = Field(default_factory=dict)

# =============================================================================
# Document Models
# =============================================================================
class DocumentItem(BaseModel):
    document_id: int
    document_name: str
    timestamp: datetime | None = None
    content: str
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    
class DocumentCreateRequest(BaseModel):
    document_name: str
    content: str
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)

# =============================================================================
# Chunk Model
# =============================================================================

class ChunkItem(BaseModel):
    chunk_id: int
    document_id: int
    content: str
    vector: list[float] = Field(
        default_factory=list,
        description="The dense vector representation of a chunk that interprets the semantic meaning of the text",
    )
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata)

# =============================================================================
# Chat Models 
# =============================================================================

class ChatMessage(BaseModel): 
    role: str = Field(description="Roles: Assistant, System, ")
    content = str
    metatdata = dict[str, any] = Field(default_factor=dict)

class ChatRequest(BaseModel):
    message: str
    previous_conversation: list[ChatMessage] = Field(default_factory=ChatMessage)


class ChatResponse(BaseModel):
    response: str
    
