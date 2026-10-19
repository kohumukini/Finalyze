from datetime import datetime
from typing import Any, Literal, Annotated

from pydantic import BaseModel, Field, TypeAdapter, StringConstraints, AfterValidator, ConfigDict

from .utils.validators import dedupe_strings

TrimmedShortStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        # Adjusted to 100 char over prompt to allow for breathing room
        max_length=500
    )
]

# 0-3 extra search queries (main_query is the 4th). Order of checks: each item is stripped and must be
# non-empty -> repeats are dropped (case-insensitive) -> the list is length-checked (max 3).
# Wrong types fail validation.
UniqueCleanList = Annotated[
    list[TrimmedShortStr],
    AfterValidator(dedupe_strings),
    Field(max_length=3)
]

# A stored document as returned by the /docs endpoints (list and get by name).
# TODO - Consider refactoring the metadata structure
class DocumentItem(BaseModel):
    document_id: int
    document_name: str
    timestamp: datetime | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# A stored chunk of a document together with its embedding; equivalent to one Chunks row
# TODO - Consider refactoring metadata structure
class ChunkItem(BaseModel):
    chunk_id: int
    document_id: int
    content: str
    vector: list[float] = Field(
        default_factory=list,
        description="The dense vector representation of a chunk that interprets the semantic meaning of the text",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

# Stores chat message data. 
# For storing 1 message earlier for chat history
# 'assistant' tag implemented to refuse smuggled data
class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str = Field(max_length=4000)

# HTTP IN - body of POST /chat/model.
# message: the user's new question.
# previous_conversation: earlier turns, oldest first, capped at 10.
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    previous_conversation: list[Message] = Field(default_factory=list, max_length=10)

# HTTP OUT (nested) - one passage the answer cites. Built by the backend from chunks the model
# actually cited, never written by the model.
# id: the chunk_id, also the [n] label used inside the response text, so a "[27]" in the text maps to the Source with id 27
# document_name / section: passage citation (e.g. "Coca-Cola FY2023 10-K", "Item 7").
# excerpt: chunk text, so the UI can show what the answer was based on.
class Source(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    # Maps with chunk_id
    id: int = Field(validation_alias="chunk_id")
    
    # No need for mapping
    document_name: str
    section: str | None = None
    
    # Maps with content
    excerpt: str = Field(validation_alias="content")

# HTTP OUT - what the browser receives from POST /chat/model.
# response: the answer text (or the refusal / greeting text).
# route: which path the gatekeeper chose, so the UI can style a refusal differently from an answer.
# sources: the passages cited in `response`; an empty list for refuse and direct routes.
class ChatResponse(BaseModel):
    response: str
    route: Literal['refuse', 'direct', 'rag']
    sources: list[Source] = Field(default_factory=list)

# GATEKEEPER OUTPUT (LLM JSON, not HTTP) - the request is junk, abusive, an injection attempt,
# or out of scope. `message` is shown to the user as-is. Sent back with route="refuse".
class Refuse(BaseModel):
    route: Literal['refuse']
    message: TrimmedShortStr

# GATEKEEPER OUTPUT (LLM JSON, not HTTP) - no retrieval needed: a greeting or a "what can you do" question.
# `message` is the gatekeeper's own reply, shown to the user as-is. Sent back with route="direct".
class Direct(BaseModel):
    route: Literal['direct']
    message: TrimmedShortStr

# GATEKEEPER OUTPUT (LLM JSON, not HTTP) - the question needs the documents, so retrieval runs.
# main_query: the user's question rewritten to stand alone. sub_queries: 0-3 extra searches ([] when not needed).
class RAG(BaseModel):
    route: Literal['rag']
    main_query: TrimmedShortStr
    sub_queries: UniqueCleanList = Field(default_factory=list)

GatekeeperDecision = Annotated[Refuse | Direct | RAG, Field(discriminator='route')]
gatekeeper_adapter = TypeAdapter(GatekeeperDecision)