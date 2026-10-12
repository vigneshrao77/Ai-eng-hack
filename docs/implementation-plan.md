# ModernRx Implementation Plan & Milestone Checklist

**Project Name:** ModernRx — AI-Powered Application Modernization Advisor for Pharma IT/Cloud  
**Author/Lead:** Principal Software Architect & QA Lead  
**Status:** In Progress (Milestone 0 Baseline Completed)  
**Target Completion:** All 14 Milestones Complete & Demo-Ready  

---

## 1. Executive Summary & Core Mission
ModernRx is a GxP-aware application modernization advisor specifically engineered for regulated life sciences (pharma, biotech, CDMO) environments. Generic AI tools transform code blindly without regulatory risk awareness. ModernRx converts legacy pharma monoliths into a Living Architecture Twin, scans for 21 CFR Part 11 / EU Annex 11 / CSA regulatory criticality, computes Cloud Readiness, executes Blast-Radius-Aware decomposition, convenes an AI Architecture Council, optimizes migration roadmaps using CP-SAT and Monte Carlo, and generates audit-ready CSA Evidence Packs with tamper-evident audit trails.

---

## 2. Source of Truth & Architecture Foundation
- **Primary Specifications:**
  - `ModernRx_Solution_Blueprint.md` (System Architecture, 7 Engines, APIs, Models, UI, AcmeLIMS, Security)
  - FDA Computer Software Assurance (CSA) Final Guidance (Sept 2025 / Feb 2026)
  - EU GMP Annex 11 (Computerised Systems) & Draft Annex 22 (AI in GMP)
- **The Seven Engines:**
  1. *Living Architecture Twin:* Code + SQL + Config + Traces -> Neo4j / NetworkX Knowledge Graph.
  2. *GxP Criticality Scanner:* Deterministic rules + propagation + LLM fallback -> HIGH/MEDIUM/LOW tiers + GxP Heatmap.
  3. *Cloud Readiness Scorer:* 12-factor checks, tech debt, shared DB couplings -> 0–100 explainable score with deductions.
  4. *Blast-Radius-Aware Decomposition:* Multi-modal similarity matrix (structural, runtime, data, co-change, semantic) + HDBSCAN + GxP must-link/cannot-link constraints -> Louvain vs Plain HDBSCAN vs ModernRx comparison with RevalScope reduction.
  5. *AI Architecture Council:* Multi-agent debate (Cloud Architect, QA Lead, Security Officer, FinOps, Regulatory Affairs, Moderator) -> 7R strategies + target patterns + effort estimates.
  6. *Roadmap Optimizer & Monte Carlo:* OR-Tools CP-SAT wave scheduling (freeze windows, capacity, risk caps) + 10,000 PERT Monte Carlo simulations (P50/P80/P95).
  7. *Evidence Pack Generator:* Audit-ready PDF with CSA assurance plan, characterization test recommendations, differential testing plans, and traceability.

---

## 3. Environment & Runtime Analysis

| Component | Host State | Strategy / Adaptation |
|---|---|---|
| **Python** | Python 3.13.1 | Build robust backend with Python 3.11–3.13 compatibility, pinned dependencies, fallback handling for pure-python wheels where native binaries vary. |
| **Node.js / npm** | Node v24.18.0, npm 11.16.0 | Use Next.js 14/15 App Router, TypeScript, Tailwind CSS, Cytoscape, Recharts, Lucide, React Query. |
| **Java** | Java 25.0.3 LTS | AcmeLIMS Java target application with Maven wrapper / Java source tree for deterministic parsing and inspection. |
| **Docker** | Docker 29.8.0, Compose v5.5.1 (daemon currently stopped) | Full `docker-compose.yml` for multi-container stack (Neo4j, Postgres, Redis, MinIO) + Built-in dual-mode architecture: zero-external-dependency local standalone mode (SQLite, NetworkX Graph engine, In-memory job worker, Local storage). |
| **LLM Access** | Configurable via Anthropic API | Anthropic Claude client with strict model pinning (`claude-3-5-sonnet-20241022` / `claude-sonnet-5-5`) + Deterministic offline fallback mode producing schema-validated, evidence-linked responses when offline/no key is provided. |

---

## 4. Scope & Cut Line (MVP vs Stretch)

### Required MVP (Non-Negotiable)
- Monorepo structure: `backend/`, `frontend/`, `demo-lims/`, `docs/`, `eval/`.
- Dual runtime support (Dockerized stack + Standalone local mode with SQLite/NetworkX/In-memory queue).
- Engine 1: Repository ingestion, language detect, LOC, Java/SQL/Config parsing, knowledge graph, whitelisted Cypher/query API, C4 Mermaid generator.
- Engine 2: Deterministic GxP rules (Audit, Esig, Access, Data Integrity, Product Release, Time Source), propagation, review queue, override API with audit logging, GxP Heatmap.
- Engine 3: Cloud Readiness Scorer (10+ checks, explainable deductions, evidence node IDs, dead code & quick wins).
- Engine 4: Blast-Radius-Aware Decomposition (similarity matrix, baseline Louvain, plain HDBSCAN, ModernRx constrained refinement) with explicit headline RevalScope comparison.
- Engine 5: AI Architecture Council (Specialist agents + Moderator, structured schema validation, evidence citation check, offline deterministic demo mode).
- Engine 6: Roadmap Optimizer (CP-SAT / deterministic scheduler with freeze windows, team capacity, 1 HIGH cutover per wave) + Monte Carlo (P50, P80, P95).
- Engine 7: Evidence Pack PDF generation (CSA plan, characterization tests, data integrity checks, downloadable real PDF).
- Self-Compliance & Audit: SHA-256 hash-chained audit log with verification endpoint.
- AcmeLIMS demo app: Intentionally legacy Java monolith with all 6 planted issues, test fixtures, and golden-finding regression tests.
- Complete responsive frontend UI connecting all engines with real APIs, graph visualization, live debate stream, Gantt/histogram, and PDF download.

### Optional Stretch Goals
- PyTorch Geometric GNN GraphSAGE embeddings (fallback to sentence-transformers / structural feature concatenation).
- Deep Git commit mining (fallback to static file proximity / commit simulation when scanning standalone ZIPs).
- Dynamic interactive what-if re-simulation sliders in UI (provided as fast API recalculation).

---

## 5. Milestone Checklist & Execution Plan

### Milestone 0: Baseline & Plan (Current)
- [x] Inspect repository, runtime environment, tools, and blueprint.
- [x] Initialize Git repository.
- [x] Create planning documents (`docs/implementation-plan.md`, `docs/architecture-decisions.md`, `docs/requirements-traceability.md`, `docs/test-plan.md`, `docs/demo-runbook.md`).
- [x] Define feature-to-test traceability matrix.
- **Acceptance:** Baseline documented, risks identified, roadmap established.

### Milestone 1: Runnable Foundation
- [ ] Backend skeleton with FastAPI, Pydantic v2, SQLAlchemy 2 (dual Postgres/SQLite), configuration with pydantic-settings.
- [ ] Frontend skeleton with Next.js App Router, TypeScript, Tailwind CSS, Lucide icons, dark/light theme.
- [ ] `docker-compose.yml`, `.env.example`, and developer scripts (`Makefile` / `run.ps1`).
- [ ] Health endpoints (`/health`, `/ready`), database auto-init/migrations, seed command.
- [ ] Automated smoke tests passing in CI/local runner.
- **Acceptance:** Clean setup works, backend and frontend start cleanly, health checks return 200 OK.

### Milestone 2: Authentication, Projects, and Job Management
- [ ] User authentication with JWT and bcrypt password hashing.
- [ ] RBAC roles: `viewer`, `architect`, `qa_approver`, `admin`.
- [ ] Projects API: create, list, inspect target cloud (AWS, Azure, GCP).
- [ ] Safe repository upload (ZIP archive validation, path traversal protection, archive bomb limits, secret masking).
- [ ] Job lifecycle manager (PENDING, RUNNING, COMPLETED, FAILED) with progress reporting (REST polling + WebSocket).
- [ ] Asynchronous task runner supporting both Celery/Redis and in-memory background worker.
- **Acceptance:** Create project, upload repo, track progress, test auth and RBAC restrictions.

### Milestone 3: Living Architecture Twin (Engine 1)
- [ ] Repository ingester: language detection, LOC counting, file metadata.
- [ ] Tree-sitter / regex AST parsers for Java (classes, methods, annotations `@Entity`, `@Transactional`, `@Scheduled`, `@PreAuthorize`, field types, calls).
- [ ] SQL parser (sqlglot) for tables, columns, read/write queries.
- [ ] Config parser (`application.properties`, XML, YAML) for DB URLs, file shares, hard-coded credentials.
- [ ] Graph store abstraction: Neo4j client and NetworkX embedded graph engine.
- [ ] Whitelisted graph query API (no raw Cypher injection), Mermaid C4 diagram generator.
- [ ] "Ask the Twin" query interface citing graph node IDs.
- **Acceptance:** Analyze sample repository, produce interactive node/edge graph, generate C4 diagram, verify graph queries.

### Milestone 4: GxP Criticality Scanner (Engine 2)
- [ ] Configurable `rules.yaml` for AUDIT_TRAIL, E_SIGNATURE, ACCESS_CONTROL, DATA_INTEGRITY, PRODUCT_RELEASE, TIME_SOURCE, REPORTING_ONLY.
- [ ] Explainable classification: HIGH, MEDIUM, LOW.
- [ ] Call-graph propagation (LOW callers of HIGH write paths inherit MEDIUM indirect).
- [ ] QA override API with mandatory rationale and tamper-evident audit logging.
- [ ] GxP graph heatmap data generation and compliance gap detector.
- **Acceptance:** 100% test coverage on rule detection, propagation math, override audit logging, and gap reports.

### Milestone 5: Cloud Readiness Scorer (Engine 3)
- [ ] 10-point weighted readiness check: statelessness, local filesystem, secrets, EOL frameworks, DB coupling, complexity/LOC, tests, scheduled jobs, licensing, observability.
- [ ] Normalization math (0–100 score), explainable deductions with evidence node IDs.
- [ ] Dead code detector (unreachable classes/methods) and quick-win rehost candidate identifier.
- **Acceptance:** Deterministic fixture test verifying exact score math, deduction trace, and quick-win tagging.

### Milestone 6: Blast-Radius-Aware Decomposition (Engine 4)
- [ ] Multi-factor similarity matrix: Structural (calls), Data (shared tables), Runtime (traces), Semantic (names/docs).
- [ ] Baseline community detector (Louvain).
- [ ] Plain HDBSCAN clustering.
- [ ] ModernRx constrained decomposition: must-link on HIGH write paths, penalty on LOW utilities in HIGH clusters, local search refinement.
- [ ] Exact metric computations: Newman Modularity (Q), Inter-Cluster Call Ratio (ICP), BlastRadius, and RevalScope %.
- [ ] Side-by-side comparison endpoint demonstrating real calculated metrics.
- **Acceptance:** Real calculation runs across all three variants; RevalScope reduction clearly verified.

### Milestone 7: AI Architecture Council (Engine 5)
- [ ] 6 Specialist agent personas: Cloud Architect, Validation & QA Lead, Security Officer, FinOps Analyst, Regulatory Affairs, Moderator.
- [ ] Debate protocol: context loading -> initial opinions -> 1 rebuttal round -> moderator synthesis.
- [ ] Strict Pydantic output schema: 7R strategy, target patterns, target services, effort estimates, risks, dissent, evidence node IDs.
- [ ] Validation layer: reject hallucinated/unknown evidence node IDs.
- [ ] Offline simulation fallback with deterministic, high-quality, pre-validated arguments labeled as simulated.
- [ ] Human approval workflow: HIGH-tier recommendations require `qa_approver` role.
- **Acceptance:** Invalid evidence IDs rejected, schema validated, approval gate enforced.

### Milestone 8: Roadmap Optimizer & Monte Carlo Simulator (Engine 6)
- [ ] Task duration estimation (optimistic, likely, pessimistic) with GxP complexity multipliers.
- [ ] CP-SAT / deterministic constraint scheduler: dependency ordering, team squad capacity, GxP freeze windows, max 1 HIGH cutover per wave.
- [ ] Monte Carlo engine: 10,000 PERT/Beta simulation runs computing P50, P80, P95 completion dates and critical path.
- [ ] What-if re-simulation endpoint for dynamic schedule exploration.
- **Acceptance:** Dependency and freeze window constraints strictly honored; property test confirms P50 <= P80 <= P95.

### Milestone 9: Evidence Pack Generator (Engine 7)
- [ ] Jinja2 templated CSA-style Assurance Plan.
- [ ] Automated characterization test specifications.
- [ ] Shadow/differential testing plan and data migration verification checks.
- [ ] Traceability matrix: Requirement -> Component -> Test -> Evidence.
- [ ] PDF generation using ReportLab / WeasyPrint with disclaimer and QA sign-off block.
- **Acceptance:** Real downloadable PDF generated containing actual assessment results and diagrams.

### Milestone 10: Audit, Security, and Compliance Hardening
- [ ] Tamper-evident SHA-256 hash-chained audit log (`prev_hash`, `payload_hash`, `hash`).
- [ ] Audit log verification endpoint (`GET /audit/verify`).
- [ ] Input sanitization, path traversal prevention, secret masking before storage.
- [ ] RBAC enforcement across all mutation endpoints.
- **Acceptance:** Tamper-detection unit test confirms any modified log row breaks the verification chain.

### Milestone 11: Complete Frontend Experience
- [ ] Project management and assessment wizard.
- [ ] KPI Overview dashboard with assessment timer and metric cards.
- [ ] Interactive Twin graph using Cytoscape with search, zoom, filter, node inspector, and Mermaid C4.
- [ ] GxP Heatmap view with compliance gap list and QA override modal.
- [ ] Cloud Readiness breakdown with deduction evidence links.
- [ ] Decomposition 3-way comparison screen highlighting RevalScope.
- [ ] Live AI Council debate feed with agent avatars, dissent tabs, and QA approval buttons.
- [ ] Roadmap Gantt chart and Monte Carlo uncertainty histogram.
- [ ] Evidence Pack PDF preview and one-click download.
- [ ] Tamper-evident Audit Log viewer with live hash chain verification.
- **Acceptance:** Smooth end-to-end user experience, responsive, zero broken links, accessible design.

### Milestone 12: AcmeLIMS Legacy Monolith & Golden Findings
- [ ] Build realistic Java Spring monolith (~15 classes) covering Sample, Result, Review, Batch, Audit, Instrument, Reporting, Admin, Scheduler, and Util.
- [ ] Plant 6 specific issues:
  1. Missing audit reason column in `AUDIT_TRAIL`.
  2. Local filesystem dependency (`C:\instrument\import`).
  3. Hard-coded admin credential in configuration.
  4. Non-standard local timestamp generation (`new Date()`).
  5. Dead utility code without callers.
  6. Shared regulated `RESULT` table between core write service and reporting.
- [ ] Golden-findings test suite verifying 100% recall of planted issues.
- **Acceptance:** Automated test confirms all 6 planted issues are detected and linked to evidence.

### Milestone 13: Automated Testing & Evaluation Suite
- [ ] Unit tests, property-based tests (Hypothesis), API integration tests.
- [ ] Full end-to-end evaluation script generating evaluation metrics table.
- **Acceptance:** Test suite executes and reports real measured metrics.

### Milestone 14: Demo Polish & Delivery Runbook
- [ ] One-command launch script (`run_demo.bat` / `run_demo.ps1`).
- [ ] Seed data script loading AcmeLIMS ready for instantaneous demo.
- [ ] Complete 5-minute demo runbook with backup contingencies.
- **Acceptance:** Full end-to-end rehearsal passes repeatedly without error.
