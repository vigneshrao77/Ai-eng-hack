import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.models import AuditLog
from app.core.logging import logger, mask_secrets

GENESIS_PREV_HASH = "0" * 64


def canonical_json(data: Any) -> str:
    """Produce deterministic canonical JSON string for cryptographic hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def compute_event_hash(prev_hash: str, payload_str: str) -> str:
    content = f"{prev_hash}{payload_str}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def record_audit_event(
    db: Session,
    actor: str,
    action: str,
    entity: str,
    entity_id: str,
    payload: Dict[str, Any],
) -> AuditLog:
    """Append a new tamper-evident audit record to the cryptographic hash chain."""
    # Find latest event in chain
    latest_event = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = latest_event.hash if latest_event else GENESIS_PREV_HASH

    # Redact any passwords/tokens from audit payloads
    sanitized_payload = {}
    for k, v in payload.items():
        k_lower = str(k).lower()
        if any(sec in k_lower for sec in ("password", "secret", "token", "api_key", "credential")):
            sanitized_payload[k] = "***"
        elif isinstance(v, str):
            sanitized_payload[k] = mask_secrets(v)
        else:
            sanitized_payload[k] = v

    payload_canonical = canonical_json(sanitized_payload)
    event_hash = compute_event_hash(prev_hash, payload_canonical)

    audit_entry = AuditLog(
        ts=datetime.now(timezone.utc),
        actor=actor,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        payload_json=sanitized_payload,
        prev_hash=prev_hash,
        hash=event_hash,
    )

    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)

    logger.info(f"Audit event recorded: [{action}] on {entity}:{entity_id} by {actor} (hash: {event_hash[:8]}...)")
    return audit_entry


def verify_audit_chain(db: Session) -> Dict[str, Any]:
    """Verify entire SHA-256 audit log hash chain from genesis to tip."""
    events = db.query(AuditLog).order_by(AuditLog.id.asc()).all()

    if not events:
        return {
            "valid": True,
            "total_events": 0,
            "tampered_at_id": None,
            "message": "Audit chain is empty. Genesis state valid.",
        }

    expected_prev = GENESIS_PREV_HASH

    for event in events:
        if event.prev_hash != expected_prev:
            return {
                "valid": False,
                "total_events": len(events),
                "tampered_at_id": event.id,
                "message": f"Hash chain broken at event #{event.id}: prev_hash mismatch. Expected {expected_prev[:12]}, found {event.prev_hash[:12]}",
            }

        payload_canonical = canonical_json(event.payload_json)
        calculated_hash = compute_event_hash(event.prev_hash, payload_canonical)

        if event.hash != calculated_hash:
            return {
                "valid": False,
                "total_events": len(events),
                "tampered_at_id": event.id,
                "message": f"Tampering detected at event #{event.id}: payload does not match cryptographic hash. Expected {calculated_hash[:12]}, found {event.hash[:12]}",
            }

        expected_prev = event.hash

    return {
        "valid": True,
        "total_events": len(events),
        "tampered_at_id": None,
        "message": f"Cryptographic audit chain fully verified: {len(events)} events authentic and tamper-free.",
    }
