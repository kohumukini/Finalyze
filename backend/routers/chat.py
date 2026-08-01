import json

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..core.config import DEFAULT_TEMPERATURE, GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, RATE_LIMIT
from ..core.database import get_db_session
from ..core.logger import get_logger
from ..core.schema import ChatRequest, ChatResponse
from ..services.ingest import load_chunks

logger = get_logger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None

router = APIRouter(prefix="/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

@router.post("/model", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT)
def chat(request: Request, payload: ChatRequest, db: Session = Depends(get_db_session)):
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    client = None
    if Groq is not None and GROQ_API_KEY:
        client = Groq(api_key=GROQ_API_KEY)

    logger.info("Received chat request")
    
    if client is not None:
        doc_context = load_chunks()
        context = json.dumps(doc_context, indent = 4)
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Use the following data to answer any of the users questions:\n"
                        + context,
                    },
                    {"role": "user", "content": user_message},
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            assistant_response_text = response.choices[0].message.content.strip()
            logger.info("Groq chat completed successfully")
            print(assistant_response_text)
            print(len(assistant_response_text))
        except Exception as exc:
            logger.error("Groq chat failed: %s", exc, exc_info=True)
            assistant_response_text = f"I couldn't reach Groq right now, so I'm echoing your request: {user_message}"
    else:
        logger.warning("Groq client unavailable; falling back to echo mode")
        assistant_response_text = f"Echo: {user_message}"

    return ChatResponse(response=assistant_response_text)
