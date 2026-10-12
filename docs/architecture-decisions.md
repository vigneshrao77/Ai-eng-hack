# Architecture Decision Records (ADR) — ModernRx

## ADR 001: Dual-Mode Infrastructure (Docker Full Stack vs Standalone Lightweight Local)
- **Status:** Accepted
- **Context:** Regulated pharma environments have varied operational environments, and local developers/evaluators may not have Docker Desktop running. Furthermore, hackathons and quick evaluation runs need zero-friction startup.
- **Decision:** ModernRx will implement an abstract repository/storage/graph provider pattern:
  - **Relational DB:** PostgreSQL 16 (production/Docker) with automatic fallback to SQLite (standalone local).
  - **Knowledge Graph:** Neo4j 5 with Cypher query templates (production/Docker) with automatic fallback to an in-memory/JSON-backed NetworkX graph store implementing identical query abstractions.
  - **Task Queue:** Celery with Redis broker (production) with automatic fallback to FastAPI BackgroundTasks / ThreadPoolExecutor.
  - **Object Storage:** MinIO/S3 (production) with automatic fallback to local encrypted/sandboxed directory storage (`data/storage`).
- **Consequences:** Tests and local execution run reliably anywhere without requiring running daemon dependencies, while Docker Compose remains available for containerized deployment.

## ADR 002: Deterministic-First Analysis & Grounded AI Council
- **Status:** Accepted
- **Context:** In GxP regulated systems (FDA 21 CFR Part 11, EU Annex 11, draft Annex 22), AI models cannot be black-box decision makers that hallucinate code facts or metrics.
- **Decision:**
  - All AST parsing, LOC counting, static dependency extraction, cyclomatic complexity, GxP rule matching, and cloud readiness deductions are 100% deterministic code.
  - The AI Architecture Council uses structured Pydantic schemas. Every claim must cite valid `evidence_node_ids` existing in the Living Twin graph. Any output with unknown node IDs is automatically rejected.
  - If no external LLM API key is configured or offline mode is enabled, the system uses a high-fidelity deterministic offline engine that outputs pre-validated, evidence-linked arguments labeled with `[Simulated Offline Response]`.
- **Consequences:** Absolute compliance reproducibility, zero hallucination of repository structure, and full audit traceability.

## ADR 003: Blast-Radius & RevalScope Formulation for Decomposition
- **Status:** Accepted
- **Context:** Generic microservice decomposition (Louvain, plain HDBSCAN) creates service boundaries solely based on coupling/cohesion, which can scatter regulated write paths across multiple microservices or mix low-risk utilities into high-risk services, triggering enormous re-validation blast radiuses.
- **Decision:**
  - ModernRx implements a multi-modal similarity matrix:
    $$S(i,j) = w_1 \cdot \text{Structural}(i,j) + w_2 \cdot \text{Runtime}(i,j) + w_3 \cdot \text{Data}(i,j) + w_4 \cdot \text{CoChange}(i,j) + w_5 \cdot \text{Semantic}(i,j)$$
  - Constrained clustering applies:
    1. **Must-Link:** Nodes participating in the same HIGH-tier write path to the same regulated table are bound together.
    2. **Cannot-Link Penalty:** Penalty applied to prevent pulling LOW-tier reporting/utility components into HIGH-tier clusters.
  - Objective optimization: $\text{Objective} = \alpha \cdot \text{Coupling}(P) - \beta \cdot \text{Cohesion}(P) + \gamma \cdot \text{BlastRadius}(P)$.
  - **Headline Metric:** $\text{RevalScope}(P) = \frac{\text{Components in or calling HIGH clusters}}{\text{Total Components}}$.
- **Consequences:** The system delivers provable reductions in regulatory re-validation scope while preserving architectural modularity.

## ADR 004: Tamper-Evident SHA-256 Hash Chaining for Audit Logs
- **Status:** Accepted
- **Context:** 21 CFR Part 11 and EU GMP Chapter 4 / Annex 11 require computer-generated, time-stamped audit trails that cannot be modified or deleted.
- **Decision:**
  - Audit log entries are strictly append-only.
  - Each entry stores: `id`, `timestamp`, `actor`, `action`, `entity`, `entity_id`, `payload_json`, `prev_hash`, and `hash`.
  - The hash is computed as $\text{SHA256}(\text{prev\_hash} + \text{canonical\_json}(\text{payload}))$.
  - An explicit `/audit/verify` endpoint verifies the integrity of the entire chain from the genesis block.
- **Consequences:** Any tampering, deletion, or modification of historical audit logs immediately breaks the chain and is flagged.

## ADR 005: CP-SAT and PERT Monte Carlo Scheduling
- **Status:** Accepted
- **Context:** Pharma cloud modernization roadmaps must respect hard constraints: foundation landing zones must precede workloads, team squad capacities are finite, GxP freeze windows forbid high-risk cutovers during regulatory inspection/batch release periods, and no more than one HIGH-tier cutover is permitted per wave.
- **Decision:**
  - OR-Tools CP-SAT (with a deterministic topological fallback) schedules migration waves subject to hard dependencies, freeze windows, and squad capacity.
  - Monte Carlo simulation uses three-point PERT/Beta distributions $(o, m, p)$ over 10,000 runs to calculate P50, P80, and P95 delivery confidence.
- **Consequences:** Realistic, defensible project timelines rather than simplistic single-point estimates.

## ADR 006: Standalone PDF Evidence Generation
- **Status:** Accepted
- **Context:** The system must generate professional, audit-ready Computer Software Assurance (CSA) Evidence Packs directly downloadable by users.
- **Decision:** ModernRx will support server-side PDF generation via ReportLab / WeasyPrint with structured HTML/canvas templates including system diagrams, GxP classifications, characterization test plans, data integrity checks, and human sign-off blocks.
- **Consequences:** Instant export of comprehensive compliance documentation.
