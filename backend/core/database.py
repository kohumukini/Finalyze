import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, func, create_engine, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from pgvector import Vector
from dotenv import load_dotenv
from .config import MODEL_VECTOR_SIZE

load_dotenv(dotenv_path=Path(__file__).resolve.parent.parent.parent.env)

USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASS")
DB = os.getenv("POSTGRES_DB")
PORT = os.getenv("POSTGRES_PORT")

if os.getenv("IS_DOCKER"): 
    HOST = "db"
else: 
    HOST = "localhost"

URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
ENGINE = create_engine(URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = ENGINE)

class Base(DeclarativeBase): 
    pass

class Documents(Base): 
    __tablename__ = "documents"
    
    document_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    timestamp: Mapped[datetime] = mapped_column(default = func.now())
    content: Mapped[str] = mapped_column(Text, nullable = False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable = False)
    
class Chunks(Base): 
    __tablename__ = "document_chunks"
    
    chunk_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    vector: Mapped[list[float]] = mapped_column(Vector(MODEL_VECTOR_SIZE))
    metadata: Mapped[dict] = mapped_column(JSONB)
    
    
def init_db(): 
    Base.metadata.create_all(bind = ENGINE)
    
def get_db_session(): 
    db = SessionLocal()
    
    try: 
        yield db
    finally: 
        db.close()
        
if __name__ == "__main__": 
    init_db()
    print("Database Initialized")