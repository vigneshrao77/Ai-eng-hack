import re
from pathlib import Path
from typing import Dict, List, Any
from app.core.logging import mask_secrets


def parse_properties_file(file_path: str) -> List[Dict[str, Any]]:
    items = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
            elif ":" in line:
                k, v = line.split(":", 1)
            else:
                continue

            key = k.strip()
            val = v.strip()

            kind = "property"
            if "password" in key.lower() or "secret" in key.lower():
                kind = "secret"
            elif "url" in key.lower() or "host" in key.lower():
                kind = "host"
            elif "path" in key.lower() or "directory" in key.lower() or ":\\" in val or "/var" in val:
                kind = "path"

            items.append({
                "key": key,
                "value_masked": "[REDACTED]" if kind == "secret" else val,
                "is_secret": (kind == "secret"),
                "raw_value": val,
                "kind": kind,
                "line_number": line_num,
                "file_path": file_path,
            })
    return items
