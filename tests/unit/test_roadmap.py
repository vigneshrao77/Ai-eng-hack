import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_password_hash
from app.db.graph_store import get_graph_store
from app.db.models import Project, User
from app.db.session import SessionLocal
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.roadmap.montecarlo import run_monte_carlo_simulation
from app.engines.roadmap.scheduler import schedule_roadmap
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


def test_scheduler_constraints_and_freeze_window():
    workload = [
        {
            "id": "MOD-reporting",
            "name": "Reporting Service Rehost",
            "gxp_tier": "LOW",
            "strategy": "Rehost",
            "effort_triple": (1.0, 2.0, 3.0),
            "dependencies": [],
        },
        {
            "id": "MOD-sample_core",
            "name": "Sample Core Replatform",
            "gxp_tier": "HIGH",
            "strategy": "Replatform",
            "effort_triple": (3.0, 4.0, 6.0),
            "dependencies": [],
        },
        {
            "id": "MOD-batch_core",
            "name": "Batch Release Replatform",
            "gxp_tier": "HIGH",
            "strategy": "Replatform",
            "effort_triple": (2.0, 3.0, 5.0),
            "dependencies": [],
        },
    ]

    freeze_windows = [(5, 7)]
    result = schedule_roadmap(workload_tasks=workload, squads=2, freeze_windows=freeze_windows)

    assert result["status"] == "success"
    tasks = result["tasks"]
    task_map = {t["id"]: t for t in tasks}

    # 1. Foundation tasks must precede all workload tasks
    fnd_ends = [t["end_week"] for t in tasks if t["id"].startswith("FND-")]
    max_fnd_end = max(fnd_ends)

    for wt in workload:
        scheduled_wt = task_map[wt["id"]]
        assert scheduled_wt["start_week"] >= max_fnd_end

    # 2. GxP Freeze Window: No HIGH-tier cutover inside freeze weeks 5..7
    for t in tasks:
        if t["gxp_tier"] == "HIGH":
            cutover = t["end_week"]
            assert not (5 <= cutover <= 7), f"HIGH-tier task {t['id']} cut over during freeze window: week {cutover}"

    # 3. Waves structure exists
    assert len(result["waves"]) >= 2
    assert result["waves"][0]["theme"] == "Foundation"

    # 4. Critical path identified
    assert len(result["critical_path"]) > 0


def test_monte_carlo_statistical_invariants():
    tasks = [
        {
            "id": "FND-01",
            "duration": 2,
            "start_week": 0,
            "end_week": 2,
            "dependencies": [],
            "effort_triple": (1.5, 2.0, 3.0),
        },
        {
            "id": "MOD-task1",
            "duration": 4,
            "start_week": 2,
            "end_week": 6,
            "dependencies": ["FND-01"],
            "effort_triple": (3.0, 4.0, 6.5),
        },
        {
            "id": "MOD-task2",
            "duration": 5,
            "start_week": 6,
            "end_week": 11,
            "dependencies": ["MOD-task1"],
            "effort_triple": (4.0, 5.0, 8.0),
        },
    ]

    mc = run_monte_carlo_simulation(tasks, runs=10000, target_weeks=12.0, seed=123)

    assert mc["runs"] == 10000
    p50 = mc["p50_weeks"]
    p80 = mc["p80_weeks"]
    p95 = mc["p95_weeks"]

    # Critical requirement: P50 <= P80 <= P95
    assert p50 <= p80 <= p95, f"Percentiles violation: P50={p50}, P80={p80}, P95={p95}"

    # Prob meeting target
    assert 0.0 <= mc["prob_meeting_target"] <= 100.0

    # Histogram
    assert len(mc["histogram"]) == 20
    assert sum(b["count"] for b in mc["histogram"]) == 10000

    # Sensitivity Drivers
    assert len(mc["drivers_of_uncertainty"]) > 0
    top_driver = mc["drivers_of_uncertainty"][0]
    assert "task_id" in top_driver
    assert "variance_contribution" in top_driver


def test_roadmap_api_and_whatif_scenario(auth_headers):
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

    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")
    run_gxp_scan(store)

    # 1. Trigger Baseline Roadmap Generation
    resp = client.post(
        f"/projects/{project.id}/roadmap",
        json={"squads": 2, "freeze_windows": [[12, 14]], "target_weeks": 26.0},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project.id
    assert "schedule" in data
    assert "monte_carlo" in data
    baseline_makespan = data["schedule"]["makespan_weeks"]
    baseline_p80 = data["monte_carlo"]["p80_weeks"]
    assert baseline_makespan > 0
    assert baseline_p80 > 0

    # 2. Get Roadmap Endpoint
    resp_get = client.get(f"/projects/{project.id}/roadmap", headers=auth_headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["schedule"]["makespan_weeks"] == baseline_makespan

    # 3. What-If Interactive Simulation (add 2 squads -> squads=4)
    resp_whatif = client.post(
        f"/projects/{project.id}/roadmap/whatif",
        json={"squads": 4, "freeze_windows": [[10, 12]], "target_weeks": 20.0},
        headers=auth_headers,
    )
    assert resp_whatif.status_code == 200
    whatif_data = resp_whatif.json()
    assert whatif_data["schedule"]["squads"] == 4
    # More squads should result in less or equal makespan
    assert whatif_data["schedule"]["makespan_weeks"] <= baseline_makespan

    # 4. Verify Cryptographic SHA-256 Audit Chain
    resp_audit = client.get("/audit/verify", headers=auth_headers)
    assert resp_audit.status_code == 200
    assert resp_audit.json()["valid"] is True
    db.close()
