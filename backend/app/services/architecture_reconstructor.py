"""Heuristic architecture pattern inference from directory signals."""


def _dir_set(tree: dict) -> set[str]:
    dirs = tree.get("dirs", []) if tree else []
    out: set[str] = set()
    for d in dirs:
        part = str(d).replace("\\", "/").strip("/").lower()
        if not part:
            continue
        out.add(part)
        out.add(part.split("/")[-1])
        out.add(part.split("/")[0])
    files = tree.get("files", []) if tree else []
    for f in files:
        f = str(f).replace("\\", "/").lower()
        if "/" in f:
            out.add(f.split("/")[0])
    return out


def infer(tree: dict, imports_by_file: dict) -> dict:
    dirs = _dir_set(tree)
    files = [str(f).lower() for f in (tree.get("files", []) if tree else [])]
    has = lambda *names: any(n in dirs for n in names)

    scores: dict[str, float] = {}
    # MVC: models + views + (controllers|routes), +2 each present
    scores["mvc"] = (2 if has("models") else 0) + (2 if has("views") else 0) \
        + (2 if (has("controllers") or has("routes")) else 0)
    # Layered: api|services|db|models count
    scores["layered"] = sum(1 for n in ("api", "services", "db", "models") if has(n))
    # Hexagonal: ports|adapters|domain count
    scores["hexagonal"] = sum(1 for n in ("ports", "adapters", "domain") if has(n))
    # Event-driven: events|handlers|bus|queue count
    scores["event-driven"] = sum(1 for n in ("events", "handlers", "bus", "queue") if has(n))
    # Microservices: services dir with 2+ subdirs or docker-compose + >1 top service dir
    micro = 0
    if has("services"):
        subdirs = {d for d in dirs if d.startswith("services/") or d.startswith("services\\")}
        # tree dirs may be flat names; also count files under services/
        svc_subs = set()
        for f in files:
            if f.startswith("services/"):
                parts = f.split("/")
                if len(parts) > 2:
                    svc_subs.add(parts[1])
        if len(subdirs) >= 2 or len(svc_subs) >= 2:
            micro = 5
        else:
            has_compose = any("docker-compose" in f for f in files)
            top_dirs = {f.split("/")[0] for f in files if "/" in f}
            top_dirs |= {d.split("/")[0] for d in dirs if "/" in d}
            if has_compose and len(top_dirs) > 2:
                micro = 5
    scores["microservices"] = micro
    # Frontend-SPA: components+pages | src+public (+2 each present, cap 4)
    spa = 0
    if has("components"):
        spa += 2
    if has("pages"):
        spa += 2
    if spa == 0:
        if has("src"):
            spa += 1
        if has("public"):
            spa += 1
    scores["frontend-spa"] = spa

    best = max(scores.values()) if scores else 0
    winners = [k for k, v in scores.items() if v == best]
    pattern = winners[0] if len(winners) == 1 else "layered"
    if best == 0:
        pattern = "layered"

    key_dirs = sorted(d for d in ("models", "views", "controllers", "routes", "api",
                                  "services", "db", "ports", "adapters", "domain",
                                  "events", "handlers", "bus", "queue",
                                  "components", "pages", "src", "public") if has(d))
    dirs_txt = ", ".join(key_dirs) if key_dirs else "a flat module layout"
    intent = (
        f"This codebase follows a {pattern} architecture. "
        f"Key directories include {dirs_txt}. "
        f"The original intent appears to separate concerns along {dirs_txt}, "
        f"with the dominant signals pointing to {pattern}."
    )

    signal_rationale = {
        "models": "domain models directory signals data layer",
        "views": "views directory signals presentation layer",
        "controllers": "controllers directory signals MVC control flow",
        "routes": "routes directory signals request routing layer",
        "api": "api directory signals boundary/layered service",
        "services": "services directory signals business-logic layer",
        "db": "db directory signals persistence layer",
        "ports": "ports directory signals hexagonal boundary",
        "adapters": "adapters directory signals hexagonal adapters",
        "domain": "domain directory signals hexagonal core",
        "events": "events directory signals event-driven design",
        "handlers": "handlers directory signals event handling",
        "bus": "bus module signals message bus",
        "queue": "queue module signals async messaging",
        "components": "components directory signals frontend SPA",
        "pages": "pages directory signals frontend routing",
        "src": "src layout signals frontend project",
        "public": "public assets signal frontend SPA",
    }
    decisions = [{"choice": d, "rationale": signal_rationale[d]}
                 for d in key_dirs[:5]]
    return {"pattern": pattern, "scores": scores, "intent": intent, "decisions": decisions}
