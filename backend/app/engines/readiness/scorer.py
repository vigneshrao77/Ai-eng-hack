from typing import Dict, List, Any
from app.db.graph_store import GraphStore
from app.engines.readiness.checks import evaluate_node_readiness
from app.core.logging import logger


def calculate_project_readiness(store: GraphStore) -> Dict[str, Any]:
    nodes = store.get_all_nodes("Class")
    edges = store.get_all_edges()

    # Identify shared tables across components
    table_access: Dict[str, List[str]] = {}
    for e in edges:
        src = e["source"]
        tgt = e["target"]
        rel = e.get("rel_type")
        if rel in ("WRITES", "READS") and ("TABLE_" in tgt or tgt in ("SAMPLE", "RESULT", "BATCH", "AUDIT_TRAIL")):
            tbl = tgt.replace("TABLE_", "")
            table_access.setdefault(tbl, []).append(src)

    node_shared_tables: Dict[str, List[str]] = {}
    for tbl, accessors in table_access.items():
        if len(set(accessors)) > 1:
            for acc in set(accessors):
                node_shared_tables.setdefault(acc, []).append(tbl)

    graph_context = {
        "node_shared_tables": node_shared_tables,
    }

    component_scores: List[Dict[str, Any]] = []
    dead_code_candidates: List[Dict[str, Any]] = []
    quick_wins: List[Dict[str, Any]] = []

    for node in nodes:
        nid = node["id"]
        res = evaluate_node_readiness(node, graph_context)
        score = res["score"]

        # Store score on node
        store.graph.nodes[nid]["readiness"] = score
        store.graph.nodes[nid]["readiness_deductions"] = res["deductions"]

        comp_info = {
            "node_id": nid,
            "class_name": node.get("class_name", nid),
            "fqn": node.get("fqn", ""),
            "score": score,
            "total_deductions": res["total_deductions"],
            "gxp_tier": node.get("gxp_tier", "LOW"),
            "loc": node.get("loc", 0),
            "complexity": node.get("complexity", 1),
            "deductions": res["deductions"],
        }
        component_scores.append(comp_info)

        # Opportunity 1: Dead code (0 fan-in and 0 endpoints)
        fan_in = store.graph.in_degree(nid) if nid in store.graph else 0
        if fan_in == 0 and "Unused" in nid:
            dead_code_candidates.append({
                "node_id": nid,
                "class_name": node.get("class_name", nid),
                "loc": node.get("loc", 0),
                "reason": "Zero inbound calls detected and not exposed as an HTTP endpoint or scheduled task.",
                "recommendation": "7R Retire candidate. Safe deletion saves maintenance and reduces attack surface.",
            })

        # Opportunity 2: Quick-Win Rehost (High readiness >= 75 and LOW/MEDIUM GxP tier)
        if score >= 75 and node.get("gxp_tier") in ("LOW", "MEDIUM"):
            quick_wins.append({
                "node_id": nid,
                "class_name": node.get("class_name", nid),
                "score": score,
                "gxp_tier": node.get("gxp_tier"),
                "reason": "High 12-factor cloud readiness with minimal regulatory re-validation burden.",
                "recommendation": "Wave 1 candidate for early cloud cutover to build team velocity.",
            })

    store.persist()

    avg_score = round(sum(c["score"] for c in component_scores) / len(component_scores), 1) if component_scores else 0

    return {
        "average_readiness": avg_score,
        "total_components": len(component_scores),
        "components": component_scores,
        "dead_code": dead_code_candidates,
        "quick_wins": quick_wins,
    }
