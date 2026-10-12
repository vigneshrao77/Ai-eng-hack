import numpy as np
from app.db.graph_store import get_graph_store
from app.engines.twin.graph_builder import build_living_twin
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.decompose.features import compute_similarity_matrix
from app.engines.decompose.metrics import compute_decomposition_metrics
from app.engines.decompose.cluster import execute_3way_decomposition


def test_similarity_matrix_properties():
    nodes = [
        {"id": "ServiceA", "class_name": "ServiceA", "package": "com.acme.sample"},
        {"id": "ServiceB", "class_name": "ServiceB", "package": "com.acme.sample"},
        {"id": "ReportService", "class_name": "ReportService", "package": "com.acme.report"},
    ]
    edges = [
        {"source": "ServiceA", "target": "ServiceB", "rel_type": "CALLS", "count": 10},
    ]

    S, node_ids = compute_similarity_matrix(nodes, edges)
    assert S.shape == (3, 3)
    assert np.all(S >= 0.0)
    assert np.all(S <= 1.0)
    # Diagonal must be 1.0
    for i in range(3):
        assert S[i, i] == 1.0
    # Symmetry
    assert np.allclose(S, S.T)


def test_metrics_blast_radius_and_reval_scope():
    nodes = [
        {"id": "HighCore", "gxp_tier": "HIGH"},
        {"id": "CallerToHigh", "gxp_tier": "MEDIUM"},
        {"id": "IsolatedLow", "gxp_tier": "LOW"},
    ]
    edges = [
        {"source": "CallerToHigh", "target": "HighCore", "rel_type": "CALLS", "count": 5},
    ]

    # Partition where each is in its own cluster
    partition = {
        "HighCore": "c_high",
        "CallerToHigh": "c_caller",
        "IsolatedLow": "c_isolated",
    }

    metrics = compute_decomposition_metrics(partition, nodes, edges)
    # c_high has size 1 + caller cluster size 1 = blast radius 2
    assert metrics["blast_radius"] == 2
    # RevalScope = 2 out of 3 components = 66.7%
    assert metrics["reval_scope_pct"] == 66.7
    assert metrics["services_count"] == 3


def test_3way_decomposition_and_reval_scope_reduction(client):
    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")
    run_gxp_scan(store)

    result = execute_3way_decomposition(store)
    variants = result["variants"]
    assert "louvain" in variants
    assert "hdbscan" in variants
    assert "modernrx" in variants

    m_hdbscan = variants["hdbscan"]["metrics"]
    m_modernrx = variants["modernrx"]["metrics"]

    # ModernRx constrained decomposition must achieve lower or equal RevalScope than naive split
    assert m_modernrx["reval_scope_pct"] <= m_hdbscan["reval_scope_pct"]
    assert m_modernrx["blast_radius"] <= m_hdbscan["blast_radius"]

    # Headline comparison checks
    headline = result["headline_comparison"]
    assert "reval_scope_naive_pct" in headline
    assert "reval_scope_modernrx_pct" in headline
    assert headline["reval_scope_reduction_pct"] >= 0

    # Test API endpoint
    res = client.get("/projects/acmelims-demo/decomposition")
    assert res.status_code == 200
    data = res.json()
    assert "variants" in data
    assert "headline_comparison" in data
