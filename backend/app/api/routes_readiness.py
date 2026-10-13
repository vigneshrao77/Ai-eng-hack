import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Project
from app.db.graph_store import get_graph_store
from app.engines.twin.graph_builder import build_living_twin
from app.engines.readiness.scorer import calculate_project_readiness
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["Cloud Readiness Scorer"])


@router.get("/{id}/readiness")
def get_readiness(id: str, db: Session = Depends(get_db)):
    store = get_graph_store(id)
    if not store.get_all_nodes():
        p = db.query(Project).filter(Project.id == id).first()
        repo_path = p.local_path if p and p.local_path else ("demo-lims" if id == "acmelims-demo" else None)
        if repo_path and os.path.exists(repo_path):
            logger.info(f"Auto-building twin graph for readiness check on project {id} from {repo_path}")
            build_living_twin(id, repo_path)
            if p:
                p.status = "ANALYZED"
                db.commit()

    if not store.get_all_nodes():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Twin graph for project {id} is not initialized. Run /projects/{id}/analyze first.",
        )

    result = calculate_project_readiness(store)
    return result
