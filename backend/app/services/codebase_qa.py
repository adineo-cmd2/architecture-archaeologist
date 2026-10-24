"""Grounded Q&A over retrieved code chunks (hash-embed + keyword overlap)."""

import os
import re

from app.services.embedder import cosine, embed

_TOKEN_RE = re.compile(r"[a-z0-9']+", re.IGNORECASE)


def _keyword_overlap(question: str, content: str) -> float:
    q = set(_TOKEN_RE.findall((question or "").lower()))
    c = set(_TOKEN_RE.findall((content or "").lower()))
    if not q:
        return 0.0
    return len(q & c) / max(len(q), 1)


def _try_llm(question: str, refs: list[dict]) -> str | None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        return None
    return None  # hook: LLM call would go here when keys are configured


def answer(question: str, files: list[dict]) -> dict:
    q_emb = embed(question or "")
    scored = []
    for f in files or []:
        emb = f.get("embedding") or embed((f.get("content") or "")[:4000])
        score = cosine(q_emb, emb) + 0.2 * _keyword_overlap(question, f.get("content", ""))
        scored.append((score, f))
    scored.sort(key=lambda t: t[0], reverse=True)
    top = [(s, f) for s, f in scored[:3] if s > 0]
    if not top and scored:
        top = scored[:1]
    refs = [{"path": f.get("path", ""),
             "snippet": (f.get("content", "")[:500])} for _, f in top]
    llm = _try_llm(question, refs)
    if llm:
        return {"answer": llm, "refs": refs}
    if not refs:
        return {"answer": "No code files available to answer the question.", "refs": []}
    parts = [f"The most relevant file is {refs[0]['path']}."]
    for r in refs:
        preview = r["snippet"].splitlines()[0][:120] if r["snippet"].splitlines() else ""
        parts.append(f"{r['path']} shows: {preview!r} (...)".rstrip())
    return {"answer": f"Based on {len(refs)} retrieved file(s). " + " ".join(parts),
            "refs": refs}
