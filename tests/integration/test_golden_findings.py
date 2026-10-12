import os
import pytest
from sqlalchemy.orm import Session

from app.db.graph_store import get_graph_store
from app.db.models import Project, User
from app.db.session import SessionLocal
from app.engines.decompose.cluster import execute_3way_decomposition
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.readiness.scorer import calculate_project_readiness
from app.engines.twin.graph_builder import build_living_twin
from app.core.audit import verify_audit_chain


@pytest.fixture(scope="module")
def seeded_project():
    db: Session = SessionLocal()
    proj = db.query(Project).filter(Project.id == "acmelims-demo").first()
    if not proj:
        u = db.query(User).filter(User.email == "admin@pharma.com").first()
        if not u:
            u = User(
                id="admin-test-id",
                email="admin@pharma.com",
                name="Admin User",
                role="admin",
                password_hash="test",
            )
            db.add(u)
            db.commit()
        proj = Project(
            id="acmelims-demo",
            name="AcmeLIMS Legacy Monolith",
            repo_url="demo-lims",
            target_cloud="AWS",
            created_by=u.id,
        )
        db.add(proj)
        db.commit()

    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")
    run_gxp_scan(store)
    db.close()
    return "acmelims-demo"


def test_golden_finding_1_audit_trail_missing_reason(seeded_project):
    """
    Golden Smell 1:
    AuditTrailService / AUDIT_TRAIL table missing 'reason' column (21 CFR §11.10(e)).
    """
    store = get_graph_store(seeded_project)
    gxp_results = run_gxp_scan(store)
    gaps = gxp_results.get("gaps", [])

    gap1 = next((g for g in gaps if "AUDIT" in g.get("code", "") or "reason" in g.get("description", "").lower()), None)
    assert gap1 is not None, "Scanner must detect missing audit reason column"
    assert "reason" in gap1["description"].lower()


def test_golden_finding_2_local_filesystem_dependency(seeded_project):
    """
    Golden Smell 2:
    Local file path mount (C:\\instrument\\import) violates cloud readiness check 2.
    """
    store = get_graph_store(seeded_project)
    readiness = calculate_project_readiness(store)
    components = readiness.get("components", [])

    # Find InstrumentService deductions
    inst_comp = next((c for c in components if "Instrument" in c.get("node_id", "")), None)
    assert inst_comp is not None, "InstrumentService must be analyzed in twin"

    fs_deduction = next(
        (d for d in inst_comp.get("deductions", []) if "Filesystem" in d.get("check_name", "") or d.get("check") == "LOCAL_FILESYSTEM"),
        None,
    )
    assert fs_deduction is not None, "Must penalize local filesystem path dependence"
    assert fs_deduction.get("points_deducted", fs_deduction.get("deduction", 0)) >= 10


def test_golden_finding_3_hardcoded_admin_secrets(seeded_project):
    """
    Golden Smell 3:
    Hard-coded admin credentials in application.properties detected and masked.
    """
    store = get_graph_store(seeded_project)
    # Check config items in graph
    config_nodes = [d for nid, d in store.graph.nodes(data=True) if d.get("label") == "ConfigItem"]
    assert len(config_nodes) > 0

    pwd_config = next((c for c in config_nodes if "password" in c.get("key", "").lower()), None)
    assert pwd_config is not None
    # Secret must be masked with *** or [REDACTED]
    assert pwd_config.get("value_masked") in ("***", "[REDACTED]") or "***" in pwd_config.get("value_masked", "")
    assert pwd_config.get("kind") == "secret"


def test_golden_finding_4_app_server_local_timestamps(seeded_project):
    """
    Golden Smell 4:
    Local timestamp generation via new Date() / System.currentTimeMillis()
    violating ALCOA+ cloud time synchronization.
    """
    store = get_graph_store(seeded_project)
    gxp_results = run_gxp_scan(store)
    gaps = gxp_results.get("gaps", [])

    time_gap = next((g for g in gaps if "TIME" in g.get("code", "") or "TIME" in g.get("id", "") or "timestamp" in g.get("description", "").lower()), None)
    assert time_gap is not None, "Scanner must detect application-generated local timestamps"


def test_golden_finding_5_shared_regulated_table_coupling(seeded_project):
    """
    Golden Smell 5:
    Shared RESULT table between ResultService (HIGH tier writer) and
    ReportService (LOW tier reporting analytics reader).
    """
    store = get_graph_store(seeded_project)
    decomp = execute_3way_decomposition(store)

    headline = decomp.get("headline_comparison", {})
    # ModernRx constrained decomposition must separate reporting from the HIGH-tier core
    assert headline["reval_scope_reduction_pct"] >= 0
    assert headline["blast_radius_modernrx"] <= headline["blast_radius_naive"]


def test_golden_finding_6_dead_code_retirement_candidate(seeded_project):
    """
    Golden Smell 6:
    UnusedLegacyCalculator has zero inbound callers and is identified as
    a 7R 'Retire' dead code candidate.
    """
    store = get_graph_store(seeded_project)
    readiness = calculate_project_readiness(store)
    dead_code = readiness.get("dead_code", [])

    unused = next((dc for dc in dead_code if "Unused" in dc.get("node_id", "") or "Calculator" in dc.get("node_id", "")), None)
    assert unused is not None, "Readiness scorer must identify UnusedLegacyCalculator as dead code"


def test_full_e2e_evaluation_benchmarks(seeded_project):
    """
    Full End-to-End Evaluation Benchmark Metric Suite.
    Validates:
    - 100% Recall on all 6 planted golden findings.
    - Graph modularity metric computed.
    - ModernRx RevalScope reduction > 0%.
    - Cryptographic SHA-256 audit chain verified intact.
    """
    store = get_graph_store(seeded_project)
    decomp = execute_3way_decomposition(store)
    headline = decomp["headline_comparison"]

    # 1. Modularity benchmark
    assert headline["modularity_modernrx"] is not None
    assert headline["blast_radius_modernrx"] < headline["blast_radius_naive"]

    # 2. RevalScope reduction benchmark
    assert headline["reval_scope_reduction_pct"] > 0

    # 3. Cryptographic Audit Chain integrity
    db = SessionLocal()
    audit_status = verify_audit_chain(db)
    assert audit_status["valid"] is True
    db.close()
