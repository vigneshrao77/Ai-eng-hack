import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_password_hash
from app.db.graph_store import get_graph_store
from app.db.models import EvidencePack, Project, User
from app.db.session import SessionLocal
from app.engines.evidence.generator import generate_wave_evidence_pdf
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.twin.graph_builder import build_living_twin
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers(db):
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
    token = create_access_token(data={"sub": u.id, "role": "admin", "name": "Admin User"})
    return {"Authorization": f"Bearer {token}"}


def test_generate_wave_evidence_pdf_direct():
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == "admin@pharma.com").first()
    if not user:
        user = User(
            id="admin-test-id",
            email="admin@pharma.com",
            name="Admin User",
            role="admin",
            password_hash=get_password_hash("Pass123!"),
        )
        db.add(user)
        db.commit()

    project = db.query(Project).filter(Project.id == "acmelims-demo").first()
    if not project:
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

    result = generate_wave_evidence_pdf(
        project_id="acmelims-demo",
        wave_num=1,
        db=db,
        actor="qa_engineer@pharma.com",
    )

    assert result["status"] == "success"
    assert result["wave"] == "Wave_1"
    pdf_path = result["file_path"]
    assert os.path.exists(pdf_path)
    assert result["size_bytes"] > 5000

    # Verify PDF magic bytes
    with open(pdf_path, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-", "Generated file must be a valid PDF document"

    # Verify stored in DB
    pack = db.query(EvidencePack).filter(EvidencePack.id == result["pack_id"]).first()
    assert pack is not None
    assert pack.sha256_hash == result["sha256_hash"]
    db.close()


def test_evidence_api_generate_list_and_download(auth_headers):
    db: Session = SessionLocal()
    project = db.query(Project).filter(Project.id == "acmelims-demo").first()
    if not project:
        user = db.query(User).filter(User.email == "admin@pharma.com").first()
        project = Project(
            id="acmelims-demo",
            name="AcmeLIMS Legacy Monolith",
            repo_url="demo-lims",
            target_cloud="AWS",
            created_by=user.id,
        )
        db.add(project)
        db.commit()

    # 1. Trigger Evidence Generation via API
    resp_gen = client.post(
        f"/projects/{project.id}/evidence/1",
        headers=auth_headers,
    )
    assert resp_gen.status_code == 200
    gen_data = resp_gen.json()
    assert gen_data["status"] == "success"
    assert "sha256_hash" in gen_data
    assert gen_data["size_bytes"] > 5000

    # 2. List Evidence Packs
    resp_list = client.get(
        f"/projects/{project.id}/evidence",
        headers=auth_headers,
    )
    assert resp_list.status_code == 200
    packs = resp_list.json()["evidence_packs"]
    assert len(packs) >= 1
    target_pack = next(p for p in packs if p["wave"] == "Wave_1")
    assert target_pack["sha256_hash"] == gen_data["sha256_hash"]

    # 3. Download Binary PDF
    resp_dl = client.get(
        f"/projects/{project.id}/evidence/1/download",
        headers=auth_headers,
    )
    assert resp_dl.status_code == 200
    assert resp_dl.headers["content-type"] == "application/pdf"
    assert resp_dl.content.startswith(b"%PDF-")
    assert len(resp_dl.content) == gen_data["size_bytes"]

    # 4. Verify Cryptographic SHA-256 Audit Chain
    resp_audit = client.get("/audit/verify", headers=auth_headers)
    assert resp_audit.status_code == 200
    assert resp_audit.json()["valid"] is True
    db.close()
