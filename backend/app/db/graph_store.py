import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import networkx as nx
from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


class GraphStore:
    """Abstract Graph Store supporting Neo4j and embedded NetworkX engine."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.use_neo4j = settings.USE_NEO4J
        self.graph = nx.DiGraph()
        self._load_local_cache()

    def _get_cache_path(self) -> Path:
        cache_dir = Path("data/graphs")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / f"{self.project_id}.json"

    def _load_local_cache(self):
        cache_file = self._get_cache_path()
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data, directed=True, multigraph=False)
                    logger.info(f"Loaded graph for project {self.project_id}: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.error(f"Failed to load cached graph: {e}")
                self.graph = nx.DiGraph()

    def persist(self):
        cache_file = self._get_cache_path()
        try:
            data = nx.node_link_data(self.graph)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Persisted graph for project {self.project_id}: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        except Exception as e:
            logger.error(f"Failed to persist graph: {e}")

    def add_node(self, node_id: str, label: str, **properties):
        self.graph.add_node(node_id, label=label, **properties)

    def add_edge(self, source_id: str, target_id: str, rel_type: str, **properties):
        self.graph.add_edge(source_id, target_id, rel_type=rel_type, **properties)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if node_id in self.graph.nodes:
            data = dict(self.graph.nodes[node_id])
            data["id"] = node_id
            return data
        return None

    def get_all_nodes(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        nodes = []
        for n, data in self.graph.nodes(data=True):
            if label is None or data.get("label") == label:
                d = dict(data)
                d["id"] = n
                nodes.append(d)
        return nodes

    def get_all_edges(self, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        edges = []
        for u, v, data in self.graph.edges(data=True):
            if rel_type is None or data.get("rel_type") == rel_type:
                d = dict(data)
                d["source"] = u
                d["target"] = v
                edges.append(d)
        return edges

    def get_neighbors(self, node_id: str, direction: str = "both") -> List[str]:
        if node_id not in self.graph:
            return []
        if direction == "out":
            return list(self.graph.successors(node_id))
        elif direction == "in":
            return list(self.graph.predecessors(node_id))
        else:
            return list(set(list(self.graph.successors(node_id)) + list(self.graph.predecessors(node_id))))

    def run_template_query(self, template_id: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Whitelisted graph queries simulating Cypher templates safely."""
        results = []
        if template_id == "who_writes_table":
            table_name = params.get("table", "").lower()
            for u, v, data in self.graph.edges(data=True):
                if data.get("rel_type") == "WRITES":
                    target_node = self.graph.nodes.get(v, {})
                    if target_node.get("name", "").lower() == table_name or v.lower() == table_name:
                        src_node = dict(self.graph.nodes.get(u, {}))
                        src_node["id"] = u
                        results.append(src_node)

        elif template_id == "blast_radius_3_hops":
            target_fqn = params.get("fqn", "")
            target_id = None
            for n, data in self.graph.nodes(data=True):
                if data.get("fqn") == target_fqn or n == target_fqn:
                    target_id = n
                    break
            if target_id and target_id in self.graph:
                visited = set()
                queue = [(target_id, 0)]
                while queue:
                    curr, depth = queue.pop(0)
                    if depth < 3:
                        for pred in self.graph.predecessors(curr):
                            if pred not in visited:
                                visited.add(pred)
                                queue.append((pred, depth + 1))
                for v in visited:
                    node_data = dict(self.graph.nodes[v])
                    node_data["id"] = v
                    results.append(node_data)

        elif template_id == "high_gxp_nodes":
            for n, data in self.graph.nodes(data=True):
                if data.get("gxp_tier") == "HIGH":
                    node_data = dict(data)
                    node_data["id"] = n
                    results.append(node_data)

        return results


_graph_stores: Dict[str, GraphStore] = {}


def get_graph_store(project_id: str) -> GraphStore:
    if project_id not in _graph_stores:
        _graph_stores[project_id] = GraphStore(project_id)
    return _graph_stores[project_id]
