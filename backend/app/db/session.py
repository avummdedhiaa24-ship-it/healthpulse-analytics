import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

# SQLite fix (for now)
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
