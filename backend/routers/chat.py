from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..core.config import GROQ_API_KEY, RATE_LIMIT
from ..core.database import get_db_session
from ..core.logger import get_logger
from ..core.schema import ChatRequest, ChatResponse
from ..services.response_generator import generate_response
from ..services.search import retrieve_text

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

@router.post("/model", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT)
def chat(request: Request, payload: ChatRequest, db: Session = Depends(get_db_session)):
    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    logger.info("Received chat request")

    if not GROQ_API_KEY:
        logger.error("Groq API key unavailable; falling back to echo mode")
        return ChatResponse(response=f"Echo: {user_message}")

    # Clients may only supply user/assistant turns; a forged "system" turn would override the prompt
    history = [m for m in payload.previous_conversation if m.get("role") in {"user", "assistant"}]

    try:
        chunks = retrieve_text(user_message, db)
        assistant_response_text = generate_response(chunks, history, user_message)
        logger.info("Groq chat completed successfully")
    except Exception as exc:
        logger.error("Chat pipeline failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Unable to generate a response.") from exc

    return ChatResponse(response=assistant_response_text)
