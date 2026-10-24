from typing import Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    codebase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("codebases.id"), index=True
    )
    path: Mapped[str] = mapped_column(String(1024), default="")
    language: Mapped[str] = mapped_column(String(100), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=None)
