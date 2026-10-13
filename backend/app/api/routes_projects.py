import io
import os
import zipfile
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Project, User
from app.core.auth import get_current_user, require_roles
from app.core.audit import record_audit_event
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["Projects"])

MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50 MB compressed
MAX_EXTRACTED_SIZE = 150 * 1024 * 1024  # 150 MB uncompressed limit (anti-zip bomb)
MAX_FILE_COUNT = 5000


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    repo_url: Optional[str] = None
    target_cloud: str = Field(default="AWS", pattern="^(AWS|Azure|GCP)$")


class ProjectResponse(BaseModel):
    id: str
    name: str
    repo_url: Optional[str]
    target_cloud: str
    status: str
    created_at: str


@router.post("", response_model=ProjectResponse)
def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(require_roles(["architect", "admin"])),
    db: Session = Depends(get_db),
):
    project = Project(
        name=request.name,
        repo_url=request.repo_url,
        target_cloud=request.target_cloud,
        status="CREATED",
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Immutable audit trail entry
    record_audit_event(
        db=db,
        actor=current_user.email,
        action="PROJECT_CREATED",
        entity="Project",
        entity_id=project.id,
        payload={
            "name": project.name,
            "target_cloud": project.target_cloud,
            "repo_url": project.repo_url,
        },
    )

    return {
        "id": project.id,
        "name": project.name,
        "repo_url": project.repo_url,
        "target_cloud": project.target_cloud,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
    }


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "repo_url": p.repo_url,
            "target_cloud": p.target_cloud,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]


@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "repo_url": project.repo_url,
        "target_cloud": project.target_cloud,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
    }


@router.post("/{id}/upload")
async def upload_repository_zip(
    id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["architect", "admin"])),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    content = await file.read()
    if len(content) > MAX_ZIP_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ZIP archive exceeds 50MB limit.")

    dest_dir = Path("data/uploads") / id
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            total_size = 0
            file_count = 0
            # Validate all paths before extracting (Path traversal & Zip Bomb check)
            for info in zf.infolist():
                file_count += 1
                if file_count > MAX_FILE_COUNT:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ZIP contains too many files (>5000).")

                # Check path traversal
                norm_name = os.path.normpath(info.filename)
                if norm_name.startswith("..") or os.path.isabs(norm_name) or ":\\" in norm_name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Security violation: path traversal detected in ZIP entry: {info.filename}",
                    )

                total_size += info.file_size
                if total_size > MAX_EXTRACTED_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Security violation: uncompressed archive exceeds size threshold (Zip Bomb).",
                    )

            zf.extractall(path=dest_dir)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ZIP archive.")

    # Detect if ZIP extracted into a single nested folder
    subdirs = [p for p in dest_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
    effective_path = subdirs[0] if (len(subdirs) == 1 and len(list(dest_dir.iterdir())) == 1) else dest_dir

    project.local_path = str(effective_path)
    db.commit()

    # Automatically build the living twin graph and analyze the repository immediately
    from app.engines.twin.graph_builder import build_living_twin
    twin_res = None
    try:
        twin_res = build_living_twin(project.id, str(effective_path))
        project.status = "ANALYZED"
        db.commit()
        logger.info(f"Auto-built twin graph for uploaded project {id}: {twin_res.get('total_nodes')} nodes")
    except Exception as e:
        logger.error(f"Error auto-building twin graph for {id}: {e}")

    record_audit_event(
        db=db,
        actor=current_user.email,
        action="REPOSITORY_UPLOADED",
        entity="Project",
        entity_id=project.id,
        payload={"filename": file.filename, "size_bytes": len(content), "nodes": twin_res.get("total_nodes") if twin_res else 0},
    )

    logger.info(f"Repository uploaded and extracted safely for project {id} into {effective_path}")
    return {
        "status": "uploaded",
        "project_id": id,
        "path": str(effective_path),
        "total_nodes": twin_res.get("total_nodes") if twin_res else 0,
        "total_edges": twin_res.get("total_edges") if twin_res else 0,
    }
