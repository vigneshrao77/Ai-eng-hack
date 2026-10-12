# ModernRx Live Demonstration Runbook (5-Minute Script)

## 1. Demo Overview & Narrative Arc
- **Target Audience:** Pharma CIO/CTO, Head of Cloud Architecture, Head of Quality Assurance & Computer Software Assurance (CSA).
- **Core Value Proposition:** Generic AI rewrites code blindly. ModernRx tells pharma IT *what* to modernize, *in what order*, and *how to prove to FDA/EMA that nothing broke*.
- **Demo Subject:** `AcmeLIMS` — a realistic legacy Java Spring Boot monolith with typical GxP compliance gaps, technical debt, and monolithic coupling.

---

## 2. Minute-by-Minute Runbook

### 0:00 – 0:20 | The Hook
- **Visual:** Project Overview dashboard with modern dark/light UI.
- **Narrative:** "79% of enterprise cloud migrations fail or blow their budgets. In pharma, it's far worse: every architectural change triggers 21 CFR Part 11 or Annex 11 re-validation. ModernRx solves this by reasoning about regulatory criticality alongside architectural modularity."
- **Action:** Click "New Assessment" and select `AcmeLIMS` (or show pre-seeded project).

### 0:20 – 0:40 | The Living Twin Ingestion
- **Visual:** Ingestion progress and Cytoscape Living Twin Knowledge Graph rendering.
- **Narrative:** "Within seconds, ModernRx parses the source code, SQL queries, configuration, and runtime traces into a Living Knowledge Graph. We see classes, methods, database tables, and API endpoints mapped in real time."
- **Action:** Click on `ReviewService` in the graph. The slide-out inspector opens showing LOC, cyclomatic complexity, incoming calls, and touched tables.
- **Interactive Action:** Ask the Twin: *"Which code writes batch release records?"* The Twin returns `BatchReleaseService.releaseBatch()` with clickable evidence node IDs.

### 0:40 – 1:20 | GxP Criticality & Compliance Gaps
- **Visual:** Switch to GxP Heatmap view. The graph highlights in Red (HIGH), Amber (MEDIUM), and Green (LOW).
- **Narrative:** "This is ModernRx's regulatory moat. Notice how our deterministic rules engine identified the regulated core: audit trails, electronic signatures, and batch release decisions. Non-critical code that calls into this core automatically inherits indirect risk."
- **Action:** Open the Compliance Gaps tab:
  - Point to: *"AUDIT_TRAIL table missing reason column"* (21 CFR Part 11 violation).
  - Point to: *"Local timestamp generation `new Date()`"* (ALCOA+ contemporaneous time gap).
  - Point to: *"Local filesystem dependency `C:\instrument\import`"*.
  - Show QA Override: change a node's tier with mandatory justification, immediately logging an immutable audit event.

### 1:20 – 2:00 | Blast-Radius Decomposition & The RevalScope Headline
- **Visual:** Decomposition screen showing 3 side-by-side tabs: Louvain Baseline, Plain HDBSCAN, and ModernRx Constrained.
- **Narrative:** "Traditional algorithms like Louvain or plain HDBSCAN split code purely by technical coupling. Look at the result: plain HDBSCAN scatters regulated write paths across 4 microservices, causing an 82% Re-validation Scope."
- **Action:** Switch to the ModernRx tab.
- **Punchline:** "ModernRx applies must-link constraints on regulated write paths and penalizes mixing low-risk utilities into high-risk clusters. **Our RevalScope drops to 38%** while improving modularity! That saves 6+ months of validation testing."

### 2:00 – 2:50 | AI Architecture Council Debate & Human Approval Gate
- **Visual:** Live Council stream with agent avatars (Cloud Architect, QA Lead, Security Officer, FinOps, Regulatory Affairs, Moderator).
- **Narrative:** "Instead of one generic prompt, ModernRx convenes an AI Architecture Council. Watch the debate: the Cloud Architect proposes event-driven microservices for the Batch engine; the Validation Lead pushes back, warning of high re-validation blast radius; FinOps highlights licensing."
- **Action:** The Moderator synthesizes a Strangler Fig pattern with managed DB.
- **Compliance Highlight:** Point out that every recommendation cites real graph node IDs. Click "Approve as QA Approver" to approve the decision into the audit trail.

### 2:50 – 3:40 | Constraint-Optimized Roadmap & Monte Carlo Uncertainty
- **Visual:** Roadmap Gantt view and Monte Carlo probability distribution chart.
- **Narrative:** "How do we get there safely? Our CP-SAT solver generates migration waves respecting team capacity, dependencies, and regulatory freeze windows (e.g. FDA inspection month). No more than one high-tier service is cut over per wave."
- **Action:** Show the Monte Carlo curve: P50 at Month 8, P80 at Month 10.
- **Interactive Action:** Toggle team squad capacity or move a freeze window to demonstrate instant re-simulation.

### 3:40 – 4:30 | Evidence Pack Generation (CSA Plan)
- **Visual:** Evidence Pack preview and PDF Download.
- **Narrative:** "ModernRx doesn't just plan—it proves. In one click, we generate an audit-ready Computer Software Assurance (CSA) Evidence Pack."
- **Action:** Click "Download PDF" and open the generated document showing:
  - System architecture diagrams.
  - GxP risk classification per component.
  - Risk-based assurance testing plan.
  - Characterization test specifications.
  - SHA-256 digital provenance watermark.

### 4:30 – 5:00 | Tamper-Evident Audit Verification & Close
- **Visual:** Audit Log view with "Verify Chain" button.
- **Narrative:** "Under EU Annex 22 and 21 CFR Part 11, the modernization tool itself must be trustworthy. Every recommendation, override, and approval is sealed in a SHA-256 cryptographic hash chain."
- **Action:** Click "Verify Hash Chain". The screen displays: *"Chain Verified: 14/14 Blocks Valid, Zero Tampering"*.
- **Closing:** "ModernRx: Modernize pharma systems faster, cheaper, and prove to regulators that nothing broke. Thank you."

---

## 3. Contingency & Backup Plan
- **Offline / Disconnected Demo:** The backend automatically falls back to pre-seeded local data and simulated council deliberation if an external network or Anthropic API key is unreachable.
- **Resetting Demo State:** Run `python scripts/seed_demo.py` to restore pristine AcmeLIMS assessment data in 2 seconds.
