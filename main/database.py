import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    engine_url = DATABASE_URL
    logger.info("Using DATABASE_URL from environment.")
else:
    db_path = Path(__file__).parent / "resources" / "movies.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine_url = f"sqlite:///{db_path.as_posix()}"
    logger.info(f"DATABASE_URL not set — falling back to SQLite at {db_path}")

engine = create_engine(
    engine_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()