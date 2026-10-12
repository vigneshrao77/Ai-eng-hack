import os
from pathlib import Path
from typing import Dict, Any, List
from app.db.graph_store import get_graph_store, GraphStore
from app.engines.twin.ingest import scan_repository
from app.engines.twin.parsers.java_parser import parse_java_file
from app.engines.twin.parsers.config_parser import parse_properties_file
from app.core.logging import logger


def build_living_twin(project_id: str, repo_path: str) -> Dict[str, Any]:
    logger.info(f"Building Living Twin for project {project_id} from {repo_path}")
    store = get_graph_store(project_id)
    scan_meta = scan_repository(repo_path)

    classes_parsed = []
    config_items = []
    tables_discovered = set()

    # 1. Parse all Java and Config files
    for file_info in scan_meta["files"]:
        fpath = file_info["full_path"]
        if file_info["extension"] == ".java":
            try:
                parsed = parse_java_file(fpath)
                classes_parsed.append(parsed)
                for top in parsed["table_operations"]:
                    tables_discovered.add(top["table"])
            except Exception as e:
                logger.error(f"Error parsing Java file {fpath}: {e}")

        elif file_info["extension"] in (".properties", ".conf"):
            try:
                cfg_list = parse_properties_file(fpath)
                config_items.extend(cfg_list)
            except Exception as e:
                logger.error(f"Error parsing config file {fpath}: {e}")

    # 2. Add Tables
    for tbl in tables_discovered:
        store.add_node(
            f"TABLE_{tbl}",
            label="Table",
            name=tbl,
            regulated=True,  # Default for tables discovered in regulated codebase
            gxp_tier="HIGH" if tbl in ("SAMPLE", "RESULT", "BATCH", "AUDIT_TRAIL") else "LOW",
        )

    # 3. Add Classes
    class_map = {}
    for c in classes_parsed:
        cid = c["class_name"]
        class_map[cid.lower()] = c
        class_map[c["fqn"].lower()] = c

        store.add_node(
            cid,
            label="Class",
            fqn=c["fqn"],
            class_name=c["class_name"],
            package=c["package"],
            loc=c["loc"],
            complexity=c["complexity"],
            annotations=c["annotations"],
            file_path=c["file_path"],
            has_local_fs=c["has_local_fs"],
            has_local_timestamp=c["has_local_timestamp"],
            gxp_tier="LOW",  # Will be refined by GxP engine
            gxp_tags=[],
            readiness=100,  # Will be refined by Readiness engine
            cluster_id=f"cluster_{cid.lower()}",
        )

    # 4. Add Edges (Calls & Table Operations)
    for c in classes_parsed:
        cid = c["class_name"]
        # Table edges
        for top in c["table_operations"]:
            tbl_node = f"TABLE_{top['table']}"
            rel = "WRITES" if top["operation"] == "WRITE" else "READS"
            store.add_edge(cid, tbl_node, rel)

        # Cross-class calls
        for call in c["calls"]:
            tgt_obj = call["target_object"].lower()
            # Match target object to class name (e.g. reviewService -> ReviewService)
            matched_cls = None
            for key, candidate in class_map.items():
                if tgt_obj in key:
                    matched_cls = candidate["class_name"]
                    break

            if matched_cls and matched_cls != cid:
                store.add_edge(cid, matched_cls, "CALLS", target_method=call["target_method"])

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
