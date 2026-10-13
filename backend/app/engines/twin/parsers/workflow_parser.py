import json
from pathlib import Path
from typing import Dict, List, Any


def parse_workflow_json_file(file_path: str) -> Dict[str, Any]:
    """
    Parse workflow pipeline definitions (e.g. n8n, LangChain, Flowise, Zapier, JSON pipelines).
    Extracts individual component nodes and directional dataflow/dependency edges.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except Exception:
        return {"is_workflow": False}

    if not isinstance(data, dict):
        return {"is_workflow": False}

    # Check for workflow nodes structure (e.g. n8n format)
    raw_nodes = data.get("nodes")
    if not isinstance(raw_nodes, list) or len(raw_nodes) == 0:
        return {"is_workflow": False}

    parsed_nodes = []
    edges = []
    tables = set()

    node_id_to_name = {}
    for n in raw_nodes:
        if not isinstance(n, dict):
            continue
        nid = str(n.get("id") or n.get("name") or "")
        name = str(n.get("name") or nid)
        node_id_to_name[nid] = name
        node_id_to_name[name] = name

    for n in raw_nodes:
        if not isinstance(n, dict):
            continue
        raw_id = str(n.get("id") or n.get("name") or "")
        name = str(n.get("name") or raw_id)
        ntype = str(n.get("type") or "WorkflowNode")
        short_type = ntype.split(".")[-1] if "." in ntype else ntype
        params = n.get("parameters", {}) if isinstance(n.get("parameters"), dict) else {}

        # Detect table/database operations
        table_ops = []
        param_str = json.dumps(params).lower()
        if any(kw in param_str for kw in ("database", "table", "notion", "datastore")):
            tbl_name = "WORKFLOW_DATASTORE"
            tables.add(tbl_name)
            table_ops.append({"table": tbl_name, "operation": "WRITE" if "create" in name.lower() or "upload" in name.lower() else "READ"})

        # Detect local filesystem usage
        has_local_fs = any(kw in param_str for kw in ("file", "drive", "download", "upload", "path"))
        # Detect timestamp
        has_local_timestamp = any(kw in param_str for kw in ("timestamp", "now", "date", "time"))

        # GxP signal hints
        annotations = [short_type]
        if "agent" in name.lower() or "agent" in ntype.lower():
            annotations.append("AIAgent")
        if "model" in name.lower() or "gemini" in name.lower() or "chat" in name.lower():
            annotations.append("LLM")
        if "form" in name.lower() or "trigger" in name.lower():
            annotations.append("Trigger")

        loc = max(10, len(json.dumps(n, indent=2).splitlines()))
        complexity = max(1, len(params))

        parsed_nodes.append({
            "class_name": name,
            "name": name,
            "package": ntype.split(".")[0] if "." in ntype else "Workflow",
            "fqn": f"workflow.{name}",
            "is_interface": False,
            "loc": loc,
            "complexity": complexity,
            "annotations": annotations,
            "methods": [{"name": "execute", "params": "", "line_number": 1}],
            "calls": [],  # Will be populated from connections
            "table_operations": table_ops,
            "has_local_timestamp": has_local_timestamp,
            "has_local_fs": has_local_fs,
            "file_path": file_path,
        })

    # Parse connections
    conns = data.get("connections", {})
    if isinstance(conns, dict):
        node_dict = {pn["class_name"]: pn for pn in parsed_nodes}
        for src_key, target_groups in conns.items():
            src_name = node_id_to_name.get(src_key, src_key)
            if not isinstance(target_groups, dict):
                continue
            for rel_type, target_lists in target_groups.items():
                if not isinstance(target_lists, list):
                    continue
                for group in target_lists:
                    if not isinstance(group, list):
                        continue
                    for target in group:
                        if isinstance(target, dict) and "node" in target:
                            tgt_name = node_id_to_name.get(str(target["node"]), str(target["node"]))
                            edges.append({
                                "source": src_name,
                                "target": tgt_name,
                                "rel_type": target.get("type") or rel_type or "FLOWS_TO",
                            })
                            if src_name in node_dict:
                                node_dict[src_name]["calls"].append({
                                    "target_object": tgt_name,
                                    "target_method": rel_type,
                                })

    return {
        "is_workflow": True,
        "nodes": parsed_nodes,
        "edges": edges,
        "tables": list(tables),
    }
