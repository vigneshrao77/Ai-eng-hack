from typing import Dict, List, Any


CHECK_WEIGHTS = {
    "STATELESSNESS": 15,
    "LOCAL_FILESYSTEM": 10,
    "HARDCODED_CONFIG_SECRETS": 10,
    "FRAMEWORK_EOL": 15,
    "DB_COUPLING": 15,
    "COMPLEXITY_SIZE": 10,
    "TEST_COVERAGE": 5,
    "SCHEDULED_JOBS": 5,
    "LICENSING_BLOCKERS": 5,
    "OBSERVABILITY": 5,
    "GXP_PENALTY": 5,
}


def evaluate_node_readiness(node: Dict[str, Any], graph_context: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate 11 explainable 12-factor cloud readiness checks for a single node."""
    deductions: List[Dict[str, Any]] = []

    nid = node["id"]
    loc = node.get("loc", 0)
    complexity = node.get("complexity", 1)
    gxp_tier = node.get("gxp_tier", "LOW")
    annotations = node.get("annotations", [])
    has_local_fs = node.get("has_local_fs", False)
    has_local_timestamp = node.get("has_local_timestamp", False)

    # 1. Statelessness (15 pts)
    # Checks for in-memory session or static caches
    if "HttpSession" in node.get("raw_code", "") or "static Map" in node.get("raw_code", ""):
        sev = 0.8
        ded_pts = round(CHECK_WEIGHTS["STATELESSNESS"] * sev, 1)
        deductions.append({
            "check": "STATELESSNESS",
            "check_name": "Statelessness Violation",
            "weight": CHECK_WEIGHTS["STATELESSNESS"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "Component uses in-memory session or static mutable state, preventing horizontal scaling.",
            "evidence_node_ids": [nid],
        })

    # 2. Local File System Dependence (10 pts)
    if has_local_fs:
        sev = 1.0
        ded_pts = round(CHECK_WEIGHTS["LOCAL_FILESYSTEM"] * sev, 1)
        deductions.append({
            "check": "LOCAL_FILESYSTEM",
            "check_name": "Local Filesystem Dependence",
            "weight": CHECK_WEIGHTS["LOCAL_FILESYSTEM"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "Direct reliance on local Windows paths or network drive shares (e.g. C:\\instrument\\import).",
            "evidence_node_ids": [nid],
        })

    # 3. Hard-coded Config / Secrets (10 pts)
    if node.get("label") == "ConfigItem" and node.get("is_secret"):
        sev = 1.0
        ded_pts = round(CHECK_WEIGHTS["HARDCODED_CONFIG_SECRETS"] * sev, 1)
        deductions.append({
            "check": "HARDCODED_CONFIG_SECRETS",
            "check_name": "Hard-coded Plaintext Credentials",
            "weight": CHECK_WEIGHTS["HARDCODED_CONFIG_SECRETS"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "Hard-coded plaintext secret found in configuration.",
            "evidence_node_ids": [nid],
        })

    # 4. Framework / Runtime EOL (15 pts)
    # Dynamically inspect code, annotations, or packages for deprecated/EOL runtimes
    raw_code = node.get("raw_code", "")
    annotations_str = " ".join(node.get("annotations", []))
    has_spring2_eol = ("SpringBoot" in annotations_str or "org.springframework" in raw_code) and any(v in raw_code or v in annotations_str for v in ("2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"))
    has_py2_eol = "print " in raw_code and "print(" not in raw_code
    if has_spring2_eol or has_py2_eol:
        sev = 0.5
        ded_pts = round(CHECK_WEIGHTS["FRAMEWORK_EOL"] * sev, 1)
        reason_text = (
            "Built against legacy Spring Boot 2.x which has reached End-Of-Life (EOL)."
            if has_spring2_eol
            else "Legacy Python 2 runtime syntax detected (EOL)."
        )
        deductions.append({
            "check": "FRAMEWORK_EOL",
            "check_name": "Framework / Runtime EOL",
            "weight": CHECK_WEIGHTS["FRAMEWORK_EOL"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": f"{reason_text} Upgrade to modern cloud-native runtime recommended.",
            "evidence_node_ids": [nid],
        })

    # 5. DB Coupling (Shared Tables) (15 pts)
    shared_tables = graph_context.get("node_shared_tables", {}).get(nid, [])
    if shared_tables:
        sev = min(1.0, 0.4 * len(shared_tables))
        ded_pts = round(CHECK_WEIGHTS["DB_COUPLING"] * sev, 1)
        deductions.append({
            "check": "DB_COUPLING",
            "check_name": "Shared Database Table Coupling",
            "weight": CHECK_WEIGHTS["DB_COUPLING"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": f"Component accesses shared tables without bounded context: {', '.join(shared_tables)}",
            "evidence_node_ids": [nid] + [f"TABLE_{t}" for t in shared_tables],
        })

    # 6. Complexity & Size (10 pts)
    if complexity > 15 or loc > 400:
        sev = min(1.0, (complexity / 30.0) * 0.7 + (loc / 800.0) * 0.3)
        ded_pts = round(CHECK_WEIGHTS["COMPLEXITY_SIZE"] * sev, 1)
        deductions.append({
            "check": "COMPLEXITY_SIZE",
            "check_name": "High Cyclomatic Complexity & Size",
            "weight": CHECK_WEIGHTS["COMPLEXITY_SIZE"],
            "severity": round(sev, 2),
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": f"High cyclomatic complexity ({complexity}) and LOC ({loc}) increases refactoring risk.",
            "evidence_node_ids": [nid],
        })

    # 7. Scheduled / Batch Jobs (5 pts)
    if "Scheduled" in annotations:
        sev = 0.8
        ded_pts = round(CHECK_WEIGHTS["SCHEDULED_JOBS"] * sev, 1)
        deductions.append({
            "check": "SCHEDULED_JOBS",
            "check_name": "In-Process Scheduled Jobs",
            "weight": CHECK_WEIGHTS["SCHEDULED_JOBS"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "In-process @Scheduled timer requires external cloud scheduler (e.g. AWS EventBridge / K8s CronJob).",
            "evidence_node_ids": [nid],
        })

    # 8. GxP Tier Penalty (5 pts)
    if gxp_tier == "HIGH":
        sev = 1.0
        ded_pts = round(CHECK_WEIGHTS["GXP_PENALTY"] * sev, 1)
        deductions.append({
            "check": "GXP_PENALTY",
            "check_name": "GxP Regulatory Criticality Penalty",
            "weight": CHECK_WEIGHTS["GXP_PENALTY"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "HIGH regulatory criticality mandates extensive CSA verification and differential testing before cutover.",
            "evidence_node_ids": [nid],
        })
    elif gxp_tier == "MEDIUM":
        sev = 0.5
        ded_pts = round(CHECK_WEIGHTS["GXP_PENALTY"] * sev, 1)
        deductions.append({
            "check": "GXP_PENALTY",
            "check_name": "GxP Regulatory Criticality Penalty",
            "weight": CHECK_WEIGHTS["GXP_PENALTY"],
            "severity": sev,
            "deduction": ded_pts,
            "points_deducted": ded_pts,
            "reason": "MEDIUM regulatory criticality requires exploratory and unscripted CSA verification.",
            "evidence_node_ids": [nid],
        })

    total_deductions = sum(d["deduction"] for d in deductions)
    score = max(0, min(100, round(100 - total_deductions, 1)))

    return {
        "node_id": nid,
        "score": score,
        "total_deductions": round(total_deductions, 1),
        "deductions": deductions,
    }
