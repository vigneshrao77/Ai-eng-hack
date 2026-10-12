from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import GxpOverride, User
from app.db.graph_store import get_graph_store
from app.engines.gxp.scanner import run_gxp_scan
from app.core.auth import get_current_user, require_roles
from app.core.audit import record_audit_event
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["GxP Criticality Scanner"])


class OverrideGxpRequest(BaseModel):
    new_tier: str = Field(..., pattern="^(HIGH|MEDIUM|LOW)$")
    reason: str = Field(..., min_length=5, max_length=500)


@router.get("/{id}/gxp")
def get_gxp_assessment(id: str):
    store = get_graph_store(id)
    scan_result = run_gxp_scan(store)
    return scan_result


@router.patch("/{id}/gxp/{node_id}")
def override_gxp_tier(
    id: str,
    node_id: str,
    request: OverrideGxpRequest,
    current_user: User = Depends(require_roles(["qa_approver", "admin"])),
    db: Session = Depends(get_db),
):
    store = get_graph_store(id)
    node = store.get_node(node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in Twin Graph",
        )

    old_tier = node.get("gxp_tier", "LOW")
    if old_tier == request.new_tier:
        return {
            "status": "unchanged",
            "node_id": node_id,
            "old_tier": old_tier,
            "new_tier": request.new_tier,
            "reason": request.reason,
            "actor": current_user.email,
        }

    # Record QA Override in database
    override_record = GxpOverride(
        project_id=id,
        node_id=node_id,
        old_tier=old_tier,
        new_tier=request.new_tier,
        reason=request.reason,
        user_id=current_user.id,
    )
    db.add(override_record)
    db.commit()

    # Immutable Audit Log Chain
    record_audit_event(
        db=db,
        actor=current_user.email,
        action="GXP_TIER_OVERRIDDEN",
        entity="TwinNode",
        entity_id=node_id,
        payload={
            "project_id": id,
            "node_id": node_id,
            "old_tier": old_tier,
            "new_tier": request.new_tier,
            "reason": request.reason,
            "user_role": current_user.role,
        },
    )

    # Mutate Graph Store
    store.graph.nodes[node_id]["gxp_tier"] = request.new_tier
    store.graph.nodes[node_id].setdefault("gxp_rationales", []).append(
        f"HUMAN QA OVERRIDE by {current_user.email}: {request.reason}"
    )
    store.persist()

    logger.info(f"QA Override applied: {node_id} {old_tier} -> {request.new_tier} by {current_user.email}")
    return {
        "status": "overridden",
        "node_id": node_id,
        "old_tier": old_tier,
        "new_tier": request.new_tier,
        "reason": request.reason,
        "actor": current_user.email,
    }
