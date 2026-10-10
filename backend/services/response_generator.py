from .llm import generate_response as generate_llm_response
from .prompts import CHAT_SYSTEM_PROMPT


# Chunks are labelled [1], [2], ... so the model can cite them; keep in sync with CHAT_SYSTEM_PROMPT
def _format_context(chunks: list[str]) -> str:
    body = "\n\n".join(f"[{i}] {chunk}" for i, chunk in enumerate(chunks, start=1))
    return f"<context>\n{body}\n</context>"


def generate_response(chunks: list[str], history: list[dict[str, str]], question: str) -> str:
    if not CHAT_SYSTEM_PROMPT.strip():
        raise RuntimeError("CHAT_SYSTEM_PROMPT is empty; fill it in services/prompts.py")

    messages: list[dict[str, str]] = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": f"{_format_context(chunks)}\n\nQuestion: {question}"},
    ]
    return generate_llm_response(messages)
