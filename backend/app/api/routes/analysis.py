import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.analysis_report import AnalysisReport
from app.models.codebase import Codebase
from app.models.drift_record import DriftRecord
from app.models.source_file import SourceFile
from app.models.user import User
from app.services import architecture_reconstructor as recon
from app.services import git_analyser
from app.services.code_analyser import analyse_file
from app.services.drift_scorer import detect_violations, score_file
from app.services.report_generator import mermaid_text

router = APIRouter()


def _own(db: Session, user: User, cid: int) -> Codebase:
    c = db.query(Codebase).filter(Codebase.id == cid, Codebase.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Codebase not found")
    return c


def _storage_path(codebase_id: int) -> str:
    backend_dir = Path(__file__).resolve().parents[3]
    return os.path.join(str(backend_dir), "storage", str(codebase_id))


@router.post("/{cid}/analyse")
def analyse(cid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _own(db, user, cid)
    rows = db.query(SourceFile).filter(SourceFile.codebase_id == cid).all()
    imports_by_file: dict[str, list] = {}
    complexity_by_file: dict[str, int] = {}
    paths: list[str] = []
    for f in rows:
        info = analyse_file(f.path, f.content or "")
        imports_by_file[f.path] = info.get("imports", [])
        complexity_by_file[f.path] = int(info.get("complexity", 0) or 0)
        paths.append(f.path)
    dirs = sorted({os.path.dirname(p) for p in paths if "/" in p and os.path.dirname(p)})
    tree = {"dirs": dirs, "files": paths}
    inferred = recon.infer(tree, imports_by_file)
    pattern = inferred.get("pattern", "layered")
    intent = inferred.get("intent", "")
    decisions = inferred.get("decisions", [])

    storage = _storage_path(cid)
    git_info = git_analyser.analyse(storage) if os.path.isdir(storage) else {"emergency_by_file": {}, "total_commits": 0, "has_git": False}
    emergency_by_file = git_info.get("emergency_by_file", {})
    total_commits = int(git_info.get("total_commits", 0) or 0)
    violations = detect_violations(imports_by_file, {})

    scored = []
    for p in paths:
        em = int(emergency_by_file.get(p, 0) or 0)
        cx = int(complexity_by_file.get(p, 0) or 0)
        scored.append(score_file(p, cx, em, total_commits, violations))
    scored.sort(key=lambda d: d.get("score", 0), reverse=True)

    # Re-runnable: clear prior report + drift rows first.
    db.query(DriftRecord).filter(DriftRecord.codebase_id == cid).delete(synchronize_session=False)
    db.query(AnalysisReport).filter(AnalysisReport.codebase_id == cid).delete(synchronize_session=False)
    db.commit()

    # Top modules by files for mermaid.
    counts: dict[str, int] = {}
    for p in paths:
        top = p.split("/")[0] if "/" in p else "(root)"
        counts[top] = counts.get(top, 0) + 1
    modules = [{"name": k, "files": v} for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]
    mermaid = mermaid_text(modules)

    db.add(AnalysisReport(codebase_id=cid, pattern=pattern, intent=intent, decisions=decisions, mermaid=mermaid))
    for d in scored:
        db.add(DriftRecord(codebase_id=cid, path=d.get("path", ""), score=float(d.get("score", 0.0)), reasons=d.get("reasons", [])))
    db.commit()
    return {"pattern": pattern, "drift_zones": [d.get("path", "") for d in scored[:3]]}
