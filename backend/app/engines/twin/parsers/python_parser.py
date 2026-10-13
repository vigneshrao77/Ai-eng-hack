import ast
import re
from pathlib import Path
from typing import Dict, List, Any

SQL_PATTERN = re.compile(r"(?i)(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+([A-Za-z0-9_]+)")


def estimate_python_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def parse_python_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a Python source file, extracting classes or top-level module components."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []

    lines = content.splitlines()
    loc = len(lines)
    rel_stem = Path(file_path).stem

    try:
        tree = ast.parse(content, filename=file_path)
    except Exception:
        # Fallback if syntax error
        return [{
            "file_path": file_path,
            "class_name": rel_stem,
            "package": Path(file_path).parent.name or "app",
            "fqn": f"{Path(file_path).parent.name}.{rel_stem}",
            "is_interface": False,
            "loc": loc,
            "complexity": max(1, loc // 20),
            "annotations": ["PythonModule"],
            "methods": [],
            "calls": [],
            "table_operations": [],
            "has_local_timestamp": "datetime" in content or "time.time" in content,
            "has_local_fs": "open(" in content or "os.path" in content,
        }]

    # Detect imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    # Detect SQL tables in code
    table_ops = []
    for match in SQL_PATTERN.finditer(content):
        op, tbl = match.group(1).upper(), match.group(2).upper()
        rel_op = "WRITE" if "INSERT" in op or "UPDATE" in op or "DELETE" in op else "READ"
        table_ops.append({"table": tbl, "operation": rel_op})

    has_local_fs = bool(re.search(r"\b(open|read_text|write_text|Path|os\.path|shutil)\b", content))
    has_local_timestamp = bool(re.search(r"\b(datetime\.now|time\.time|timezone\.utc)\b", content))

    classes_found = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            c_name = node.name
            c_methods = [
                {"name": n.name, "params": "", "line_number": n.lineno, "class_fqn": f"{rel_stem}.{c_name}"}
                for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            c_loc = len([ln for ln in lines[node.lineno - 1 : getattr(node, "end_lineno", node.lineno)]])

            # Calls
            calls = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and isinstance(child.func.value, ast.Name):
                        calls.append({"target_object": child.func.value.id, "target_method": child.func.attr})
                    elif isinstance(child.func, ast.Name):
                        calls.append({"target_object": child.func.id, "target_method": "call"})

            classes_found.append({
                "file_path": file_path,
                "class_name": c_name,
                "package": rel_stem,
                "fqn": f"{rel_stem}.{c_name}",
                "is_interface": any("abc" in getattr(b, "id", "") for b in node.bases if hasattr(b, "id")),
                "loc": max(1, c_loc),
                "complexity": estimate_python_complexity(node),
                "annotations": [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                "methods": c_methods,
                "calls": calls,
                "table_operations": table_ops,
                "has_local_timestamp": has_local_timestamp,
                "has_local_fs": has_local_fs,
            })

    # If no classes defined, represent the file as a module component
    if not classes_found:
        mod_methods = [
            {"name": n.name, "params": "", "line_number": n.lineno, "class_fqn": f"{rel_stem}.{n.name}"}
            for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        calls = []
        for imp in imports:
            calls.append({"target_object": imp.split(".")[-1], "target_method": "import"})

        classes_found.append({
            "file_path": file_path,
            "class_name": rel_stem,
            "package": Path(file_path).parent.name or "root",
            "fqn": f"{Path(file_path).parent.name}.{rel_stem}",
            "is_interface": False,
            "loc": loc,
            "complexity": estimate_python_complexity(tree),
            "annotations": ["PythonModule"],
            "methods": mod_methods,
            "calls": calls,
            "table_operations": table_ops,
            "has_local_timestamp": has_local_timestamp,
            "has_local_fs": has_local_fs,
        })

    return classes_found
