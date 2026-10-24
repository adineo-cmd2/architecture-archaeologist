"""Git history scan for emergency keywords mapped to files."""

import re
import subprocess

EMERGENCY_RE = re.compile(
    r"\b(fix|hack|workaround|temp|todo|hotfix|quick)\b", re.IGNORECASE
)


def analyse(repo_dir: str) -> dict:
    try:
        proc = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:COMMIT:%H:%s"],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {"emergency_by_file": {}, "total_commits": 0, "has_git": False}
    if proc.returncode != 0:
        return {"emergency_by_file": {}, "total_commits": 0, "has_git": False}
    emergency_by_file: dict[str, int] = {}
    total_commits = 0
    current_emergency = False
    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("COMMIT:"):
            total_commits += 1
            msg = line[len("COMMIT:"):]
            # strip hash prefix "COMMIT:<sha>:<subject>"
            parts = msg.split(":", 1)
            subject = parts[1] if len(parts) > 1 else parts[0]
            current_emergency = bool(EMERGENCY_RE.search(subject.lower()))
        elif line == "":
            continue
        elif current_emergency and line:
            emergency_by_file[line] = emergency_by_file.get(line, 0) + 1
    return {"emergency_by_file": emergency_by_file,
            "total_commits": total_commits, "has_git": True}
