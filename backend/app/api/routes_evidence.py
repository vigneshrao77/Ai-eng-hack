import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.models import EvidencePack, Project, User
from app.db.session import get_db
from app.engines.evidence.generator import generate_wave_evidence_pdf

router = APIRouter(prefix="/projects", tags=["Evidence Pack Generator"])


@router.post("/{id}/evidence/{wave}")
def trigger_evidence_generation(
    id: str,
    wave: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates an FDA CSA / EU Annex 11 compliant Evidence Pack PDF for a specified migration wave.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Parse wave number
    try:
        wave_clean = wave.lower().replace("wave_", "").replace("wave", "")
        wave_num = int(wave_clean)
    except ValueError:
        wave_num = 1

    result = generate_wave_evidence_pdf(
        project_id=id,
        wave_num=wave_num,
        db=db,
        actor=current_user.email,
    )

    return result


@router.get("/{id}/evidence")
def list_evidence_packs(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists all generated Evidence Packs and cryptographic SHA-256 signatures for a project.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    packs = (
        db.query(EvidencePack)
        .filter(EvidencePack.project_id == id)
        .order_by(EvidencePack.created_at.desc())
        .all()
    )

    return {
        "project_id": id,
        "count": len(packs),
        "evidence_packs": [
            {
                "id": p.id,
                "wave": p.wave,
                "file_name": p.file_name,
                "sha256_hash": p.sha256_hash,
                "created_at": p.created_at.isoformat(),
                "download_url": f"/projects/{id}/evidence/{p.wave}/download",
            }
            for p in packs
        ],
    }


@router.get("/{id}/evidence/{wave}/download")
def download_evidence_pack(
    id: str,
    wave: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Downloads the actual binary PDF Evidence Pack file.
    """
    wave_clean = f"Wave_{wave.lower().replace('wave_', '').replace('wave', '')}"

    pack = (
        db.query(EvidencePack)
        .filter(EvidencePack.project_id == id, EvidencePack.wave == wave_clean)
        .first()
    )

    if not pack:
        # Try raw wave string
        pack = (
            db.query(EvidencePack)
            .filter(EvidencePack.project_id == id, EvidencePack.wave == wave)
            .first()
        )

    if not pack or not os.path.exists(pack.file_path):
        raise HTTPException(status_code=404, detail="Evidence Pack PDF not found for this wave. Generate it first.")

    return FileResponse(
        path=pack.file_path,
        media_type="application/pdf",
        filename=pack.file_name,
    )
