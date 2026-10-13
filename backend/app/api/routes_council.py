from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.models import Decision, Project, User
from app.db.session import get_db
from app.engines.council.runner import run_council_for_clusters
from app.engines.council.schema import CouncilDebate

router = APIRouter(prefix="/projects", tags=["Council"])


class RunCouncilRequest(BaseModel):
    cluster_ids: Optional[List[str]] = None
    force_offline: Optional[bool] = False


@router.post("/{id}/council/run")
def trigger_council_run(
    id: str,
    request: Optional[RunCouncilRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes the multi-agent AI Architecture Council debate and synthesis for project clusters.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cluster_ids = request.cluster_ids if request else None
    from app.config import get_settings
    settings = get_settings()
    force_offline = request.force_offline if (request and request.force_offline is not None) else False

    debates = run_council_for_clusters(
        project_id=id,
        db=db,
        cluster_ids=cluster_ids,
        actor=current_user.email,
        force_offline=force_offline,
    )

    return {
        "status": "success",
        "project_id": id,
        "cluster_count": len(debates),
        "debates": [d.model_dump() for d in debates],
    }


@router.get("/{id}/council/decisions")
def get_council_decisions(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all generated Council decisions and their approval states for a project.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    decisions = (
        db.query(Decision)
        .filter(Decision.project_id == id)
        .order_by(Decision.cluster_id.asc())
        .all()
    )

    results = []
    for d in decisions:
        approvals_list = [
            {
                "id": a.id,
                "user_id": a.user_id,
                "action": a.action,
                "comment": a.comment,
                "timestamp": a.ts.isoformat(),
            }
            for a in d.approvals
        ]
        results.append({
            "id": d.id,
            "cluster_id": d.cluster_id,
            "strategy": d.strategy,
            "target_pattern": d.target_pattern,
            "target_services": d.target_services,
            "confidence": d.confidence,
            "rationale": d.rationale,
            "risks": d.risks,
            "dissent": d.dissent,
            "evidence_node_ids": d.evidence_node_ids,
            "effort_weeks": d.effort_weeks,
            "status": d.status,
            "model_id": d.model_id,
            "prompt_hash": d.prompt_hash,
            "input_hash": d.input_hash,
            "created_at": d.created_at.isoformat(),
            "approvals": approvals_list,
        })

    return {
        "project_id": id,
        "count": len(results),
        "decisions": results,
    }
