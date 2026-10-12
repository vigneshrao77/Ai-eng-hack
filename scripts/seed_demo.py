import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.db.session import init_db, SessionLocal
from app.db.models import User, Project, Decision, Roadmap, AuditLog
from app.core.auth import get_password_hash
from app.core.audit import record_audit_event
from app.db.graph_store import get_graph_store
from app.core.logging import logger


def seed_demo_data():
    logger.info("Initializing database...")
    init_db()
    db = SessionLocal()

    try:
        # 1. Seed Users
        users_to_seed = [
            ("qa@modernrx.internal", "Dr. Eleanor Vance", "qa_approver"),
            ("architect@modernrx.internal", "Marcus Chen", "architect"),
            ("admin@modernrx.internal", "System Administrator", "admin"),
            ("viewer@modernrx.internal", "Auditor Viewer", "viewer"),
        ]

        created_users = {}
        for email, name, role in users_to_seed:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    name=name,
                    role=role,
                    password_hash=get_password_hash("Password123!"),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created demo user: {email} ({role})")
            created_users[role] = user

        # 2. Seed AcmeLIMS Project
        project = db.query(Project).filter(Project.id == "acmelims-demo").first()
        if not project:
            project = Project(
                id="acmelims-demo",
                name="AcmeLIMS (Legacy Monolith)",
                repo_url="com.acme.lims:v2.4",
                local_path="demo-lims",
                target_cloud="AWS",
                status="ANALYZED",
                created_by=created_users["architect"].id,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info("Created AcmeLIMS demo project record.")

        # 3. Seed Living Twin Knowledge Graph in GraphStore
        store = get_graph_store("acmelims-demo")
        
        # Classes & components
        nodes_data = [
            # Regulated Core (HIGH tier)
            ("SampleService", "Class", {"fqn": "com.acme.lims.sample.SampleService", "loc": 420, "complexity": 14, "gxp_tier": "HIGH", "gxp_tags": ["DATA_INTEGRITY"], "readiness": 55, "cluster_id": "c1_sample_core"}),
            ("ResultService", "Class", {"fqn": "com.acme.lims.result.ResultService", "loc": 510, "complexity": 18, "gxp_tier": "HIGH", "gxp_tags": ["DATA_INTEGRITY"], "readiness": 52, "cluster_id": "c2_testing_review"}),
            ("ReviewService", "Class", {"fqn": "com.acme.lims.review.ReviewService", "loc": 380, "complexity": 16, "gxp_tier": "HIGH", "gxp_tags": ["E_SIGNATURE", "DATA_INTEGRITY"], "readiness": 48, "cluster_id": "c2_testing_review"}),
            ("BatchReleaseService", "Class", {"fqn": "com.acme.lims.batch.BatchReleaseService", "loc": 620, "complexity": 22, "gxp_tier": "HIGH", "gxp_tags": ["PRODUCT_RELEASE", "E_SIGNATURE"], "readiness": 44, "cluster_id": "c3_batch_disposition"}),
            ("AuditTrailService", "Class", {"fqn": "com.acme.lims.audit.AuditTrailService", "loc": 290, "complexity": 8, "gxp_tier": "HIGH", "gxp_tags": ["AUDIT_TRAIL"], "readiness": 60, "cluster_id": "c4_audit_security"}),
            
            # Supporting / Low / Medium Tier
            ("InstrumentImportService", "Class", {"fqn": "com.acme.lims.instrument.InstrumentImportService", "loc": 340, "complexity": 12, "gxp_tier": "MEDIUM", "gxp_tags": ["DATA_INTEGRITY"], "readiness": 40, "cluster_id": "c5_instruments"}),
            ("ReportService", "Class", {"fqn": "com.acme.lims.reporting.ReportService", "loc": 450, "complexity": 9, "gxp_tier": "LOW", "gxp_tags": ["REPORTING_ONLY"], "readiness": 85, "cluster_id": "c6_reporting_analytics"}),
            ("NightlyJobScheduler", "Class", {"fqn": "com.acme.lims.scheduler.NightlyJobScheduler", "loc": 180, "complexity": 6, "gxp_tier": "LOW", "gxp_tags": ["TIME_SOURCE"], "readiness": 70, "cluster_id": "c7_jobs"}),
            ("SecurityConfig", "Class", {"fqn": "com.acme.lims.admin.SecurityConfig", "loc": 220, "complexity": 7, "gxp_tier": "MEDIUM", "gxp_tags": ["ACCESS_CONTROL"], "readiness": 65, "cluster_id": "c4_audit_security"}),
            ("UnusedLegacyCalculator", "Class", {"fqn": "com.acme.lims.util.UnusedLegacyCalculator", "loc": 150, "complexity": 5, "gxp_tier": "LOW", "gxp_tags": [], "readiness": 90, "cluster_id": "outlier_dead_code"}),

            # Regulated Tables
            ("TABLE_SAMPLE", "Table", {"name": "SAMPLE", "regulated": True, "gxp_tier": "HIGH"}),
            ("TABLE_RESULT", "Table", {"name": "RESULT", "regulated": True, "gxp_tier": "HIGH"}),
            ("TABLE_BATCH", "Table", {"name": "BATCH", "regulated": True, "gxp_tier": "HIGH"}),
            ("TABLE_AUDIT_TRAIL", "Table", {"name": "AUDIT_TRAIL", "regulated": True, "gxp_tier": "HIGH"}),
            ("TABLE_REPORT_CACHE", "Table", {"name": "REPORT_CACHE", "regulated": False, "gxp_tier": "LOW"}),
        ]

        for nid, lbl, props in nodes_data:
            store.add_node(nid, label=lbl, **props)

        # Edges (Calls and Data Writes)
        edges_data = [
            ("SampleService", "TABLE_SAMPLE", "WRITES"),
            ("ResultService", "TABLE_RESULT", "WRITES"),
            ("ResultService", "SampleService", "CALLS", {"count": 14}),
            ("ReviewService", "ResultService", "CALLS", {"count": 28}),
            ("ReviewService", "AuditTrailService", "CALLS", {"count": 19}),
            ("BatchReleaseService", "ReviewService", "CALLS", {"count": 12}),
            ("BatchReleaseService", "TABLE_BATCH", "WRITES"),
            ("BatchReleaseService", "AuditTrailService", "CALLS", {"count": 25}),
            ("InstrumentImportService", "ResultService", "CALLS", {"count": 8}),
            ("ReportService", "TABLE_RESULT", "READS"),
            ("ReportService", "TABLE_REPORT_CACHE", "WRITES"),
            ("AuditTrailService", "TABLE_AUDIT_TRAIL", "WRITES"),
        ]

        for src, tgt, rel, *extra in edges_data:
            extra_props = extra[0] if extra else {}
            store.add_edge(src, tgt, rel, **extra_props)

        store.persist()
        logger.info("Seeded AcmeLIMS Living Twin Knowledge Graph.")

        # 4. Record Initial Genesis Audit Event
        record_audit_event(
            db=db,
            actor="system@modernrx.internal",
            action="PROJECT_SEEDED",
            entity="Project",
            entity_id="acmelims-demo",
            payload={
                "project_name": "AcmeLIMS (Legacy Monolith)",
                "nodes_count": len(nodes_data),
                "edges_count": len(edges_data),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        logger.info("Demo data seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
