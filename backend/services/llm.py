from groq import Groq

from typing import Literal

from .prompts import GATEKEEPER_SYSTEM_PROMPT
from ..core.config import DEFAULT_TEMPERATURE, GROQ_API_KEY, GROQ_GATEKEEPER_MODEL, GROQ_MODEL, MAX_TOKENS
from ..core.logger import get_logger
from ..core.schema import GatekeeperDecision, Message, gatekeeper_adapter
from ..core.utils.helper import fence

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
        logger.error(f"[Generate LLM Response] Issue importing groq model: {e}")
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

def gatekeeper(query: str, history: list[Message], catalog: list[str]) -> GatekeeperDecision:
    try: 
        client = _get_groq_client()
    except Exception as e: 
        logger.error(f"[Gatekeeper] Issue with importing groq model: {e}")
        raise
    
    
    
    if not catalog:
        raise RuntimeError("Gatekeeper catalog is empty; ingest documents first")

    # The catalog comes from our own DB, so only the user's text is fenced
    catalog_text = "\n".join(f"- {name}" for name in catalog)
    response = client.chat.completions.create(
        model=GATEKEEPER.model,
        messages=[
            {"role": "system", "content": GATEKEEPER_SYSTEM_PROMPT},
            *(m.model_dump() for m in history[-4:]),
            {"role": "user", "content": f"<catalog>\n{catalog_text}\n</catalog>\n{fence('user_message', query)}"},
        ],
        temperature=GATEKEEPER.temperature,
        max_tokens=GATEKEEPER.max_tokens,
        reasoning_effort=GATEKEEPER.reasoning_effort,
        timeout=GATEKEEPER.timeout,
        response_format={"type": "json_object"},
    )

    choice = response.choices[0]
    if choice.finish_reason == "length":
        raise RuntimeError("Gatekeeper output was cut off at max_tokens; raise GATEKEEPER.max_tokens")

    raw = choice.message.content or ""
    try:
        return gatekeeper_adapter.validate_json(raw)
    except ValueError as e:
        logger.error(f"[Gatekeeper] Output did not match a route: {e}; raw={raw[:300]!r}")
        raise