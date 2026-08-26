from typing import Any

from .llm import generate_response as generate_llm_response


def generate_response(
	context: str,
	previous_conversation: list[dict[str, str]],
	groq_api_key: str | None = None,
) -> str:
	messages: list[dict[str, Any]] = [
		{
			"role": "system",
			"content": "You are a helpful assistant. Use the following data to answer any of the users questions:\n"
			+ context,
		},
		*previous_conversation,
	]
	return generate_llm_response(messages)
