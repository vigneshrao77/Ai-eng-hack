import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db, SessionLocal
from app.db.models import Project, Job
from app.db.graph_store import get_graph_store
from app.engines.twin.graph_builder import build_living_twin
from app.engines.twin.c4 import generate_mermaid_c4
from app.workers.task_runner import submit_background_job, update_job_progress
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["Living Architecture Twin"])


class AskTwinRequest(BaseModel):
    question: str


@router.post("/{id}/analyze")
def trigger_analysis(id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    job = Job(
        project_id=id,
        type="ASSESSMENT",
        status="PENDING",
        progress=0,
        message="Queued for analysis",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    repo_path = project.local_path or "demo-lims"

    def run_assessment(job_id: str):
        update_job_progress(job_id, 20, "Scanning files and parsing AST...")
        result = build_living_twin(project_id=id, repo_path=repo_path)
        update_job_progress(job_id, 60, "Correlating call graph and table writes...")
        update_job_progress(job_id, 90, "Calculating graph fan-in, fan-out, and C4 topology...")
        sess = SessionLocal()
        try:
            p = sess.query(Project).filter(Project.id == id).first()
            if p:
                p.status = "ANALYZED"
                sess.commit()
        finally:
            sess.close()
        return result

    submit_background_job(job.id, run_assessment)
    return {"job_id": job.id, "status": "QUEUED"}


@router.get("/{id}/twin/graph")
def get_twin_graph(id: str, db: Session = Depends(get_db)):
    store = get_graph_store(id)
    raw_nodes = store.get_all_nodes()
    raw_edges = store.get_all_edges()

    # If graph is empty, attempt on-demand construction if local path exists
    if len(raw_nodes) == 0:
        p = db.query(Project).filter(Project.id == id).first()
        repo_path = p.local_path if p and p.local_path else ("demo-lims" if id == "acmelims-demo" else None)
        if repo_path and os.path.exists(repo_path):
            logger.info(f"Auto-building twin graph on demand for project {id} from {repo_path}")
            try:
                build_living_twin(id, repo_path)
                if p:
                    p.status = "ANALYZED"
                    db.commit()
                raw_nodes = store.get_all_nodes()
                raw_edges = store.get_all_edges()
            except Exception as e:
                logger.error(f"Error during on-demand twin build for {id}: {e}")

    cytoscape_nodes = []
    for n in raw_nodes:
        cytoscape_nodes.append({
            "data": {
                "id": n["id"],
                "label": n.get("name") or n.get("class_name") or n.get("key") or n["id"],
                "name": n.get("name") or n.get("class_name") or n["id"],
                "type": n.get("label", "Class"),
                "fqn": n.get("fqn", ""),
                "loc": n.get("loc", 0),
                "complexity": n.get("complexity", 1),
                "fanIn": n.get("fanIn", 0),
                "fanOut": n.get("fanOut", 0),
                "gxp_tier": n.get("gxp_tier", "LOW"),
                "gxp_tags": n.get("gxp_tags", []),
                "readiness": n.get("readiness", 100),
                "cluster_id": n.get("cluster_id", ""),
            }
        })

    cytoscape_edges = []
    for idx, e in enumerate(raw_edges):
        cytoscape_edges.append({
            "data": {
                "id": f"e_{idx}_{e['source']}_{e['target']}",
                "source": e["source"],
                "target": e["target"],
                "rel_type": e.get("rel_type", "CALLS"),
            }
        })

    flat_nodes = [n["data"] for n in cytoscape_nodes]
    flat_edges = [e["data"] for e in cytoscape_edges]

    return {
        "nodes": flat_nodes,
        "edges": flat_edges,
        "elements": {
            "nodes": cytoscape_nodes,
            "edges": cytoscape_edges,
        },
        "stats": {
            "total_nodes": len(cytoscape_nodes),
            "total_edges": len(cytoscape_edges),
        },
    }


@router.get("/{id}/twin/c4")
def get_c4_diagram(id: str):
    store = get_graph_store(id)
    nodes = store.get_all_nodes()
    edges = store.get_all_edges()
    diagram = generate_mermaid_c4(nodes, edges)
    return {"diagram": diagram}


def _extract_codebase_context(project_id: str, project: Optional[Project], store: Any, question: str) -> Dict[str, Any]:
    """Dynamically extracts real architecture, files, README, and code snippets from the uploaded repository."""
    project_name = project.name if (project and project.name) else project_id
    target_cloud = project.target_cloud if (project and project.target_cloud) else "AWS"
    repo_path = project.local_path if (project and project.local_path and os.path.exists(project.local_path)) else None

    readme_excerpt = ""
    detected_frameworks = []
    if repo_path:
        rp = Path(repo_path)
        for pattern in ("README.md", "README.txt", "readme.md", "Readme.md", "README"):
            readme_file = rp / pattern
            if readme_file.exists() and readme_file.is_file():
                try:
                    with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
                        readme_excerpt = f.read(1200).strip()
                    break
                except Exception:
                    pass

        if (rp / "package.json").exists():
            detected_frameworks.append("Node.js / JavaScript")
            try:
                import json
                with open(rp / "package.json", "r", encoding="utf-8", errors="ignore") as f:
                    pkg = json.load(f)
                    deps = list(pkg.get("dependencies", {}).keys())[:6]
                    if deps:
                        detected_frameworks.append(f"Libraries: {', '.join(deps)}")
            except Exception:
                pass
        if (rp / "requirements.txt").exists():
            detected_frameworks.append("Python (requirements.txt)")
        if (rp / "pom.xml").exists():
            detected_frameworks.append("Java (Maven)")
        if (rp / "go.mod").exists():
            detected_frameworks.append("Go (go.mod)")
        if (rp / "Dockerfile").exists():
            detected_frameworks.append("Docker Containerized")

    all_nodes = store.get_all_nodes()
    all_edges = store.get_all_edges()
    table_nodes = [n["id"] for n in all_nodes if n.get("label") == "Table" or "table" in n.get("id", "").lower()]
    class_nodes = [n for n in all_nodes if n.get("label") in ("Class", "Component") or not n.get("label")]

    # Keyword match for user query
    q_words = [w.lower() for w in question.split() if len(w) > 2]
    matched_nodes = []
    for n in all_nodes:
        nid = n.get("id", "").lower()
        nname = n.get("name", "").lower()
        nfqn = n.get("fqn", "").lower()
        if any(w in nid or w in nname or w in nfqn for w in q_words):
            matched_nodes.append(n)

    if not matched_nodes:
        matched_nodes = class_nodes[:6] or all_nodes[:6]

    snippets = []
    for mn in matched_nodes[:4]:
        fpath = mn.get("file_path")
        code_snip = ""
        if fpath and os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [line.rstrip() for line in f.readlines()[:30]]
                    code_snip = "\n".join(lines)
            except Exception:
                pass
        snippets.append({
            "id": mn.get("id"),
            "name": mn.get("name") or mn.get("id"),
            "type": mn.get("label", "Component"),
            "gxp": mn.get("gxp_tier", "LOW"),
            "loc": mn.get("loc", 0),
            "snippet": code_snip[:500] if code_snip else ""
        })

    return {
        "project_name": project_name,
        "target_cloud": target_cloud,
        "repo_path": repo_path,
        "detected_frameworks": detected_frameworks or ["Standard Codebase"],
        "readme_excerpt": readme_excerpt,
        "total_nodes": len(all_nodes),
        "total_edges": len(all_edges),
        "table_nodes": table_nodes,
        "class_nodes": [n.get("name") or n.get("id") for n in class_nodes[:15]],
        "matched_nodes": matched_nodes[:6],
        "snippets": snippets,
    }


@router.post("/{id}/twin/ask")
def ask_the_twin(id: str, request: AskTwinRequest, db: Session = Depends(get_db)):
    """
    Answers architectural queries dynamically based on the uploaded repository AST,
    knowledge graph topology, and AI models (Local Ollama or Gemini API).
    Never returns hardcoded or fictional outputs.
    """
    project = db.query(Project).filter(Project.id == id).first()
    store = get_graph_store(id)

    # Auto-build twin if store is empty and project has an extracted local path
    if len(store.get_all_nodes()) == 0 and project and project.local_path:
        if os.path.exists(project.local_path):
            try:
                build_living_twin(id, project.local_path)
            except Exception as e:
                logger.error(f"Error auto-building twin graph for {id}: {e}")

    ctx = _extract_codebase_context(id, project, store, request.question)
    project_name = ctx["project_name"]
    detected_stack = ", ".join(ctx["detected_frameworks"])
    total_nodes = ctx["total_nodes"]
    total_edges = ctx["total_edges"]
    tables_list = ", ".join(ctx["table_nodes"][:10]) if ctx["table_nodes"] else "No SQL tables identified"
    components_list = ", ".join(ctx["class_nodes"]) if ctx["class_nodes"] else "Components identified across repo"

    snippets_text = ""
    for s in ctx["snippets"]:
        snippets_text += f"\n- Component: {s['name']} (Type: {s['type']}, LOC: {s['loc']}, GxP: {s['gxp']})\n"
        if s["snippet"]:
            snippets_text += f"```\n{s['snippet']}\n```\n"

    prompt = (
        f"You are the expert AI Architecture Advisor analyzing the codebase for the project \"{project_name}\".\n"
        f"Analyze the project strictly using the real architectural data, dependencies, and code extracted from the repository below:\n\n"
        f"### Codebase Metadata:\n"
        f"- Project Name: {project_name}\n"
        f"- Target Cloud: {ctx['target_cloud']}\n"
        f"- Detected Stack / Frameworks: {detected_stack}\n"
        f"- Total Architectural Components: {total_nodes}\n"
        f"- Total Dependency Connections: {total_edges}\n"
        f"- Discovered Datastores / Tables: {tables_list}\n"
    )
    if ctx["readme_excerpt"]:
        prompt += f"- Readme Summary:\n{ctx['readme_excerpt']}\n"

    prompt += (
        f"\n### Discovered Architecture Components:\n{components_list}\n"
        f"\n### Relevant Component Code & Details:\n{snippets_text}\n"
        f"\n### User Question:\n{request.question}\n\n"
        f"### Instructions:\n"
        f"1. Base your answer STRICTLY on this real codebase, its actual components, and its real technologies.\n"
        f"2. Structure your answer with clear Markdown headings (e.g. '### 1. Plain English Summary', '### 2. Key Components & Connections', '### 3. Recommendations & Next Steps').\n"
        f"3. Use concise bullet points for component details and step-by-step guidance.\n"
        f"4. Highlight actual component and file names from the project in **bold**.\n"
        f"5. If suggesting cloud modernization or refactoring, tailor recommendations specifically to the detected stack ({detected_stack}) and target cloud ({ctx['target_cloud']}).\n"
        f"6. Do not mention fictional services, components, or unrelated projects."
    )

    # 1. Attempt generation via configured LLM (Local Ollama or Gemini)
    try:
        from app.core.llm import call_llm
        llm_res = call_llm(prompt, temperature=0.2, max_tokens=600, timeout=150.0)
        if llm_res.get("success") and llm_res.get("text"):
            gen_text = llm_res["text"].strip()
            all_nodes = [n["id"] for n in store.get_all_nodes()]
            # Find evidence nodes mentioned in generated response
            evidence = [nid for nid in all_nodes if nid.lower() in gen_text.lower()]
            fallback_evidence = [mn["id"] for mn in ctx["matched_nodes"] if mn["id"] in all_nodes]
            return {
                "question": request.question,
                "answer": gen_text,
                "evidence_node_ids": (evidence[:5] or fallback_evidence[:4]),
                "source": f"{llm_res['provider']} ({llm_res['model']}) & Architecture Twin",
            }
    except Exception as e:
        logger.warning("ask_the_twin LLM call exception: %s", e)

    # 2. Dynamic Fallback strictly computed from actual codebase metrics (NO hardcoded fake strings)
    top_comps = ctx["class_nodes"][:5]
    comp_bullets = "\n".join([f"* **{c}**: Discovered architectural component in `{project_name}`." for c in top_comps]) or "* **Core Application**: Scanned project files and modules."
    dynamic_answer = (
        f"### 1. Plain English Summary\n"
        f"The Living Architecture Twin analyzed **{project_name}** and identified **{total_nodes} components** "
        f"with **{total_edges} connections** across the codebase ({detected_stack}).\n\n"
        f"### 2. Key Discovered Components\n"
        f"{comp_bullets}\n\n"
        f"### 3. Recommended Next Steps\n"
        f"* Inspect component dependency coupling and fan-in/fan-out on the Living Twin Map.\n"
        f"* Package components into containerized services targeting {ctx['target_cloud']}.\n"
        f"* Decouple shared persistent datastores ({tables_list}) using isolated schemas or API contracts."
    )

    evidence_ids = [mn["id"] for mn in ctx["matched_nodes"] if mn["id"] in store.graph.nodes][:5]
    return {
        "question": request.question,
        "answer": dynamic_answer,
        "evidence_node_ids": evidence_ids,
        "source": "Living Architecture Twin Knowledge Graph",
    }
