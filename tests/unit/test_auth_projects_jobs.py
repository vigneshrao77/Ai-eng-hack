import io
import zipfile
import pytest
from app.db.models import User
from app.core.auth import get_password_hash


@pytest.fixture
def auth_tokens(client, db):
    # Ensure test users exist
    users = [
        ("test_arch@modernrx.internal", "Architect User", "architect"),
        ("test_viewer@modernrx.internal", "Viewer User", "viewer"),
    ]
    tokens = {}
    for email, name, role in users:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(email=email, name=name, role=role, password_hash=get_password_hash("Pass123!"))
            db.add(u)
            db.commit()

        res = client.post("/auth/login", json={"email": email, "password": "Pass123!"})
        assert res.status_code == 200
        tokens[role] = res.json()["access_token"]

    return tokens


def test_auth_login_success_and_failure(client, auth_tokens):
    # Success
    res = client.post("/auth/login", json={"email": "test_arch@modernrx.internal", "password": "Pass123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "architect"

    # Bad password
    res = client.post("/auth/login", json={"email": "test_arch@modernrx.internal", "password": "WrongPassword"})
    assert res.status_code == 401

    # Non-existent email
    res = client.post("/auth/login", json={"email": "nobody@modernrx.internal", "password": "Pass123!"})
    assert res.status_code == 401


def test_rbac_project_creation(client, auth_tokens):
    viewer_token = auth_tokens["viewer"]
    arch_token = auth_tokens["architect"]

    # Viewer should be forbidden from creating project
    res = client.post(
        "/projects",
        json={"name": "ForbiddenProject", "target_cloud": "AWS"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403

    # Architect should succeed
    res = client.post(
        "/projects",
        json={"name": "ArchitectProject", "target_cloud": "AWS"},
        headers={"Authorization": f"Bearer {arch_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "ArchitectProject"
    assert "id" in data


def test_safe_zip_upload_and_path_traversal_rejection(client, auth_tokens):
    arch_token = auth_tokens["architect"]

    # Create project first
    res = client.post(
        "/projects",
        json={"name": "UploadTestProject", "target_cloud": "AWS"},
        headers={"Authorization": f"Bearer {arch_token}"},
    )
    project_id = res.json()["id"]

    # 1. Test Malicious ZIP with Path Traversal
    malicious_buf = io.BytesIO()
    with zipfile.ZipFile(malicious_buf, "w") as zf:
        zf.writestr("../../etc/passwd", "root:x:0:0:")
    malicious_buf.seek(0)

    res_malicious = client.post(
        f"/projects/{project_id}/upload",
        files={"file": ("malicious.zip", malicious_buf, "application/zip")},
        headers={"Authorization": f"Bearer {arch_token}"},
    )
    assert res_malicious.status_code == 400
    assert "path traversal" in res_malicious.json()["detail"].lower()

    # 2. Test Safe ZIP
    safe_buf = io.BytesIO()
    with zipfile.ZipFile(safe_buf, "w") as zf:
        zf.writestr("src/main/java/App.java", "public class App {}")
    safe_buf.seek(0)

    res_safe = client.post(
        f"/projects/{project_id}/upload",
        files={"file": ("safe.zip", safe_buf, "application/zip")},
        headers={"Authorization": f"Bearer {arch_token}"},
    )
    assert res_safe.status_code == 200
    assert res_safe.json()["status"] == "uploaded"
