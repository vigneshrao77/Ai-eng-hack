# Test Plan & Verification Strategy — ModernRx

## 1. Objectives
The ModernRx test suite ensures high scientific, regulatory, and engineering rigor. Because ModernRx operates in regulated pharma IT domains, testing must verify both functional accuracy (e.g. parser, scheduler, and API correctness) and regulatory behavior (e.g. GxP rules, audit trail immutability, evidence citation validation).

---

## 2. Test Pyramid & Methodologies

| Test Tier | Scope | Framework | Pass Criteria |
|---|---|---|---|
| **Unit Tests** | AST parsers, GxP deterministic rules, readiness scoring formulas, blast-radius math, audit hash chain. | `pytest` | 100% pass; mathematical assertions match blueprint formulas. |
| **Property-Based** | Schedule constraint boundaries (no tasks violate dependencies or freeze windows); Monte Carlo order invariants ($P_{50} \le P_{80} \le P_{95}$). | `hypothesis` | 100 iterations pass with random valid inputs without constraint violation. |
| **Golden Findings** | AcmeLIMS planted issue detection (missing audit reason, local file shares, hardcoded admin credential, local timestamps, dead code, shared regulated table). | `pytest` | 100% recall (6/6 planted issues detected with valid evidence node IDs). |
| **Security & Audit** | Audit hash chain tamper detection; RBAC permission checks; path traversal prevention in ZIP uploads; secret redaction before storage. | `pytest`, `httpx` | Tampering detected immediately; unauthorized endpoints return 403 Forbidden. |
| **API Integration** | End-to-end flow from project creation -> analysis -> decomposition -> council -> roadmap -> evidence PDF -> audit verification. | `pytest`, FastAPI `TestClient` / `httpx` | Full lifecycle executes with valid status codes and conforming schemas. |
| **Frontend Smoke** | View loading, Cytoscape graph rendering, decomposition comparison table, live council stream, PDF download button. | `vitest` / Playwright / Node smoke | All routes render without uncaught errors or broken links. |

---

## 3. Specific Test Suites

### 3.1 Unit Test Suite (`tests/unit/`)
1. `test_audit_chain.py`:
   - Genesis block creation.
   - Sequential block appending with SHA-256 hash chaining.
   - Tamper detection: modifying `payload_json` or `prev_hash` causes verification failure.
2. `test_gxp_scanner.py`:
   - Verification of each rule in `rules.yaml` against mock AST fixtures.
   - Classification logic (HIGH, MEDIUM, LOW).
   - Upstream/downstream call propagation.
3. `test_readiness_scorer.py`:
   - Exact deduction calculation for 10 cloud blockers.
   - Score bounds $[0, 100]$.
   - Verification that evidence node IDs are preserved for every deduction.
4. `test_decomp_metrics.py`:
   - Newman Modularity calculation.
   - Inter-cluster call ratio calculation.
   - BlastRadius formula verification: $\sum_{c \in \text{HIGH}} (|c| + \sum |c_{\text{callers}}|)$.
   - RevalScope percentage calculation.
5. `test_council_validation.py`:
   - Schema adherence to `CouncilDecision`.
   - Automatic rejection when an unknown evidence node ID is cited.
6. `test_roadmap_scheduler.py`:
   - Hard dependency ordering (APIs before callers).
   - Freeze window prohibition (no HIGH-tier cutover during freeze weeks).
   - Team capacity limits honored.
7. `test_monte_carlo.py`:
   - Sampling correctness from PERT/Beta distribution.
   - Invariant: $P_{50} \le P_{80} \le P_{95}$.

### 3.2 Integration & Golden Findings Suite (`tests/integration/`)
1. `test_acmelims_golden_findings.py`:
   - Ingests AcmeLIMS repository.
   - Asserts detection of:
     - `GAP_AUDIT_NO_REASON`: `AUDIT_TRAIL` table lacking `reason` column.
     - `BLOCKER_LOCAL_FS`: `InstrumentFileService` referencing `C:\\instrument\\import`.
     - `SEC_HARDCODED_CREDS`: `admin.password=SuperSecret123!` in properties.
     - `GAP_LOCAL_TIMESTAMP`: `new Date()` calls on GxP write paths.
     - `OPP_DEAD_CODE`: `UnusedLegacyCalculator` with 0 fan-in and 0 traces.
     - `COUP_SHARED_TABLE`: `RESULT` table shared between `ResultService` (HIGH) and `ReportService` (LOW).
2. `test_full_pipeline_e2e.py`:
   - Runs full assessment lifecycle through HTTP client.
   - Verifies PDF generation outputs valid `%PDF-` binary with nonzero size.

---

## 4. Execution Commands
```bash
# Run all unit tests
pytest tests/unit -v

# Run golden findings and integration tests
pytest tests/integration -v

# Run with test coverage
pytest --cov=app tests/
```
