from groq import Groq

from ..core.config import DEFAULT_TEMPERATURE, GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from ..core.logger import get_logger

logger = get_logger(__name__)

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client successfully loaded")
    except Exception as exc:
        logger.error("Groq client failed to load: %s", exc)
else:
    logger.error("Groq API Key Missing!")


def generate_response(messages: list[dict]) -> str:
    if client is None:
        raise RuntimeError("Groq client has not been initialized")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages, 
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()