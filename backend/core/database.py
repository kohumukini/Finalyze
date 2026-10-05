import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import Text, create_engine, func, ForeignKey, text
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

from .config import MODEL_VECTOR_SIZE

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")

EXTERNAL_URL = os.getenv("EXTERNAL_URL")

if not EXTERNAL_URL: 
    raise ValueError("EXTERNAL_URL environment var not set")

try: 
    # SQLAlchemy 2 rejects the legacy "postgres://" scheme that some hosts (e.g. Render) still hand out
    # pool_pre_ping drops connections the host closed while idle
    ENGINE = create_engine(EXTERNAL_URL.replace("postgres://", "postgresql://", 1), pool_pre_ping=True)
    SessionLocal = sessionmaker(ENGINE)
except Exception as e: 
    logger.error(f"Postgres database connection failed: {e}")
    raise


class Base(DeclarativeBase):
    pass


metadata_column_type = JSONB


class Documents(Base):
    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column("document_id", primary_key=True, autoincrement=True)
    
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
    
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type, default = dict)
    
    chunks: Mapped[list["Chunks"]] = relationship("Chunks", back_populates="document", cascade="all, delete-orphan")


class Chunks(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.document_id"))
    content: Mapped[str] = mapped_column(Text)
    
    embedding: Mapped[list[float]] = mapped_column(VECTOR(MODEL_VECTOR_SIZE))
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type, default = dict)
    
    document: Mapped["Documents"] = relationship("Documents", back_populates="chunks")


def init_db():
    with ENGINE.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=connection)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database Initialized")