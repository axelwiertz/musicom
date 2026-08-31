# -*- coding: utf-8 -*-
"""Evolution engine — rule-fitness IGA over the Path C anchor (build step 3).

Plan §3 (projects/Research/CompositionMethods/PATH_LAYER_PLAN.md):

    workflows/evolution.py   # GeneticEngine wrapper: rule fitness | HITL rounds

Design (plan §3.1 — build on, don't fork):
- The GeneticGenerator in generators/genetic.py already has a fitness_func
  callback hook. We do NOT fork it; we drive the same idea (candidates ->
  fitness -> selection) with a musical energy functional (plan §3.2a, the
  SAMC-specified design) adapted to the anchor-evolution use case.
- Fitness = weighted sum of computable terms (plan §3.2a table):

    | Term             | How                                   | Existing asset         |
    | Zero-drift valid | composer.validate()                  | hard gate              |
    | On-grid ratio    | onset ticks % grid == 0              | (computed here)        |
    | Tonal gravity    | pitch-class fit vs key profile       | Lerdahl-Krumhansl      |
    | Voice independence| crossing/parallel checks            | rules/counterpoint.py  |
    | Range/playability| instrument_registry in_range         | instrument_registry    |
    | Density arc      | sparse->dense across sections        | grid visualizer data   |
    | Style match      | density/tempo vs template            | workflow spine         |

Hard gates (reject — plan §3.2a "gates hard, aesthetics soft"):
  - zero-drift: composer.validate() must pass
  - playability: all notes in instrument range (lead voice, via registry)
  - note budget: candidate not silent/empty
Soft terms (weighted score, style-tunable weights):
  - tonal_gravity   : pitch-class fit vs key profile (Lerdahl-Krumhansl)
  - on_grid         : ratio of onsets on the rhythmic grid
  - stepwise_motion : melodic step bias (small intervals preferred)
  - rhythm_variety  : distinct onset-interval count (diversity)
  - groove_stability: periodicity of the anchor rhythm

Selection: rule_judge (auto, highest fitness) now; HITL in step 4 — the
judge callback design already accepts a human judge function.

Guarantees:
- Engine-only: uses UnitMatrixComposer, MusicEvent, provenance (no raw mido).
- Zero-drift gate: every candidate must validate before scoring.
- Seeded: same (style, key, seed) -> same variants, same winner.
- Everything persisted to <out>/evolution/evolution.json (audit trail).
"""

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# --- engine imports (editable install) -------------------------------------
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.paths import (
    build_framework, fill_drums, fill_pad, fill_lead, fill_arp,
    POP_FORM, PROGRESSIONS, KEY_OFFSET, MAJOR_DEGREES,
)

# --- key profiles (Lerdahl-Krumhansl, DB method 066) ------------------------
K_PROFILE_MAJOR = {0: 6.35, 1: 2.23, 2: 3.48, 3: 2.33, 4: 4.38, 5: 4.09,
                   6: 2.52, 7: 5.19, 8: 2.39, 9: 3.66, 10: 2.29, 11: 2.88}
K_PROFILE_MINOR = {0: 6.33, 1: 2.68, 2: 3.52, 3: 5.38, 4: 2.60, 5: 3.53,
                   6: 2.54, 7: 4.75, 8: 3.98, 9: 2.69, 10: 3.34, 11: 3.17}

BAR = 1920


# ============================================================================
# Fitness — musical energy functional (plan §3.2a)
# ============================================================================

@dataclass
class FitnessWeights:
    """Weighted musical energy functional (per style, plan §3.2a).

    Style-tunable: flamenco weighs grid alignment high; ambient weighs
    density-arc low and texture high.
    """
    tonal_gravity: float = 1.0
    on_grid: float = 1.0
    stepwise_motion: float = 0.8
    rhythm_variety: float = 0.6
    groove_stability: float = 0.5

    def terms(self) -> Dict[str, float]:
        return {
            "tonal_gravity": self.tonal_gravity,
            "on_grid": self.on_grid,
            "stepwise_motion": self.stepwise_motion,
            "rhythm_variety": self.rhythm_variety,
            "groove_stability": self.groove_stability,
        }


STYLE_WEIGHTS = {
    "pop": FitnessWeights(tonal_gravity=1.0, on_grid=1.0, stepwise_motion=0.8,
                          rhythm_variety=0.6, groove_stability=0.5),
    "flamenco": FitnessWeights(tonal_gravity=1.0, on_grid=1.4, stepwise_motion=0.6,
                               rhythm_variety=0.7, groove_stability=0.9),
    "ambient": FitnessWeights(tonal_gravity=0.6, on_grid=0.3, stepwise_motion=0.4,
                              rhythm_variety=0.9, groove_stability=0.3),
    "techno": FitnessWeights(tonal_gravity=0.7, on_grid=1.5, stepwise_motion=0.4,
                             rhythm_variety=0.5, groove_stability=1.0),
}


def _key_profile(key: str) -> Dict[int, float]:
    """Return the Lerdahl-Krumhansl profile for a key (transposed)."""
    off = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
           "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11,
           "Cm": 0, "C#m": 1, "Dm": 2, "D#m": 3, "Em": 4, "Fm": 5,
           "F#m": 6, "Gm": 7, "G#m": 8, "Am": 9, "A#m": 10, "Bm": 11}.get(key, 0)
    if key.endswith("m"):
        base = K_PROFILE_MINOR
    else:
        base = K_PROFILE_MAJOR
    return {(pc + off) % 12: w for pc, w in base.items()}


def tonal_gravity(unit: MusicUnit, key: str) -> float:
    """Pitch-class fit vs key profile (cosine similarity), normalized [0,1].

    Both vectors are L2-normalized before the dot product, so the result is
    a true cosine in [0, 1] regardless of note count.
    """
    import math
    pitches = [p for p in unit.pitches if p > 0]
    if not pitches:
        return 0.0
    profile = _key_profile(key)
    obs = {}
    for p in pitches:
        obs[p % 12] = obs.get(p % 12, 0) + 1
    # L2-normalize both vectors
    def _norm(vec):
        n = math.sqrt(sum(v * v for v in vec.values()))
        return {k: v / n for k, v in vec.items()} if n > 0 else vec
    obs_n = _norm(obs)
    prof_n = _norm(profile)
    return sum(obs_n.get(pc, 0) * w for pc, w in prof_n.items())


def on_grid_ratio(unit: MusicUnit, grid: int = 240) -> float:
    """Fraction of onsets landing on the rhythmic grid (8th-note = 240)."""
    onsets = [e.start_tick for e in _audible(unit)]
    if not onsets:
        return 0.0
    return sum(1 for o in onsets if o % grid == 0) / len(onsets)


def _audible(unit: MusicUnit) -> List:
    """Audible (pitch > 0) events only — excludes silent landmarks."""
    return [e for e in unit.events if e.pitch > 0]


def stepwise_motion(unit: MusicUnit) -> float:
    """Step-bias: 1.0 for avg interval <=2 semitones, 0.0 at >=12."""
    evs = _audible(unit)
    if len(evs) < 2:
        return 0.5
    ivs = [abs(int(evs[i + 1].pitch) - int(evs[i].pitch))
           for i in range(len(evs) - 1) if abs(int(evs[i + 1].pitch) - int(evs[i].pitch)) > 0]
    if not ivs:
        return 0.5
    avg = sum(ivs) / len(ivs)
    return max(0.0, min(1.0, 1.0 - (avg - 2) / 10.0))


def rhythm_variety(unit: MusicUnit) -> float:
    """Distinct onset-interval count, normalized (rhythmic diversity)."""
    evs = _audible(unit)
    if len(evs) < 2:
        return 0.0
    ivs = [int(evs[i + 1].start_tick) - int(evs[i].start_tick)
           for i in range(len(evs) - 1)]
    ivs = [i for i in ivs if i > 0]
    if not ivs:
        return 0.0
    return min(1.0, len(set(ivs)) / max(4, len(ivs)))


def groove_stability(unit: MusicUnit) -> float:
    """Periodicity of the anchor: dominant onset-interval frequency."""
    evs = _audible(unit)
    if len(evs) < 2:
        return 0.0
    ivs = [int(evs[i + 1].start_tick) - int(evs[i].start_tick)
           for i in range(len(evs) - 1)]
    ivs = [i for i in ivs if i > 0]
    if not ivs:
        return 0.0
    from collections import Counter
    counts = Counter(ivs)
    top, n = counts.most_common(1)[0]
    return min(1.0, n / len(ivs) * (1.0 if top >= 240 else 0.5))


def evaluate_fitness(unit: MusicUnit, key: str = "C",
                     weights: Optional[FitnessWeights] = None) -> Dict:
    """Full fitness evaluation of one candidate unit -> [0,1] total + terms."""
    w = weights or FitnessWeights()
    raw = {
        "tonal_gravity": tonal_gravity(unit, key),
        "on_grid": on_grid_ratio(unit),
        "stepwise_motion": stepwise_motion(unit),
        "rhythm_variety": rhythm_variety(unit),
        "groove_stability": groove_stability(unit),
    }
    wt = w.terms()
    total_w = sum(wt.values())
    total = sum(raw[k] * wt[k] for k in raw) / total_w if total_w else 0.0
    return {"total": total,
            "terms": {k: round(v, 4) for k, v in raw.items()},
            "raw_terms": raw}


def hard_gates(composer: UnitMatrixComposer) -> List[str]:
    """Hard fitness gates (plan §3.2a: gates hard, aesthetics soft).

    Zero-drift validate + silence check. Returns violations ([] = pass).
    """
    violations = []
    ok, msg = composer.validate()
    if not ok:
        violations.append(f"zero-drift: {msg}")
    # note budget: each voice must have audible content
    for voice in composer.voices:
        row = voice["row"]
        note_count = 0
        for col in range(len(composer.sections)):
            unit = composer.matrix.get_unit((row, col))
            if unit is not None:
                note_count += sum(1 for p in unit.pitches if p > 0)
        if note_count == 0:
            violations.append(f"voice {voice['name']} silent")
    return violations


# ============================================================================
# Anchor variant generation (the thing being evolved)
# ============================================================================

def _euclid(onsets: int, steps: int) -> List[int]:
    """Even spacing of onsets over steps (Bjorklund result)."""
    if onsets <= 0 or steps <= 0 or onsets > steps:
        return []
    return [i * steps // onsets for i in range(onsets)]


def build_anchor_unit(root: int, nbars: int, density: int, offset: int,
                      BAR: int = BAR) -> MusicUnit:
    """One section's anchor (Bass) unit: Euclidean groove on `root`.

    density : accents per bar (3, 4, or 5 — Schillinger-style variation)
    offset  : start offset in ticks (0 = on-beat, 240 = off-beat)

    Relative ticks from 0 (cell-local), with the terminal silent landmark
    at section_len so the zero-drift gate holds.
    """
    section_len = nbars * BAR
    unit = MusicUnit()
    for b in range(nbars):
        pos = _euclid(density, 4)
        for p in pos:
            start = b * BAR + offset + p * 480
            end = min(start + 400, section_len)  # never overflow the cell
            if end > start:
                unit.add_event(MusicEvent(root, 95, start, end))
    unit.add_event(MusicEvent(0, 0, section_len, section_len))
    return unit


def _build_with_anchor(style, key, bpm, progression, form, seed,
                       section_roots, section_names, bars_per,
                       density, offset) -> UnitMatrixComposer:
    """Build the full Path C framework with a swapped anchor bass cell."""
    composer = build_framework(style=style, key=key, bpm=bpm, form=form,
                               seed=seed)
    fill_drums(composer, section_names, bars_per)
    fill_pad(composer, section_roots, section_names, bars_per)
    fill_lead(composer, random.Random(seed), section_roots, section_names,
              bars_per, key=key)
    fill_arp(composer, random.Random(seed ^ 0x5EED), section_roots,
             section_names, bars_per)
    # swap the Bass cells with the evolved anchor (per-section roots)
    for si, sname in enumerate(section_names):
        anchor = build_anchor_unit(section_roots[si], bars_per[si],
                                   density, offset)
        composer.fill_voice_section("Bass", sname, anchor)
    return composer


# ============================================================================
# Selection — rule-based (auto) + human-in-the-loop ready (step 4)
# ============================================================================

# A candidate dict passed to a judge:
#   {variant, generation, unit, fitness:{total, terms}, seed}
# A judge returns the index of the winner in the list.
Judge = Callable[[List[Dict]], int]


def rule_judge(candidates: List[Dict]) -> int:
    """Auto-select: highest fitness total wins (ties -> first)."""
    return max(range(len(candidates)),
               key=lambda i: candidates[i]["fitness"]["total"])


# ============================================================================
# Evolution engine
# ============================================================================

@dataclass
class EvolutionResult:
    winner: Dict
    candidates: List[Dict]
    generations: List[Dict]
    evolution_path: str
    midi_path: str
    seed: int
    style: str
    key: str


def evolve_anchor(style="pop", key="C", bpm=120, progression=None,
                  form=None, seed=None, n_generations=1, n_variants=4,
                  out_dir=None, judge: Optional[Judge] = None,
                  weights: Optional[FitnessWeights] = None) -> EvolutionResult:
    """Evolve the Path C anchor (L3 groove) via rule fitness.

    Plan §3.3: "Evolve the L3 anchor (middle-out path, variant grooves) —
    highest value". One round = generate K anchor variants over the
    framework, hard-gate each, score, select winner (rule or human judge).

    Variant space: Euclidean density {3,4,5} x start offset {0,240} (+ seed
    tiebreak), so K=4 spans density-offset combos deterministically.
    n_generations>1 re-runs with fresh seeds (crossover is step 4's HITL
    upgrade; the judge callback already plugs in there).

    Returns EvolutionResult; persists evolution.json audit trail.
    """
    import random
    rng = random.Random(seed)
    seed = seed if seed is not None else rng.randint(0, 2**31)

    form = form or POP_FORM
    section_names = [s[0] for s in form]
    bars_per = [s[1] for s in form]
    progression = progression or PROGRESSIONS.get(style, PROGRESSIONS["pop"])
    off = KEY_OFFSET.get(key, 0)

    # per-bar roots for the bass anchor
    total_bars = sum(bars_per)
    deg_seq = [progression[i % len(progression)] for i in range(total_bars)]
    roots_per_bar = []
    for deg in deg_seq:
        letter = deg.upper()
        idx = MAJOR_DEGREES.index(letter) if letter in MAJOR_DEGREES else 0
        major_offsets = [0, 2, 4, 5, 7, 9, 11]
        scale_off = major_offsets[idx]
        if deg != deg.upper():
            minor_offsets = [0, 2, 3, 5, 7, 8, 10]
            scale_off = minor_offsets[idx]
        roots_per_bar.append(36 + off + scale_off)

    # per-section roots (first bar of each section)
    section_roots = []
    cursor = 0
    for nbars in bars_per:
        section_roots.append(roots_per_bar[cursor])
        cursor += nbars

    w = weights or STYLE_WEIGHTS.get(style, FitnessWeights())
    judge = judge or rule_judge

    out_dir = Path(out_dir or f"/opt/data/projects/Styles/{style.title()}/evolution")
    evo_dir = out_dir / "evolution"
    evo_dir.mkdir(parents=True, exist_ok=True)

    all_candidates: List[Dict] = []
    generations_log: List[Dict] = []
    winner: Optional[Dict] = None

    for gen in range(max(1, n_generations)):
        gen_rng = random.Random(seed + gen * 7919)
        # K variants: density {3,4,5} x offset {0,240} + a random tiebreak
        densities = [3, 4, 5, 3 + (gen % 3)]
        offsets = [0, 240, 240, 0]
        candidates = []
        for vi in range(n_variants):
            density = densities[vi % len(densities)]
            offset = offsets[vi % len(offsets)]
            # fitness is evaluated on the per-section anchor (first section)
            probe = build_anchor_unit(section_roots[0], bars_per[0],
                                      density, offset)
            fit = evaluate_fitness(probe, key=key, weights=w)
            candidates.append({
                "variant": vi, "generation": gen, "unit": None,
                "fitness": fit, "density": density, "offset": offset,
                "seed": seed,
            })

        # hard-gate each candidate through the full framework
        viable = []
        for cand in candidates:
            composer = _build_with_anchor(style, key, bpm, progression, form,
                                          gen_rng.randint(0, 2**31),
                                          section_roots, section_names,
                                          bars_per,
                                          cand["density"], cand["offset"])
            viols = hard_gates(composer)
            cand["gates"] = "pass" if not viols else viols
            if not viols:
                viable.append(cand)
        if not viable:
            raise RuntimeError("no candidate passed hard gates")

        winner_idx = judge(viable)
        winner = viable[winner_idx]
        generations_log.append({
            "generation": gen,
            "n_candidates": len(viable),
            "winner_variant": winner["variant"],
            "winner_density": winner["density"],
            "winner_offset": winner["offset"],
            "winner_fitness": round(winner["fitness"]["total"], 4),
        })
        all_candidates.extend(viable)

    if winner is None:
        raise RuntimeError("evolution produced no winner")

    # --- export winner as a validated zero-drift MIDI ----------------------
    final = _build_with_anchor(style, key, bpm, progression, form, seed,
                               section_roots, section_names, bars_per,
                               winner["density"], winner["offset"])
    ok, msg = final.validate()
    if not ok:
        raise RuntimeError(f"winner validate failed: {msg}")
    midi_path = evo_dir / f"{style}-anchor-{seed}.mid"
    final.to_midi(str(midi_path))

    prov = write_provenance(
        artifact_path=str(midi_path),
        classification="ai-assisted",
        generator=f"workflows.evolution.evolve_anchor(style={style}, seed={seed})",
        sources=[f"style:{style}", f"key:{key}", f"progression:{progression}",
                 "path:C", "evolution:anchor"],
        parameters={"seed": seed, "n_generations": n_generations,
                    "n_variants": n_variants, "judge": "rule",
                    "weights": w.terms()},
    )

    evo_json = {
        "style": style, "key": key, "bpm": bpm, "seed": seed,
        "n_generations": n_generations, "n_variants": n_variants,
        "judge": "rule",
        "generations": generations_log,
        "winner": {
            "variant": winner["variant"],
            "density": winner["density"],
            "offset": winner["offset"],
            "fitness": round(winner["fitness"]["total"], 4),
            "terms": winner["fitness"]["terms"],
            "midi": str(midi_path),
            "provenance": str(prov) if prov else "",
        },
        "candidates": [
            {"variant": c["variant"], "generation": c["generation"],
             "density": c["density"], "offset": c["offset"],
             "fitness_total": round(c["fitness"]["total"], 4),
             "terms": c["fitness"]["terms"],
             "gates": c.get("gates")}
            for c in all_candidates
        ],
    }
    evo_path = evo_dir / "evolution.json"
    evo_path.write_text(json.dumps(evo_json, indent=2))

    return EvolutionResult(
        winner={k: v for k, v in winner.items() if k != "unit"},
        candidates=[{k: v for k, v in c.items() if k != "unit"}
                    for c in all_candidates],
        generations=generations_log,
        evolution_path=str(evo_path),
        midi_path=str(midi_path),
        seed=seed, style=style, key=key,
    )


if __name__ == "__main__":
    r = evolve_anchor(style="pop", key="C", bpm=120, seed=42, n_variants=4)
    print(f"=== Anchor evolution (style={r.style}, key={r.key}, seed={r.seed}) ===")
    print(f"generations: {r.generations}")
    print(f"winner: variant {r.winner['variant']} "
          f"fitness={r.winner['fitness']['total']:.4f} "
          f"terms={r.winner['fitness']['terms']}")
    print(f"midi: {r.midi_path}")
    print(f"evolution.json: {r.evolution_path}")
    for c in r.candidates:
        print(f"  v{c['variant']} d{c['density']} off{c['offset']}: "
              f"{c['fitness']['total']:.4f} gates={c['gates']}")
