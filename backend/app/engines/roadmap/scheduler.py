import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from ortools.sat.python import cp_model

logger = logging.getLogger("modernrx.roadmap.scheduler")

FOUNDATION_TASKS = [
    {
        "id": "FND-01",
        "name": "Cloud Landing Zone & VPC Core",
        "duration": 2,
        "gxp_tier": "LOW",
        "strategy": "Replatform",
        "effort_triple": (1.5, 2.0, 3.0),
        "dependencies": [],
    },
    {
        "id": "FND-02",
        "name": "Zero-Trust IAM & Vault Secrets Engine",
        "duration": 2,
        "gxp_tier": "MEDIUM",
        "strategy": "Replatform",
        "effort_triple": (1.5, 2.0, 3.0),
        "dependencies": ["FND-01"],
    },
    {
        "id": "FND-03",
        "name": "Validated CI/CD & GxP Compliance Guardrails",
        "duration": 2,
        "gxp_tier": "HIGH",
        "strategy": "Replatform",
        "effort_triple": (1.5, 2.0, 3.5),
        "dependencies": ["FND-01"],
    },
    {
        "id": "FND-04",
        "name": "Cloud Supplier Qualification (SOC 2 / Annex 11)",
        "duration": 1,
        "gxp_tier": "HIGH",
        "strategy": "Retain",
        "effort_triple": (1.0, 1.0, 2.0),
        "dependencies": ["FND-02", "FND-03"],
    },
]


def schedule_roadmap(
    workload_tasks: List[Dict[str, Any]],
    squads: int = 2,
    freeze_windows: Optional[List[Tuple[int, int]]] = None,
    max_weeks: int = 104,
) -> Dict[str, Any]:
    """
    Schedules application modernization using OR-Tools CP-SAT.
    Enforces:
    1. Precedence: Foundation tasks first, plus inter-workload call dependencies.
    2. GxP Freeze Windows: No HIGH-tier cutover allowed in freeze weeks.
    3. Risk Cap: No more than 1 HIGH-tier cutover concurrently.
    4. Squad capacity: Cumulative concurrency bounded by squad count.
    5. Objective: Minimize makespan + risk-weighted task starts.
    """
    freeze_windows = freeze_windows or [(12, 14)]
    all_tasks: List[Dict[str, Any]] = []

    # 1. Foundation tasks
    for ft in FOUNDATION_TASKS:
        all_tasks.append(dict(ft))

    # 2. Add workload tasks
    fnd_deps = ["FND-04"]  # All workload tasks must wait for foundation completion
    for wt in workload_tasks:
        task = dict(wt)
        existing_deps = task.get("dependencies", [])
        combined_deps = list(set(existing_deps + fnd_deps))
        task["dependencies"] = combined_deps
        # Ensure duration is at least 1 week integer
        likely = task.get("effort_triple", (2.0, 3.0, 5.0))[1]
        task["duration"] = max(1, int(round(likely)))
        all_tasks.append(task)

    task_map = {t["id"]: t for t in all_tasks}

    model = cp_model.CpModel()
    start_vars = {}
    end_vars = {}
    interval_vars = {}

    for t in all_tasks:
        tid = t["id"]
        dur = t["duration"]
        start_v = model.NewIntVar(0, max_weeks, f"start_{tid}")
        end_v = model.NewIntVar(dur, max_weeks, f"end_{tid}")
        interval_v = model.NewIntervalVar(start_v, dur, end_v, f"interval_{tid}")

        start_vars[tid] = start_v
        end_vars[tid] = end_v
        interval_vars[tid] = interval_v

    # Precedence Constraints
    for t in all_tasks:
        tid = t["id"]
        for pred_id in t.get("dependencies", []):
            if pred_id in end_vars:
                model.Add(start_vars[tid] >= end_vars[pred_id])

    # GxP Freeze Windows (No HIGH-tier cutover in freeze window weeks)
    high_tasks = [t for t in all_tasks if t.get("gxp_tier") == "HIGH"]
    for ht in high_tasks:
        tid = ht["id"]
        for fw_start, fw_end in freeze_windows:
            # Cutover occurs at end_vars[tid]. end_vars cannot be inside [fw_start, fw_end]
            # Formulate using boolean or: end_vars[tid] < fw_start OR end_vars[tid] > fw_end
            b_before = model.NewBoolVar(f"freeze_before_{tid}_{fw_start}")
            b_after = model.NewBoolVar(f"freeze_after_{tid}_{fw_end}")
            model.Add(end_vars[tid] < fw_start).OnlyEnforceIf(b_before)
            model.Add(end_vars[tid] > fw_end).OnlyEnforceIf(b_after)
            model.AddBoolOr([b_before, b_after])

    # Risk Cap: Max 1 HIGH-tier cutover in the same week
    for i, ht1 in enumerate(high_tasks):
        for j, ht2 in enumerate(high_tasks):
            if i < j:
                # Disallow end_vars[ht1] == end_vars[ht2]
                b_diff = model.NewBoolVar(f"diff_high_{ht1['id']}_{ht2['id']}")
                model.Add(end_vars[ht1["id"]] != end_vars[ht2["id"]]).OnlyEnforceIf(b_diff)
                model.Add(b_diff == 1)

    # Squad Capacity (Cumulative resource constraint)
    # Each task consumes 1 squad demand
    demands = [1 for _ in all_tasks]
    intervals = [interval_vars[t["id"]] for t in all_tasks]
    model.AddCumulative(intervals, demands, max(1, squads))

    # Objective: Minimize makespan + 0.1 * sum(risk_weighted_start)
    makespan = model.NewIntVar(0, max_weeks, "makespan")
    for t in all_tasks:
        model.Add(makespan >= end_vars[t["id"]])

    risk_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    risk_start_terms = [
        start_vars[t["id"]] * risk_weights.get(t.get("gxp_tier", "LOW"), 1)
        for t in all_tasks
    ]

    model.Minimize(makespan * 10 + sum(risk_start_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        logger.warning("OR-Tools CP-SAT found no solution within constraints. Falling back to deterministic wave scheduling.")
        return deterministic_wave_fallback(all_tasks, squads, freeze_windows)

    # Extract solution
    scheduled_tasks = []
    for t in all_tasks:
        tid = t["id"]
        st = solver.Value(start_vars[tid])
        et = solver.Value(end_vars[tid])
        dur = t["duration"]
        scheduled_tasks.append({
            "id": tid,
            "name": t.get("name", tid),
            "cluster_id": t.get("cluster_id"),
            "gxp_tier": t.get("gxp_tier", "LOW"),
            "strategy": t.get("strategy", "Replatform"),
            "duration": dur,
            "start_week": st,
            "end_week": et,
            "dependencies": t.get("dependencies", []),
            "effort_triple": t.get("effort_triple", (dur * 0.75, dur, dur * 1.4)),
        })

    # Sort tasks by start_week
    scheduled_tasks.sort(key=lambda x: (x["start_week"], x["end_week"]))
    total_makespan = max((t["end_week"] for t in scheduled_tasks), default=0)

    # Assign Waves based on timing and tier
    waves = build_waves_structure(scheduled_tasks)
    critical_path = identify_critical_path(scheduled_tasks)

    return {
        "status": "success",
        "solver": "OR-Tools CP-SAT",
        "makespan_weeks": total_makespan,
        "squads": squads,
        "freeze_windows": freeze_windows,
        "tasks": scheduled_tasks,
        "waves": waves,
        "critical_path": critical_path,
    }


def deterministic_wave_fallback(
    all_tasks: List[Dict[str, Any]],
    squads: int,
    freeze_windows: List[Tuple[int, int]],
) -> Dict[str, Any]:
    """
    Deterministic topological wave scheduler used if solver constraints are overly tight.
    """
    scheduled = []
    current_week = 0

    # Foundation wave
    fnd = [t for t in all_tasks if t["id"].startswith("FND-")]
    for t in fnd:
        dur = t["duration"]
        scheduled.append({
            "id": t["id"],
            "name": t.get("name", t["id"]),
            "cluster_id": t.get("cluster_id"),
            "gxp_tier": t.get("gxp_tier", "LOW"),
            "strategy": t.get("strategy", "Replatform"),
            "duration": dur,
            "start_week": current_week,
            "end_week": current_week + dur,
            "dependencies": t.get("dependencies", []),
            "effort_triple": t.get("effort_triple", (dur * 0.75, dur, dur * 1.4)),
        })
        current_week += dur

    # Workload tasks
    workloads = [t for t in all_tasks if not t["id"].startswith("FND-")]
    # Order: LOW (quick wins) first, then MEDIUM, then HIGH
    tier_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    workloads.sort(key=lambda x: tier_order.get(x.get("gxp_tier", "LOW"), 2))

    for t in workloads:
        dur = t["duration"]
        start_w = current_week
        end_w = start_w + dur

        # Avoid freeze window for HIGH tier
        if t.get("gxp_tier") == "HIGH":
            for fw_s, fw_e in freeze_windows:
                if fw_s <= end_w <= fw_e:
                    start_w = fw_e + 1
                    end_w = start_w + dur

        scheduled.append({
            "id": t["id"],
            "name": t.get("name", t["id"]),
            "cluster_id": t.get("cluster_id"),
            "gxp_tier": t.get("gxp_tier", "LOW"),
            "strategy": t.get("strategy", "Replatform"),
            "duration": dur,
            "start_week": start_w,
            "end_week": end_w,
            "dependencies": t.get("dependencies", []),
            "effort_triple": t.get("effort_triple", (dur * 0.75, dur, dur * 1.4)),
        })
        current_week = max(current_week, end_w)

    total_makespan = max((t["end_week"] for t in scheduled), default=0)
    waves = build_waves_structure(scheduled)
    critical_path = identify_critical_path(scheduled)

    return {
        "status": "success",
        "solver": "Deterministic Wave Fallback",
        "makespan_weeks": total_makespan,
        "squads": squads,
        "freeze_windows": freeze_windows,
        "tasks": scheduled,
        "waves": waves,
        "critical_path": critical_path,
    }


def build_waves_structure(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    wave_0_tasks = [t for t in tasks if t["id"].startswith("FND-")]
    other_tasks = [t for t in tasks if not t["id"].startswith("FND-")]

    waves = []
    if wave_0_tasks:
        waves.append({
            "wave_number": 0,
            "title": "Wave 0 — Cloud Foundation & Compliance Guardrails",
            "theme": "Foundation",
            "start_week": min(t["start_week"] for t in wave_0_tasks),
            "end_week": max(t["end_week"] for t in wave_0_tasks),
            "tasks": wave_0_tasks,
            "high_tier_count": sum(1 for t in wave_0_tasks if t["gxp_tier"] == "HIGH"),
        })

    # Group remaining tasks into waves (Wave 1: Quick Wins, Wave 2: Core Modernization, Wave 3: Regulated Core)
    low_tasks = [t for t in other_tasks if t["gxp_tier"] == "LOW"]
    med_tasks = [t for t in other_tasks if t["gxp_tier"] == "MEDIUM"]
    high_tasks = [t for t in other_tasks if t["gxp_tier"] == "HIGH"]

    w_idx = 1
    if low_tasks:
        waves.append({
            "wave_number": w_idx,
            "title": f"Wave {w_idx} — Peripheral Quick Wins & Reporting",
            "theme": "Quick Wins",
            "start_week": min(t["start_week"] for t in low_tasks),
            "end_week": max(t["end_week"] for t in low_tasks),
            "tasks": low_tasks,
            "high_tier_count": 0,
        })
        w_idx += 1

    if med_tasks:
        waves.append({
            "wave_number": w_idx,
            "title": f"Wave {w_idx} — Medium Criticality & Decoupled APIs",
            "theme": "Core APIs",
            "start_week": min(t["start_week"] for t in med_tasks),
            "end_week": max(t["end_week"] for t in med_tasks),
            "tasks": med_tasks,
            "high_tier_count": 0,
        })
        w_idx += 1

    if high_tasks:
        waves.append({
            "wave_number": w_idx,
            "title": f"Wave {w_idx} — Regulated Core Cutover & Validation",
            "theme": "Regulated Core",
            "start_week": min(t["start_week"] for t in high_tasks),
            "end_week": max(t["end_week"] for t in high_tasks),
            "tasks": high_tasks,
            "high_tier_count": len(high_tasks),
        })

    return waves


def identify_critical_path(tasks: List[Dict[str, Any]]) -> List[str]:
    """Finds tasks on the critical path."""
    if not tasks:
        return []
    total_makespan = max(t["end_week"] for t in tasks)
    critical_tasks = [t["id"] for t in tasks if t["end_week"] == total_makespan]
    # Trace dependencies backward
    task_map = {t["id"]: t for t in tasks}
    curr = critical_tasks[0] if critical_tasks else None
    path = []
    while curr:
        path.append(curr)
        deps = task_map.get(curr, {}).get("dependencies", [])
        if not deps:
            break
        # Pick dependency that finishes latest
        curr = max(deps, key=lambda d: task_map.get(d, {}).get("end_week", -1), default=None)
    path.reverse()
    return path
