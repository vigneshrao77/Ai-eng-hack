from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.models import Project, Roadmap, User
from app.db.session import get_db
from app.engines.roadmap.service import generate_project_roadmap

router = APIRouter(prefix="/projects", tags=["Roadmap & Monte Carlo"])


class RoadmapGenerateRequest(BaseModel):
    squads: Optional[int] = Field(default=2, ge=1, le=10, description="Available development squads")
    freeze_windows: Optional[List[Tuple[int, int]]] = Field(
        default=None, description="List of (start_week, end_week) freeze windows"
    )
    target_weeks: Optional[float] = Field(
        default=None, ge=1.0, description="Target completion duration in weeks"
    )


class WhatIfRequest(BaseModel):
    squads: Optional[int] = Field(default=2, ge=1, le=10)
    freeze_windows: Optional[List[Tuple[int, int]]] = None
    target_weeks: Optional[float] = None
    strategy_overrides: Optional[Dict[str, str]] = None


@router.post("/{id}/roadmap")
def trigger_roadmap_generation(
    id: str,
    request: Optional[RoadmapGenerateRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Executes CP-SAT schedule optimization and 10,000-run PERT Monte Carlo simulation.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    squads = request.squads if request and request.squads else 2
    freeze_windows = request.freeze_windows if request and request.freeze_windows else [(12, 14)]
    target_weeks = request.target_weeks if request else None

    roadmap_data = generate_project_roadmap(
        project_id=id,
        db=db,
        squads=squads,
        freeze_windows=freeze_windows,
        target_weeks=target_weeks,
        actor=current_user.email,
        persist=True,
    )

    return roadmap_data


@router.get("/{id}/roadmap")
def get_project_roadmap(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the optimized roadmap schedule and Monte Carlo simulation distribution.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    roadmap_rec = (
        db.query(Roadmap)
        .filter(Roadmap.project_id == id)
        .order_by(Roadmap.created_at.desc())
        .first()
    )

    if not roadmap_rec:
        # Generate baseline on the fly
        return generate_project_roadmap(
            project_id=id,
            db=db,
            actor=current_user.email,
            persist=True,
        )

    return {
        "project_id": id,
        "schedule": roadmap_rec.schedule_json,
        "monte_carlo": roadmap_rec.montecarlo_json,
        "created_at": roadmap_rec.created_at.isoformat(),
    }


@router.post("/{id}/roadmap/whatif")
def simulate_whatif_scenario(
    id: str,
    request: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fast interactive What-If simulation for UI sliders (does not overwrite baseline unless saved).
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    squads = request.squads if request.squads else 2
    freeze_windows = request.freeze_windows if request.freeze_windows else [(12, 14)]

    sim_data = generate_project_roadmap(
        project_id=id,
        db=db,
        squads=squads,
        freeze_windows=freeze_windows,
        target_weeks=request.target_weeks,
        actor=current_user.email,
        persist=False,
    )

    return sim_data
