## 3. Solution Overview

ModernRx is a web platform with **7 engines** in a pipeline:

```
 Upload repo / connect Git
        │
        ▼
 [1] Living Architecture Twin  ── code + DB + config + runtime traces → Knowledge Graph
        │
        ├──► [2] GxP Criticality Scanner   (Part 11 / Annex 11 / CSA risk tagging)
        ├──► [3] Cloud Readiness Scorer    (12‑factor, tech debt, dependencies)
        │
        ▼
 [4] Blast‑Radius‑Aware Decomposition  (HDBSCAN + GxP constraint)
        │
        ▼
 [5] AI Architecture Council  (5 agents debate → 7R + target pattern per component)
        │
        ▼
 [6] Roadmap Optimizer + Monte Carlo  (wave plan, P50/P80 dates, risk)
        │
        ▼
 [7] Evidence Pack Generator  (CSA assurance plan, characterization tests, PDF)
        │
        ▼
 Dashboard + Chat with the Twin + Human approval gates (audit trail record)
```
