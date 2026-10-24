"""Hash-based 128-dim embeddings with L2 normalisation + cosine (P2 pattern)."""

import hashlib
import math
import re

DIM = 128

_TOKEN_RE = re.compile(r"[a-z0-9']+", re.IGNORECASE)


def embed(text: str) -> list[float]:
    vec = [0.0] * DIM
    if not text or not text.strip():
        return vec
    for token in _TOKEN_RE.findall(text.lower()):
        digest = hashlib.md5(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "little") % DIM
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)
