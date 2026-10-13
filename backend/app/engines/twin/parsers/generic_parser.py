import re
from pathlib import Path
from typing import Dict, List, Any

JS_CLASS_PATTERN = re.compile(r"(?:export\s+)?(?:default\s+)?class\s+([A-Za-z0-9_]+)")
JS_FUNC_PATTERN = re.compile(r"(?:export\s+)?(?:default\s+)?(?:function|const|let)\s+([A-Za-z0-9_]+)\s*(?:=\s*(?:async\s*)?\([^)]*\)\s*=>|\()")
JS_IMPORT_PATTERN = re.compile(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]")
SQL_PATTERN = re.compile(r"(?i)(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([A-Za-z0-9_]+)")


def parse_generic_code_file(file_path: str, extension: str, language: str) -> List[Dict[str, Any]]:
    """
    Parse JavaScript, TypeScript, or other programming files.
    Extracts detected classes/components or creates a file-level architectural module.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []

    lines = content.splitlines()
    loc = len(lines)
    stem = Path(file_path).stem

    # Table detections
    table_ops = []
    for match in SQL_PATTERN.finditer(content):
        op, tbl = match.group(1).upper(), match.group(2).upper()
        rel_op = "WRITE" if "INSERT" in op or "UPDATE" in op or "DELETE" in op else "READ"
        table_ops.append({"table": tbl, "operation": rel_op})

    # Local fs and timestamps
    has_local_fs = bool(re.search(r"\b(fs\.|readFile|writeFile|path\.|File|FileInputStream)\b", content))
    has_local_timestamp = bool(re.search(r"\b(Date\.now|new Date|DateTime\.Now)\b", content))

    # Detect imports/calls
    calls = []
    for match in JS_IMPORT_PATTERN.finditer(content):
        mod = match.group(1).split("/")[-1].replace(".js", "").replace(".ts", "")
        calls.append({"target_object": mod, "target_method": "import"})

    # Classes or top-level functions
    classes_found = []
    for match in JS_CLASS_PATTERN.finditer(content):
        cname = match.group(1)
        classes_found.append({
            "file_path": file_path,
            "class_name": cname,
            "package": stem,
            "fqn": f"{stem}.{cname}",
            "is_interface": False,
            "loc": max(1, loc // 2),
            "complexity": max(1, content.count("if ") + content.count("for ")),
            "annotations": [language],
            "methods": [],
            "calls": calls,
            "table_operations": table_ops,
            "has_local_timestamp": has_local_timestamp,
            "has_local_fs": has_local_fs,
        })

    if not classes_found:
        # File module
        classes_found.append({
            "file_path": file_path,
            "class_name": stem,
            "package": Path(file_path).parent.name or "src",
            "fqn": f"{Path(file_path).parent.name}.{stem}",
            "is_interface": False,
            "loc": loc,
            "complexity": max(1, content.count("if ") + content.count("switch") + 1),
            "annotations": [language],
            "methods": [],
            "calls": calls,
            "table_operations": table_ops,
            "has_local_timestamp": has_local_timestamp,
            "has_local_fs": has_local_fs,
        })

    return classes_found
