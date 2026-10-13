# Architecture Index

This index is a navigation aid for implementation and design work. **This index is not the full contract. Do not implement from this file alone; follow the artifact paths below.**

## Implementation Guide

### Global artifacts

- `unit_graph.yaml` — all workers; filter by assigned unit for trigger, source anchors, exported signatures, dependencies, and shared refs.
- `wire_contracts.yaml` — workers touching REST/file/API edges; filter `unit`, and also read the `global` frontend-backend contract.
- `shared_modules.yaml` — workers whose unit has `shared_refs`; filter `used_by_units` and use only the listed field/method subset.
- `cross_unit_state.yaml` — workers touching auth, graph, decisions, or UI/API state; filter flows where their unit is writer or reader.
- `project-structure.md`, `tech-stack.md`, `data-model.md` — design/context views of the repository structure, current stack, and persisted entities.
- There is no migration boundary artifact because this request is an architecture analysis, not a requested rewrite or migration.

### Per-unit contract

Every unit has:

- `units/<unit>/behavior.yaml` — externally observable side effects, significant branches, errors, and transaction/concurrency behavior.
- `units/<unit>/bindings.yaml` — route/dependency/config wiring that must remain connected.
- `units/<unit>/unit_decomposition.yaml` — advisory split candidates only; `commit: false` means design must decide.

### Units

| Unit | External trigger | Required global filters |
|---|---|---|
| `health-api` | `/health`, `/ready` | `shared_modules` rows for `settings` |
| `auth-api` | `/auth/login`, `/auth/me` | `cross_unit_state` browser token flow |
| `projects-api` | `/projects` and upload | `audit-service`, `db-session`, project REST contract |
| `jobs-api` | `/jobs/{job_id}` | `db-session` |
| `audit-api` | `/audit`, `/audit/verify` | audit REST contract and auth |
| `twin-api` | analysis, graph, C4, ask endpoints | graph-store, job flow, twin graph contract |
| `gxp-api` | GxP assessment/override | graph-store, audit-service |
| `readiness-api` | readiness endpoint | graph-store and project-graph flow |
| `decomposition-api` | decomposition endpoints | graph-store, settings, project-graph flow |
| `council-api` | council run/decisions | auth, decision approval flow |
| `approvals-api` | approve/reject decision | audit-service and decision approval flow |
| `roadmap-api` | roadmap and what-if | database roadmap contract |
| `evidence-api` | evidence generation/list/download | file contract, auth, database |

Before completion, an implementation worker must report: artifact paths read; each implemented `must_preserve`/`must_appear_in_target` item; unresolved or deferred contracts; and build/test/runtime evidence.

