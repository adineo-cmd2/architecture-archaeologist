"""Zip ingestion + git clone + shared hash-embed helpers."""

import io
import os
import subprocess
import zipfile

from app.services.code_analyser import analyse_file, should_skip
from app.services.embedder import cosine, embed  # noqa: F401  (shared like P2)

__all__ = ["embed", "cosine", "ingest_zip", "clone_repo"]

MAX_FILES = 2000
MAX_FILE_BYTES = 5 * 1024 * 1024

SKIP_DIR_NAMES = {"venv", ".venv", "node_modules", ".git", "__pycache__"}


def _skipped(name: str) -> bool:
    parts = str(name).replace("\\", "/").split("/")
    for p in parts:
        if p in SKIP_DIR_NAMES:
            return True
        if p.startswith(".") and p not in (".", ".."):
            return True
    if should_skip(name):
        return True
    return False


def _storage_dir(codebase_id: int) -> str:
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "storage", str(codebase_id))
    # app/services -> app -> backend, so storage = backend/storage/{id}
    base = os.path.abspath(base)
    os.makedirs(base, exist_ok=True)
    return base


def ingest_zip(db, codebase_id: int, zip_bytes: bytes) -> int:
    from app.models.source_file import SourceFile

    count = 0
    storage = _storage_dir(codebase_id)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            if count >= MAX_FILES:
                break
            name = info.filename
            if not name or name.endswith("/") or info.is_dir():
                continue
            if _skipped(name):
                continue
            if info.file_size > MAX_FILE_BYTES:
                continue
            try:
                raw = zf.read(info.filename)
            except (KeyError, RuntimeError, zipfile.BadZipFile):
                continue
            try:
                content = raw.decode("utf-8", errors="replace")
            except Exception:
                continue
            if "\x00" in content:
                continue
            analysed = analyse_file(name, content)
            rel = name.lstrip("/")
            dest = os.path.abspath(os.path.join(storage, rel))
            if not dest.startswith(storage):
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", errors="replace") as fh:
                fh.write(content)
            db.add(SourceFile(codebase_id=codebase_id, path=rel,
                              language=analysed["language"],
                              content=content,
                              embedding=embed(content[:4000])))
            count += 1
    db.commit()
    return count


def clone_repo(url: str, dest: str) -> str:
    proc = subprocess.run(
        ["git", "clone", "--depth", "1", url, dest],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git clone failed: {(proc.stderr or '').strip()[:500]}")
    return dest
