import os
from pathlib import Path
from typing import Dict, Any, List
from app.db.graph_store import get_graph_store, GraphStore
from app.engines.twin.ingest import scan_repository
from app.engines.twin.parsers.java_parser import parse_java_file
from app.engines.twin.parsers.config_parser import parse_properties_file
from app.engines.twin.parsers.workflow_parser import parse_workflow_json_file
from app.engines.twin.parsers.python_parser import parse_python_file
from app.engines.twin.parsers.generic_parser import parse_generic_code_file
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.readiness.scorer import calculate_project_readiness
from app.core.logging import logger


def build_living_twin(project_id: str, repo_path: str) -> Dict[str, Any]:
    logger.info(f"Building Living Twin for project {project_id} from {repo_path}")
    store = get_graph_store(project_id)
    scan_meta = scan_repository(repo_path)

    classes_parsed: List[Dict[str, Any]] = []
    config_items: List[Dict[str, Any]] = []
    tables_discovered = set()
    direct_edges: List[Dict[str, Any]] = []

    # 1. Parse repository files based on extension
    for file_info in scan_meta["files"]:
        fpath = file_info["full_path"]
        ext = file_info["extension"].lower()
        lang = file_info.get("language", "Other")

        if ext == ".java":
            try:
                parsed = parse_java_file(fpath)
                classes_parsed.append(parsed)
                for top in parsed["table_operations"]:
                    tables_discovered.add(top["table"])
            except Exception as e:
                logger.error(f"Error parsing Java file {fpath}: {e}")

        elif ext in (".properties", ".conf", ".env"):
            try:
                cfg_list = parse_properties_file(fpath)
                config_items.extend(cfg_list)
            except Exception as e:
                logger.error(f"Error parsing config file {fpath}: {e}")

        elif ext == ".json":
            try:
                wf_res = parse_workflow_json_file(fpath)
                if wf_res.get("is_workflow"):
                    classes_parsed.extend(wf_res.get("nodes", []))
                    direct_edges.extend(wf_res.get("edges", []))
                    for tbl in wf_res.get("tables", []):
                        tables_discovered.add(tbl)
            except Exception as e:
                logger.error(f"Error parsing JSON workflow file {fpath}: {e}")

        elif ext == ".py":
            try:
                py_classes = parse_python_file(fpath)
                classes_parsed.extend(py_classes)
                for c in py_classes:
                    for top in c.get("table_operations", []):
                        tables_discovered.add(top["table"])
            except Exception as e:
                logger.error(f"Error parsing Python file {fpath}: {e}")

        elif ext in (".js", ".jsx", ".ts", ".tsx", ".cs", ".go", ".sql"):
            try:
                code_items = parse_generic_code_file(fpath, ext, lang)
                classes_parsed.extend(code_items)
                for c in code_items:
                    for top in c.get("table_operations", []):
                        tables_discovered.add(top["table"])
            except Exception as e:
                logger.error(f"Error parsing code file {fpath}: {e}")

    # Fallback: if no architectural components parsed, convert scanned files into Component nodes
    if not classes_parsed:
        for f in scan_meta["files"]:
            f_stem = Path(f["path"]).stem or Path(f["path"]).name
            f_parent = str(Path(f["path"]).parent).replace("\\", "/")
            classes_parsed.append({
                "file_path": f["full_path"],
                "class_name": f_stem,
                "name": f_stem,
                "package": f_parent if f_parent != "." else "root",
                "fqn": f["path"],
                "is_interface": False,
                "loc": f["loc"],
                "complexity": max(1, f["loc"] // 25),
                "annotations": [f.get("language", "File")],
                "methods": [],
                "calls": [],
                "table_operations": [],
                "has_local_timestamp": False,
                "has_local_fs": False,
            })

    # 2. Add Tables
    for tbl in tables_discovered:
        store.add_node(
            f"TABLE_{tbl}",
            label="Table",
            name=tbl,
            regulated=True,  # Default for tables discovered in regulated codebase
            gxp_tier="HIGH" if tbl in ("SAMPLE", "RESULT", "BATCH", "AUDIT_TRAIL", "WORKFLOW_DATASTORE") else "LOW",
        )

    # 3. Add Classes / Architectural Components
    class_map = {}
    for c in classes_parsed:
        cid = c["class_name"]
        class_map[cid.lower()] = c
        class_map[c["fqn"].lower()] = c

        store.add_node(
            cid,
            label="Class",
            name=c.get("name") or cid,
            fqn=c["fqn"],
            class_name=cid,
            package=c["package"],
            loc=c["loc"],
            complexity=c["complexity"],
            annotations=c.get("annotations", []),
            file_path=c["file_path"],
            has_local_fs=c.get("has_local_fs", False),
            has_local_timestamp=c.get("has_local_timestamp", False),
            gxp_tier="LOW",  # Refined below by GxP engine
            gxp_tags=[],
            readiness=100,  # Refined below by Readiness engine
            cluster_id=f"cluster_{cid.lower()}",
        )

    # 4. Add Edges (Calls, Table Operations, and direct workflow edges)
    for c in classes_parsed:
        cid = c["class_name"]
        # Table edges
        for top in c.get("table_operations", []):
            tbl_node = f"TABLE_{top['table']}"
            rel = "WRITES" if top["operation"] == "WRITE" else "READS"
            store.add_edge(cid, tbl_node, rel)

        # Cross-class calls
        for call in c.get("calls", []):
            tgt_obj = call["target_object"].lower()
            matched_cls = None
            for key, candidate in class_map.items():
                if tgt_obj in key or key in tgt_obj:
                    matched_cls = candidate["class_name"]
                    break

            if matched_cls and matched_cls != cid:
                store.add_edge(cid, matched_cls, "CALLS", target_method=call.get("target_method", "invoke"))

    # Direct edges from workflows or parsed relations
    for de in direct_edges:
        store.add_edge(de["source"], de["target"], de.get("rel_type", "CALLS"))

    # If few edges exist, establish folder containment / sequential dataflow edges
    if store.graph.number_of_edges() == 0 and len(classes_parsed) > 1:
        for i in range(len(classes_parsed) - 1):
            store.add_edge(classes_parsed[i]["class_name"], classes_parsed[i + 1]["class_name"], "FLOWS_TO")

    # 5. Add Config Nodes
    for idx, cfg in enumerate(config_items):
        cfg_id = f"CFG_{cfg['key']}_{idx}"
        store.add_node(
            cfg_id,
            label="ConfigItem",
            key=cfg["key"],
            value_masked=cfg["value_masked"],
            kind=cfg["kind"],
            is_secret=cfg["is_secret"],
            file_path=cfg["file_path"],
            line_number=cfg["line_number"],
        )

    # 6. Calculate Graph Topology Metrics (Fan-In and Fan-Out)
    for n in store.graph.nodes:
        in_degree = store.graph.in_degree(n)
        out_degree = store.graph.out_degree(n)
        store.graph.nodes[n]["fanIn"] = in_degree
        store.graph.nodes[n]["fanOut"] = out_degree

    store.persist()

    # 7. Automatically execute deterministic GxP scan and Readiness calculation
    try:
        run_gxp_scan(store)
    except Exception as e:
        logger.warning(f"GxP scan post-build skipped or failed: {e}")

    try:
        calculate_project_readiness(store)
    except Exception as e:
        logger.warning(f"Readiness calculation post-build skipped or failed: {e}")

    store.persist()

    total_nodes = store.graph.number_of_nodes()
    total_edges = store.graph.number_of_edges()
    logger.info(f"Twin Graph construction complete: {total_nodes} nodes, {total_edges} edges.")

    return {
        "project_id": project_id,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_loc": scan_meta["total_loc"],
        "languages": scan_meta["language_loc"],
    }
