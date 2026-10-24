from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.analysis_report import AnalysisReport
from app.models.codebase import Codebase
from app.models.drift_record import DriftRecord
from app.models.source_file import SourceFile
from app.models.user import User
from app.services.report_generator import generate

router = APIRouter()


def _own(db: Session, user: User, cid: int) -> Codebase:
    c = db.query(Codebase).filter(Codebase.id == cid, Codebase.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Codebase not found")
    return c


@router.get("/{cid}/drift")
def drift(cid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, cid)
    rows = db.query(DriftRecord).filter(DriftRecord.codebase_id == cid).order_by(DriftRecord.score.desc()).all()
    return [{"path": r.path, "score": r.score, "reasons": r.reasons or []} for r in rows]


@router.get("/{cid}/report")
def report(cid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, cid)
    rep = db.query(AnalysisReport).filter(AnalysisReport.codebase_id == cid).first()
    if not rep:
        raise HTTPException(status_code=404, detail="Report not found")
    rows = db.query(DriftRecord).filter(DriftRecord.codebase_id == cid).order_by(DriftRecord.score.desc()).all()
    drift_top = [{"path": r.path, "score": r.score, "reasons": r.reasons or []} for r in rows]
    markdown = generate(rep.pattern or "", rep.intent or "", rep.decisions or [], drift_top, rep.mermaid or "")
    return {"markdown": markdown, "mermaid": rep.mermaid or ""}


@router.get("/{cid}/files")
def files(cid: int, path: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, cid)
    if not path:
        rows = db.query(SourceFile).filter(SourceFile.codebase_id == cid).order_by(SourceFile.path).all()
        return {"tree": [r.path for r in rows]}
    f = db.query(SourceFile).filter(SourceFile.codebase_id == cid, SourceFile.path == path).first()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    d = db.query(DriftRecord).filter(DriftRecord.codebase_id == cid, DriftRecord.path == path).first()
    return {"path": f.path, "content": f.content or "", "drift": float(d.score) if d else 0.0, "language": f.language or ""}
