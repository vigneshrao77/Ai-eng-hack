from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.audit import record_audit_event
from app.core.auth import get_current_user
from app.db.models import Approval, Decision, User
from app.db.session import get_db

router = APIRouter(prefix="/decisions", tags=["Approvals"])


class ApprovalActionRequest(BaseModel):
    comment: Optional[str] = Field(default="", description="QA rationale or rejection reason")


@router.post("/{id}/approve")
def approve_decision(
    id: str,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Human QA approval gate for an AI Architecture Council decision.
    High-risk decisions cannot bypass QA approval.
    """
    decision = db.query(Decision).filter(Decision.id == id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision.status = "APPROVED"
    approval = Approval(
        decision_id=id,
        user_id=current_user.id,
        action="APPROVED",
        comment=request.comment or "Approved by QA Lead",
    )
    db.add(approval)
    db.commit()

    record_audit_event(
        db=db,
        actor=current_user.email,
        action="DECISION_APPROVED",
        entity="Decision",
        entity_id=id,
        payload={
            "project_id": decision.project_id,
            "cluster_id": decision.cluster_id,
            "strategy": decision.strategy,
            "user_role": current_user.role,
            "comment": request.comment,
        },
    )

    return {
        "status": "APPROVED",
        "decision_id": id,
        "cluster_id": decision.cluster_id,
        "approved_by": current_user.email,
        "comment": request.comment,
    }


@router.post("/{id}/reject")
def reject_decision(
    id: str,
    request: ApprovalActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Rejects an AI Architecture Council decision with mandatory explanation.
    """
    if not request.comment or len(request.comment.strip()) < 5:
        raise HTTPException(status_code=400, detail="Rejection reason of at least 5 characters is mandatory")

    decision = db.query(Decision).filter(Decision.id == id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision.status = "REJECTED"
    approval = Approval(
        decision_id=id,
        user_id=current_user.id,
        action="REJECTED",
        comment=request.comment,
    )
    db.add(approval)
    db.commit()

    record_audit_event(
        db=db,
        actor=current_user.email,
        action="DECISION_REJECTED",
        entity="Decision",
        entity_id=id,
        payload={
            "project_id": decision.project_id,
            "cluster_id": decision.cluster_id,
            "strategy": decision.strategy,
            "user_role": current_user.role,
            "comment": request.comment,
        },
    )

    return {
        "status": "REJECTED",
        "decision_id": id,
        "cluster_id": decision.cluster_id,
        "rejected_by": current_user.email,
        "comment": request.comment,
    }
