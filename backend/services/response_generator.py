from typing import Any

from .llm import generate_response as generate_llm_response
from ..core.config import MAX_TOKENS
from ..core.schema import ModelDecision

def generate_response(
	context: str,
	previous_conversation: list[dict[str, str]],
	instructions: str, 
	groq_api_key: str | None = None, 
) -> str:
	messages: list[dict[str, Any]] = [
		{
			"role": "system",
			"content": f"{instructions} \n"
			+ context,
		},
		*previous_conversation,
	]
	return generate_llm_response(messages)

def route_query(user_prompt: str, chat_hist): 
    return