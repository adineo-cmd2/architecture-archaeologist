"""Static analysis: Python AST per .py file, extension census for others."""

import ast
import os

EXT_MAP = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "jsx": "javascript",
    "tsx": "typescript",
    "java": "java",
    "go": "go",
    "rb": "ruby",
    "php": "php",
    "cs": "csharp",
    "c": "c",
    "cpp": "cpp",
    "h": "c",
    "rs": "rust",
    "swift": "swift",
    "kt": "kotlin",
    "md": "markdown",
    "yml": "yaml",
    "yaml": "yaml",
    "toml": "toml",
    "json": "json",
    "html": "html",
    "css": "css",
}

SKIP_DIRS = {"venv", ".venv", "node_modules", ".git", "__pycache__"}


def should_skip(path: str) -> bool:
    parts = str(path).replace("\\", "/").split("/")
    for p in parts:
        if p.startswith(".") and p not in (".", ".."):
            # allow e.g. .py files themselves but skip hidden dirs/files
            # hidden = any path segment starting with '.' except the leaf ext
            return True
        if p in SKIP_DIRS:
            return True
    return False


def _language_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    return EXT_MAP.get(ext, "text")


def _complexity_of(tree: ast.AST) -> tuple[int, list[str], list[str]]:
    functions: list[str] = []
    classes: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    branch_types = (ast.If, ast.For, ast.AsyncFor, ast.While,
                    ast.ExceptHandler, ast.With, ast.AsyncWith)
    complexity = 0
    func_nodes = [n for n in ast.walk(tree)
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if func_nodes:
        for fn in func_nodes:
            count = 0
            for node in ast.walk(fn):
                if isinstance(node, branch_types):
                    count += 1
                elif isinstance(node, ast.BoolOp):
                    count += 1
            complexity += 1 + count
    else:
        for node in ast.walk(tree):
            if isinstance(node, branch_types):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += 1
    return complexity, functions, classes


def analyse_file(path: str, content: str) -> dict:
    language = _language_for(path)
    loc = len((content or "").splitlines())
    if path.lower().endswith(".py"):
        try:
            tree = ast.parse(content or "")
        except SyntaxError:
            return {"language": "python", "imports": [],
                    "defs": {"functions": [], "classes": []},
                    "complexity": 0, "loc": loc, "parse_error": True}
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        complexity, functions, classes = _complexity_of(tree)
        return {"language": "python", "imports": imports,
                "defs": {"functions": functions, "classes": classes},
                "complexity": complexity, "loc": loc, "parse_error": False}
    return {"language": language, "imports": [],
            "defs": {"functions": [], "classes": []},
            "complexity": 0, "loc": loc, "parse_error": False}
