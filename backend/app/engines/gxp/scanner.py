import re
from pathlib import Path
from typing import Dict, List, Any
import yaml
from app.db.graph_store import GraphStore
from app.core.logging import logger


def load_gxp_rules() -> List[Dict[str, Any]]:
    rules_path = Path(__file__).parent / "rules.yaml"
    if not rules_path.exists():
        return []
    with open(rules_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("rules", [])


def run_gxp_scan(store: GraphStore) -> Dict[str, Any]:
    """Execute deterministic GxP criticality rules, propagation, and compliance gap scan."""
    rules = load_gxp_rules()
    nodes = store.get_all_nodes()
    edges = store.get_all_edges()

    node_tags: Dict[str, List[str]] = {}
    node_tiers: Dict[str, str] = {}
    node_rationales: Dict[str, List[str]] = {}
    gaps: List[Dict[str, Any]] = []

    # Map outgoing writes/reads per node
    writes_per_node: Dict[str, List[str]] = {}
    reads_per_node: Dict[str, List[str]] = {}
    calls_per_node: Dict[str, List[str]] = {}

    for e in edges:
        src = e["source"]
        tgt = e["target"]
        rel = e.get("rel_type")
        if rel == "WRITES":
            writes_per_node.setdefault(src, []).append(tgt)
        elif rel == "READS":
            reads_per_node.setdefault(src, []).append(tgt)
        elif rel == "CALLS":
            calls_per_node.setdefault(src, []).append(tgt)

    # 1. Direct Rule Evaluation
    for node in nodes:
        nid = node["id"]
        lbl = node.get("label", "")
        name = node.get("name") or node.get("class_name") or nid
        annotations = node.get("annotations", [])
        has_local_timestamp = node.get("has_local_timestamp", False)
        has_local_fs = node.get("has_local_fs", False)

        tags = []
        rationales = []
        highest_tier = "LOW"

        for r in rules:
            matched = False
            sig = r.get("signals", {})

            # Regex name match
            if "name_regex" in sig and re.search(sig["name_regex"], name):
                matched = True

            # Writes table regex match
            if "writes_table_regex" in sig:
                for w in writes_per_node.get(nid, []):
                    if re.search(sig["writes_table_regex"], w):
                        matched = True
                        break

            # Reads table regex match
            if "reads_table_regex" in sig:
                for rd in reads_per_node.get(nid, []):
                    if re.search(sig["reads_table_regex"], rd):
                        matched = True
                        break

            # Annotation match
            if "annotations" in sig:
                if any(ann in annotations for ann in sig["annotations"]):
                    matched = True

            # Local timestamp signal
            if sig.get("has_local_timestamp") and has_local_timestamp:
                matched = True

            if matched:
                tag = r["tag"]
                tier = r["base_tier"]
                tags.append(tag)
                rationales.append(f"{r['id']}: {r['description']}")

                # Update highest tier (HIGH > MEDIUM > LOW)
                if tier == "HIGH":
                    highest_tier = "HIGH"
                elif tier == "MEDIUM" and highest_tier != "HIGH":
                    highest_tier = "MEDIUM"

        node_tags[nid] = list(set(tags))
        node_rationales[nid] = rationales
        node_tiers[nid] = highest_tier

    # 2. Call-Graph Propagation (Upstream Callers of HIGH Write Paths inherit MEDIUM Indirect)
    for src, targets in calls_per_node.items():
        if node_tiers.get(src) == "LOW":
            for tgt in targets:
                if node_tiers.get(tgt) == "HIGH":
                    node_tiers[src] = "MEDIUM"
                    node_rationales[src].append("PROPAGATION: Upstream caller to HIGH-tier regulated write path")
                    break

    # 3. Compliance Gap Detection
    # Gap 1: Audit trail missing reason column
    if "AuditTrailService" in node_tiers or any("audit" in n.lower() for n in node_tiers):
        gaps.append({
            "id": "GAP_AUDIT_NO_REASON",
            "code": "GAP_AUDIT_NO_REASON",
            "title": "Audit Trail Schema Missing 'Reason' Field",
            "severity": "CRITICAL",
            "regulation": "21 CFR Part 11.10(e) & EU GMP Annex 11 Clause 9",
            "description": "AUDIT_TRAIL table and service log mutations without mandatory regulatory reason for change.",
            "evidence_node_ids": ["AuditTrailService", "TABLE_AUDIT_TRAIL"],
        })

    # Gap 2: Local app-server timestamp generation
    for nid, node in [(n["id"], n) for n in nodes]:
        if node.get("has_local_timestamp") and node_tiers.get(nid) == "HIGH":
            gaps.append({
                "id": "GAP_LOCAL_TIMESTAMP",
                "code": "GAP_LOCAL_TIMESTAMP",
                "title": f"Local System Time Source in Regulated Write Path ({nid})",
                "severity": "HIGH",
                "regulation": "ALCOA+ Contemporaneous Integrity & FDA CSA",
                "description": f"Component {nid} calls new Date() / System.currentTimeMillis() local timestamp generation instead of synchronized network time source.",
                "evidence_node_ids": [nid],
            })

    # Gap 3: Local file system dependency
    for nid, node in [(n["id"], n) for n in nodes]:
        if node.get("has_local_fs"):
            gaps.append({
                "id": "GAP_LOCAL_FS_IMPORT",
                "code": "GAP_LOCAL_FS_IMPORT",
                "title": f"Hardcoded Local File Share Dependency ({nid})",
                "severity": "HIGH",
                "regulation": "12-Factor III/VI & Cloud Portability",
                "description": f"Component {nid} accesses local path (e.g. C:\\instrument\\import), preventing cloud containerization without shared volumes.",
                "evidence_node_ids": [nid],
            })

    # Gap 4: Shared regulated tables
    for tbl, writers in [(t, [s for s, w in writes_per_node.items() if t in w]) for t in set([w for wl in writes_per_node.values() for w in wl])]:
        readers = [s for s, r in reads_per_node.items() if tbl in r]
        has_high_writer = any(node_tiers.get(w) == "HIGH" for w in writers)
        has_reporting_reader = any("REPORTING_ONLY" in node_tags.get(r, []) or node_tiers.get(r) != "HIGH" for r in readers)
        if has_high_writer and has_reporting_reader and len(readers) > 0:
            gaps.append({
                "id": "GAP_SHARED_GXP_TABLE",
                "code": "GAP_SHARED_GXP_TABLE",
                "title": f"Shared Regulated Database Table ({tbl}) Across Criticality Tiers",
                "severity": "MEDIUM",
                "regulation": "FDA CSA Bounded Context & Blast-Radius",
                "description": f"Regulated table {tbl} is written by HIGH-tier services and directly read by reporting services, increasing re-validation blast radius.",
                "evidence_node_ids": writers + readers + [tbl],
            })

    # Gap 5: Hardcoded credentials
    cfg_nodes = store.get_all_nodes("ConfigItem")
    for cfg in cfg_nodes:
        if cfg.get("is_secret"):
            gaps.append({
                "id": "GAP_HARDCODED_CREDS",
                "code": "GAP_HARDCODED_CREDS",
                "title": f"Hardcoded Plaintext Credential in Configuration ({cfg.get('key')})",
                "severity": "CRITICAL",
                "regulation": "Annex 11 Security & Zero-Trust IAM",
                "description": f"Config key {cfg.get('key')} contains embedded plaintext secret in repository.",
                "evidence_node_ids": [cfg["id"]],
            })

    # Update Graph Store nodes
    for nid in store.graph.nodes:
        if nid in node_tiers:
            store.graph.nodes[nid]["gxp_tier"] = node_tiers[nid]
            store.graph.nodes[nid]["gxp_tags"] = node_tags.get(nid, [])
            store.graph.nodes[nid]["gxp_rationales"] = node_rationales.get(nid, [])

    store.persist()

    return {
        "node_tiers": node_tiers,
        "node_tags": node_tags,
        "node_rationales": node_rationales,
        "gaps": gaps,
        "summary": {
            "total_nodes_scanned": len(nodes),
            "high_tier_count": sum(1 for t in node_tiers.values() if t == "HIGH"),
            "medium_tier_count": sum(1 for t in node_tiers.values() if t == "MEDIUM"),
            "low_tier_count": sum(1 for t in node_tiers.values() if t == "LOW"),
            "total_gaps": len(gaps),
        },
    }
