import re
from pathlib import Path
from typing import Dict, List, Any

CLASS_PATTERN = re.compile(r"(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+)?(class|interface)\s+([A-Za-z0-9_]+)")
PACKAGE_PATTERN = re.compile(r"package\s+([a-zA-Z0-9_\.]+);")
ANNOTATION_PATTERN = re.compile(r"@([A-Za-z0-9_]+)(?:\([^\)]*\))?")
METHOD_PATTERN = re.compile(r"(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+([a-zA-Z0-9_]+)\s*\(([^\)]*)\)\s*\{")
CALL_PATTERN = re.compile(r"([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s*\(")
SQL_PATTERN = re.compile(r"(?i)(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([A-Za-z0-9_]+)")


def estimate_cyclomatic_complexity(code: str) -> int:
    """Deterministic cyclomatic complexity based on branching keywords."""
    branches = len(re.findall(r"\b(if|else\s+if|for|while|case|catch|\&\&|\|\|)\b", code))
    return 1 + branches


def parse_java_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.splitlines()
    loc = len(lines)

    pkg_match = PACKAGE_PATTERN.search(content)
    package_name = pkg_match.group(1) if pkg_match else ""

    class_match = CLASS_PATTERN.search(content)
    class_name = class_match.group(2) if class_match else Path(file_path).stem
    is_interface = (class_match.group(1) == "interface") if class_match else False

    fqn = f"{package_name}.{class_name}" if package_name else class_name

    annotations = list(set(ANNOTATION_PATTERN.findall(content)))

    # Detect methods
    methods = []
    for line_idx, line in enumerate(lines, 1):
        m_match = METHOD_PATTERN.search(line)
        if m_match and not any(kw in line for kw in ("if", "while", "for", "switch", "catch")):
            m_name = m_match.group(1)
            params = m_match.group(2)
            methods.append({
                "name": m_name,
                "params": params,
                "line_number": line_idx,
                "class_fqn": fqn,
                "fqn": f"{fqn}.{m_name}",
            })

    # Detect method calls
    calls = []
    for match in CALL_PATTERN.finditer(content):
        target_obj, target_method = match.group(1), match.group(2)
        if target_obj not in ("this", "super", "logger", "System", "String", "Math"):
            calls.append({"target_object": target_obj, "target_method": target_method})

    # Detect table operations
    table_ops = []
    for match in SQL_PATTERN.finditer(content):
        op, table = match.group(1).upper(), match.group(2).upper()
        table_ops.append({"operation": "WRITE" if "INSERT" in op or "UPDATE" in op or "DELETE" in op else "READ", "table": table})

    # Detect local filesystem usage
    has_local_fs = bool(
        re.search(r'new\s+File\s*\(\s*["\']([A-Za-z]:|/|\\\\)', content)
        or ("new File(" in content and ("C:" in content or "instrument" in content))
    )
    # Detect local timestamps
    has_local_timestamp = bool(re.search(r'\bnew\s+Date\(\)|\bSystem\.currentTimeMillis\(\)', content))

    return {
        "file_path": file_path,
        "package": package_name,
        "class_name": class_name,
        "fqn": fqn,
        "is_interface": is_interface,
        "loc": loc,
        "complexity": estimate_cyclomatic_complexity(content),
        "annotations": annotations,
        "methods": methods,
        "calls": calls,
        "table_operations": table_ops,
        "has_local_fs": has_local_fs,
        "has_local_timestamp": has_local_timestamp,
    }
