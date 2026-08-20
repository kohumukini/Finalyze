import os

from typing import Dict

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .core.config import CORS_ALLOW_ORIGINS, RATE_LIMIT
from .core.logger import configure_logging, get_logger
from .core.database import init_db
from .routers.chat import router as chat_router
from .routers.documents import router as documents_router

from contextlib import asynccontextmanager

FRONTEND_URL = os.getenv("FRONTEND_URL")
SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "true").lower() not in {"0", "false", "no", "off"}

configure_logging()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema during startup.")
    try: 
        init_db()
        logger.info("Database schema ready.")
    except Exception as e:
        logger.error(f"Database failed to initialize: {e}")
    yield

app = FastAPI(title="Finalyze RAG Backend", docs_url=None, redoc_url=None, lifespan = lifespan)

if isinstance(CORS_ALLOW_ORIGINS, str) and CORS_ALLOW_ORIGINS.strip() == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in str(CORS_ALLOW_ORIGINS).split(",") if o.strip()]
    
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(documents_router)
app.include_router(chat_router)

logger.info("FastAPI app initialized with documents and chat routers.")


@app.get("/health")
def health_check() -> Dict[str, str]:
    logger.debug("Health check requested")
    return {"status": "ok"}

if SERVE_FRONTEND and FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    logger.info("Static frontend mount enabled at the app root.")
else:
    logger.info("Static frontend mount disabled; backend API-only mode is active.")