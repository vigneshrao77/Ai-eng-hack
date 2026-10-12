from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import AuditLog, User
from app.core.auth import get_current_user
from app.core.audit import verify_audit_chain

router = APIRouter(prefix="/audit", tags=["Audit Log"])


class AuditLogResponse(BaseModel):
    id: int
    ts: str
    actor: str
    action: str
    entity: str
    entity_id: str
    payload_json: dict
    prev_hash: str
    hash: str


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    entity: Optional[str] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditLog)
    if entity:
        query = query.filter(AuditLog.entity == entity)
    if action:
        query = query.filter(AuditLog.action == action)

    events = query.order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "ts": e.ts.isoformat(),
            "actor": e.actor,
            "action": e.action,
            "entity": e.entity,
            "entity_id": e.entity_id,
            "payload_json": e.payload_json,
            "prev_hash": e.prev_hash,
            "hash": e.hash,
        }
        for e in events
    ]


@router.get("/verify")
def verify_chain(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify cryptographic integrity of the entire append-only SHA-256 audit log."""
    return verify_audit_chain(db)
