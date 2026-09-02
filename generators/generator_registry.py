# -*- coding: utf-8 -*-
"""Generator registry — maps methods_db.md method IDs to working code.

This is the bridge between the knowledge DB (methods_db.md) and the
implementation (generators/). It exists so:
  1. A composer agent can resolve a method ID ("002") to a callable.
  2. The methods DB table can be auto-generated from reality (no drift).

Each entry: method ID -> (module_path, class_or_callable, short_desc)

The tables in docs/methods.md should be generated from this registry via
`registry_table()` — never hand-maintained.
"""

import importlib

# method ID -> (module path, class/function name, one-line description)
# Entries marked NOT-IMPLEMENTED have spec in methods_db.md but no shared
# code yet — resolve to a clear error rather than a misleading fake.
GENERATOR_REGISTRY = {
    "001": ("generators.base", "FunctionGenerator", "Skeleton-First Refinement (form-first drafting)"),
    "002": ("generators.chain", "MarkovChainGenerator", "Markov Probabilistic Transitions"),
    "003": ("generators.genetic", "GeneticGenerator", "Genetic Genome Selection"),
    "010": ("generators.chain", "MarkovChainGenerator", "Hierarchical Diffusion (multi-level, markov base)"),
    "012": ("generators.rhythm", "euclidian", "Euclidean Groove Locking (Bjorklund)"),
    "018": ("generators.schillinger", "SchillingerGenerator", "Schillinger System of Musical Design"),
    "023": ("generators.tendency_masking", "TendencyMaskingGenerator", "Tendency Masking Stochastic Bounds"),
    "026": (None, None, "DPSM — spec only, NO shared code yet (was one-off project script)"),
    "040": ("generators.pitchpattern", None, "Perlin Noise Composition (see pitchpattern.py)"),
    "048": (None, None, "RBMPD — spec only, NO shared code yet (was one-off project script)"),
    "HC-012": ("generators.chord_degrees", None, "Flamenco Compas & Falseta (human method)"),
    # --- Abstract layer (rules/subset_network.py — LAYER_ARCHITECTURE.md) ---
    "ABS-001": ("rules.subset_network", None, "Tension Curve Planner (abstract: per-section tension targets)"),
    "ABS-002": ("rules.subset_network", None, "Subset Walker (abstract: pattern-network walk -> progression)"),
    "ABS-003": ("rules.subset_network", None, "Z-Variation (abstract: same-ICV re-harmonization)"),
    "ABS-004": ("rules.subset_network", None, "Parsimonious Voice Leading (abstract: P/L/R smooth moves)"),
    "ABS-005": ("rules.subset_network", None, "Complement Contrast (abstract: matched-tension contrast)"),
}


def _resolve(entry):
    mod_path, class_name, _ = entry
    if mod_path is None:
        raise NotImplementedError(
            "This method has spec in methods_db.md but no shared code yet. "
            "Promote the one-off project implementation to generators/ first.")
    mod = importlib.import_module(mod_path)
    if class_name:
        return getattr(mod, class_name)
    return mod


def get_generator(method_id):
    """Resolve a method ID to its implementation (class or module)."""
    if method_id not in GENERATOR_REGISTRY:
        raise KeyError(
            f"Method {method_id!r} not in registry. "
            f"Available: {sorted(GENERATOR_REGISTRY)}")
    return _resolve(GENERATOR_REGISTRY[method_id])


def registry_table():
    """Markdown table of method ID -> implementation (for docs/)."""
    rows = ["| Method ID | Implementation | Description |", "|---|---|---|"]
    for mid in sorted(GENERATOR_REGISTRY):
        mod_path, class_name, desc = GENERATOR_REGISTRY[mid]
        if mod_path is None:
            impl = "⚠️ NO CODE (spec only)"
        else:
            impl = f"`{mod_path}`"
            if class_name:
                impl += f".{class_name}"
        rows.append(f"| {mid} | {impl} | {desc} |")
    return "\n".join(rows)


if __name__ == "__main__":
    print(registry_table())
