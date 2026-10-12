import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="architect")  # viewer, architect, qa_approver, admin
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    repo_url = Column(String(500), nullable=True)
    local_path = Column(String(500), nullable=True)
    target_cloud = Column(String(50), default="AWS")  # AWS, Azure, GCP
    status = Column(String(50), default="CREATED")  # CREATED, ANALYZING, ANALYZED, FAILED
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # ASSESSMENT, DECOMPOSITION, COUNCIL, ROADMAP, EVIDENCE
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    progress = Column(Integer, default=0)  # 0 to 100
    message = Column(String(500), default="")
    error = Column(Text, nullable=True)
    result_json = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="jobs")


class GxpOverride(Base):
    __tablename__ = "gxp_overrides"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    node_id = Column(String(255), nullable=False, index=True)
    old_tier = Column(String(50), nullable=False)
    new_tier = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    cluster_id = Column(String(100), nullable=False, index=True)
    strategy = Column(String(50), nullable=False)  # Retain, Rehost, Relocate, Replatform, Repurchase, Refactor, Retire
    target_pattern = Column(JSON, nullable=True)
    target_services = Column(JSON, nullable=True)
    confidence = Column(Float, default=0.85)
    rationale = Column(Text, nullable=True)
    risks = Column(JSON, nullable=True)
    dissent = Column(JSON, nullable=True)
    evidence_node_ids = Column(JSON, nullable=True)
    effort_weeks = Column(JSON, nullable=True)  # [opt, likely, pess]
    status = Column(String(50), default="PROPOSED")  # PROPOSED, APPROVED, REJECTED
    model_id = Column(String(100), nullable=False)
    prompt_hash = Column(String(64), nullable=True)
    input_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    approvals = relationship("Approval", back_populates="decision", cascade="all, delete-orphan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    decision_id = Column(String(36), ForeignKey("decisions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # APPROVED, REJECTED
    comment = Column(Text, nullable=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False)

    decision = relationship("Decision", back_populates="approvals")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    schedule_json = Column(JSON, nullable=False)
    montecarlo_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EvidencePack(Base):
    __tablename__ = "evidence_packs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    wave = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    sha256_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    actor = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(String(255), nullable=False)
    payload_json = Column(JSON, nullable=False)
    prev_hash = Column(String(64), nullable=False)
    hash = Column(String(64), nullable=False)
