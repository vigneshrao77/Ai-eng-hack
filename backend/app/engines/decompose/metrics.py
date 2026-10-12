from typing import Dict, List, Any, Set
import networkx as nx
from networkx.algorithms.community import modularity


def compute_decomposition_metrics(
    partition: Dict[str, str],  # node_id -> cluster_id
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute Newman Modularity, Inter-Cluster Call Ratio, BlastRadius, and RevalScope %."""
    all_node_ids = [n["id"] for n in nodes]
    N = len(all_node_ids)
    if N == 0:
        return {"modularity": 0.0, "icp": 0.0, "services_count": 0, "blast_radius": 0, "reval_scope_pct": 0.0}

    node_dict = {n["id"]: n for n in nodes}

    # Group nodes by cluster
    clusters: Dict[str, Set[str]] = {}
    for nid, cid in partition.items():
        clusters.setdefault(cid, set()).add(nid)

    # Build NetworkX graph for modularity calculation
    G = nx.Graph()
    for nid in all_node_ids:
        G.add_node(nid)

    total_calls = 0
    inter_cluster_calls = 0

    # Cluster-level dependency graph
    cluster_calls: Dict[str, Set[str]] = {cid: set() for cid in clusters}

    for e in edges:
        u, v = e["source"], e["target"]
        if u in partition and v in partition:
            cnt = e.get("count", 1)
            G.add_edge(u, v, weight=cnt)
            total_calls += cnt

            c_u = partition[u]
            c_v = partition[v]
            if c_u != c_v:
                inter_cluster_calls += cnt
                cluster_calls[c_v].add(c_u)  # c_u calls into c_v

    # 1. Modularity (Newman)
    communities = [list(c_nodes) for c_nodes in clusters.values()]
    try:
        mod = modularity(G, communities) if G.number_of_edges() > 0 else 0.0
    except Exception:
        mod = 0.0

    # 2. Inter-Cluster Call Ratio (ICP)
    icp = (inter_cluster_calls / total_calls) if total_calls > 0 else 0.0

    # 3. Identify HIGH-tier clusters (clusters containing >= 1 HIGH-tier node)
    high_clusters: Set[str] = set()
    for cid, c_nodes in clusters.items():
        if any(node_dict.get(nid, {}).get("gxp_tier") == "HIGH" for nid in c_nodes):
            high_clusters.add(cid)

    # 4. BlastRadius(P) = sum over HIGH clusters: |c| + sum |c_callers|
    blast_radius = 0
    reval_components: Set[str] = set()

    for cid in high_clusters:
        c_nodes = clusters[cid]
        callers = cluster_calls.get(cid, set())
        
        # Nodes in HIGH cluster
        reval_components.update(c_nodes)
        
        # Nodes in caller clusters
        caller_nodes_count = 0
        for caller_cid in callers:
            caller_nodes = clusters[caller_cid]
            caller_nodes_count += len(caller_nodes)
            reval_components.update(caller_nodes)

        blast_radius += (len(c_nodes) + caller_nodes_count)

    # 5. RevalScope(P) % = (# components needing full re-validation) / (total components)
    reval_scope_pct = (len(reval_components) / N) * 100.0 if N > 0 else 0.0

    return {
        "modularity": round(mod, 3),
        "icp": round(icp, 3),
        "services_count": len(clusters),
        "blast_radius": blast_radius,
        "reval_scope_pct": round(reval_scope_pct, 1),
        "high_clusters_count": len(high_clusters),
        "reval_components_count": len(reval_components),
    }
