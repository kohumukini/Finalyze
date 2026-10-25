from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..core.config import RATE_LIMIT
from ..core.database import get_db_session
from ..core.logger import get_logger
from ..core.schema import ChatRequest, ChatResponse
from ..services.response_generator import cited_sources, generate_response
from ..services.search import retrieve_sources, list_document_names
from ..services.llm import gatekeeper

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
        decision = gatekeeper(user_message, payload.previous_conversation, list_document_names(db))
        if decision.route != "rag": 
            return ChatResponse(response=decision.message, route=decision.route)
        
        sources = retrieve_sources([decision.main_query, *decision.sub_queries], db)
        if not sources: 
            return ChatResponse(
                response="I cannot find any relevant information in the provided documents.", 
                route="refuse", 
                sources=[]
            )
        
        assistant_response_text = generate_response(sources, payload.previous_conversation, user_message)
        logger.info("Groq chat completed successfully")
    except Exception as exc:
        logger.error("Chat pipeline failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Unable to generate a response.") from exc

    return ChatResponse(
        response=assistant_response_text,
        route="rag",
        sources=cited_sources(assistant_response_text, sources),
    )
