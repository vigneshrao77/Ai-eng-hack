from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.db.graph_store import get_graph_store
from app.engines.decompose.cluster import execute_3way_decomposition
from app.config import get_settings

router = APIRouter(prefix="/projects", tags=["Decomposition & RevalScope Engine"])
settings = get_settings()


class DecomposeRequest(BaseModel):
    weights: Optional[List[float]] = None
    gamma: Optional[float] = None


@router.post("/{id}/decompose")
def trigger_decomposition(id: str, request: Optional[DecomposeRequest] = None):
    store = get_graph_store(id)
    weights = (request.weights if request and request.weights else settings.weights_list)
    gamma = (request.gamma if request and request.gamma is not None else settings.DECOMP_GAMMA)

    result = execute_3way_decomposition(store, weights=weights, gamma=gamma)
    return result


@router.get("/{id}/decomposition")
def get_decomposition(id: str):
    store = get_graph_store(id)
    if not store.get_all_nodes("Class"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Twin graph for project {id} is empty. Run /projects/{id}/analyze first.",
        )

    result = execute_3way_decomposition(store, weights=settings.weights_list, gamma=settings.DECOMP_GAMMA)
    return result
