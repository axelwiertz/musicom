"""Paradigm-compare workflow (Phase 5, T5.1).

Generate the same musical slot three ways — Stochastic vs Rules-based vs
Nature-led — render each to MIDI, and emit a side-by-side comparison table.

Matches the user's interest in contrasting algorithmic composition paradigms.

Paradigms:
  - stochastic : StochasticGenerator (random pitch/duration draws, seeded)
  - rules      : diatonic scale-degree walk (rules-based, deterministic)
  - nature     : SchillingerGenerator resultant rhythm (interference of periods)

Each returns a MusicUnit; the workflow wraps each in a single-voice, single-
section UnitMatrixComposer and exports MIDI + a grid visualization.
"""
import os
import random
from typing import Dict, List

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_GENERATED

C_MAJOR = [60, 62, 64, 65, 67, 69, 71, 72]
BAR = 480 * 4


def _stochastic_unit(length: int = 8, seed: int = 42) -> MusicUnit:
    """Stochastic paradigm: seeded random draws over a pitch/duration set."""
    rng = random.Random(seed)
    unit = MusicUnit()
    tick = 0
    step = BAR // length
    for _ in range(length):
        pitch = rng.choice(C_MAJOR)
        unit.add_event(MusicEvent(pitch=pitch, volume=rng.randint(70, 110),
                                  start_tick=tick, end_tick=tick + step))
        tick += step
    return unit


def _rules_unit(length: int = 8) -> MusicUnit:
    """Rules-based paradigm: deterministic diatonic scale-degree ascent/descent."""
    unit = MusicUnit()
    tick = 0
    step = BAR // length
    # simple rule: stepwise up then resolve down to tonic
    degrees = list(range(length))
    for i in degrees:
        idx = i if i < len(C_MAJOR) else (len(C_MAJOR) - 1 - (i - len(C_MAJOR)))
        pitch = C_MAJOR[max(0, min(idx, len(C_MAJOR) - 1))]
        unit.add_event(MusicEvent(pitch=pitch, volume=90,
                                  start_tick=tick, end_tick=tick + step))
        tick += step
    return unit


def _nature_unit(length: int = 8) -> MusicUnit:
    """Nature-led paradigm: Schillinger resultant (interference of two periods)."""
    from generators.schillinger import SchillingerGenerator
    gen = SchillingerGenerator(generator_a=3, generator_b=2)
    unit = gen.generate_unit(base_tick_dur=BAR // 12, key_scale=C_MAJOR)
    return unit


PARADIGMS = {
    "stochastic": _stochastic_unit,
    "rules": _rules_unit,
    "nature": _nature_unit,
}


def compose_paradigm(name: str, unit: MusicUnit, bpm: int = 120) -> UnitMatrixComposer:
    """Wrap a melody unit in a single-voice / single-section composer."""
    c = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=1, num_sections=1)
    c.add_voice(name, program=MidiInstrument.PIANO, channel=0)
    c.add_section("A", bars=1)
    c.set_unit(0, 0, unit)
    return c


def _unit_stats(unit: MusicUnit) -> Dict:
    pitches = [p for p in unit.pitches if p > 0]
    intervals = unit.pitch_intervals
    return {
        "notes": len(pitches),
        "range": (max(pitches) - min(pitches)) if pitches else 0,
        "unique_pitches": len(set(pitches)),
        "avg_abs_interval": round(sum(abs(i) for i in intervals) / len(intervals), 2) if intervals else 0,
        "len_ticks": unit.len_ticks(),
    }


def compare_table(stats_by_paradigm: Dict[str, Dict]) -> str:
    """Render a markdown comparison table."""
    cols = ["notes", "unique_pitches", "range", "avg_abs_interval", "len_ticks"]
    lines = ["| paradigm | " + " | ".join(cols) + " |",
             "|" + "---|" * (len(cols) + 1)]
    for name, st in stats_by_paradigm.items():
        lines.append("| " + name + " | " + " | ".join(str(st[c]) for c in cols) + " |")
    return "\n".join(lines)


def run_comparison(output_dir: str, bpm: int = 120, seed: int = 42) -> Dict:
    """Generate all three paradigms, render MIDI + grids, write compare table.

    Returns a dict with per-paradigm paths, stats, and the table path.
    """
    os.makedirs(output_dir, exist_ok=True)
    result = {"paradigms": {}, "output_dir": output_dir}
    stats = {}

    for name, fn in PARADIGMS.items():
        unit = fn()
        composer = compose_paradigm(name, unit, bpm=bpm)
        ok, msg = composer.validate()
        if not ok:
            raise ValueError(f"{name} failed validation: {msg}")

        midi_path = os.path.join(output_dir, f"{name}.mid")
        composer.to_midi(midi_path)
        grid_path = write_grid_visualization(
            composer.matrix, os.path.join(output_dir, f"{name}_grid.txt"),
            ticks_per_character=120, voice_names=[name], bpm=bpm)

        prov_path = write_provenance(
            midi_path, classification=AI_GENERATED,
            generator=f"paradigm_compare/{name}",
            sources=[f"seed={seed}", "scale=C_major"],
            parameters={"bpm": bpm, "paradigm": name},
            notes="Auto-generated by paradigm comparison workflow.")

        st = _unit_stats(unit)
        stats[name] = st
        result["paradigms"][name] = {
            "midi": midi_path, "grid": grid_path, "provenance": prov_path,
            "stats": st, "midi_bytes": os.path.getsize(midi_path),
        }

    table = compare_table(stats)
    table_path = os.path.join(output_dir, "comparison.md")
    with open(table_path, "w", encoding="utf-8") as f:
        f.write("# Paradigm Comparison\n\n" + table + "\n")
    result["table"] = table
    result["table_path"] = table_path
    return result


if __name__ == "__main__":
    import json
    out = "outputs/paradigm_compare"
    r = run_comparison(out)
    print(r["table"])
    print("\nArtifacts:")
    for name, info in r["paradigms"].items():
        print(f"  {name}: {info['midi']} ({info['midi_bytes']} B), {info['grid']}")
