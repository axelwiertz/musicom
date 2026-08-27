# Open Knowledge Format (OKF) v0.1 Specification

**The Open Knowledge Format (OKF)** is a vendor-neutral, model-agnostic, and agent-friendly open specification for representing metadata, operational context, and curated knowledge in living, directory-based AI wikis.

---

## 1. Structural Architecture (The Bundle)
An OKF **bundle** is a standardized directory containing concepts. Each concept represents a distinct asset or topic (such as a database table, metric, runbook, or API).

### Rules of Conformance:
1.  **Just Files:** Every concept is stored as exactly one `.md` markdown file.
2.  **Explicit Frontmatter:** Every concept markdown file MUST begin with a YAML frontmatter block.
3.  **Strict Link-Graph:** Relational links between concepts are represented via standard relative markdown link syntax: `[Title](/path/to/concept.md)`. This turns the flat folder structure into an explicitly queryable semantic graph.

---

## 2. YAML Frontmatter Schema
Every conformant OKF document must provide the following queryable metadata keys inside its YAML frontmatter:

```yaml
---
type: STRING         # REQUIRED. The category of the concept (e.g., Table, Metric, Skill, Rule)
title: STRING        # REQUIRED. Clear, human-friendly display name.
description: STRING  # REQUIRED. One-sentence functional abstract.
resource: URI        # OPTIONAL. Absolute URL to the asset in production.
tags: [LIST]         # OPTIONAL. Array of categorization keywords.
timestamp: ISO-8601  # REQUIRED. Explicit tracking of compilation or modification state.
---
```

### Reference Implementation File Structure:
```
sales/
├── index.md
├── datasets/
│   ├── index.md
│   └── orders_db.md
├── tables/
│   ├── index.md
│   ├── orders.md
│   └── customers.md
└── metrics/
    ├── index.md
    └── weekly_active_users.md
```

---

## 3. Core Design Principles
*   **Minimally Opinionated:** OKF strictly enforces only the `type` field; schema rules and content bodies are customized by the producer.
*   **Producer/Consumer Independence:** Allows decoupling authorship (humans or programmatic agents) from search/retrieval layers (agents, web visualizers, or RAG models).
*   **Format, Not Platform:** Open, vendor-neutral standard requiring zero accounts, runtimes, or custom SDKs.
