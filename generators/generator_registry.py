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
    "079": ("generators.tintinnabuli", None, "Tintinnabuli Composition (TINC) — Arvo Pärt M/T-voice"),
    "HC-012": ("generators.chord_degrees", None, "Flamenco Compas & Falseta (human method)"),
    # --- Abstract layer (rules/subset_network.py — LAYER_ARCHITECTURE.md) ---
    "ABS-001": ("rules.subset_network", None, "Tension Curve Planner (abstract: per-section tension targets)"),
    "ABS-002": ("rules.subset_network", None, "Subset Walker (abstract: pattern-network walk -> progression)"),
    "ABS-003": ("rules.subset_network", None, "Z-Variation (abstract: same-ICV re-harmonization)"),
    "ABS-004": ("rules.subset_network", None, "Parsimonious Voice Leading (abstract: P/L/R smooth moves)"),
    "ABS-005": ("rules.subset_network", None, "Complement Contrast (abstract: matched-tension contrast)"),
    # --- Human methods (HC-*, human_methods_db.md) — spec-only until shared code ---
    "HC-018": (None, None, "Clave-Guided Montuno (Cuban son; spec in human_methods_db.md)"),
    "HC-019": (None, None, "Bulgarian Aksak Horo (spec in human_methods_db.md)"),
    "HC-020": (None, None, "Tension-and-Release Drop Arrangement (spec in human_methods_db.md)"),
    "HC-021": (None, None, "Species Counterpoint (spec in human_methods_db.md)"),
    "HC-022": (None, None, "Twelve-Bar Blues AAB Form (spec in human_methods_db.md)"),
    "HC-023": (None, None, "Spectral Listening & Harmonic-Series Orchestration (spec in human_methods_db.md)"),
    "HC-024": (None, None, "Graphic Score & Indeterminate Notation (spec in human_methods_db.md)"),
    "HC-025": (None, None, "Kora Griot Ostinato-Song (spec in human_methods_db.md)"),
    "HC-026": (None, None, "Scottish Pibroch Theme-and-Variation (spec in human_methods_db.md)"),
    "HC-027": (None, None, "Tuvan Overtone Throat Singing (spec in human_methods_db.md)"),
    # --- Human methods weekly promotion 2026-09-13 (reports HC-028..HC-034) ---
    "HC-028": (None, None, "Jazz Chord-Scale Improvisation & Comping (spec in human_methods_db.md)"),
    "HC-029": (None, None, "Shakuhachi Honkyoku Breath-Phrase & Ma (spec in human_methods_db.md)"),
    "HC-030": (None, None, "Argentine Tango Marcato Counterpoint (spec in human_methods_db.md)"),
    "HC-031": (None, None, "Persian Radif Dastgah-Gusheh Ordering (spec in human_methods_db.md)"),
    "HC-032": (None, None, "Guqin Jianzipu Tablature & Dapu Reconstruction (spec in human_methods_db.md)"),
    "HC-033": (None, None, "Inuit Katajjaq Throat-Singing Duet (spec in human_methods_db.md)"),
    "HC-034": (None, None, "Choro Rondo & Baixaria Counterpoint (spec in human_methods_db.md)"),
    # --- Human methods weekly promotion 2026-09-20 (reports HC-035..HC-040) ---
    "HC-035": (None, None, "Shona Mbira Kushaura/Kutsinhira Interlocking (spec in human_methods_db.md)"),
    "HC-036": (None, None, "Norwegian Hardanger Fiddle Slått Craft (spec in human_methods_db.md)"),
    "HC-037": (None, None, "Klezmer Ornament-Led Ensemble Craft (spec in human_methods_db.md)"),
    "HC-038": (None, None, "Sonata Form Process (spec in human_methods_db.md)"),
    "HC-039": (None, None, "Irish Traditional Dance Tune Setting & Ornamentation Craft (spec in human_methods_db.md)"),
    "HC-040": (None, None, "Andalusi Nūbah Suite Architecture & Mīzān Metric Acceleration (spec in human_methods_db.md)"),
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
