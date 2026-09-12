# -*- coding: utf-8 -*-
"""Phase 3: HITL evolution round over the pop-ballad anchor.

Plan §3.2b (projects/Research/CompositionMethods/PATH_LAYER_PLAN.md):

    round r:
      1. generate K candidates (K <= 4 — cognitive-load cap)
      2. render excerpt of each -> OGG (Telegram-playable)
      3. send all K + one-line metadata to chat
      4. user replies with pick/ranking
      5. selection -> crossover+mutation -> round r+1
      6. stop: winner chosen | 3-5 rounds | plateau

This script drives the engine's HITL round machinery
(`workflows.hitl.run_hitl_round` / `record_pick`) but keeps the ballad's
OWN framework: per-section harmonic regions, per-part lead methods and the
ballad voice stack. The generic `run_hitl_round` builds a plain I-V-vi-IV
pop anchor, which would discard everything phase 1 established.

Search space: the L3 anchor (bass) groove — Euclidean density x on/off-beat
offset. Macro-structure (form, harmony, per-part methods) stays fixed, per
plan advice #5: evolve phrases/anchors, not whole songs.

Usage:
    python phase3_hitl.py            # round 0 (fresh candidates)
    python phase3_hitl.py --round 1 --parent-density 4 --parent-offset 240
    python phase3_hitl.py --pick 2   # record the human pick -> evolution.json
"""
import argparse
import json
import random
import shutil
import sys
from pathlib import Path

PROJECT = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl")
SCRIPTS = PROJECT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from phase1_compose import build_ballad, FORM, KEY, BPM  # noqa: E402
from workflows.hitl import record_pick, HITLCandidate, HITLRound  # noqa: E402
from workflows.evolution import (  # noqa: E402
    evaluate_fitness, STYLE_WEIGHTS, hard_gates,
)
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402
from utilities.env import fluidsynth_bin  # noqa: E402
from sound.render.fluidsynth import discover_soundfont  # noqa: E402

MAX_CANDIDATES = 4          # Takagi 2001 cognitive-load cap (plan §3.2b)
EXCERPT_SECONDS = 30        # excerpt cap (plan §3.2b)
HITL_DIR = PROJECT / "HITL"


def _render_excerpt(midi_path: Path, out_dir: Path, base: str,
                    seconds: int = EXCERPT_SECONDS) -> str:
    """Render a MIDI to a <=30 s OGG excerpt (Telegram-playable)."""
    import subprocess
    ogg_path = out_dir / f"{base}.ogg"
    wav_path = out_dir / f"{base}.wav"
    sf = discover_soundfont()
    if not sf:
        raise FileNotFoundError("no SoundFont — install FluidR3_GM.sf2")
    r = subprocess.run(
        [fluidsynth_bin(), "-ni", "-g", "1.2", "-F", str(wav_path),
         sf, str(midi_path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"fluidsynth failed: {r.stderr[-300:]}")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
         "-t", str(seconds),
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
         str(ogg_path)],
        capture_output=True, text=True)
    if not ogg_path.exists() or ogg_path.stat().st_size < 1000:
        raise RuntimeError("excerpt render failed/empty")
    return str(ogg_path)


def _variant_set(parent_density=None, parent_offset=None, seed=None,
                 n_candidates=MAX_CANDIDATES):
    """(density, offset) variants: mutate around the parent + fill from pool.

    Without a parent: probe fixed densities 3/4/5 plus an off-beat variant.
    With a parent: stay / +1 / -1 / flip-phase. Density is clamped to
    [3, 5], so a parent sitting at either boundary would otherwise emit a
    DUPLICATE variant (e.g. winner d3 -> {3, 4, 2->3} = two d3 on-beats).
    Remaining slots are filled from the unexplored pool, which doubles as
    the epsilon-wildcard (exploration outlier, plan §3.2b).
    """
    rng = random.Random(seed)
    if parent_density is None or parent_offset is None:
        return [(3, 0), (4, 0), (5, 0), (4, 240)][:n_candidates]

    proposed = [
        (parent_density, parent_offset),                 # stay
        (parent_density + 1, parent_offset),             # denser
        (parent_density - 1, parent_offset),             # sparser
        (parent_density, 240 - parent_offset),           # flip phase
    ]
    variants = []
    for d, o in proposed:
        d = max(3, min(5, d))
        if (d, o) not in variants and len(variants) < n_candidates:
            variants.append((d, o))

    pool = [(d, o) for d in (3, 4, 5) for o in (0, 240)
            if (d, o) not in variants]
    rng.shuffle(pool)
    while len(variants) < n_candidates and pool:
        variants.append(pool.pop())
    return variants


def run_ballad_round(round_num=0, seed=7, parent_density=None,
                     parent_offset=None, n_candidates=MAX_CANDIDATES,
                     out_dir=None):
    """Generate + render K ballad candidates (same framework, evolved anchor).

    Returns a HITLRound (engine dataclass) so `record_pick` works unchanged.
    """
    if n_candidates > MAX_CANDIDATES:
        raise ValueError(f"K capped at {MAX_CANDIDATES} (Takagi 2001 fatigue)")

    out_dir = Path(out_dir or HITL_DIR / f"round{round_num}")
    cand_dir = out_dir / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)

    weights = STYLE_WEIGHTS.get("pop")
    variants = _variant_set(parent_density, parent_offset, seed, n_candidates)

    candidates = []
    for vi, (density, offset) in enumerate(variants):
        composer = build_ballad(seed=seed + vi * 131, density=density,
                                offset=offset)
        viols = hard_gates(composer)
        if viols:
            print(f"  cand{vi} (d{density} off{offset}) rejected: {viols}")
            continue
        ok, msg = composer.validate()
        if not ok:
            raise RuntimeError(f"cand{vi} validate failed: {msg}")

        # fitness on the composed Bass row (the evolved layer), so the score
        # reflects the actual anchor, not a detached probe unit.
        bass_row = next(v["row"] for v in composer.voices
                        if v["name"] == "Bass")
        bass_unit = composer.matrix.get_unit((bass_row, 0))
        fit = evaluate_fitness(bass_unit, key="Dm", weights=weights)

        base = f"cand{vi}-d{density}-off{offset}"
        midi_path = cand_dir / f"{base}.mid"
        composer.to_midi(str(midi_path))
        assert midi_path.stat().st_size > 40, "empty MIDI"
        ogg_path = _render_excerpt(midi_path, cand_dir, base)

        candidates.append(HITLCandidate(
            variant=vi, density=density, offset=offset, fitness=fit,
            midi_path=str(midi_path), ogg_path=ogg_path,
            is_wildcard=False,
        ))

    if not candidates:
        raise RuntimeError("no candidate passed the hard gates")

    # The exploration outlier: with a parent, it's the slot that broke the
    # mutation neighbourhood; without one, any non-default groove.
    defaults = {(3, 0), (4, 0), (5, 0)}
    neighbourhood = {(parent_density, parent_offset),
                     (parent_density + 1, parent_offset),
                     (parent_density - 1, parent_offset),
                     (parent_density, 240 - parent_offset)} if \
        parent_density is not None and parent_offset is not None else None
    for c in candidates:
        if neighbourhood is not None:
            c.is_wildcard = (c.density, c.offset) not in neighbourhood
        else:
            c.is_wildcard = (c.density, c.offset) not in defaults
    if not any(c.is_wildcard for c in candidates) and len(candidates) > 1:
        candidates[-1].is_wildcard = True

    round_obj = HITLRound(round_num=round_num, candidates=candidates,
                          seed=seed, style="pop-ballad", key=KEY, bpm=BPM,
                          out_dir=str(out_dir))
    (out_dir / "round.json").write_text(json.dumps({
        "round": round_num, "seed": seed, "key": KEY, "bpm": BPM,
        "parent_density": parent_density, "parent_offset": parent_offset,
        "candidates": [
            {"variant": c.variant, "density": c.density, "offset": c.offset,
             "fitness_total": round(c.fitness["total"], 4),
             "terms": c.fitness["terms"], "wildcard": c.is_wildcard,
             "midi": c.midi_path, "ogg": c.ogg_path,
             "form": str(FORM), "progression": "i-VI-III-VII (Dm-Bb-F-C)"}
            for c in candidates],
    }, indent=2))
    return round_obj


def load_round(out_dir):
    """Rebuild a HITLRound from a rendered round.json (no re-render).

    Lets a pick be recorded without regenerating + re-rendering all four
    excerpts — round.json already carries density/offset/fitness/paths.
    """
    out_dir = Path(out_dir)
    data = json.loads((out_dir / "round.json").read_text())
    candidates = [
        HITLCandidate(
            variant=c["variant"], density=c["density"], offset=c["offset"],
            fitness={"total": c["fitness_total"], "terms": c["terms"]},
            midi_path=c["midi"], ogg_path=c["ogg"],
            is_wildcard=c["wildcard"],
        )
        for c in data["candidates"]
    ]
    return HITLRound(round_num=data["round"], candidates=candidates,
                     seed=data["seed"], style="pop-ballad",
                     key=data["key"], bpm=data["bpm"], out_dir=str(out_dir))


def hitl_summary(round_obj):
    """One-line metadata per candidate (the message the human sees)."""
    lines = [f"HITL round {round_obj.round_num} — {round_obj.style} "
             f"{round_obj.key} {round_obj.bpm}bpm "
             f"(seed {round_obj.seed}, form "
             f"{'/'.join(n for n, _ in FORM)}):"]
    for i, c in enumerate(round_obj.candidates):
        tag = " [wildcard]" if c.is_wildcard else ""
        lines.append(f"  {i}: density={c.density} offset={c.offset} "
                     f"fitness={c.fitness['total']:.3f}{tag}")
    return "\n".join(lines)


def record_ballad_pick(round_obj, pick_index):
    """Record the human pick + write provenance on the winning MIDI."""
    res = record_pick(round_obj, pick_index,
                      evolution_path=str(Path(round_obj.out_dir)
                                         / "evolution.json"))
    winner = res["winner"]
    write_provenance(
        artifact_path=winner.midi_path,
        classification=AI_ASSISTED,
        generator=f"pop-ballad-hitl phase3 HITL (round {round_obj.round_num}, "
                  f"human pick {pick_index})",
        sources=["style:pop-ballad", f"key:{round_obj.key}",
                 f"bpm:{round_obj.bpm}", "progression:i-VI-III-VII",
                 "path:C middle-out", "judge:human",
                 "methods:001,012,018,015,004,011,023,013"],
        parameters={"density": winner.density, "offset": winner.offset,
                    "fitness": winner.fitness["terms"],
                    "search_space": "L3 anchor Euclidean density x offset"},
    )
    return res


def main():
    ap = argparse.ArgumentParser(description="Pop-ballad HITL round")
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--parent-density", type=int, default=None)
    ap.add_argument("--parent-offset", type=int, default=None)
    ap.add_argument("--n-candidates", type=int, default=MAX_CANDIDATES)
    ap.add_argument("--pick", type=int, default=None,
                    help="record this candidate index as the human pick")
    args = ap.parse_args()

    r = run_ballad_round(round_num=args.round, seed=args.seed,
                         parent_density=args.parent_density,
                         parent_offset=args.parent_offset,
                         n_candidates=args.n_candidates)
    print(hitl_summary(r))
    print()
    for c in r.candidates:
        print(f"  cand{c.variant}: {c.ogg_path}")
        print(f"         midi: {c.midi_path}")

    if args.pick is not None:
        res = record_ballad_pick(r, args.pick)
        w = res["winner"]
        print(f"\nPICK RECORDED: cand{w.variant} "
              f"(density={w.density} offset={w.offset})")
        print(f"  evolution.json: {res['evolution_path']}")
        print(f"  winner MIDI:    {w.midi_path}")


if __name__ == "__main__":
    main()
