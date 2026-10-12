from typing import List, Dict, Any


def generate_mermaid_c4(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], title: str = "ModernRx Living Twin - C4 Architecture") -> str:
    """Generate Mermaid diagram markup from Twin Graph nodes and edges."""
    lines = [
        "graph TD",
        f"    %% {title}",
        "    classDef highTier fill:#ef4444,stroke:#991b1b,stroke-width:2px,color:#ffffff;",
        "    classDef mediumTier fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#ffffff;",
        "    classDef lowTier fill:#10b981,stroke:#047857,stroke-width:2px,color:#ffffff;",
        "    classDef db fill:#1e293b,stroke:#3b82f6,stroke-width:2px,stroke-dasharray: 5 5,color:#60a5fa;",
    ]

    for node in nodes:
        nid = node.get("id", "").replace("-", "_").replace(".", "_")
        lbl = node.get("name") or node.get("class_name") or node.get("fqn") or nid
        tier = node.get("gxp_tier", "LOW")
        node_type = node.get("label", "Class")

        if node_type == "Table":
            lines.append(f'    {nid}[("Database: {lbl}")]:::db')
        else:
            style_cls = "highTier" if tier == "HIGH" else ("mediumTier" if tier == "MEDIUM" else "lowTier")
            lines.append(f'    {nid}["{lbl}<br/><small>{node_type} &bull; {tier}</small>"]:::{style_cls}')

    for edge in edges:
        u = edge.get("source", "").replace("-", "_").replace(".", "_")
        v = edge.get("target", "").replace("-", "_").replace(".", "_")
        rel = edge.get("rel_type", "CALLS")
        lines.append(f"    {u} -->|{rel}| {v}")

    return "\n".join(lines)
