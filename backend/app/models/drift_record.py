from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DriftRecord(Base):
    __tablename__ = "drift_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    codebase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("codebases.id"), index=True
    )
    path: Mapped[str] = mapped_column(String(1024), default="")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
