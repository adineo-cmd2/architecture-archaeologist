from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()


def _resolve_database_url(url: str) -> str:
    if url.startswith("sqlite"):
        # sqlite:///./archaeologist.db, sqlite:///archaeologist.db -> backend-relative
        # sqlite:////abs/path.db, sqlite:///:memory: -> keep as-is
        prefix = "sqlite:///"
        if url.startswith(prefix):
            path_part = url[len(prefix):]
            if path_part not in (":memory:", "") and not path_part.startswith("/"):
                backend_dir = Path(__file__).resolve().parents[2]
                if path_part.startswith("./"):
                    abs_path = backend_dir / path_part[2:]
                else:
                    abs_path = backend_dir / path_part
                return f"sqlite:///{abs_path}"
    return url


DATABASE_URL = _resolve_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
