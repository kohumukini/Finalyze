from typing import Any

from .llm import generate_response as generate_llm_response


def generate_response(context: str, previous_conversation: list[dict[str, str]]) -> str:
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer the user's questions using the following context: \n"
            + context,
        },
        *previous_conversation,
    ]
    return generate_llm_response(messages)
