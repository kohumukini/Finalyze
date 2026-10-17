from groq import Groq

from typing import Literal

from ..core.config import DEFAULT_TEMPERATURE, GROQ_API_KEY, GROQ_GATEKEEPER_MODEL, GROQ_MODEL, MAX_TOKENS
from ..core.logger import get_logger

from dataclasses import dataclass
@dataclass(frozen=True)
class ModelProfile: 
    model: str
    max_tokens: int
    temperature: float
    reasoning_effort: Literal["low", "medium", "high"]
    timeout: float
    

GENERATOR = ModelProfile(
    GROQ_MODEL, 
    MAX_TOKENS, 
    DEFAULT_TEMPERATURE, 
    "medium", 
    60.0
)

GATEKEEPER = ModelProfile(
    GROQ_GATEKEEPER_MODEL,
    max_tokens=1000,
    temperature=DEFAULT_TEMPERATURE, 
    reasoning_effort="low", 
    timeout=10.0
)

logger = get_logger(__name__)

_groq_client: Groq | None = None

def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:     
        if not GROQ_API_KEY:
            logger.error("Groq _groq_client failed to load") 
            raise RuntimeError(
                "GROQ API KEY NOT FOUND\n"
            )
            
        _groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq _groq_client successfully loaded")
    return _groq_client

def generate_response(messages: list[dict]) -> str:
    try: 
        client = _get_groq_client()
    except Exception as e: 
        logger.error(f"[_get_groq_client] Issue importing groq model: {e}")
        raise

    response = client.chat.completions.create(
        model=GENERATOR.model,
        messages=messages, 
        temperature=GENERATOR.temperature,
        max_tokens=GENERATOR.max_tokens,
        reasoning_effort=GENERATOR.reasoning_effort, 
        timeout=GENERATOR.timeout
    )

    return (response.choices[0].message.content or "").strip()