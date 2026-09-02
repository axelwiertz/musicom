# -*- coding: utf-8 -*-
"""Method selector — (task profile) -> ordered method list (build step 2).

Plan §4 (projects/Research/CompositionMethods/PATH_LAYER_PLAN.md):

    Selector = pure function (task profile) -> ordered method list. No state,
    fully testable, makes the "why this method?" decision auditable in
    provenance (path: [016, 015, 014, 023], selector_reason: {...}).

Design rules honored:
- **Registry-aware routing** (advice #3): route by generator_registry's
  implementation status, never by DB presence. A spec-only method is a dead
  end — the selector filters it out regardless of how well it matches.
- **Derives, doesn't duplicate**: memory-depth factor is computed from the
  SCALE registry (workflows/paths.py), so methods added daily to SCALE flow
  in automatically. Only the trait tags that can't be derived (tonal gravity,
  metric binding, corpus use, determinism, cost) live here — and unknown/new
  methods get level-derived defaults so they stay selectable.
- **Cost guard** (advice #7): executable_headless flag per method; heavy
  AI-Driven methods are filtered out of cron/headless contexts automatically
  but remain selectable for explicit interactive runs.

Pure function, no state, no I/O. Every decision is returned with its reason
so provenance can record why a method was picked.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from workflows.paths import SCALE, LEVELS, methods_by_scale, impl_status, scale_of

# Neutral default level for registry-only methods not yet classified in SCALE
# (daily additions land in the registry first; classification follows).
_DEFAULT_LEVEL = "L3"  # meso — the safest default (anchors, loops, motifs)

# --- reality check: implementation truth lives in generator_registry --------
# paths.SCALE mirrors it, but generator_registry is the ground truth; consult
# it directly so the selector can't be lied to by a stale mirror.
try:
    from generators.generator_registry import GENERATOR_REGISTRY

    def _registry_has_code(method_id: str) -> bool:
        entry = GENERATOR_REGISTRY.get(method_id)
        return entry is not None and entry[0] is not None
except ImportError:  # pragma: no cover - defensive; registry always present
    GENERATOR_REGISTRY = {}

    def _registry_has_code(method_id: str) -> bool:
        return impl_status(method_id)


# ============================================================================
# Task profile — the factors (plan §4 routing table)
# ============================================================================

@dataclass(frozen=True)
class TaskProfile:
    """Factors that route method selection. All optional; unset = don't care.

    tonal_gravity : "strict" (functional harmony) | "organic" (free/ambient)
    metric_binding: "grid" (quantized) | "fluid" (free time)
    memory_depth  : "macro" | "meso" | "local" (coherence horizon)
    corpus        : True if source material exists to transform
    determinism   : True if byte-reproducible output required (golden tests)
    style         : style key for HC-method affinity (e.g. "flamenco")
    headless      : True if running unattended (cron) — filters heavy methods
    """
    tonal_gravity: Optional[str] = None
    metric_binding: Optional[str] = None
    memory_depth: Optional[str] = None
    corpus: Optional[bool] = None
    determinism: Optional[bool] = None
    style: Optional[str] = None
    headless: bool = False
    layers_needed: Tuple[str, ...] = ("concrete",)
    """Layer chain the task wants, in execution order: e.g. ("abstract",
    "concrete") = design subset walk, then realize; ("concrete", "absolute")
    = realize + render audio. Default: concrete only (legacy behavior)."""


# ============================================================================
# Trait tags — the factors that CANNOT be derived from SCALE level.
# memory_depth is derived (L4->macro, L3->meso, L2/L1->local/voice) so it is
# NOT here. Methods missing from TRAITS get level-derived defaults and stay
# selectable (daily additions degrade gracefully instead of vanishing).
# ============================================================================

# trait keys: gravity, metric, corpus, deterministic, headless_ok
TRAITS: Dict[str, Dict] = {
    # --- implemented methods (tuned by hand) ---
    "001": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "002": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": True},
    "003": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": False, "headless_ok": True},
    "010": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "012": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "018": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "023": {"gravity": "organic", "metric": "fluid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "040": {"gravity": "organic", "metric": "fluid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "HC-012": {"gravity": "strict", "metric": "grid", "corpus": False,
               "deterministic": True, "headless_ok": True},
    # --- spec-only but tagged (for when they land, and for docs) ---
    "006": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "007": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "011": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "016": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "025": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "032": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "033": {"gravity": "strict", "metric": "grid", "corpus": True,
            "deterministic": True, "headless_ok": True},
    "034": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "050": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "056": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "065": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "066": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "069": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "026": {"gravity": "strict", "metric": "grid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    # AI-Driven heavy methods — training/GPU, excluded from headless (advice #7)
    "042": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "046": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "047": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "054": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "057": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "059": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "060": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "062": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    "063": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": False},
    # corpus-driven methods (need source material)
    "039": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": False, "headless_ok": True},
    "044": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": True, "headless_ok": True},
    "067": {"gravity": "organic", "metric": "fluid", "corpus": True,
            "deterministic": True, "headless_ok": True},
    # nature-led / stochastic contour methods
    "043": {"gravity": "organic", "metric": "fluid", "corpus": False,
            "deterministic": True, "headless_ok": True},
    "048": {"gravity": "organic", "metric": "fluid", "corpus": False,
            "deterministic": False, "headless_ok": True},
    "053": {"gravity": "organic", "metric": "fluid", "corpus": False,
            "deterministic": False, "headless_ok": True},
}

# Style -> human-craft method affinity (plan §4 Style fidelity factor)
STYLE_HC_MAP = {
    "flamenco": "HC-012",
    "gamelan": "HC-002",
    "raga": "HC-004",
    "ew": "HC-005",
    "minimal": "HC-008",
    "georgian": "HC-013",
    "pygmy": "HC-014",
    "sacred_harp": "HC-015",
    "sanjo": "HC-017",
    "jazz": "HC-006",
    "baroque": "HC-001",
}

# SCALE level -> memory_depth factor value (derived, never hand-maintained)
_LEVEL_TO_DEPTH = {"L4": "macro", "L3": "meso", "L2": "local", "L1": "local"}

# ============================================================================
# Layer tags (LAYER_ARCHITECTURE.md) — abstract | concrete | absolute
# ============================================================================
# Concrete = every existing SCALE method (L4/L3 structure, L2/L1 material).
# Abstract = subset-network methods (rules/subset_network.py): ABS-001..005.
# Absolute = sound production SP-* methods (workflows/musicom_workflow.SP_METHODS).
# Derived for SCALE methods (all concrete); explicit map for the rest.
_ABSTRACT_IDS = {"ABS-001", "ABS-002", "ABS-003", "ABS-004", "ABS-005"}
_ABSOLUTE_PREFIX = "SP-"


def layer_of(method_id: str) -> str:
    """Which layer a method feeds: abstract | concrete | absolute."""
    if method_id in _ABSTRACT_IDS:
        return "abstract"
    if method_id.startswith(_ABSOLUTE_PREFIX):
        return "absolute"
    return "concrete"   # all SCALE L1-L4 methods realize concrete material

# Level-derived defaults for methods with no TRAITS entry (daily additions).
# Keeps new methods selectable instead of silently unroutable.
_DEFAULT_TRAITS = {"gravity": "organic", "metric": "grid", "corpus": False,
                   "deterministic": True, "headless_ok": True}


@dataclass
class Selection:
    """One selected method with its audit trail."""
    method_id: str
    level: str
    score: int
    reasons: List[str] = field(default_factory=list)
    implemented: bool = True


def _traits_of(method_id: str) -> Dict:
    """Traits for a method; level-derived defaults for unknown/new methods."""
    return TRAITS.get(method_id, _DEFAULT_TRAITS)


def select(profile: TaskProfile, limit: Optional[int] = None) -> List[Selection]:
    """Route a task profile to an ordered list of implemented methods.

    Pure function. Reads reality (SCALE + generator_registry) on every call,
    so methods added daily are picked up automatically.

    Hard filters (a method is dropped if ANY fails):
      - must have working code (generator_registry ground truth)
      - headless profile -> method must be headless_ok (cost guard)
      - corpus=False profile -> method must not require a corpus
      - determinism=True profile -> method must be deterministic
      - memory_depth set -> method's SCALE level must match
      - metric_binding set -> method's metric tag must match
      - tonal_gravity set -> method's gravity tag must match

    Scoring (after filters): style affinity (+3 HC match), implemented-in-
    SCALE-mirror (+1, breaks ties toward curated entries). Ordered by
    (-score, method_id) for stable, auditable output.
    """
    results: List[Selection] = []
    # Candidate universe = union of SCALE (classified levels) + generator
    # registry (reality). Methods added daily to either source are routable;
    # registry-only methods get a neutral default level until classified.
    candidates = set(SCALE) | set(GENERATOR_REGISTRY)
    for method_id in sorted(candidates):
        level = scale_of(method_id) or _DEFAULT_LEVEL
        reasons: List[str] = []

        # --- hard gate: real code (registry truth, not the mirror) ---
        if not _registry_has_code(method_id):
            continue  # spec-only dead end — advice #3

        traits = _traits_of(method_id)

        # --- hard gates from profile ---
        if profile.headless and not traits["headless_ok"]:
            continue  # cost guard: heavy AI-Driven methods out of cron
        if profile.corpus is False and traits["corpus"]:
            continue  # no source material available
        if profile.corpus is True and not traits["corpus"]:
            # corpus available but method can't use it — soft penalty, not a gate
            pass
        if profile.determinism is True and not traits["deterministic"]:
            continue  # golden-test requirement
        if profile.memory_depth is not None:
            if _LEVEL_TO_DEPTH[level] != profile.memory_depth:
                continue
        if profile.metric_binding is not None and traits["metric"] != profile.metric_binding:
            continue
        if profile.tonal_gravity is not None and traits["gravity"] != profile.tonal_gravity:
            continue

        # --- reasons (audit trail) ---
        reasons.append(f"level:{level}")
        reasons.append(f"gravity:{traits['gravity']}")
        reasons.append(f"metric:{traits['metric']}")
        if profile.corpus:
            reasons.append(f"corpus:{traits['corpus']}")

        # --- scoring ---
        score = 0
        if profile.style and STYLE_HC_MAP.get(profile.style) == method_id:
            score += 3
            reasons.append(f"style-affinity:{profile.style}")
        if impl_status(method_id):  # curated SCALE mirror agrees
            score += 1

        results.append(Selection(method_id=method_id, level=level,
                                 score=score, reasons=reasons,
                                 implemented=True))

    results.sort(key=lambda s: (-s.score, s.method_id))
    if limit is not None:
        results = results[:limit]
    return results


def select_for_cron(limit: Optional[int] = 5) -> List[Selection]:
    """Convenience: the headless, deterministic, cheap set for cron jobs."""
    return select(TaskProfile(headless=True, determinism=True), limit=limit)


def select_chain(profile: TaskProfile, per_layer: int = 2) -> Dict[str, List[Selection]]:
    """Layer-ordered method chain (LAYER_ARCHITECTURE.md composition paths).

    Splits the routing by the profile's `layers_needed` (execution order,
    e.g. ("abstract", "concrete", "absolute")): for each layer, return the
    top `per_layer` implemented methods whose layer tag matches. This is
    what makes the 3-layer composition paths selectable:

        full path    ("abstract", "concrete", "absolute")
        direct path  ("concrete",)                       (legacy default)
        render-only  ("concrete", "absolute")

    Pure function like select(); auditable per layer.
    """
    from workflows.musicom_workflow import SP_METHODS  # lazy: avoid heavy import chain
    out: Dict[str, List[Selection]] = {}
    for layer in profile.layers_needed:
        layer_results = []
        # absolute layer: SP methods aren't in SCALE/registry; pull from SP_METHODS
        if layer == "absolute":
            for mid in sorted(SP_METHODS):
                layer_results.append(Selection(method_id=mid, level="SP",
                                               score=0, reasons=["layer:absolute"],
                                               implemented=True))
            out[layer] = layer_results[:per_layer]
            continue
        for s in select(profile, limit=None):
            if layer_of(s.method_id) == layer:
                s.reasons.append(f"layer:{layer}")
                layer_results.append(s)
        out[layer] = layer_results[:per_layer]
    return out


def selector_table() -> str:
    """Markdown table of trait tags (for docs/)."""
    rows = ["| Method ID | Gravity | Metric | Corpus | Deterministic | Headless |",
            "|---|---|---|---|---|---|"]
    for mid in sorted(set(list(TRAITS) + list(SCALE))):
        t = _traits_of(mid)
        rows.append(f"| {mid} | {t['gravity']} | {t['metric']} | "
                    f"{t['corpus']} | {t['deterministic']} | {t['headless_ok']} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print("=== SELECTOR: style-faithful pop, grid, meso, headless cron ===")
    for s in select(TaskProfile(tonal_gravity="strict", metric_binding="grid",
                                memory_depth="meso", headless=True), limit=5):
        print(f"  {s.method_id} ({s.level}, score {s.score}) — {', '.join(s.reasons)}")
    print()
    print("=== SELECTOR: organic ambient contour, no corpus, local ===")
    for s in select(TaskProfile(tonal_gravity="organic", metric_binding="fluid",
                                memory_depth="local", corpus=False), limit=5):
        print(f"  {s.method_id} ({s.level}, score {s.score}) — {', '.join(s.reasons)}")
    print()
    print("=== SELECTOR: flamenco style (HC affinity) ===")
    for s in select(TaskProfile(style="flamenco"), limit=5):
        print(f"  {s.method_id} ({s.level}, score {s.score}) — {', '.join(s.reasons)}")
    print()
    print("=== CRON-READY set ===")
    for s in select_for_cron(8):
        print(f"  {s.method_id} ({s.level})")
