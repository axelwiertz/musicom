# -*- coding: utf-8 -*-
"""Human-in-the-loop (HITL) evolution rounds — build step 4.

Plan §3.2(b) (projects/Research/CompositionMethods/PATH_LAYER_PLAN.md):

    round r:
      1. generate K candidates (K <= 4 — cognitive-load cap)
      2. render excerpt of each -> OGG (Telegram-playable)
      3. send all K + one-line metadata to chat
      4. user replies with pick/ranking
      5. selection -> crossover+mutation -> round r+1
      6. stop: winner chosen | 3-5 rounds | plateau

This module does steps 1-2 (generate + render) and steps 4-6 (record pick,
persist to evolution.json, prepare next round's parent). Step 3 (the
actual Telegram send) happens at the Hermes layer — the agent calls
`run_hitl_round()`, gets back rendered candidate OGG paths, sends them via
`MEDIA:`, and the user's reply drives the next `record_pick()` call.

Design rules honored:
- Engine-only: all generation via the musicom engine (no raw mido).
- K <= 4 (Takagi 2001 fatigue cap) — enforced.
- Excerpts <= 30 s — enforced by rendering a trimmed excerpt, not the full piece.
- Every rating persisted to evolution.json (training data for the
  surrogate model, step 6) + provenance sidecar on the winner.
- Deterministic per seed; the human pick is logged, not re-rolled.

The Epsilon-wildcard (plan §3.2b) is NOT auto-injected here — the agent
includes it in the candidate set it sends (see `hitl_candidates`).
"""

import json
import random
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from structures import MusicUnit, MusicEvent
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.evolution import (
    FitnessWeights, STYLE_WEIGHTS, evaluate_fitness, build_anchor_unit,
    _build_with_anchor, hard_gates, rule_judge,
)
from workflows.paths import (
    POP_FORM, PROGRESSIONS, progression_roots,
)

BAR = 1920
MAX_CANDIDATES = 4          # cognitive-load cap (plan §3.2b)
EXCERPT_SECONDS = 30        # excerpt cap (plan §3.2b)


# ============================================================================
# Candidate generation — reuse evolve_anchor machinery, per-candidate
# ============================================================================

@dataclass
class HITLCandidate:
    """One rendered candidate sent to the human judge."""
    variant: int
    density: int
    offset: int
    fitness: Dict
    midi_path: str
    ogg_path: str
    is_wildcard: bool = False   # epsilon-wildcard (exploration outlier)


@dataclass
class HITLRound:
    """One HITL round: rendered candidates + audit metadata."""
    round_num: int
    candidates: List[HITLCandidate]
    seed: int
    style: str
    key: str
    bpm: int
    out_dir: str


def _progression_roots(progression, total_bars, key, harmonic_rhythm=1):
    """Per-bar root MIDI pitches (mode-aware — delegates to rules.harmony).

    Historical bug: this used `MAJOR_DEGREES.index(deg.upper())`, which
    collapsed every uppercase minor-mode degree (VI/III/VII) onto index 0
    and produced static all-tonic harmony for minor progressions. The
    canonical mode-aware lookup lives in rules.harmony.progression_roots.
    """
    return progression_roots(progression, total_bars, key,
                             harmonic_rhythm=harmonic_rhythm)


def _render_excerpt(midi_path: Path, out_dir: Path, base: str,
                    seconds: int = EXCERPT_SECONDS) -> str:
    """Render a MIDI to a <=30s OGG excerpt (Telegram-playable)."""
    ogg_path = out_dir / f"{base}.ogg"
    wav_path = out_dir / f"{base}.wav"
    from utilities.env import fluidsynth_bin
    from sound.render.fluidsynth import discover_soundfont
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("no SoundFont — install FluidR3_GM.sf2")
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(wav_path),
         sf, str(midi_path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"fluidsynth failed: {r.stderr[-300:]}")
    # trim to excerpt length
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-t", str(seconds),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
         str(ogg_path)],
        capture_output=True, text=True)
    if not ogg_path.exists() or ogg_path.stat().st_size < 1000:
        raise RuntimeError("excerpt render failed/empty")
    return str(ogg_path)


def generate_hitl_candidates(style="pop", key="C", bpm=120, progression=None,
                             form=None, seed=None, n_candidates=MAX_CANDIDATES,
                             out_dir=None, weights: Optional[FitnessWeights] = None,
                             parent_density: Optional[int] = None,
                             parent_offset: Optional[int] = None) -> HITLRound:
    """Generate + render K candidates for one HITL round.

    Variant space: Euclidean density x on/off-beat offset. If a parent
    (winner from the previous round) is given, mutate around it
    (density +/- 1, offset flip) — crossover across rounds is step-4's
    simple extension; mutation-only keeps macro-structure intact
    (advice #5: evolve phrases/anchors, not whole songs).

    One candidate is always the epsilon-wildcard (random density/offset)
    for exploration (plan §3.2b: prevents premature convergence).
    """
    import random
    rng = random.Random(seed)
    seed = seed if seed is not None else rng.randint(0, 2**31)
    if n_candidates > MAX_CANDIDATES:
        raise ValueError(f"K capped at {MAX_CANDIDATES} (Takagi 2001 fatigue)")

    form = form or POP_FORM
    section_names = [s[0] for s in form]
    bars_per = [s[1] for s in form]
    progression = progression or PROGRESSIONS.get(style, PROGRESSIONS["pop"])
    total_bars = sum(bars_per)
    roots_per_bar = _progression_roots(progression, total_bars, key)
    section_roots = []
    cursor = 0
    for nbars in bars_per:
        section_roots.append(roots_per_bar[cursor])
        cursor += nbars

    w = weights or STYLE_WEIGHTS.get(style, FitnessWeights())

    out_dir = Path(out_dir or f"/opt/data/projects/Styles/{style.title()}/hitl")
    cand_dir = out_dir / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)

    # build the (density, offset) variant set: mutate around parent + wildcard
    if parent_density is not None and parent_offset is not None:
        base = [(parent_density + d, o) for d, o in
                [(0, parent_offset), (1, parent_offset), (-1, parent_offset),
                 (0, 240 - parent_offset)]]
    else:
        base = [(3, 0), (4, 0), (4, 240), (5, 240)]
    # clamp density to [3, 5]
    variants = [(max(3, min(5, d)), o) for d, o in base][:n_candidates]
    # epsilon-wildcard: last slot is a random outlier (plan §3.2b)
    if len(variants) == n_candidates and n_candidates > 1:
        existing = set(variants[:-1])
        pool = [(d, o) for d in (3, 4, 5) for o in (0, 240) if (d, o) not in existing]
        if pool:
            variants[-1] = rng.choice(pool)

    candidates: List[HITLCandidate] = []
    for vi, (density, offset) in enumerate(variants):
        composer = _build_with_anchor(style, key, bpm, progression, form,
                                      seed + vi * 131, section_roots,
                                      section_names, bars_per, density, offset)
        viols = hard_gates(composer)
        if viols:
            continue  # skip non-viable candidates
        probe = build_anchor_unit(section_roots[0], bars_per[0], density, offset)
        fit = evaluate_fitness(probe, key=key, weights=w)

        # export + render excerpt
        midi_path = cand_dir / f"cand{vi}-d{density}-off{offset}.mid"
        composer.to_midi(str(midi_path))
        base = f"cand{vi}-d{density}-off{offset}"
        ogg_path = _render_excerpt(midi_path, cand_dir, base)
        is_wildcard = (vi == len(variants) - 1 and n_candidates > 1)
        candidates.append(HITLCandidate(
            variant=vi, density=density, offset=offset, fitness=fit,
            midi_path=str(midi_path), ogg_path=ogg_path,
            is_wildcard=is_wildcard,
        ))

    return HITLRound(round_num=0, candidates=candidates, seed=seed,
                     style=style, key=key, bpm=bpm, out_dir=str(out_dir))


def record_pick(round_obj: HITLRound, pick_index: int,
                evolution_path: Optional[str] = None) -> Dict:
    """Record the human judge's pick and persist to evolution.json.

    Writes the round + pick into the evolution audit trail. The winner's
    density/offset become the parent for the next round's mutation.

    Returns the evolution record (winner + round log) and writes
    evolution.json beside the candidates.
    """
    if not (0 <= pick_index < len(round_obj.candidates)):
        raise IndexError(f"pick {pick_index} out of range "
                         f"[0, {len(round_obj.candidates)})")
    winner = round_obj.candidates[pick_index]
    evo_dir = Path(round_obj.out_dir) / "evolution"
    evo_dir.mkdir(parents=True, exist_ok=True)
    evo_path = Path(evolution_path or evo_dir / "evolution.json")

    def _extras(cand) -> Dict:
        """Optional per-candidate metadata set by a caller (e.g. a VariantSpec).

        The generic HITL layer knows density/offset only. Projects that
        evolve a richer search space attach extras to the candidate; they
        must survive into evolution.json, or the next round cannot inherit
        them and would silently reset to the default palette/methods.
        """
        out = {}
        spec = getattr(cand, "spec", None)
        if spec is not None:
            out["spec"] = spec
        role = getattr(cand, "role", None)
        if role is not None:
            out["role"] = role
        per_stem = cand.fitness.get("per_stem") if isinstance(
            cand.fitness, dict) else None
        if per_stem:
            out["per_stem"] = per_stem
        return out

    record = {
        "judge": "human",
        "style": round_obj.style, "key": round_obj.key, "bpm": round_obj.bpm,
        "seed": round_obj.seed,
        "round": round_obj.round_num,
        "n_candidates": len(round_obj.candidates),
        "pick_index": pick_index,
        "winner": {
            "variant": winner.variant,
            "density": winner.density,
            "offset": winner.offset,
            "fitness_total": round(winner.fitness["total"], 4),
            "terms": winner.fitness["terms"],
            "midi": winner.midi_path,
            "ogg": winner.ogg_path,
            "wildcard": winner.is_wildcard,
            **_extras(winner),
        },
        "candidates": [
            {"variant": c.variant, "density": c.density, "offset": c.offset,
             "fitness_total": round(c.fitness["total"], 4),
             "terms": c.fitness["terms"], "wildcard": c.is_wildcard,
             "midi": c.midi_path, "ogg": c.ogg_path,
             **_extras(c)}
            for c in round_obj.candidates
        ],
    }

    # merge with existing evolution.json (multi-round audit trail)
    if evo_path.exists():
        existing = json.loads(evo_path.read_text())
        existing.setdefault("rounds", []).append(record)
        existing["latest"] = record
        merged = existing
    else:
        merged = {"rounds": [record], "latest": record}
    evo_path.write_text(json.dumps(merged, indent=2))

    # provenance sidecar on the winning MIDI
    write_provenance(
        artifact_path=winner.midi_path,
        classification=AI_ASSISTED,
        generator=f"workflows.hitl (human pick {pick_index}, "
                  f"round {round_obj.round_num})",
        sources=[f"style:{round_obj.style}", f"key:{round_obj.key}",
                 f"seed:{round_obj.seed}", "judge:human"],
        parameters={"density": winner.density, "offset": winner.offset,
                    "fitness": winner.fitness["terms"]},
    )
    return {"evolution": merged, "winner": winner, "evolution_path": str(evo_path)}


def next_round_parents(round_obj: HITLRound, pick_index: int):
    """Winner density/offset -> parent for next round's mutation."""
    winner = round_obj.candidates[pick_index]
    return winner.density, winner.offset


# ============================================================================
# Orchestrator: run one full HITL round (generate + render + return)
# ============================================================================

def run_hitl_round(style="pop", key="C", bpm=120, seed=None,
                   n_candidates=MAX_CANDIDATES, out_dir=None,
                   parent_density=None, parent_offset=None,
                   round_num=0) -> HITLRound:
    """Generate K rendered candidates, ready for Telegram delivery.

    The agent sends `round.candidates[i].ogg_path` via MEDIA: and calls
    `record_pick(round, pick_index)` when the user replies.
    """
    r = generate_hitl_candidates(style=style, key=key, bpm=bpm, seed=seed,
                                 n_candidates=n_candidates, out_dir=out_dir,
                                 parent_density=parent_density,
                                 parent_offset=parent_offset)
    r.round_num = round_num
    return r


def hitl_summary(round_obj: HITLRound) -> str:
    """One-line metadata per candidate (the message the human sees)."""
    lines = [f"HITL round {round_obj.round_num} — {round_obj.style} "
             f"{round_obj.key} {round_obj.bpm}bpm (seed {round_obj.seed}):"]
    for i, c in enumerate(round_obj.candidates):
        tag = " [wildcard]" if c.is_wildcard else ""
        lines.append(f"  {i}: density={c.density} offset={c.offset} "
                     f"fitness={c.fitness['total']:.3f}{tag}")
    return "\n".join(lines)


if __name__ == "__main__":
    r = run_hitl_round(style="pop", key="C", bpm=120, seed=42)
    print(hitl_summary(r))
    print()
    for c in r.candidates:
        print(f"  cand{c.variant}: {c.ogg_path}")
