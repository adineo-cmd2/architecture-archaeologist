from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.codebase import Codebase
from app.models.source_file import SourceFile
from app.models.user import User
from app.services import codebase_qa


class AskIn(BaseModel):
    question: str = ""


router = APIRouter()


def _own(db: Session, user: User, cid: int) -> Codebase:
    c = db.query(Codebase).filter(Codebase.id == cid, Codebase.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Codebase not found")
    return c


@router.post("/{cid}/ask")
def ask(cid: int, body: AskIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, cid)
    q = (body.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question required")
    rows = db.query(SourceFile).filter(SourceFile.codebase_id == cid).all()
    files = [{"path": r.path, "content": r.content or "", "embedding": r.embedding} for r in rows]
    return codebase_qa.answer(q, files)
