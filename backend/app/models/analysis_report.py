from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    codebase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("codebases.id"), unique=True, index=True
    )
    pattern: Mapped[str] = mapped_column(String(100), default="")
    intent: Mapped[str] = mapped_column(Text, default="")
    decisions: Mapped[list] = mapped_column(JSON, default=list)
    mermaid: Mapped[str] = mapped_column(Text, default="")
