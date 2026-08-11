import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, Text, create_engine, func, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

from pgvector.sqlalchemy import VECTOR

from .logger import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in local dev
    def load_dotenv(*args, **kwargs):
        return False

try:
    from pgvector import Vector
except ImportError:  # pragma: no cover - optional dependency in local dev
    class Vector:  # type: ignore[no-redef]
        def __init__(self, dimensions):
            self.dimensions = dimensions

from .config import MODEL_VECTOR_SIZE

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

EXTERNAL_URL = os.getenv("EXTERNAL_URL")

if EXTERNAL_URL and EXTERNAL_URL.strip():
    POSTGRES_URL = EXTERNAL_URL.strip()
    logger.info("External URL Connected")
else:
    USER = os.getenv("POSTGRES_USER", "postgres")
    PASSWORD = os.getenv("POSTGRES_PASS", "postgres")
    DB = os.getenv("POSTGRES_DB", "finalyze")
    PORT = os.getenv("POSTGRES_PORT", "5432")
    HOST = os.getenv(
        "POSTGRES_HOST",
        "db" if os.getenv("IS_DOCKER", "").lower() in {"1", "true", "yes", "on"} else "localhost",
    )
    POSTGRES_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    
    logger.info("Local Postgres Connected")

SQLITE_URL = "sqlite:///./finalyze.db"

try:
    ENGINE = create_engine(POSTGRES_URL)
except Exception:
    ENGINE = create_engine(SQLITE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

class Base(DeclarativeBase):
    pass


metadata_column_type = JSONB if ENGINE.dialect.name == "postgresql" else JSON


class Documents(Base):
    __tablename__ = "documents"

    documents_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
    
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type, default = dict)
    
    chunks: Mapped[list["Chunks"]] = relationship("Chunks", back_populates="document", cascade="all, delete-orphan")


class Chunks(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.documents_id"))
    content: Mapped[str] = mapped_column(Text)
    
    embedding: Mapped[list[float]] = mapped_column(VECTOR(MODEL_VECTOR_SIZE))
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type, default = dict)
    
    document: Mapped["Documents"] = relationship("Documents", back_populates="chunks")


def init_db():
    Base.metadata.create_all(bind=ENGINE)
    return ENGINE


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database Initialized")