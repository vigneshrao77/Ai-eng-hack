from app.engines.twin.ingest import scan_repository
from app.engines.twin.parsers.java_parser import parse_java_file
from app.engines.twin.parsers.config_parser import parse_properties_file
from app.engines.twin.c4 import generate_mermaid_c4
from app.engines.twin.graph_builder import build_living_twin


def test_scan_repository():
    res = scan_repository("demo-lims")
    assert res["total_files"] >= 8
    assert res["total_loc"] > 100
    assert "Java" in res["language_loc"]
    assert "Config" in res["language_loc"]


def test_parse_java_sample_service():
    parsed = parse_java_file("demo-lims/src/main/java/com/acme/lims/sample/SampleService.java")
    assert parsed["class_name"] == "SampleService"
    assert "Service" in parsed["annotations"]
    assert "Transactional" in parsed["annotations"]
    assert parsed["has_local_timestamp"] is True
    # Table write detection
    tables = [t["table"] for t in parsed["table_operations"]]
    assert "SAMPLE" in tables


def test_parse_config_secret_masking():
    items = parse_properties_file("demo-lims/src/main/resources/application.properties")
    keys = {item["key"]: item for item in items}
    assert "acme.admin.password" in keys
    assert keys["acme.admin.password"]["value_masked"] == "[REDACTED]"
    assert keys["acme.admin.password"]["is_secret"] is True
    assert "instrument" in keys["instrument.import.directory"]["raw_value"]


def test_build_living_twin_and_c4():
    meta = build_living_twin("test-lims-twin", "demo-lims")
    assert meta["total_nodes"] >= 8
    assert meta["total_edges"] >= 4

    # Test C4 generation
    nodes = [{"id": "ServiceA", "name": "ServiceA", "label": "Class", "gxp_tier": "HIGH"}]
    edges = [{"source": "ServiceA", "target": "ServiceB", "rel_type": "CALLS"}]
    mermaid = generate_mermaid_c4(nodes, edges)
    assert mermaid.startswith("graph TD")
    assert "ServiceA" in mermaid


def test_twin_api_endpoints(client):
    # Ensure graph is seeded
    build_living_twin("acmelims-demo", "demo-lims")

    # 1. Graph elements endpoint
    res = client.get("/projects/acmelims-demo/twin/graph")
    assert res.status_code == 200
    data = res.json()
    assert "elements" in data
    assert "nodes" in data["elements"]
    assert len(data["elements"]["nodes"]) >= 8

    # 2. C4 endpoint
    res_c4 = client.get("/projects/acmelims-demo/twin/c4")
    assert res_c4.status_code == 200
    assert "graph TD" in res_c4.json()["diagram"]

    # 3. Ask the twin
    res_ask = client.post("/projects/acmelims-demo/twin/ask", json={"question": "Which code writes batch release data?"})
    assert res_ask.status_code == 200
    ask_data = res_ask.json()
    assert len(ask_data["evidence_node_ids"]) > 0
    assert "BatchReleaseService" in ask_data["answer"]
