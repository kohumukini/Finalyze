import re

from ..core.schema import Source, Message

from .llm import generate_response as generate_llm_response
from ..core.utils.helper import fence
from .prompts import CHAT_SYSTEM_PROMPT

# Matches "[3]" and "[2, 5]"
_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


# Sources are labelled [<chunk id>] so the model can cite them; keep in sync with CHAT_SYSTEM_PROMPT
def _format_context(sources: list[Source]) -> str:
    body = "\n\n".join(f"[{s.id}] ({s.document_name}): {s.excerpt}" for s in sources)
    return fence("context", body)


def cited_sources(answer: str, sources: list[Source]) -> list[Source]:
    """Keep only the retrieved sources the answer cites; a label the model invented matches nothing."""
    cited = {int(n) for group in _CITATION.findall(answer) for n in group.split(",")}
    return [s for s in sources if s.id in cited]


def generate_response(sources: list[Source], history: list[Message], question: str) -> str:
    if not CHAT_SYSTEM_PROMPT.strip():
        raise RuntimeError("CHAT_SYSTEM_PROMPT is empty; fill it in services/prompts.py")

    # Message only allows user/assistant roles, so the system turn and the context turn are plain
    # dicts, the wire format Groq expects.
    messages: list[dict[str, str]] = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        *(m.model_dump() for m in history),
        {"role": "user", "content": f"{_format_context(sources)}\n\nQuestion: {question}"},
    ]
    return generate_llm_response(messages)
