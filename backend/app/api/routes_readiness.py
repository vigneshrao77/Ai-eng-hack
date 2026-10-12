from fastapi import APIRouter, HTTPException, status
from app.db.graph_store import get_graph_store
from app.engines.readiness.scorer import calculate_project_readiness

router = APIRouter(prefix="/projects", tags=["Cloud Readiness Scorer"])


@router.get("/{id}/readiness")
def get_readiness(id: str):
    store = get_graph_store(id)
    if not store.get_all_nodes():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Twin graph for project {id} is not initialized. Run /projects/{id}/analyze first.",
        )

    result = calculate_project_readiness(store)
    return result
