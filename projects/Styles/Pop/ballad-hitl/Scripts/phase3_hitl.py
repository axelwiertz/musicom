# -*- coding: utf-8 -*-
"""Phase 3: HITL evolution rounds over the pop-ballad anchor.

Plan §3.2b (projects/Research/CompositionMethods/PATH_LAYER_PLAN.md):

    round r:
      1. generate K candidates (K <= 4 — cognitive-load cap)
      2. render excerpt of each -> OGG (Telegram-playable)
      3. send all K + one-line metadata to chat
      4. user replies with pick/ranking
      5. selection -> crossover+mutation -> round r+1
      6. stop: winner chosen | 3-5 rounds | plateau

Drives the engine's HITL machinery (`workflows.hitl.record_pick`) over the
ballad's OWN framework, and varies MULTIPLE STEMS per round:

  - instrumentation palette rotates each round (classic -> noir -> chamber
    -> folk), so a round never sounds like the last one;
  - within a round, candidates mutate DIFFERENT dimensions (lead method,
    texture pattern, pad behaviour, drum level, anchor groove) instead of
    four near-identical bass variants.

Search space (per candidate): VariantSpec in phase1_compose.
Macro-structure (form, harmony, section roles) stays fixed, per plan
advice #5: evolve phrases/anchors, not whole songs.

Usage:
    python phase3_hitl.py                       # round 0 (fresh)
    python phase3_hitl.py --round 1 --from-round 0   # mutate round-0 winner
    python phase3_hitl.py --round 0 --pick 2    # record the human pick
"""
import argparse
import json
import random
import sys
from pathlib import Path

PROJECT = Path("/opt/data/repos/musicom/projects/Styles/Pop/ballad-hitl")
SCRIPTS = PROJECT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from phase1_compose import (  # noqa: E402
    build_ballad, VariantSpec, FORM, KEY, BPM, PALETTES, PALETTE_ORDER,
    palette_for_round, REGISTER,
)
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

# Which stem each mutation slot explores, in slot order. Rotating the
# target stem (not just the value) is what stops successive rounds from
# sounding like near-duplicates.
SLOT_ROLES = ["incumbent", "anchor", "lead", "texture+bed"]
MUTATION_DIMENSIONS = {
    "incumbent": "the control — previous winner / current palette",
    "anchor": "bass groove density x offset",
    "lead": "lead composition method (per-section swap)",
    "texture+bed": "arp rate x spread, pad behaviour x drum level",
}


def _render_excerpt(midi_path: Path, out_dir: Path, base: str,
                    seconds: int = EXCERPT_SECONDS) -> str:
    """Render a MIDI to a <=30 s, LEVEL-MATCHED OGG excerpt.

    Loudness is normalized (EBU R128, -16 LUFS) before encoding. Without it
    a round's candidates are auditioned at wildly different levels — a soft
    palette (sax/oboe) lands ~7 dB under a bright one (violin), so the human
    judge picks the loudest candidate rather than the best one.
    """
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
         "-af", f"loudnorm=I=-16:TP=-1.5:LRA=11",
         "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
         str(ogg_path)],
        capture_output=True, text=True)
    if not ogg_path.exists() or ogg_path.stat().st_size < 1000:
        raise RuntimeError("excerpt render failed/empty")
    return str(ogg_path)


def _spec_to_dict(spec: VariantSpec) -> dict:
    """JSON-safe view of a VariantSpec (for round.json / evolution.json)."""
    return {
        "density": spec.density, "offset": spec.offset,
        "lead_method": spec.lead_method,
        "arp_on": list(spec.arp_on) if spec.arp_on is not None else None,
        "arp_rate": spec.arp_rate, "pad_style": spec.pad_style,
        "drum_level": spec.drum_level,
        "palette": spec.palette_map(),
    }


def variant_set(round_num, parent=None, seed=7, n_candidates=MAX_CANDIDATES):
    """K VariantSpecs for one round — each mutating a DIFFERENT stem.

    Slot 0 is the parent/incumbent (the control). Slots 1..K-1 each explore
    a distinct dimension, so a round is a genuine multi-stem audition rather
    than four takes on the same bass line.

    The palette is chosen per round (round_num % len(PALETTE_ORDER)), so
    successive rounds are heard in fresh instrumentation.
    """
    rng = random.Random(seed + round_num * 977)
    palette = palette_for_round(round_num)
    base = parent or VariantSpec()
    # rebase the parent onto this round's palette (unless it pinned one)
    base = VariantSpec(
        density=base.density, offset=base.offset,
        lead_method=base.lead_method, arp_on=base.arp_on,
        arp_rate=base.arp_rate, pad_style=base.pad_style,
        drum_level=base.drum_level, palette=palette,
    )

    variants = [base]                                   # 0: incumbent

    # 1: ANCHOR — nudge the bass groove around the parent (bounded)
    if base.density is None:
        anchor_density = rng.choice([3, 4])
    else:
        anchor_density = max(3, min(5, base.density + rng.choice([-1, 1])))
    variants.append(VariantSpec(
        density=anchor_density, offset=240 - base.offset,
        lead_method=base.lead_method, arp_on=base.arp_on,
        arp_rate=base.arp_rate, pad_style=base.pad_style,
        drum_level=base.drum_level, palette=palette))

    # 2: LEAD — a different composition method across the whole lead
    lead_choices = ["001", "004", "011", "015", "023", "013"]
    lead_choices = [m for m in lead_choices if m != base.lead_method]
    variants.append(VariantSpec(
        density=base.density, offset=base.offset,
        lead_method=rng.choice(lead_choices), arp_on=base.arp_on,
        arp_rate=base.arp_rate, pad_style=base.pad_style,
        drum_level=base.drum_level, palette=palette))

    # 3: TEXTURE — arp density + spread (the wildcard: bed varies too)
    if base.arp_rate == 4:
        rate, spread = 2, ("Verse", "Chorus", "Bridge")
    else:
        rate, spread = 4, ("Verse", "Chorus")
    variants.append(VariantSpec(
        density=base.density, offset=base.offset,
        lead_method=base.lead_method, arp_on=spread,
        arp_rate=rate,
        pad_style="pulse" if base.pad_style != "pulse" else "sustain",
        drum_level=rng.choice(["soft", "full"]), palette=palette))

    return variants[:n_candidates], palette


def _composite_fitness(composer, weights):
    """Score several stems and average — a track-level, not bass-only, view.

    Scoring just the anchor made distinct tracks (different lead/texture/bed)
    score identically. Averaging over the melodic + rhythmic layers captures
    the changes a listener actually hears.
    """
    rows = {v["name"]: v["row"] for v in composer.voices}
    per_stem = {}
    for name in ("Lead", "Bass", "Arp"):
        row = rows.get(name)
        if row is None:
            continue
        units = [composer.matrix.get_unit((row, c))
                 for c in range(len(composer.sections))]
        pitches = [p for u in units if u is not None for p in u.pitches
                   if p > 0]
        if not pitches:
            continue
        from structures import MusicUnit, MusicEvent
        merged = MusicUnit()
        for u in units:
            if u is None:
                continue
            for ev in u.events:
                merged.add_event(ev)
        per_stem[name] = evaluate_fitness(merged, key="Dm", weights=weights)
    if not per_stem:
        return {"total": 0.0, "terms": {}}
    total = sum(f["total"] for f in per_stem.values()) / len(per_stem)
    terms = {}
    for f in per_stem.values():
        for k, v in f["terms"].items():
            terms.setdefault(k, []).append(v)
    terms = {k: round(sum(v) / len(v), 4) for k, v in terms.items()}
    return {"total": total, "terms": terms, "per_stem":
            {k: round(v["total"], 4) for k, v in per_stem.items()}}


def run_ballad_round(round_num=0, seed=7, parent=None,
                     n_candidates=MAX_CANDIDATES, out_dir=None):
    """Generate + render K ballad candidates (multi-stem variation)."""
    if n_candidates > MAX_CANDIDATES:
        raise ValueError(f"K capped at {MAX_CANDIDATES} (Takagi 2001 fatigue)")

    out_dir = Path(out_dir or HITL_DIR / f"round{round_num}")
    cand_dir = out_dir / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)

    weights = STYLE_WEIGHTS.get("pop")
    specs, palette = variant_set(round_num, parent, seed, n_candidates)

    candidates = []
    for vi, spec in enumerate(specs):
        composer = build_ballad(seed=seed + vi * 131, variant=spec)
        viols = hard_gates(composer)
        if viols:
            print(f"  cand{vi} rejected: {viols}")
            continue
        ok, msg = composer.validate()
        if not ok:
            raise RuntimeError(f"cand{vi} validate failed: {msg}")

        fit = _composite_fitness(composer, weights)
        tag = _variant_tag(spec)
        base = f"cand{vi}-{tag}"
        midi_path = cand_dir / f"{base}.mid"
        composer.to_midi(str(midi_path))
        assert midi_path.stat().st_size > 40, "empty MIDI"
        ogg_path = _render_excerpt(midi_path, cand_dir, base)

        c = HITLCandidate(
            variant=vi, density=spec.density if spec.density is not None else 4,
            offset=spec.offset, fitness=fit,
            midi_path=str(midi_path), ogg_path=ogg_path, is_wildcard=False,
        )
        c.spec = _spec_to_dict(spec)            # type: ignore[attr-defined]
        c.role = SLOT_ROLES[vi % len(SLOT_ROLES)]   # type: ignore[attr-defined]
        candidates.append(c)

    if not candidates:
        raise RuntimeError("no candidate passed the hard gates")
    candidates[-1].is_wildcard = len(candidates) > 1

    round_obj = HITLRound(round_num=round_num, candidates=candidates,
                          seed=seed, style="pop-ballad", key=KEY, bpm=BPM,
                          out_dir=str(out_dir))
    (out_dir / "round.json").write_text(json.dumps({
        "round": round_num, "seed": seed, "key": KEY, "bpm": BPM,
        "palette_name": PALETTE_ORDER[round_num % len(PALETTE_ORDER)],
        "palette": palette,
        "parent": _spec_to_dict(parent) if parent else None,
        "candidates": [
            {"variant": c.variant, "fitness_total": round(c.fitness["total"], 4),
             "terms": c.fitness["terms"],
             "per_stem": c.fitness.get("per_stem"),
             "wildcard": c.is_wildcard, "role": c.role, "spec": c.spec,
             "midi": c.midi_path, "ogg": c.ogg_path,
             "form": str(FORM), "progression": "i-VI-III-VII (Dm-Bb-F-C)"}
            for c in candidates],
    }, indent=2))
    return round_obj


def _variant_tag(spec):
    """Short filename tag describing what this candidate changes."""
    bits = [f"p{(spec.palette or {}).get('Lead', '?')[:4]}".replace(" ", "")]
    bits.append(f"ld{spec.lead_method}" if spec.lead_method else "ldX")
    bits.append(f"ar{spec.arp_rate}")
    bits.append(f"pd{spec.pad_style[:4]}")
    bits.append(f"dr{spec.drum_level[:3]}")
    d = "X" if spec.density is None else spec.density
    bits.append(f"b{d}o{spec.offset}")
    return "-".join(bits)


def hitl_summary(round_obj, specs=None):
    """Human-facing metadata: what each candidate actually changes."""
    pal = JSON_PALETTE_CACHE.get(round_obj.out_dir)
    lines = [f"HITL round {round_obj.round_num} — {round_obj.style} "
             f"{round_obj.key} {round_obj.bpm}bpm"
             + (f" | palette: {pal}" if pal else "")]
    for i, c in enumerate(round_obj.candidates):
        tag = " [wildcard]" if c.is_wildcard else ""
        role = getattr(c, "role", "?")
        spec = getattr(c, "spec", {}) or {}
        pal_d = spec.get("palette") or {}
        inst = "/".join(f"{k[:2]}={v}" for k, v in pal_d.items())
        lines.append(f"  {i} [{role:9s}] fitness={c.fitness['total']:.3f}{tag}")
        if inst:
            lines.append(f"      {inst}")
        lines.append(f"      lead={spec.get('lead_method') or 'per-section'}"
                     f" arp={spec.get('arp_rate')}x "
                     f"{spec.get('arp_on') or 'default'}"
                     f" pad={spec.get('pad_style')}"
                     f" drums={spec.get('drum_level')}"
                     f" bass=d{spec.get('density')}off{spec.get('offset')}")
    return "\n".join(lines)


JSON_PALETTE_CACHE = {}


def record_ballad_pick(round_obj, pick_index):
    """Record the human pick + write provenance on the winning MIDI."""
    res = record_pick(round_obj, pick_index,
                      evolution_path=str(Path(round_obj.out_dir)
                                         / "evolution.json"))
    winner = res["winner"]
    spec = getattr(winner, "spec", {}) or {}
    write_provenance(
        artifact_path=winner.midi_path,
        classification=AI_ASSISTED,
        generator=f"pop-ballad-hitl phase3 HITL (round {round_obj.round_num}, "
                  f"human pick {pick_index})",
        sources=["style:pop-ballad", f"key:{round_obj.key}",
                 f"bpm:{round_obj.bpm}", "progression:i-VI-III-VII",
                 "path:C middle-out", "judge:human",
                 "palette:" + ",".join(f"{k}={v}" for k, v
                                       in (spec.get("palette") or {}).items())],
        parameters={"spec": spec, "fitness": winner.fitness["terms"],
                    "search_space": "multi-stem: palette x anchor x lead "
                                    "method x texture x bed"},
    )
    return res


def load_round(out_dir):
    """Rebuild a HITLRound from a rendered round.json (no re-render)."""
    out_dir = Path(out_dir)
    data = json.loads((out_dir / "round.json").read_text())
    JSON_PALETTE_CACHE[str(out_dir)] = data.get("palette_name")
    candidates = []
    for c in data["candidates"]:
        cand = HITLCandidate(
            variant=c["variant"], density=(c["spec"].get("density") or 4),
            offset=c["spec"].get("offset", 0),
            fitness={"total": c["fitness_total"], "terms": c["terms"],
                     "per_stem": c.get("per_stem")},
            midi_path=c["midi"], ogg_path=c["ogg"],
            is_wildcard=c["wildcard"],
        )
        cand.spec = c["spec"]                   # type: ignore[attr-defined]
        cand.role = c.get("role", "?")          # type: ignore[attr-defined]
        candidates.append(cand)
    return HITLRound(round_num=data["round"], candidates=candidates,
                     seed=data["seed"], style="pop-ballad",
                     key=data["key"], bpm=data["bpm"], out_dir=str(out_dir))


def main():
    ap = argparse.ArgumentParser(description="Pop-ballad HITL round")
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--from-round", type=int, default=None,
                    help="parent: winner of this earlier round")
    ap.add_argument("--n-candidates", type=int, default=MAX_CANDIDATES)
    ap.add_argument("--pick", type=int, default=None,
                    help="record this candidate index as the human pick")
    args = ap.parse_args()

    parent = None
    if args.from_round is not None:
        prev = load_round(HITL_DIR / f"round{args.from_round}")
        evo = json.loads((Path(prev.out_dir) / "evolution.json").read_text())
        pick = evo["latest"]["pick_index"]
        spec_d = evo["latest"]["winner"].get("spec") or \
            getattr(prev.candidates[pick], "spec", {})
        parent = VariantSpec(
            density=spec_d.get("density"), offset=spec_d.get("offset", 0),
            lead_method=spec_d.get("lead_method"),
            arp_on=tuple(spec_d["arp_on"]) if spec_d.get("arp_on") else None,
            arp_rate=spec_d.get("arp_rate", 2),
            pad_style=spec_d.get("pad_style", "sustain"),
            drum_level=spec_d.get("drum_level", "default"),
        )
        print(f"parent: round {args.from_round} winner = "
              f"{spec_d.get('palette', {}).get('Lead')} / "
              f"density={parent.density}")

    r = run_ballad_round(round_num=args.round, seed=args.seed, parent=parent,
                         n_candidates=args.n_candidates)
    print(hitl_summary(r))
    print()
    for c in r.candidates:
        print(f"  cand{c.variant}: {c.ogg_path}")

    if args.pick is not None:
        res = record_ballad_pick(r, args.pick)
        w = res["winner"]
        print(f"\nPICK RECORDED: cand{w.variant} (role={getattr(w, 'role', '?')})")
        print(f"  evolution.json: {res['evolution_path']}")
        print(f"  winner MIDI:    {w.midi_path}")


if __name__ == "__main__":
    main()
