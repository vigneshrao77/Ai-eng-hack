# Data Model

## Relational entities

- `User` (`users`) — identity, email, display name, role, password hash, creation timestamp.
- `Project` (`projects`) — project metadata, repository URL/local path, target cloud, status, creator, and creation timestamp.
- `Job` (`jobs`) — project-scoped asynchronous operation type, status, progress, message, error, JSON result, and timing.
- `GxpOverride` (`gxp_overrides`) — project/node tier changes with reason, user, and timestamp.
- `Decision` (`decisions`) — council strategy, target pattern/services, confidence, rationale, risks, dissent, evidence IDs, effort estimate, status, model and input/prompt hashes.
- `Approval` (`approvals`) — decision approval/rejection action, user, comment, and timestamp.
- `Roadmap` (`roadmaps`) — project schedule JSON and Monte Carlo JSON.
- `EvidencePack` (`evidence_packs`) — project wave, generated file path/name, SHA-256 hash, and timestamp.
- `AuditLog` (`audit_log`) — append-only event identity, actor/action/entity, payload, previous hash, and current hash.

## Relationships

- `Project.jobs` is one-to-many with cascade delete-orphan.
- `Decision.approvals` is one-to-many with cascade delete-orphan.
- Foreign keys connect jobs, overrides, decisions, approvals, roadmaps, evidence packs, and projects/users.
- Graph nodes and edges are persisted through the graph-store abstraction rather than SQLAlchemy entities.

## Schema evidence

The SQLAlchemy mappings are defined in `backend/app/db/models.py:19-173`. Project analysis uses graph nodes for classes/components/tables and edges for calls/dependencies; the frontend receives flattened Cytoscape-compatible node/edge records.

## Key entities

1. `Project` — root aggregate for an uploaded or demo repository assessment.
2. `Job` — progress and result envelope for long-running twin/analysis work.
3. `Decision` — AI council output awaiting human approval.
4. `Approval` — regulated human decision record.
5. `AuditLog` — cryptographically chained evidence of mutations.
6. `EvidencePack` — immutable artifact metadata and download location.
7. `GxpOverride` — QA-controlled classification override.
8. Graph node/edge records — living architecture twin topology and derived annotations.

