from typing import Any, Dict, List

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .core.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    EMBEDDING_MODEL,
    RATE_LIMIT,
    CORS_ALLOW_ORIGINS,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
)

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency
    Groq = None
    
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

app = FastAPI(title="Finalyze RAG Backend")

# Configure CORS origins from config (comma-separated or '*')
if isinstance(CORS_ALLOW_ORIGINS, str) and CORS_ALLOW_ORIGINS.strip() == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in str(CORS_ALLOW_ORIGINS).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# In-memory storage for the simple prototype backend.
documents: List[Dict[str, Any]] = []
chat_history: List[Dict[str, str]] = []


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/process-document")
def process_document(text: str = Body(..., media_type="text/plain")) -> Dict[str, Any]:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    document = {
        "id": len(documents) + 1,
        "text": cleaned_text,
        "word_count": len(cleaned_text.split()),
        "preview": cleaned_text[:200],
    }
    documents.append(document)

    return {"message": "Document processed successfully.", "document": document}


@app.get("/documents")
def list_documents() -> Dict[str, List[Dict[str, Any]]]:
    return {"documents": documents}


@app.post("/chat")
@limiter.limit(RATE_LIMIT)
def chat(request: Request, message: Dict[str, str]) -> Dict[str, str]:
    user_message = (message.get("message") or "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    chat_history.append({"role": "user", "content": user_message})

    client = None
    groq_api_key = GROQ_API_KEY
    if Groq is not None and groq_api_key:
        client = Groq(api_key=groq_api_key)

    if client is not None:
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for anything the user asks."},
                    *chat_history,
                ],
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            assistant_response_text = response.choices[0].message.content.strip()
        except Exception:
            assistant_response_text = f"I couldn't reach Groq right now, so I'm echoing your request: {user_message}"
    else:
        assistant_response_text = f"Echo: {user_message}"

    chat_history.append({"role": "assistant", "content": assistant_response_text})
    return {"response": assistant_response_text} 