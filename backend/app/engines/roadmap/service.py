import logging
from typing import Any, Dict, List, Optional, Tuple, Set

from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.db.graph_store import get_graph_store
from app.db.models import Decision, Roadmap
from app.engines.council.runner import run_council_for_clusters
from app.engines.roadmap.montecarlo import run_monte_carlo_simulation
from app.engines.roadmap.scheduler import schedule_roadmap

logger = logging.getLogger("modernrx.roadmap.service")


def generate_project_roadmap(
    project_id: str,
    db: Session,
    squads: int = 2,
    freeze_windows: Optional[List[Tuple[int, int]]] = None,
    target_weeks: Optional[float] = None,
    actor: str = "roadmap_optimizer",
    persist: bool = True,
) -> Dict[str, Any]:
    """
    Coordinates end-to-end roadmap optimization and PERT Monte Carlo simulation.
    """
    freeze_windows = freeze_windows or [(12, 14)]

    # 1. Fetch project decisions
    decisions = (
        db.query(Decision)
        .filter(Decision.project_id == project_id)
        .order_by(Decision.cluster_id.asc())
        .all()
    )

    if not decisions:
        logger.info("No decisions found for project %s. Running AI Council first...", project_id)
        run_council_for_clusters(project_id, db=db, force_offline=True)
        decisions = (
            db.query(Decision)
            .filter(Decision.project_id == project_id)
            .order_by(Decision.cluster_id.asc())
            .all()
        )

    store = get_graph_store(project_id)

    # 2. Derive inter-cluster dependencies from call graph
    # If nodes in cluster A call nodes in cluster B, B must be decomposed/facaded before A
    cluster_of_node: Dict[str, str] = {}
    for nid, d in store.graph.nodes(data=True):
        cid = d.get("cluster_id")
        if cid:
            cluster_of_node[nid] = cid

    cluster_deps: Dict[str, Set[str]] = {d.cluster_id: set() for d in decisions}
    for u, v in store.graph.edges():
        c_u = cluster_of_node.get(u)
        c_v = cluster_of_node.get(v)
        if c_u and c_v and c_u != c_v and c_v in cluster_deps:
            # Caller c_u depends on target c_v
            cluster_deps[c_u].add(f"MOD-{c_v}")

    # 3. Create workload tasks from decisions
    workload_tasks = []
    for d in decisions:
        cid = d.cluster_id
        # Determine GxP tier for cluster from nodes
        cluster_nodes = [nid for nid, c in cluster_of_node.items() if c == cid]
        cluster_tiers = [
            store.graph.nodes[nid].get("gxp_tier", "LOW")
            for nid in cluster_nodes
            if nid in store.graph.nodes
        ]
        gxp_tier = "HIGH" if "HIGH" in cluster_tiers else ("MEDIUM" if "MEDIUM" in cluster_tiers else "LOW")

        effort = tuple(d.effort_weeks) if d.effort_weeks and len(d.effort_weeks) == 3 else (2.0, 3.5, 5.0)

        task_id = f"MOD-{cid}"
        task_name = f"Migrate {cid.replace('modernrx_', '').replace('_', ' ').title()}"
        deps = list(cluster_deps.get(cid, set()))

        workload_tasks.append({
            "id": task_id,
            "name": task_name,
            "cluster_id": cid,
            "gxp_tier": gxp_tier,
            "strategy": d.strategy,
            "effort_triple": effort,
            "dependencies": deps,
        })

    # 4. Run CP-SAT scheduling
    schedule = schedule_roadmap(
        workload_tasks=workload_tasks,
        squads=squads,
        freeze_windows=freeze_windows,
    )

    # 5. Run Monte Carlo simulation
    monte_carlo = run_monte_carlo_simulation(
        scheduled_tasks=schedule["tasks"],
        runs=10000,
        target_weeks=target_weeks,
    )

    result = {
        "project_id": project_id,
        "schedule": schedule,
        "monte_carlo": monte_carlo,
        "parameters": {
            "squads": squads,
            "freeze_windows": freeze_windows,
            "target_weeks": target_weeks or monte_carlo["p80_weeks"],
        },
    }

    # 6. Database persistence
    if persist:
        existing_roadmap = (
            db.query(Roadmap)
            .filter(Roadmap.project_id == project_id)
            .first()
        )
        if existing_roadmap:
            existing_roadmap.schedule_json = schedule
            existing_roadmap.montecarlo_json = monte_carlo
            roadmap_rec = existing_roadmap
        else:
            roadmap_rec = Roadmap(
                project_id=project_id,
                schedule_json=schedule,
                montecarlo_json=monte_carlo,
            )
            db.add(roadmap_rec)

        db.commit()
        db.refresh(roadmap_rec)

        record_audit_event(
            db=db,
            actor=actor,
            action="ROADMAP_OPTIMIZED",
            entity="Roadmap",
            entity_id=roadmap_rec.id,
            payload={
                "project_id": project_id,
                "makespan_weeks": schedule["makespan_weeks"],
                "p50_weeks": monte_carlo["p50_weeks"],
                "p80_weeks": monte_carlo["p80_weeks"],
                "p95_weeks": monte_carlo["p95_weeks"],
                "squads": squads,
                "freeze_windows": freeze_windows,
            },
        )

    return result
