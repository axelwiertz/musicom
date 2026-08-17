# Hermes Agent Configuration — Musicom

Agent-specific knowledge base for composition and sound production workflows
running on the Hermes agent (cron jobs, production pipelines, interactive sessions).

**This folder is NOT library code.** It holds operational knowledge:
workflows, method registries, decision records, and playbooks that guide
how the Hermes agent uses the musicom engine.

## Contents

| File | Purpose |
|------|---------|
| `composition.md` | Composition workflow KB: UnitMatrix pipeline, two-phase architecture, zero-drift rules |
| `sound-production.md` | Sound production KB: sound/ package usage, mastering chain, stem rendering |
| `sound-methods-overview.md` | **Sound methods comparison + how-to-use**: creation/transformation table, workflow examples |
| `methods-registry.md` | Sound production method catalog (SP-001…SP-032) with replicability status |
| `surveillance.md` | Music-tech surveillance findings and replicability analyses |
| `decisions.md` | Architecture decision log (reorgs, package choices) |

## Rules

- Engine code stays in the flat packages (`structures/`, `workflows/`, `sound/`, etc.)
- Style-specific content stays OUT of both the engine and this folder (lives in projects)
- AGENTS.md at repo root remains the canonical machine-facing guide; this folder
  extends it with agent-operational knowledge
- Update these files when workflows change
