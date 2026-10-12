# Requirements Traceability Matrix (RTM) — ModernRx

| Req ID | Requirement Description | Source Document | Implemented By | Test Case / Verification | Status |
|---|---|---|---|---|---|
| **REQ-ENG-01** | Living Architecture Twin: Parse code (Java/SQL/Config), generate knowledge graph with classes, methods, tables, endpoints, and calls | Blueprint §8, PDF Obj 1 | `backend/app/engines/twin/` | `tests/test_twin_parser.py` | Planned |
| **REQ-ENG-02** | Whitelisted Cypher/Graph Queries & "Ask the Twin" tool | Blueprint §8.2 | `backend/app/api/routes_twin.py` | `tests/test_twin_queries.py` | Planned |
| **REQ-ENG-03** | Auto-generate C4 Diagrams in Mermaid format | Blueprint §8.2 | `backend/app/engines/twin/c4.py` | `tests/test_c4_generator.py` | Planned |
| **REQ-ENG-04** | GxP Criticality Scanner: Deterministic rules (Part 11, Annex 11, CSA) | Blueprint §9 | `backend/app/engines/gxp/scanner.py` | `tests/test_gxp_scanner.py` | Planned |
| **REQ-ENG-05** | GxP Tier Propagation (callers inherit indirect risk) | Blueprint §9.2 | `backend/app/engines/gxp/propagation.py` | `tests/test_gxp_propagation.py` | Planned |
| **REQ-ENG-06** | QA Override Queue with required reason and immutable audit log | Blueprint §9.2, §15 | `backend/app/api/routes_gxp.py` | `tests/test_gxp_override.py` | Planned |
| **REQ-ENG-07** | Compliance Gap Detection (missing audit reason, local timestamps, credentials) | Blueprint §9.4 | `backend/app/engines/gxp/gaps.py` | `tests/test_golden_findings.py` | Planned |
| **REQ-ENG-08** | Cloud Readiness Scorer: 10-factor explainable deductions (0–100) | Blueprint §10, PDF Obj 2 | `backend/app/engines/readiness/scorer.py` | `tests/test_readiness_scorer.py` | Planned |
| **REQ-ENG-09** | Dead code and quick-win rehost detection | Blueprint §10 | `backend/app/engines/readiness/opportunities.py` | `tests/test_readiness_opps.py` | Planned |
| **REQ-ENG-10** | Multi-factor Similarity Matrix (Structural, Runtime, Data, CoChange, Semantic) | Blueprint §11.1 | `backend/app/engines/decompose/features.py` | `tests/test_decomp_matrix.py` | Planned |
| **REQ-ENG-11** | 3-Way Decomposition Comparison: Louvain, Plain HDBSCAN, ModernRx Constrained | Blueprint §11.4, PDF Obj 4 | `backend/app/engines/decompose/cluster.py` | `tests/test_decomp_cluster.py` | Planned |
| **REQ-ENG-12** | BlastRadius & RevalScope metric calculations | Blueprint §11.4 | `backend/app/engines/decompose/metrics.py` | `tests/test_decomp_metrics.py` | Planned |
| **REQ-ENG-13** | AI Architecture Council: 6 specialist agents with debate protocol | Blueprint §12 | `backend/app/engines/council/` | `tests/test_council_debate.py` | Planned |
| **REQ-ENG-14** | Council Schema Validation & Evidence Node ID Citation Check | Blueprint §12.3 | `backend/app/engines/council/validator.py` | `tests/test_council_validation.py` | Planned |
| **REQ-ENG-15** | Human Approval Gate for High-Risk Modernization Decisions | Blueprint §12.1, §15 | `backend/app/api/routes_approvals.py` | `tests/test_approvals.py` | Planned |
| **REQ-ENG-16** | Roadmap Optimizer: Dependency ordering, team capacity, freeze windows, wave planning | Blueprint §13.1, PDF Obj 5 | `backend/app/engines/roadmap/scheduler.py` | `tests/test_roadmap_scheduler.py` | Planned |
| **REQ-ENG-17** | Monte Carlo Simulator: 10,000 PERT runs computing P50, P80, P95 | Blueprint §13.2 | `backend/app/engines/roadmap/montecarlo.py` | `tests/test_monte_carlo.py` | Planned |
| **REQ-ENG-18** | CSA Evidence Pack PDF Generator with assurance plan and characterization tests | Blueprint §14 | `backend/app/engines/evidence/report.py` | `tests/test_evidence_pdf.py` | Planned |
| **REQ-ENG-19** | Self-Compliance Audit Chain: SHA-256 hash chaining with `/audit/verify` | Blueprint §15 | `backend/app/core/audit.py` | `tests/test_audit_chain.py` | Planned |
| **REQ-ENG-20** | JWT Authentication & RBAC (viewer, architect, qa_approver, admin) | Blueprint §17, §24 | `backend/app/core/auth.py` | `tests/test_auth_rbac.py` | Planned |
| **REQ-ENG-21** | AcmeLIMS Legacy Monolith with 6 Planted Smells | Blueprint §19 | `demo-lims/` | `tests/test_golden_findings.py` | Planned |
| **REQ-ENG-22** | Complete Next.js Responsive UI across all 10 views | Blueprint §18 | `frontend/` | `frontend/e2e/smoke.test.ts` | Planned |
| **REQ-ENG-23** | Offline Demo Mode (runs without external API keys or Docker) | Blueprint §12.4, §20 | `backend/app/core/config.py` | `tests/test_offline_mode.py` | Planned |
