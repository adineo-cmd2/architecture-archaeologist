import io
import os
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app


def _run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


def _build_repo(base: str) -> str:
    repo = os.path.join(base, "repo")
    pkg = os.path.join(repo, "pkg")
    os.makedirs(pkg, exist_ok=True)
    with open(os.path.join(pkg, "models.py"), "w") as fh:
        fh.write(
            "from pkg.views import render\n\n"
            "def get_user(uid):\n"
            "    if uid:\n"
            "        for i in range(3):\n"
            "            if i == uid:\n"
            "                return render(str(i))\n"
            "    return None\n"
        )
    with open(os.path.join(pkg, "views.py"), "w") as fh:
        fh.write("def render(x):\n    return f\"<div>{x}</div>\"\n")
    _run(["git", "init"], cwd=repo)
    _run(["git", "config", "user.email", "t@t.t"], cwd=repo)
    _run(["git", "config", "user.name", "t"], cwd=repo)
    _run(["git", "add", "."], cwd=repo)
    _run(["git", "commit", "-m", "initial commit"], cwd=repo)
    with open(os.path.join(pkg, "views.py"), "a") as fh:
        fh.write("# tweak\n")
    _run(["git", "add", "."], cwd=repo)
    _run(["git", "commit", "-m", "quick hack fix for rendering"], cwd=repo)
    return repo


def _zip_pkg(repo: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(os.path.join(repo, "pkg")):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, repo)
                zf.write(full, rel)
    return buf.getvalue()


def test_api_smoke(tmp_path):
    c = TestClient(app)
    assert c.get("/healthz").json() == {"ok": True}
    repo = _build_repo(str(tmp_path))
    zb = _zip_pkg(repo)

    r = c.post("/api/codebase/upload", files={"file": ("code.zip", zb, "application/zip")})
    assert r.status_code == 200, r.text
    cid = r.json()["codebase_id"]
    assert r.json()["files"] >= 2

    r = c.post(f"/api/codebase/{cid}/analyse")
    assert r.status_code == 200, r.text
    assert r.json()["pattern"]

    r = c.get(f"/api/codebase/{cid}/drift")
    assert r.status_code == 200, r.text
    drift = r.json()
    if isinstance(drift, dict):
        drift = drift.get("drift") or drift.get("records") or []
    assert len(drift) >= 2
    assert all("path" in d and "score" in d and "reasons" in d for d in drift)

    r = c.get(f"/api/codebase/{cid}/report")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["markdown"] and body["mermaid"]
    assert "graph TD" in body["mermaid"]

    r = c.post(f"/api/codebase/{cid}/ask", json={"question": "What does models.py do?"})
    assert r.status_code == 200, r.text
    assert r.json()["answer"]
    assert r.json()["refs"]

    r = c.get(f"/api/codebase/{cid}/files")
    assert r.status_code == 200, r.text
    tree = r.json()
    paths = tree.get("tree") or tree.get("paths") or tree.get("files") or tree
    assert any("pkg/models.py" in p for p in paths)

    r = c.get(f"/api/codebase/{cid}/files", params={"path": "pkg/models.py"})
    assert r.status_code == 200, r.text
    assert "render" in r.json()["content"]
    assert r.json()["language"] == "python"

    r = c.get("/api/codebase")
    assert r.status_code == 200, r.text
    items = r.json() if isinstance(r.json(), list) else r.json().get("codebases", r.json())
    assert any(it["id"] == cid for it in items)

    r = c.delete(f"/api/codebase/{cid}")
    assert r.status_code == 200, r.text
