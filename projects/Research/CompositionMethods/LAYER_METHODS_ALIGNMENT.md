# Composition Layers — Methods Database & Path Selector Alignment

Answers: are the composition methods (algorithmic/human/sound-production) and
the path selectors aligned with the 3-layer composition paths?

## Methods database → layer alignment

The methods DB (`methods_db.md`, SCALE registry in `workflows/paths.py`,
`generator_registry.py`, skill master-map) splits by **abstraction scale**
L4→L1. Under LAYER_ARCHITECTURE.md these map onto the 3 layers:

| Layer | Holds | Methods | Registry |
|---|---|---|---|
| **Abstract** | 12TET subset sequences, tension curves, pattern network (z/P/L/R) | ABS-001..005 (new) | `rules/subset_network.py` + registry + SCALE (L4/L3) |
| **Concrete** | realized unitmatrix cells, resolved events | all SCALE L1–L4: 001, 002, 012, 018, 023, 040, HC-012, ... | `generators/*` |
| **Absolute** | audio stems → WAV/OGG | SP-001..SP-060 | `sound/render/*`, `sound/synthesis/*` |

Human methods (HC-*) sit in Concrete (they realize material) with style
affinity routing.

## Path selector alignment

`workflows/selector.py` grew from single-method routing to **layer-ordered
chains**:

- `layer_of(method_id)` → abstract | concrete | absolute.
- `TaskProfile.layers_needed` — the chain in execution order.
- `select_chain(profile, per_layer)` → {layer: [methods]} per requested layer.

| Composition path | layers_needed | What comes back |
|---|---|---|
| **Full** | ("abstract","concrete","absolute") | ABS walk → concrete fillers → SP renderers |
| **Direct** (legacy) | ("concrete",) | 001/010/012/... (default) |
| **Render-only** | ("concrete","absolute") | concrete fillers + SP-001/011/... |

Verified: `select_chain(TaskProfile(headless, deterministic,
layers_needed=("abstract","concrete","absolute")))` →
`abstract: [ABS-001, ABS-002], concrete: [001, 010], absolute: [SP-001, SP-011]`.

## Code wiring (the full path works)

`musicom_workflow.compose(method="ABS-002")` runs the abstract subset walk
(`PatternNetwork.walk` with a tension curve over intro/verse/chorus/bridge/
outro), derives per-section chord tones from the walked subsets, then fills
the concrete cells (lead arpeggio, pad, bass, arp, drums) exactly as before.

Verified end-to-end: seed 7 → walk `maj0,maj5,maj0,maj5,min2` (I–IV–I–IV–ii),
validated zero-drift MIDI 4333 B, provenance records
`method: ABS-002:subset_walk=maj0,maj5,maj0,maj5,min2`.

## Gaps remaining (future work)

- ABS methods have no dedicated generator classes (module-level functions in
  `rules/subset_network.py` suffice for walks; Z-variation/complement want
  proper class wrappers when used as standalone generators).
- `docs/methods.md` + `methods_db.md` tables don't list ABS rows yet (large
  manual tables; generator_registry + SCALE are the code truth).
- Audit (`subset membership` per section) exists in project 084's
  audit_084.py pattern; not yet a shared engine rule.
