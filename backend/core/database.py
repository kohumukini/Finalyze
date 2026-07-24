import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, Text, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

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

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASS", "postgres")
DB = os.getenv("POSTGRES_DB", "finalyze")
PORT = os.getenv("POSTGRES_PORT", "5432")
HOST = "db" if os.getenv("IS_DOCKER") else "localhost"
POSTGRES_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
SQLITE_URL = "sqlite:///./finalyze.db"

try:
    ENGINE = create_engine(POSTGRES_URL)
except Exception:
    ENGINE = create_engine(SQLITE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


class Base(DeclarativeBase):
    pass


metadata_column_type = JSONB if ENGINE.dialect.name == "postgresql" else JSON
vector_column_type = Vector(MODEL_VECTOR_SIZE) if ENGINE.dialect.name == "postgresql" else Text


class Documents(Base):
    __tablename__ = "documents"

    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(default=func.now())
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type, nullable=False)


class Chunks(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vector: Mapped[list[float]] = mapped_column(vector_column_type)
    metadata_: Mapped[dict] = mapped_column("metadata", metadata_column_type)


def init_db():
    Base.metadata.create_all(bind=ENGINE)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database Initialized")