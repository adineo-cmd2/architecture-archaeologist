"""Drift scoring: 0.4*emergency_rate + 0.35*complexity_norm + 0.25*violations."""


def score_file(path: str, complexity: int, emergency_count: int,
               total_commits: int, violations: int) -> dict:
    emergency_rate = (emergency_count / total_commits) if total_commits > 0 else 0.0
    complexity_norm = min((complexity or 0) / 20.0, 1.0)
    viol_norm = min(violations or 0, 1)
    score = round(0.4 * emergency_rate + 0.35 * complexity_norm + 0.25 * viol_norm, 3)
    score = max(0.0, min(1.0, score))
    reasons: list[str] = []
    if emergency_count and total_commits:
        reasons.append(
            f"emergency_rate={emergency_rate:.2f} ({emergency_count}/{total_commits} commits)"
        )
    if complexity_norm > 0:
        reasons.append(
            f"complexity_norm={complexity_norm:.2f} (complexity {complexity})"
        )
    if viol_norm > 0:
        reasons.append(f"violations={violations} (layer boundary crossing)")
    if not reasons:
        reasons.append("clean: no emergency commits, low complexity, no violations")
    return {"path": path, "score": score, "reasons": reasons}


def detect_violations(imports_by_file: dict, layers: dict) -> int:
    """Return 1 if a models-file imports views-ish code, else 0."""
    for path, imports in (imports_by_file or {}).items():
        if "model" not in path.lower():
            continue
        for imp in imports or []:
            low = str(imp).lower()
            if "view" in low or "route" in low or "controller" in low:
                return 1
    return 0
