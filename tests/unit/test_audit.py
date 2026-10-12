from app.core.audit import record_audit_event, verify_audit_chain, GENESIS_PREV_HASH
from app.db.models import AuditLog


def test_audit_hash_chain_genesis_and_append(db):
    # Verify initial chain verification
    status = verify_audit_chain(db)
    assert status["valid"] is True

    # Record first event
    evt1 = record_audit_event(
        db=db,
        actor="system@modernrx.internal",
        action="SYSTEM_INIT",
        entity="System",
        entity_id="0",
        payload={"message": "System baseline initialized"},
    )
    assert evt1.prev_hash == GENESIS_PREV_HASH
    assert len(evt1.hash) == 64

    # Record second event
    evt2 = record_audit_event(
        db=db,
        actor="architect@modernrx.internal",
        action="PROJECT_CREATED",
        entity="Project",
        entity_id="proj-123",
        payload={"project_name": "AcmeLIMS", "cloud": "AWS"},
    )
    assert evt2.prev_hash == evt1.hash
    assert len(evt2.hash) == 64

    # Verify intact chain
    status = verify_audit_chain(db)
    assert status["valid"] is True
    assert status["total_events"] >= 2
    assert status["tampered_at_id"] is None


def test_audit_hash_chain_tamper_detection(db):
    # Retrieve the last event and mutate its payload in database
    last_evt = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert last_evt is not None

    original_payload = dict(last_evt.payload_json)
    # Maliciously tamper with payload
    last_evt.payload_json = {"malicious_tamper": True}
    db.commit()

    # Verification must fail and report the exact tampered ID
    status = verify_audit_chain(db)
    assert status["valid"] is False
    assert status["tampered_at_id"] == last_evt.id
    assert "Tampering detected" in status["message"]

    # Restore payload and verify recovery
    last_evt.payload_json = original_payload
    db.commit()

    recovered_status = verify_audit_chain(db)
    assert recovered_status["valid"] is True


def test_audit_prev_hash_break_detection(db):
    last_evt = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert last_evt is not None
    orig_prev = last_evt.prev_hash

    # Maliciously alter prev_hash
    last_evt.prev_hash = "deadbeef" * 8
    db.commit()

    status = verify_audit_chain(db)
    assert status["valid"] is False
    assert status["tampered_at_id"] == last_evt.id
    assert "prev_hash mismatch" in status["message"]

    # Restore
    last_evt.prev_hash = orig_prev
    db.commit()
    assert verify_audit_chain(db)["valid"] is True


def test_audit_secrets_never_persisted(db):
    evt = record_audit_event(
        db=db,
        actor="dev@pharma.com",
        action="CONFIG_UPDATED",
        entity="Config",
        entity_id="app.properties",
        payload={
            "db_password": "supersecretpassword123!",
            "api_key": "sk-ant-api03-abcdef123456789",
            "normal_setting": "prod-east-1",
        },
    )
    # The payload in database must NOT contain the raw plaintext secret
    stored = evt.payload_json
    assert stored["db_password"] != "supersecretpassword123!"
    assert "***" in stored["db_password"]
    assert stored["normal_setting"] == "prod-east-1"
