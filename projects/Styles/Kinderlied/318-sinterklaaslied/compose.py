# -*- coding: utf-8 -*-
"""318-sinterklaaslied — compose a Dutch Sinterklaas liedje through the musicom engine.

Style: 'sinterklaas' (registered in the engine 2026-11-22).
Key C major, 112 BPM, 4/4 march with dotted 'arrival' lilt.

Design (see Notes/style-spec.md):
  - Lead   = recorder (GM 74)  — the school-flute sing-along melody
  - Pad    = celesta  (GM 8)   — magic bell harmonic wash (sustained triads)
  - Bass   = tuba     (GM 58)  — oom-pah root/fifth (street-organ / brass band)
  - Arp    = glockenspiel (GM 9) — bell-glitter 8th arpeggio (continuous)
  - Drums  = light march (ch9) — kick 1&3, snare 2&4, soft 8th hats

Harmony (dead-simple I–IV–V, per-bar):
  Intro:  C C C C
  Verse:  C C F G | C F G C   (question ends on V, answer lands V–I)
  Refrain:C F C G | C F G C   (sing-along hook)
  Verse2: C C F G | C F G C   (strophic repeat)
  Outro:  C C C C             (descending closure + progressive dropout)

All composition goes through UnitMatrixComposer (no raw mido authoring).
Zero-drift gate: validate() before BOTH exports (perfect + humanized).
"""

from __future__ import annotations

import json
import os
import sys

from structures import MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.cell_engine import _unit_from_events
from workflows.humanize import export_dual

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
BPM = 112
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920 ticks
SEED = 318

STYLE = "sinterklaas"
KEY = "C"
FORM = "intro-verse-refrain-verse-outro"

# GM programs
PROG = {"Lead": 74, "Pad": 8, "Bass": 58, "Arp": 9, "Drums": 0}
CHAN = {"Lead": 0, "Pad": 0, "Bass": 0, "Arp": 0, "Drums": 9}

ROOT = {"C": 48, "F": 53, "G": 55}          # bass octave (C3/F3/G3)

CHORDS = {
    "Intro":  ["C"] * 4,
    "Verse":  ["C", "C", "F", "G", "C", "F", "G", "C"],
    "Refrain": ["C", "F", "C", "G", "C", "F", "G", "C"],
    "Verse2": ["C", "C", "F", "G", "C", "F", "G", "C"],
    "Outro":  ["C", "C", "C", "C"],
}

# --- Hand-authored singable melody ------------------------------------------
# (start_16th, dur_16th, midi) — cell-local, 16 sixteenth-slots per bar.
# C-major degrees in the C5 octave: C5=72 D5=74 E5=76 F5=77 G5=79 A5=81 B5=83.
# B4=71 used as the leading tone for the authentic V->I cadence.
# Conjunct (max leap = a 3rd), narrow range B4..A5 (children singable),
# dotted-8th+16th 'arrival' lilt on the phrase heads.
TUNE_VERSE = [
    # bar 0 (question): "sol sol la sol | mi mi fa mi"  (dotted lilt)
    (0, 3, 79), (3, 1, 79), (4, 2, 81), (6, 2, 79),
    (8, 3, 76), (11, 1, 76), (12, 2, 77), (14, 2, 76),
    # bar 1: "re re mi fa sol sol fa mi"  (rise -> G, half cadence)
    (16, 2, 74), (18, 2, 74), (20, 2, 76), (22, 2, 77),
    (24, 2, 79), (26, 2, 79), (28, 2, 77), (30, 2, 76),
    # bar 2 (answer): "fa fa sol fa mi fa re re"
    (32, 3, 77), (35, 1, 77), (36, 2, 79), (38, 2, 77),
    (40, 2, 76), (42, 2, 77), (44, 2, 74), (46, 2, 74),
    # bar 3: "do re mi fa sol la sol"  (half cadence on G)
    (48, 2, 72), (50, 2, 74), (52, 2, 76), (54, 2, 77),
    (56, 2, 79), (58, 2, 81), (60, 4, 79),
    # bar 4: repeat bar 0
    (64, 3, 79), (67, 1, 79), (68, 2, 81), (70, 2, 79),
    (72, 3, 76), (75, 1, 76), (76, 2, 77), (78, 2, 76),
    # bar 5: "la la sol fa sol fa mi re"
    (80, 2, 81), (82, 2, 81), (84, 2, 79), (86, 2, 77),
    (88, 2, 79), (90, 2, 77), (92, 2, 76), (94, 2, 74),
    # bar 6: "mi fa sol la sol mi re re"
    (96, 2, 76), (98, 2, 77), (100, 2, 79), (102, 2, 81),
    (104, 2, 79), (106, 2, 76), (108, 2, 74), (110, 2, 74),
    # bar 7: "do re mi fa sol sol si do"  (authentic cadence B4 -> C5)
    (112, 2, 72), (114, 2, 74), (116, 2, 76), (118, 2, 77),
    (120, 2, 79), (122, 2, 79), (124, 2, 71), (126, 2, 72),
]

TUNE_REFRAIN = [
    # sing-along hook: quarter notes, peaks at A5
    (0, 4, 79), (4, 4, 81), (8, 4, 79), (12, 4, 76),      # G A G E
    (16, 4, 77), (20, 4, 79), (24, 4, 76), (28, 4, 74),   # F G E D
    (32, 4, 79), (36, 4, 81), (40, 4, 79), (44, 4, 76),   # G A G E
    (48, 4, 77), (52, 4, 79), (56, 8, 72),                # F G C (long)
    (64, 4, 79), (68, 4, 81), (72, 4, 79), (76, 4, 76),   # G A G E
    (80, 4, 77), (84, 4, 79), (88, 4, 76), (92, 4, 74),   # F G E D
    (96, 4, 79), (100, 4, 79), (104, 4, 81), (108, 4, 71),  # G G A B4 (leading tone)
    (112, 8, 72), (120, 8, 72),                           # C C (long tonic)
]

TUNE_OUTRO = [
    (0, 4, 79), (4, 4, 76), (8, 4, 74), (12, 4, 72),      # G E D C (descending)
    (16, 4, 76), (20, 4, 74), (24, 8, 72),                # E D C
    (32, 8, 72), (40, 8, 72),                             # C C
    (48, 16, 72),                                         # C (whole)
]

MELODY = {"Verse": TUNE_VERSE, "Refrain": TUNE_REFRAIN,
          "Verse2": TUNE_VERSE, "Outro": TUNE_OUTRO}


# ----------------------------------------------------------------------------
# Voice builders (cell-local events; no terminal landmark — _unit_from_events
# adds it at the section boundary so every voice ends at section_len).
# ----------------------------------------------------------------------------
def pad_events(bars, roots):
    """Celesta sustained triad per bar (the harmonic wash)."""
    evs = []
    for b in range(bars):
        r = roots[b]
        base = b * BAR
        for p in (r + 12, r + 16, r + 19):
            evs.append(MusicEvent(p, 62, base, base + BAR))
    return evs


def bass_events(bars, roots):
    """Tuba oom-pah: root(1) fifth(2) root(3) fifth(4)."""
    evs = []
    for b in range(bars):
        r = roots[b]
        base = b * BAR
        evs.append(MusicEvent(r, 92, base, base + 420))
        evs.append(MusicEvent(r + 7, 84, base + 480, base + 840))
        evs.append(MusicEvent(r, 92, base + 960, base + 1380))
        evs.append(MusicEvent(r + 7, 84, base + 1440, base + 1800))
    return evs


def arp_events(bars, roots):
    """Glockenspiel 8th-note bell arpeggio (continuous glitter)."""
    evs = []
    for b in range(bars):
        r = roots[b]
        tones = (r + 12, r + 16, r + 19, r + 24)
        base = b * BAR
        for e in range(8):
            evs.append(MusicEvent(tones[e % 4], 66, base + e * 240, base + e * 240 + 230))
    return evs


def drums_events(bars):
    """Light march: kick 1&3, snare 2&4, soft 8th hats."""
    evs = []
    for b in range(bars):
        base = b * BAR
        for beat in (0, 2):
            evs.append(MusicEvent(36, 90, base + beat * 480, base + beat * 480 + 100))
        for beat in (1, 3):
            evs.append(MusicEvent(38, 82, base + beat * 480, base + beat * 480 + 90))
        for e in range(8):
            evs.append(MusicEvent(42, 46, base + e * 240, base + e * 240 + 70))
    return evs


def melody_events(tune, bars):
    """Recorder melody from a (start16, dur16, midi) table."""
    evs = []
    for (s16, d16, midi) in tune:
        start = s16 * 120
        end = start + d16 * 120 - 8   # 8-tick (~4 ms) breath gap
        evs.append(MusicEvent(midi, 96, start, end))
    return evs


# ----------------------------------------------------------------------------
# Fill one section
# ----------------------------------------------------------------------------
def fill_section(composer, section, tune, mode):
    roots = [ROOT[c] for c in CHORDS[section]]
    bars = len(roots)
    section_len = bars * BAR

    lead = melody_events(tune, bars) if tune else []
    pad = pad_events(bars, roots)

    if mode == "intro":
        bass, arp, drums = [], arp_events(bars, roots), []
    elif mode == "outro":
        # progressive dropout: bass/drums bar0, arp bars0-1, pad all bars
        bass = bass_events(1, roots[:1])
        drums = drums_events(1)
        arp = arp_events(2, roots[:2])
    else:
        bass = bass_events(bars, roots)
        arp = arp_events(bars, roots)
        drums = drums_events(bars)

    cells = {
        "Lead": lead, "Pad": pad, "Bass": bass, "Arp": arp, "Drums": drums,
    }
    for vname, evs in cells.items():
        composer.fill_voice_section(vname, section, _unit_from_events(evs, section_len))


# ----------------------------------------------------------------------------
# Compose + export (dual: perfect + humanized)
# ----------------------------------------------------------------------------
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    midi_dir = os.path.join(out_dir, "MIDI")
    os.makedirs(midi_dir, exist_ok=True)
    base = os.path.join(midi_dir, "318-sinterklaaslied")

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=5, num_sections=5)

    for vname in ("Lead", "Pad", "Bass", "Arp", "Drums"):
        composer.add_voice(vname, program=PROG[vname], channel=CHAN[vname])

    for sname, bars in [("Intro", 4), ("Verse", 8), ("Refrain", 8),
                        ("Verse2", 8), ("Outro", 4)]:
        composer.add_section(sname, bars=bars)

    fill_section(composer, "Intro", None, "intro")
    fill_section(composer, "Verse", TUNE_VERSE, "full")
    fill_section(composer, "Refrain", TUNE_REFRAIN, "full")
    fill_section(composer, "Verse2", TUNE_VERSE, "full")
    fill_section(composer, "Outro", TUNE_OUTRO, "outro")

    # drums anchor (2 ms); melodic voices use the style profile (8 ms).
    instruments = {"Drums": (2.0, 4.0, 0.0, 0.01)}

    hz = export_dual(composer, base + "-perfect.mid", base + "-humanized.mid",
                     style=STYLE, seed=SEED, bpm=BPM, instruments=instruments)

    # provenance
    prov = {
        "project": "318-sinterklaaslied",
        "style": STYLE, "key": KEY, "bpm": BPM, "time_sig": "4/4",
        "form": FORM, "seed": SEED,
        "voices": [{"name": v, "program": PROG[v], "channel": CHAN[v]}
                   for v in ("Lead", "Pad", "Bass", "Arp", "Drums")],
        "sections": {s: CHORDS[s] for s in CHORDS},
        "melody": {
            "register": "B4..A5", "range_semitones": 10,
            "cadence": "verse: half (V) then authentic (V-I); refrain: authentic",
            "style_note": "conjunct, dotted 'arrival' lilt, children singable",
        },
        "humanize": hz,
    }
    with open(os.path.join(midi_dir, "318-sinterklaaslied.provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print("wrote", base + "-perfect.mid")
    print("wrote", base + "-humanized.mid")
    print("humanize summary:", json.dumps(hz, indent=2))


if __name__ == "__main__":
    main()
