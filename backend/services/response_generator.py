from ..core.schema import Source, Message

from .llm import generate_response as generate_llm_response
from .prompts import CHAT_SYSTEM_PROMPT


# Chunks are labelled [1], [2], ... so the model can cite them; keep in sync with CHAT_SYSTEM_PROMPT
def _format_context(sources: list[Source]) -> str:
    body = "\n\n".join(f"[{s.id}] ({s.document_name}): {s.excerpt}" for s in sources)
    return f"<context>\n{body}\n</context>"


def generate_response(chunks: list[Source], history: list[Message], question: str) -> str:
    if not CHAT_SYSTEM_PROMPT.strip():
        raise RuntimeError("CHAT_SYSTEM_PROMPT is empty; fill it in services/prompts.py")

    messages: list[Message] = [
        Message(
            role = "assistant", 
            content = CHAT_SYSTEM_PROMPT
        ),
        *history,
        Message(
            role = "user", 
            content = f"{_format_context(chunks)}\n\nQuestion: {question}"
        ),
    ]
    return generate_llm_response(messages)
