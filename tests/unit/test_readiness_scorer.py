from app.db.graph_store import get_graph_store
from app.engines.twin.graph_builder import build_living_twin
from app.engines.gxp.scanner import run_gxp_scan
from app.engines.readiness.scorer import calculate_project_readiness
from app.engines.readiness.checks import evaluate_node_readiness, CHECK_WEIGHTS


def test_readiness_weight_sum():
    total_weights = sum(CHECK_WEIGHTS.values())
    assert total_weights == 100


def test_readiness_exact_math():
    mock_node = {
        "id": "TestService",
        "loc": 100,
        "complexity": 2,
        "gxp_tier": "LOW",
        "annotations": [],
        "has_local_fs": True,  # 10 pts deduction
        "has_local_timestamp": False,
        "label": "Class",
    }
    graph_context = {"node_shared_tables": {}}
    res = evaluate_node_readiness(mock_node, graph_context)

    # 10 pts for local fs + 7.5 pts (0.5 * 15) for Spring Boot 2 EOL = 17.5 total deductions
    assert res["total_deductions"] == 17.5
    assert res["score"] == 82.5

    # Check evidence node IDs
    for d in res["deductions"]:
        assert len(d["evidence_node_ids"]) > 0
        assert "TestService" in d["evidence_node_ids"]


def test_project_readiness_and_opportunities(client):
    build_living_twin("acmelims-demo", "demo-lims")
    store = get_graph_store("acmelims-demo")
    run_gxp_scan(store)

    result = calculate_project_readiness(store)
    assert "average_readiness" in result
    assert 40 <= result["average_readiness"] <= 95
    assert len(result["components"]) >= 6

    # Verify Dead Code detection
    dead_code_ids = [d["node_id"] for d in result["dead_code"]]
    assert "UnusedLegacyCalculator" in dead_code_ids

    # Verify Quick Wins
    quick_win_ids = [q["node_id"] for q in result["quick_wins"]]
    assert len(quick_win_ids) > 0

    # Test API endpoint
    res = client.get("/projects/acmelims-demo/readiness")
    assert res.status_code == 200
    api_data = res.json()
    assert "average_readiness" in api_data
    assert len(api_data["components"]) > 0
