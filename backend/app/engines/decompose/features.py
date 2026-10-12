import numpy as np
from typing import List, Dict, Any, Tuple
from app.db.graph_store import GraphStore


def compute_similarity_matrix(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    weights: List[float] = [0.30, 0.20, 0.25, 0.10, 0.15],
) -> Tuple[np.ndarray, List[str]]:
    """Compute normalized multi-modal similarity matrix S(i,j) across components."""
    node_ids = [n["id"] for n in nodes]
    N = len(node_ids)
    if N == 0:
        return np.zeros((0, 0)), []

    idx_map = {nid: i for i, nid in enumerate(node_ids)}

    S_struct = np.zeros((N, N))
    S_runtime = np.zeros((N, N))
    S_data = np.zeros((N, N))
    S_cochange = np.zeros((N, N))
    S_semantic = np.zeros((N, N))

    # 1. Structural Similarity (Static Calls)
    call_counts = np.zeros((N, N))
    for e in edges:
        u, v = e["source"], e["target"]
        if u in idx_map and v in idx_map:
            i, j = idx_map[u], idx_map[v]
            cnt = e.get("count", 1)
            call_counts[i, j] += cnt
            call_counts[j, i] += cnt

    max_calls = np.max(call_counts) if np.max(call_counts) > 0 else 1.0
    S_struct = call_counts / max_calls

    # 2. Data Similarity (Jaccard of shared tables accessed)
    tables_per_node: Dict[int, set] = {i: set() for i in range(N)}
    for e in edges:
        u, v = e["source"], e["target"]
        rel = e.get("rel_type")
        if rel in ("WRITES", "READS") and u in idx_map:
            tables_per_node[idx_map[u]].add(v)

    for i in range(N):
        for j in range(i + 1, N):
            set_i, set_j = tables_per_node[i], tables_per_node[j]
            if set_i and set_j:
                jaccard = len(set_i & set_j) / len(set_i | set_j)
                S_data[i, j] = jaccard
                S_data[j, i] = jaccard

    # 3. Runtime Similarity (Correlated use-cases / traces)
    # Default correlated for services with direct call edges
    S_runtime = S_struct * 0.9

    # 4. Co-Change Similarity (Static package proximity)
    for i in range(N):
        pkg_i = nodes[i].get("package", "")
        for j in range(i + 1, N):
            pkg_j = nodes[j].get("package", "")
            if pkg_i and pkg_j and pkg_i == pkg_j:
                S_cochange[i, j] = 0.8
                S_cochange[j, i] = 0.8

    # 5. Semantic Similarity (Name similarity)
    for i in range(N):
        name_i = nodes[i].get("class_name", node_ids[i]).lower()
        for j in range(i + 1, N):
            name_j = nodes[j].get("class_name", node_ids[j]).lower()
            # Simple token overlap
            tokens_i = set(name_i.replace("service", "").replace("controller", "").split())
            tokens_j = set(name_j.replace("service", "").replace("controller", "").split())
            if tokens_i and tokens_j and (tokens_i & tokens_j):
                S_semantic[i, j] = 0.6
                S_semantic[j, i] = 0.6

    # Identity self-similarity
    for i in range(N):
        S_struct[i, i] = 1.0
        S_data[i, i] = 1.0
        S_runtime[i, i] = 1.0
        S_cochange[i, i] = 1.0
        S_semantic[i, i] = 1.0

    # Weighted Sum
    w1, w2, w3, w4, w5 = weights
    S = (
        w1 * S_struct +
        w2 * S_runtime +
        w3 * S_data +
        w4 * S_cochange +
        w5 * S_semantic
    )

    # Normalize matrix to [0, 1]
    S = np.clip(S, 0.0, 1.0)
    return S, node_ids
