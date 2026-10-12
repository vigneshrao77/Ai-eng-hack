import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.config import settings
from app.core.audit import canonical_json, record_audit_event
from app.db.models import Decision
from app.engines.council.agents import (
    CloudArchitectAgent,
    CouncilModeratorAgent,
    FinOpsAgent,
    RegulatoryAffairsAgent,
    SecurityOfficerAgent,
    ValidationQAAgent,
)
from app.engines.council.schema import (
    CouncilDebate,
    CouncilDecision,
    SpecialistOpinion,
)
from app.engines.council.validator import DecisionValidationError, validate_decision
from app.db.graph_store import get_graph_store
from app.engines.decompose.cluster import execute_3way_decomposition

logger = logging.getLogger("modernrx.council.runner")


def run_council_for_clusters(
    project_id: str,
    db: Session,
    cluster_ids: Optional[List[str]] = None,
    actor: str = "ai_council_moderator",
    force_offline: bool = True,
) -> List[CouncilDebate]:
    """
    Executes the multi-agent AI Architecture Council workflow for a project's clusters.
    Sequence:
    1. Load project twin knowledge graph and decomposition clusters.
    2. Collect specialist opinions (Cloud Architect, Validation/QA, Security, FinOps, Regulatory).
    3. Conduct Moderator rebuttal round.
    4. Moderator synthesizes consensus CouncilDecision.
    5. Validate schema and evidence citations against knowledge graph nodes.
    6. Persist decision with status PROPOSED and record immutable audit event.
    """
    store = get_graph_store(project_id)
    valid_node_ids = set(store.graph.nodes.keys()) if store.graph.nodes else {"SYSTEM_CORE"}

    # Get decomposition clusters
    decomp_results = execute_3way_decomposition(
        store, weights=settings.weights_list, gamma=settings.DECOMP_GAMMA
    )
    raw_clusters = decomp_results.get("clusters", [])

    clusters = []
    for c in raw_clusters:
        clusters.append({
            "id": c["cluster_id"],
            "name": c["name"],
            "nodes": c["components"],
            "gxp_max": c["gxp_max_tier"],
            "readiness_avg": c["readiness_avg"],
            "total_loc": len(c["components"]) * 350,
        })

    if not clusters:
        class_nodes = [n["id"] for n in store.get_all_nodes("Class")]
        clusters = [{
            "id": "cluster_0",
            "name": "Core Service Cluster",
            "nodes": class_nodes or list(valid_node_ids)[:5],
            "gxp_max": "HIGH",
            "readiness_avg": 55.0,
            "total_loc": 2500,
        }]

    if cluster_ids:
        clusters = [c for c in clusters if c.get("id") in cluster_ids]

    specialists = [
        CloudArchitectAgent(),
        ValidationQAAgent(),
        SecurityOfficerAgent(),
        FinOpsAgent(),
        RegulatoryAffairsAgent(),
    ]
    moderator = CouncilModeratorAgent()

    debates: List[CouncilDebate] = []

    for cluster in clusters:
        cid = cluster.get("id", "cluster_unknown")
        cluster_nodes = cluster.get("nodes", [])
        cluster_valid_nodes = [nid for nid in cluster_nodes if nid in valid_node_ids]
        if not cluster_valid_nodes:
            cluster_valid_nodes = list(valid_node_ids)[:3]

        # 1. Parallel / sequential specialist opinions
        opinions: List[SpecialistOpinion] = []
        for agent in specialists:
            opinion = agent.form_opinion(cluster, cluster_valid_nodes)
            opinions.append(opinion)

        # 2. Moderator Rebuttal Round
        rebuttals = moderator.conduct_rebuttal(opinions)

        # 3. Moderator Synthesis
        offline_mode = force_offline or not settings.ANTHROPIC_API_KEY
        decision = moderator.synthesize(
            cluster_info=cluster,
            opinions=opinions,
            rebuttals=rebuttals,
            valid_node_ids=cluster_valid_nodes,
            offline_simulated=offline_mode,
        )

        # 4. Strict Schema and Evidence Validation
        is_valid, errors = validate_decision(decision, valid_node_ids)
        if not is_valid:
            logger.warning("Council decision failed validation on first attempt: %s. Retrying...", errors)
            # Retry once: filter out any invalid evidence IDs
            clean_evidence = [nid for nid in decision.evidence_node_ids if nid in valid_node_ids]
            if not clean_evidence:
                clean_evidence = cluster_valid_nodes[:2]
            decision.evidence_node_ids = clean_evidence
            is_valid, errors = validate_decision(decision, valid_node_ids)
            if not is_valid:
                raise DecisionValidationError(errors)

        # 5. Compute cryptographic hashes for reproducibility
        input_hash = hashlib.sha256(canonical_json(cluster).encode("utf-8")).hexdigest()
        prompt_meta = {
            "model_id": decision.model_id,
            "version": "1.0",
            "cluster_id": cid,
            "gxp_tier": cluster.get("gxp_max"),
        }
        prompt_hash = hashlib.sha256(canonical_json(prompt_meta).encode("utf-8")).hexdigest()

        # 6. Database Persistence
        existing_decision = (
            db.query(Decision)
            .filter(Decision.project_id == project_id, Decision.cluster_id == cid)
            .first()
        )

        if existing_decision:
            existing_decision.strategy = decision.strategy
            existing_decision.target_pattern = decision.target_pattern
            existing_decision.target_services = decision.target_services
            existing_decision.confidence = decision.confidence
            existing_decision.rationale = decision.rationale
            existing_decision.risks = decision.risks
            existing_decision.dissent = [d.model_dump() for d in decision.dissent]
            existing_decision.evidence_node_ids = decision.evidence_node_ids
            existing_decision.effort_weeks = list(decision.effort_weeks)
            existing_decision.status = "PROPOSED"
            existing_decision.model_id = decision.model_id
            existing_decision.prompt_hash = prompt_hash
            existing_decision.input_hash = input_hash
            decision_record = existing_decision
        else:
            decision_record = Decision(
                project_id=project_id,
                cluster_id=cid,
                strategy=decision.strategy,
                target_pattern=decision.target_pattern,
                target_services=decision.target_services,
                confidence=decision.confidence,
                rationale=decision.rationale,
                risks=decision.risks,
                dissent=[d.model_dump() for d in decision.dissent],
                evidence_node_ids=decision.evidence_node_ids,
                effort_weeks=list(decision.effort_weeks),
                status="PROPOSED",
                model_id=decision.model_id,
                prompt_hash=prompt_hash,
                input_hash=input_hash,
            )
            db.add(decision_record)

        db.commit()
        db.refresh(decision_record)
        decision.decision_id = decision_record.id

        # 7. Immutable Audit Trail Entry
        record_audit_event(
            db=db,
            actor=actor,
            action="COUNCIL_DECISION_PROPOSED",
            entity="Decision",
            entity_id=decision_record.id,
            payload={
                "project_id": project_id,
                "cluster_id": cid,
                "strategy": decision.strategy,
                "target_pattern": decision.target_pattern,
                "confidence": decision.confidence,
                "effort_weeks": decision.effort_weeks,
                "evidence_node_ids": decision.evidence_node_ids,
                "offline_simulated": decision.offline_simulated,
                "status": "PROPOSED",
            },
        )

        debates.append(
            CouncilDebate(
                cluster_id=cid,
                cluster_name=cluster.get("name"),
                gxp_tier=cluster.get("gxp_max", "LOW"),
                opinions=opinions,
                rebuttals=rebuttals,
                decision=decision,
            )
        )

    return debates
