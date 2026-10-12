import pytest
from app.db.graph_store import get_graph_store
from app.engines.twin.graph_builder import build_living_twin
from app.engines.gxp.scanner import run_gxp_scan
from app.core.auth import get_password_hash
from app.db.models import User


@pytest.fixture
def qa_tokens(client, db):
    users = [
        ("qa_lead@modernrx.internal", "QA Approver Lead", "qa_approver"),
        ("dev_viewer@modernrx.internal", "Viewer Dev", "viewer"),
    ]
    tokens = {}
    for email, name, role in users:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(email=email, name=name, role=role, password_hash=get_password_hash("Pass123!"))
            db.add(u)
            db.commit()
        res = client.post("/auth/login", json={"email": email, "password": "Pass123!"})
        tokens[role] = res.json()["access_token"]
    return tokens


def test_gxp_scanner_classifications_and_gaps():
    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")

    result = run_gxp_scan(store)
    tiers = result["node_tiers"]
    tags = result["node_tags"]
    gaps = result["gaps"]

    # Verify Regulated Core
    assert tiers["BatchReleaseService"] == "HIGH"
    assert "PRODUCT_RELEASE" in tags["BatchReleaseService"]

    assert tiers["ReviewService"] == "HIGH"
    assert "E_SIGNATURE" in tags["ReviewService"]

    assert tiers["AuditTrailService"] == "HIGH"
    assert "AUDIT_TRAIL" in tags["AuditTrailService"]

    assert tiers["SampleService"] == "HIGH"
    assert "DATA_INTEGRITY" in tags["SampleService"]

    assert "REPORTING_ONLY" in tags["ReportService"]
    assert tiers["UnusedLegacyCalculator"] == "LOW"

    # Verify Planted Compliance Gaps
    gap_ids = [g["id"] for g in gaps]
    assert "GAP_AUDIT_NO_REASON" in gap_ids
    assert "GAP_LOCAL_TIMESTAMP" in gap_ids
    assert "GAP_LOCAL_FS_IMPORT" in gap_ids
    assert "GAP_SHARED_GXP_TABLE" in gap_ids
    assert "GAP_HARDCODED_CREDS" in gap_ids


def test_gxp_override_and_audit_trail(client, qa_tokens):
    build_living_twin("acmelims-demo", "demo-lims")
    qa_token = qa_tokens["qa_approver"]
    viewer_token = qa_tokens["viewer"]

    # 1. Viewer is blocked from QA override
    res_forbidden = client.patch(
        "/projects/acmelims-demo/gxp/ReportService",
        json={"new_tier": "HIGH", "reason": "Arbitrary change attempt"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res_forbidden.status_code == 403

    # 2. QA Approver successfully overrides with mandatory reason
    res_success = client.patch(
        "/projects/acmelims-demo/gxp/ReportService",
        json={"new_tier": "MEDIUM", "reason": "Qualified Person determined report contains critical release CoA metadata"},
        headers={"Authorization": f"Bearer {qa_token}"},
    )
    assert res_success.status_code == 200
    assert res_success.json()["new_tier"] == "MEDIUM"

    # 3. Verify node in Graph Store is updated
    store = get_graph_store("acmelims-demo")
    node = store.get_node("ReportService")
    assert node["gxp_tier"] == "MEDIUM"

    # 4. Verify audit chain integrity with new override block
    res_verify = client.get("/audit/verify", headers={"Authorization": f"Bearer {qa_token}"})
    assert res_verify.status_code == 200
    assert res_verify.json()["valid"] is True
