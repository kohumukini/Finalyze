from typing import Any

from ..core.config import DEFAULT_TEMPERATURE, GROQ_MODEL, MAX_TOKENS

try:
	from groq import Groq
except ImportError:
	Groq = None


def generate_response(
	context: str,
	previous_conversation: list[dict[str, str]],
	groq_api_key: str | None,
) -> str:
	if Groq is None or not groq_api_key:
		raise RuntimeError("Groq client is unavailable")

	client = Groq(api_key=groq_api_key)
	messages: list[dict[str, Any]] = [
		{
			"role": "system",
			"content": "You are a helpful assistant. Use the following data to answer any of the users questions:\n"
			+ context,
		},
		*previous_conversation,
	]
	response = client.chat.completions.create(
		model=GROQ_MODEL,
		messages=messages,
		temperature=DEFAULT_TEMPERATURE,
		max_tokens=MAX_TOKENS,
	)
	return response.choices[0].message.content.strip()
