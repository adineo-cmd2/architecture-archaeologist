import os
import shutil
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.analysis_report import AnalysisReport
from app.models.codebase import Codebase
from app.models.drift_record import DriftRecord
from app.models.source_file import SourceFile
from app.models.user import User
from app.schemas.codebase import GithubIn
from app.services import ingestion_pipeline as ingest
from app.services.code_analyser import analyse_file, should_skip
from app.services.embedder import embed

router = APIRouter()

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_FILES = 2000
SKIP_DIR_NAMES = {"venv", ".venv", "node_modules", ".git", "__pycache__"}


def _own(db: Session, user: User, cid: int) -> Codebase:
    c = db.query(Codebase).filter(Codebase.id == cid, Codebase.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Codebase not found")
    return c


def _storage_path(codebase_id: int) -> str:
    backend_dir = Path(__file__).resolve().parents[3]
    return os.path.join(str(backend_dir), "storage", str(codebase_id))


def _skipped(rel: str) -> bool:
    parts = str(rel).replace("\\", "/").split("/")
    for p in parts:
        if p in SKIP_DIR_NAMES:
            return True
        if p.startswith(".") and p not in (".", ".."):
            return True
    if should_skip(rel):
        return True
    return False


@router.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = await file.read()
    name = file.filename or "upload.zip"
    try:
        import io as _io
        with zipfile.ZipFile(_io.BytesIO(data)) as zf:
            bad = zf.testzip()
    except (zipfile.BadZipFile, ValueError, RuntimeError):
        raise HTTPException(status_code=400, detail="Invalid zip")
    c = Codebase(user_id=user.id, name=name, source="upload")
    db.add(c)
    db.commit()
    db.refresh(c)
    try:
        count = ingest.ingest_zip(db, c.id, data)
    except (zipfile.BadZipFile, ValueError, RuntimeError):
        db.query(SourceFile).filter(SourceFile.codebase_id == c.id).delete()
        db.query(Codebase).filter(Codebase.id == c.id).delete()
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid zip")
    return {"codebase_id": c.id, "files": count}


@router.post("/github")
def github(body: GithubIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    url = (body.url or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    name = url.rstrip("/").split("/")[-1] or url
    c = Codebase(user_id=user.id, name=name[:255], source=url)
    db.add(c)
    db.commit()
    db.refresh(c)
    storage = _storage_path(c.id)
    # Ensure clean dest for git clone (clone requires non-existing or empty dir).
    if os.path.exists(storage):
        shutil.rmtree(storage, ignore_errors=True)
    try:
        ingest.clone_repo(url, storage)
    except Exception as e:
        db.query(Codebase).filter(Codebase.id == c.id).delete()
        db.commit()
        shutil.rmtree(storage, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Clone failed: {str(e)[:300]}")
    count = 0
    for root, dirs, files in os.walk(storage):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES and not d.startswith(".")]
        for fn in files:
            if count >= MAX_FILES:
                break
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, storage)
            if _skipped(rel):
                continue
            try:
                if os.path.getsize(full) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
            except OSError:
                continue
            if "\x00" in content:
                continue
            analysed = analyse_file(rel, content)
            db.add(SourceFile(codebase_id=c.id, path=rel, language=analysed["language"], content=content, embedding=embed(content[:4000])))
            count += 1
    db.commit()
    return {"codebase_id": c.id, "files": count}


@router.get("", include_in_schema=False)
def list_root_noslash(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _list(db, user)


@router.get("/")
def _list_slash(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _list(db, user)


def _list(db: Session, user: User):
    out = []
    for c in db.query(Codebase).filter(Codebase.user_id == user.id).order_by(Codebase.id).all():
        files = db.query(SourceFile).filter(SourceFile.codebase_id == c.id).count()
        analysed = db.query(AnalysisReport).filter(AnalysisReport.codebase_id == c.id).count() > 0
        out.append({"id": c.id, "name": c.name, "source": c.source, "files": files, "analysed": analysed})
    return out


@router.delete("/{cid}")
def delete(cid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = _own(db, user, cid)
    db.query(SourceFile).filter(SourceFile.codebase_id == c.id).delete(synchronize_session=False)
    db.query(DriftRecord).filter(DriftRecord.codebase_id == c.id).delete(synchronize_session=False)
    db.query(AnalysisReport).filter(AnalysisReport.codebase_id == c.id).delete(synchronize_session=False)
    db.query(Codebase).filter(Codebase.id == c.id).delete(synchronize_session=False)
    db.commit()
    shutil.rmtree(_storage_path(cid), ignore_errors=True)
    # Also remove legacy double-nested path backend/backend/storage/{id} if present
    try:
        backend_dir = Path(__file__).resolve().parents[3]
        legacy = os.path.join(str(backend_dir), "backend", "storage", str(cid))
        shutil.rmtree(legacy, ignore_errors=True)
    except Exception:
        pass
    return {"deleted": cid}
