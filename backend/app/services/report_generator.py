"""Markdown report + Mermaid diagram generation."""


def _effort(score: float) -> str:
    if score < 0.4:
        return "low"
    if score < 0.7:
        return "medium"
    return "high"


def mermaid_text(modules: list[dict]) -> str:
    mods = (modules or [])[:8]
    lines = ["graph TD"]
    ids = []
    for i, m in enumerate(mods):
        node_id = chr(ord("A") + i)
        ids.append(node_id)
        name = str(m.get("name", f"mod{i}")).replace('"', "'")
        lines.append(f'  {node_id}["{name} ({m.get("files", 0)} files)"]')
    for i in range(len(ids) - 1):
        lines.append(f"  {ids[i]}-->{ids[i + 1]}")
    if not mods:
        lines.append('  A["empty"]')
    return "\n".join(lines)


def generate(pattern: str, intent: str, decisions: list[dict],
             drift_top: list[dict], mermaid: str) -> str:
    lines = ["# Architecture Archaeology Report", "",
             "## Executive summary", "",
             f"Detected pattern: **{pattern}**.", "",
             intent or "", ""]
    lines += ["## Original architecture", "", "```mermaid",
              mermaid or "graph TD", "```", ""]
    if decisions:
        lines += ["### Key decisions", ""]
        for d in decisions:
            if isinstance(d, dict):
                lines.append(f"- **{d.get('choice')}**: {d.get('rationale')}")
            else:
                lines.append(f"- {d}")
        lines.append("")
    lines += ["## Drift zones", "",
              "| File | Score | Reasons |",
              "| ---- | ----- | ------- |"]
    for d in (drift_top or []):
        reasons = "; ".join(d.get("reasons", []))
        lines.append(f"| {d.get('path')} | {d.get('score')} | {reasons} |")
    if not (drift_top or []):
        lines.append("| (none) | 0 | clean |")
    lines += ["", "## Modernisation priorities", ""]
    for d in (drift_top or [])[:3]:
        lines.append(f"- **{d.get('path')}** (score {d.get('score')}, "
                     f"effort: {_effort(float(d.get('score', 0)))}) — "
                     f"{'; '.join(d.get('reasons', []))}")
    if not (drift_top or []):
        lines.append("- No drift hotspots detected.")
    lines += ["",
              "_Drift = 0.4*emergency_rate + 0.35*complexity_norm + 0.25*violations._",
              ""]
    return "\n".join(lines)
