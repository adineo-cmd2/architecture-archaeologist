# AI Architecture Archaeologist — backend

Run from `backend/`:

```bash
pip install -r requirements.txt
cp .env.example .env   # optional; works with no keys (static analysis engine)
python3 -m uvicorn app.main:app --port 8007
```

Tests: `python3 -m pytest tests/ -v` (7 tests).
