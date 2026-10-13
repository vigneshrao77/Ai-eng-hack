# Project Structure

## Project type

Full-stack application with a Python/FastAPI API, a Next.js/React frontend, and a separate Java/Spring Boot AcmeLIMS demo target used as modernization input.

## Top-level modules

- `backend/` — FastAPI application, persistence, graph store, analysis engines, and background job runner.
- `frontend/` — Next.js App Router UI for projects, twin graph, GxP, readiness, decomposition, council, roadmap, and evidence.
- `demo-lims/` — Spring Boot 2.7.18 Java 17 legacy LIMS sample.
- `tests/` — Python unit and integration tests.
- `scripts/` — demo data/bootstrap scripts.
- `docker-compose.yml` — optional Neo4j, PostgreSQL/pgvector, Redis, MinIO, backend, worker, and frontend services.

## Backend layers

- API layer: `backend/app/api/routes_*.py`; route modules are the externally triggerable API units.
- Core layer: auth, audit-chain logging, LLM access, and structured logging.
- Persistence layer: SQLAlchemy models/session and graph-store abstraction.
- Engine layer: twin ingestion/parsing, GxP scanning, readiness scoring, decomposition, council, roadmap, and evidence generation.
- Worker layer: background job submission/progress updates.

## Frontend layers

- App Router pages under `frontend/app/`.
- Shared layout/navigation under `frontend/app/layout.tsx` and `frontend/app/projects/[id]/layout.tsx`.
- HTTP client and API contracts under `frontend/lib/api.ts`.
- Shared presentation components under `frontend/components/`.

## Runtime entrypoints

- FastAPI app: `backend/app/main.py:15`, exposed by Uvicorn on port 8000.
- Next.js app: `frontend/app/layout.tsx:11`, development server on port 3000.
- Spring Boot app: `demo-lims/src/main/java/com/acme/lims/AcmeLimsApplication.java:7`, port 8080.
- Scheduled Java job: `demo-lims/src/main/java/com/acme/lims/scheduler/NightlyJobScheduler.java:13`.

## Functional areas

- Authentication and role-based access.
- Project registration and repository upload.
- Living architecture twin ingestion, graph, C4, and question answering.
- GxP criticality assessment and QA overrides.
- Cloud readiness scoring.
- Decomposition/RevalScope analysis.
- AI architecture council and human approvals.
- Roadmap scheduling and Monte Carlo what-if analysis.
- Evidence-pack PDF generation and download.
- Tamper-evident audit log.
- AcmeLIMS sample laboratory workflows: samples, results, review/signature, batch release, instruments, reports, audit, and nightly stability checks.

