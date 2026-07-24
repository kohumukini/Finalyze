from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import CORS_ALLOW_ORIGINS, RATE_LIMIT
from .routers.chat import router as chat_router
from .routers.documents import router as documents_router

limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

app = FastAPI(title="Finalyze RAG Backend", docs_url=None, redoc_url=None)

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

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"} 