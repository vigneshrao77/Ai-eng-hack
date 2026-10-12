import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.db.models import Decision, Project, User
from app.db.session import SessionLocal
from app.engines.council.runner import run_council_for_clusters
from app.engines.council.schema import CouncilDecision, DissentItem
from app.engines.council.validator import validate_decision
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers(db):
    from app.core.auth import get_password_hash
    u = db.query(User).filter(User.email == "admin@pharma.com").first()
    if not u:
        u = User(
            id="admin-test-id",
            email="admin@pharma.com",
            name="Admin User",
            role="admin",
            password_hash=get_password_hash("Pass123!"),
        )
        db.add(u)
        db.commit()
    token = create_access_token(
        data={"sub": u.id, "role": "admin", "name": "Admin User"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def qa_headers(db):
    from app.core.auth import get_password_hash
    u = db.query(User).filter(User.email == "qa@pharma.com").first()
    if not u:
        u = User(
            id="qa-test-id",
            email="qa@pharma.com",
            name="QA Lead",
            role="qa_approver",
            password_hash=get_password_hash("Pass123!"),
        )
        db.add(u)
        db.commit()
    token = create_access_token(
        data={"sub": u.id, "role": "qa_approver", "name": "QA Lead"}
    )
    return {"Authorization": f"Bearer {token}"}


def test_validator_accepts_valid_decision():
    valid_nodes = {"com.acme.lims.service.SampleService", "com.acme.lims.service.AuditService"}
    decision = CouncilDecision(
        cluster_id="cluster_0",
        strategy="Replatform",
        target_pattern=["StranglerFig", "Containerized"],
        target_services=["AWS ECS", "Amazon RDS"],
        confidence=0.88,
        rationale="Substantive consensus rationale for replatforming the regulated service cluster.",
        risks=["Dual-write data consistency"],
        dissent=[
            DissentItem(
                agent="Validation & QA Lead",
                position="Preferred Retain",
                reason="Minimize 21 CFR Part 11 re-validation scope",
            )
        ],
        evidence_node_ids=["com.acme.lims.service.SampleService"],
        effort_weeks=(3.0, 4.5, 6.0),
        offline_simulated=True,
    )
    is_valid, errors = validate_decision(decision, valid_nodes)
    assert is_valid is True
    assert len(errors) == 0


def test_validator_rejects_hallucinated_evidence_node_ids():
    valid_nodes = {"com.acme.lims.service.SampleService"}
    decision = CouncilDecision(
        cluster_id="cluster_0",
        strategy="Refactor",
        target_pattern=["EventDriven"],
        target_services=["RabbitMQ"],
        confidence=0.75,
        rationale="Rationale citing nonexistent hallucinated classes.",
        risks=[],
        dissent=[],
        evidence_node_ids=["com.nonexistent.FakeClass", "com.invented.PhantomService"],
        effort_weeks=(2.0, 3.0, 5.0),
        offline_simulated=True,
    )
    is_valid, errors = validate_decision(decision, valid_nodes)
    assert is_valid is False
    assert any("Unknown evidence node IDs cited" in err for err in errors)


def test_validator_rejects_invalid_effort_estimates():
    valid_nodes = {"com.acme.lims.service.SampleService"}
    # Optimistic (6.0) > Likely (4.0)
    decision = CouncilDecision(
        cluster_id="cluster_0",
        strategy="Refactor",
        target_pattern=["EventDriven"],
        target_services=["RabbitMQ"],
        confidence=0.75,
        rationale="Invalid effort ordering rationale.",
        risks=[],
        dissent=[],
        evidence_node_ids=["com.acme.lims.service.SampleService"],
        effort_weeks=(6.0, 4.0, 5.0),
        offline_simulated=True,
    )
    is_valid, errors = validate_decision(decision, valid_nodes)
    assert is_valid is False
    assert any("Optimistic effort" in err for err in errors)


def test_council_runner_and_approval_workflow(auth_headers, qa_headers):
    from app.engines.twin.graph_builder import build_living_twin
    from app.engines.gxp.scanner import run_gxp_scan
    from app.db.graph_store import get_graph_store

    db: Session = SessionLocal()
    project = db.query(Project).filter(Project.id == "acmelims-demo").first()
    if not project:
        user = db.query(User).filter(User.email == "admin@pharma.com").first()
        if not user:
            user = User(
                email="admin@pharma.com",
                name="Admin User",
                role="admin",
                password_hash="test",
            )
            db.add(user)
            db.commit()
        project = Project(
            id="acmelims-demo",
            name="AcmeLIMS Legacy Monolith",
            repo_url="demo-lims",
            target_cloud="AWS",
            created_by=user.id,
        )
        db.add(project)
        db.commit()

    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")
    run_gxp_scan(store)

    # 1. Run Council
    resp = client.post(
        f"/projects/{project.id}/council/run",
        json={"force_offline": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["cluster_count"] >= 1
    debates = data["debates"]
    first_debate = debates[0]
    assert len(first_debate["opinions"]) == 5
    assert "rebuttals" in first_debate
    decision = first_debate["decision"]
    assert decision["strategy"] in ["Retain", "Rehost", "Relocate", "Replatform", "Repurchase", "Refactor", "Retire"]
    assert decision["offline_simulated"] is True
    assert decision["status"] == "PROPOSED"
    assert len(decision["evidence_node_ids"]) > 0

    # 2. Query Decisions
    resp_decisions = client.get(
        f"/projects/{project.id}/council/decisions",
        headers=auth_headers,
    )
    assert resp_decisions.status_code == 200
    dec_list = resp_decisions.json()["decisions"]
    assert len(dec_list) >= 1
    target_decision = dec_list[0]
    dec_id = target_decision["id"]

    # 3. QA Approval Gate
    resp_approve = client.post(
        f"/decisions/{dec_id}/approve",
        json={"comment": "Approved following GxP risk assessment and CSA testing plan."},
        headers=qa_headers,
    )
    assert resp_approve.status_code == 200
    assert resp_approve.json()["status"] == "APPROVED"

    # Verify status changed in DB
    updated_dec = db.query(Decision).filter(Decision.id == dec_id).first()
    assert updated_dec.status == "APPROVED"

    # 4. Rejection endpoint test with another decision or re-rejecting with comment validation
    resp_bad_reject = client.post(
        f"/decisions/{dec_id}/reject",
        json={"comment": ""},
        headers=qa_headers,
    )
    assert resp_bad_reject.status_code == 400

    resp_reject = client.post(
        f"/decisions/{dec_id}/reject",
        json={"comment": "Insufficient evidence provided for data migration continuity."},
        headers=qa_headers,
    )
    assert resp_reject.status_code == 200
    assert resp_reject.json()["status"] == "REJECTED"

    # 5. Verify Cryptographic SHA-256 Audit Chain
    resp_audit = client.get("/audit/verify", headers=auth_headers)
    assert resp_audit.status_code == 200
    assert resp_audit.json()["valid"] is True
    db.close()
