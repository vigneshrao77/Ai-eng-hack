import os
from pathlib import Path
from typing import Dict, List, Any

LANGUAGE_EXTENSIONS = {
    ".java": "Java",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".cs": "C#",
    ".sql": "SQL",
    ".xml": "XML",
    ".properties": "Config",
    ".yml": "YAML",
    ".yaml": "YAML",
}


def scan_repository(repo_path: str) -> Dict[str, Any]:
    """Scan repository path, inventory files, detect languages, count LOC."""
    root = Path(repo_path)
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    files_by_lang: Dict[str, List[Dict[str, Any]]] = {}
    total_loc = 0
    language_loc: Dict[str, int] = {}
    all_files: List[Dict[str, Any]] = []

    for path in root.rglob("*"):
        if path.is_file():
            # Skip VCS and cache folders
            parts = path.parts
            if any(p in (".git", ".svn", "node_modules", ".venv", "target", "bin", "obj", "__pycache__") for p in parts):
                continue

            ext = path.suffix.lower()
            lang = LANGUAGE_EXTENSIONS.get(ext, "Other")

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    loc = len(lines)
            except Exception:
                loc = 0

            file_info = {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "full_path": str(path),
                "extension": ext,
                "language": lang,
                "loc": loc,
            }

            all_files.append(file_info)
            total_loc += loc
            language_loc[lang] = language_loc.get(lang, 0) + loc

            if lang not in files_by_lang:
                files_by_lang[lang] = []
            files_by_lang[lang].append(file_info)

    return {
        "root_path": str(root),
        "total_files": len(all_files),
        "total_loc": total_loc,
        "language_loc": language_loc,
        "files": all_files,
    }
