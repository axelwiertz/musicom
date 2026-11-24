# -*- coding: utf-8 -*-
"""320-axel-style-study — iteration 01 of the 'axel' personal style.

Style 'axel': genre-neutral personal voice (guitar/violin/piano/percussion).
E major, 115 BPM, 4/4, through-composed S1..S6.

Paradigm (the four words):
  abstract   — harmony chosen as a subset-walk over the E-major set network
               (I-IV-vi-V-ii-I), parsimonious voice-leading (ABS-004 flavor).
               ABS-002 subset-walker / ABS-003 Z-variation are the next
               iteration (Z-variation needs tetrads, not triads).
  balanced   — accompaniment bed from the registered 'axel' rhythm recipe
               (light kit + root-5th bass + sustained pad + 16th guitar arp),
               humanize profile 5 ms / 5 / 0.35 / 2 ms (midpoint).
  harmonious — every note diatonic to E major; strong beats snap to the
               section chord tones (two-phase: abstract variation -> tonal).
  changing   — one 16-note motif evolves across 6 sections via the variation
               operators transpose / invert / retrograde / density_scale.
"""

from __future__ import annotations

import json
import os

from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.cell_engine import CellContext, _unit_from_events
from workflows.style_rhythm import style_fillers
from workflows.variation import invert, transpose, retrograde, density_scale
from workflows.humanize import export_dual

BPM = 115
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
SEED = 320
STYLE = "axel"
KEY = "E"

PROG = {"Lead": 40, "Pad": 1, "Bass": 43, "Arp": 24, "Drums": 0}
CHAN = {"Lead": 0, "Pad": 1, "Bass": 2, "Arp": 3, "Drums": 9}

SECTION_NAMES = ["S1", "S2", "S3", "S4", "S5", "S6"]
BARS_PER = [4] * 6

# per-section harmony: degree, bass root, chord tones (root, third, fifth)
HARMONY = [
    ("I",  40, (52, 56, 59)),   # E
    ("IV", 45, (57, 61, 64)),   # A
    ("vi", 49, (49, 52, 56)),   # C#m
    ("V",  47, (59, 63, 66)),   # B
    ("ii", 42, (54, 57, 61)),   # F#m
    ("I",  40, (64, 68, 71)),   # E (octave lift recap)
]

E_SCALE_PCS = {4, 6, 8, 9, 11, 1, 3}   # E F# G# A B C# D#

# 16-note base motif (4 bars x 4 quarters) — singable, all E major:
# E G# B G# | A G# F# E | F# G# A B | C# B G# E
MOTIF = [64, 68, 71, 68, 69, 68, 66, 64, 66, 68, 69, 71, 73, 71, 68, 64]

FILLERS = style_fillers(STYLE)


def base_lead_events():
    evs = []
    for i, p in enumerate(MOTIF):
        t = i * 480
        evs.append(MusicEvent(p, 88, t, t + 360))
    return evs


def snap_scale(p):
    if p % 12 in E_SCALE_PCS:
        return p
    for d in range(1, 12):
        for cand in (p - d, p + d):
            if cand % 12 in E_SCALE_PCS:
                return cand
    return p


def snap_chord(p, tones):
    cands = [t + o for t in tones for o in (-24, -12, 0, 12, 24)]
    return min(cands, key=lambda c: abs(c - p))


def lead_section_events(s_idx, tones):
    """Phase 1: abstract variation of the base motif. Phase 2: snap to E major
    scale (weak beats) + section chord tones (strong beats 1 & 3)."""
    if s_idx == 0:
        raw = base_lead_events()
    elif s_idx == 1:
        raw = transpose(base_lead_events(), 5)          # up a 4th
    elif s_idx == 2:
        raw = invert(base_lead_events(), axis=68)       # mirror
    elif s_idx == 3:
        raw = retrograde(base_lead_events(), section_len=4 * BAR)  # reverse
    elif s_idx == 4:
        raw = density_scale(base_lead_events(), 0.5)    # sparse contrast
    else:
        raw = transpose(base_lead_events(), 12)         # octave recap

    out = []
    for ev in raw:
        if ev.pitch == 0:
            continue
        t = ev.start_tick
        p = snap_chord(ev.pitch, tones) if t % 960 == 0 else snap_scale(ev.pitch)
        p = int(max(55, min(96, p)))
        out.append(MusicEvent(p, ev.volume, t, ev.end_tick))
    return out


def cell_ctx(tones, root):
    return CellContext(
        key=KEY, pattern="major", chord_tones=tuple(tones), register=(0, 127),
        density=1.0, root_midi=root, section_bars=4, section_len=4 * BAR,
        bar_ticks=BAR,
    )


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    midi_dir = os.path.join(out_dir, "MIDI")
    os.makedirs(midi_dir, exist_ok=True)
    base = os.path.join(midi_dir, "320-axel-style-study")

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=5, num_sections=6)
    for vname in ("Lead", "Pad", "Bass", "Arp", "Drums"):
        composer.add_voice(vname, program=PROG[vname], channel=CHAN[vname])
    for sname, bars in zip(SECTION_NAMES, BARS_PER):
        composer.add_section(sname, bars=bars)

    section_len = 4 * BAR
    for s, sname in enumerate(SECTION_NAMES):
        degree, root, tones = HARMONY[s]
        ctx = cell_ctx(tones, root)
        lead = lead_section_events(s, tones)
        cells = {
            "Lead": lead,
            "Pad": FILLERS["pad"](ctx),
            "Bass": FILLERS["bass"](ctx),
            "Arp": FILLERS["arp"](ctx),
            "Drums": FILLERS["rhythm"](ctx),
        }
        for vname, evs in cells.items():
            composer.fill_voice_section(vname, sname, _unit_from_events(evs, section_len))

    instruments = {"Drums": (2.0, 4.0, 0.0, 0.02), "Bass": (None, None, 8.0, None)}
    hz = export_dual(composer, base + "-perfect.mid", base + "-humanized.mid",
                     style=STYLE, seed=SEED, bpm=BPM, instruments=instruments)

    prov = {
        "project": "320-axel-style-study",
        "style": STYLE, "key": KEY, "bpm": BPM, "time_sig": "4/4",
        "form": "through-composed S1..S6", "seed": SEED,
        "paradigm": "abstract + balanced + harmonious + changing",
        "instruments": {"Lead": "violin(40)", "Pad": "piano(1)",
                        "Bass": "double_bass(43)", "Arp": "acoustic_guitar(24)",
                        "Drums": "drum kit(ch9)"},
        "harmony": "E-major subset walk I-IV-vi-V-ii-I, parsimonious voice-leading (ABS-004 flavor)",
        "motif": MOTIF,
        "variation_arc": ["S1 original", "S2 transpose +5", "S3 invert(axis 68)",
                          "S4 retrograde", "S5 density_scale 0.5", "S6 transpose +12"],
        "phase2": "weak beats -> E-major scale; strong beats (1&3) -> section chord tones",
        "humanize": hz,
    }
    with open(os.path.join(midi_dir, "320-axel-style-study.provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print("wrote", base + "-perfect.mid")
    print("wrote", base + "-humanized.mid")
    print("humanize summary:", json.dumps(hz, indent=2))


if __name__ == "__main__":
    main()
