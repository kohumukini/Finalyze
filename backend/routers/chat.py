from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..core.config import RATE_LIMIT
from ..core.database import get_db_session
from ..core.logger import get_logger
from ..core.schema import ChatRequest, ChatResponse
from ..services.response_generator import cited_sources, generate_response
from ..services.search import retrieve_sources

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

    # No role filtering needed: Message.role is Literal['user','assistant'], so a forged "system" turn gets a 422
    try:
        sources = retrieve_sources(user_message, db)
        assistant_response_text = generate_response(sources, payload.previous_conversation, user_message)
        logger.info("Groq chat completed successfully")
    except Exception as exc:
        logger.error("Chat pipeline failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Unable to generate a response.") from exc

    # shortcut: route is hardcoded until the gatekeeper layer decides it
    return ChatResponse(
        response=assistant_response_text,
        route="rag",
        sources=cited_sources(assistant_response_text, sources),
    )
