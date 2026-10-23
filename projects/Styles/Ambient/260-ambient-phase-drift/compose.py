# -*- coding: utf-8 -*-
"""260-ambient-phase-drift — ambient DPSM (Phase-Shift Minimalism) demo.

Method 026 DPSM (phase-shift minimalism), layer concrete. Style Ambient.
D dorian, 72 BPM, 24 bars (6 sections x 4), NO percussion.

Axis-combo demonstrated (see COMPOSITION_DESIGN_SPACE.md):
  - layer path: concrete-only (method realizes directly)
  - paradigm: Nature-Led (phase-shift minimalism)
  - percussion: NONE (axis 4)
  - lead: 1 lead + arp texture (axis 3+5)
  - harmonization: pad (sustained) + arp (16th phase-drift) (axis 5)
  - register: bass 36-52 -> pad 48-72 -> arp 60-84 -> lead 67-84 (non-crossing)
  - humanization: style Ambient (6ms / layback 0), melodic voices style-governed

Two arp voices: ArpA fixed, ArpB phase-drifts +1 beat per section (Reich
phase process). Dual-version export (perfect + humanized).
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import FLUTE, GLOCKENSPIEL, STRING_ENSEMBLE, DOUBLE_BASS  # noqa: E402

GENRE = "Ambient"
NAME = "260-ambient-phase-drift"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 2                       # D
KEY_NAME = "D dorian"
DORIAN_OFFS = [0, 2, 3, 5, 7, 9, 10]
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in DORIAN_OFFS]   # D E F G A B C
SCALE_PCS = set(SCALE_DEG_PCS)
BPM = 72
TPB = 480
BAR = 1920
BEAT = BAR // 4                 # 480
EIGHTH = 240
SIXTEENTH = 120
SEED = 20261023

FORM = [("S1", 4), ("S2", 4), ("S3", 4), ("S4", 4), ("S5", 4), ("S6", 4)]
FORM_NAME = "s1-s2-s3-s4-s5-s6"
N_BARS = sum(b for _, b in FORM)
SECTION_TICKS = {}
_t = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _t)
    _t += b * BAR
TOTAL_TICKS = _t

# diatonic dorian chords per section (D E F G A B C)
CHORD_PCS = {
    "S1": [2, 5, 9, 0],      # Dm7 (i7)
    "S2": [0, 4, 7, 11],     # Cmaj7 (bVII)
    "S3": [2, 5, 9, 0],      # Dm7
    "S4": [7, 11, 2],        # G (IV)
    "S5": [9, 0, 4],         # Am (v)
    "S6": [2, 5, 9, 0],      # Dm7
}


def section_of_bar(b):
    acc = 0
    for s, n in FORM:
        if acc <= b < acc + n:
            return s
        acc += n
    return FORM[-1][0]


def chord_tones(pcs, floor, ceil):
    out = []
    for pc in sorted(set(pcs)):
        p = floor + ((pc - floor) % 12)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


# ---- voice builders (absolute whole-piece ticks) ---------------------------

def lead_events():
    """Sparse breathy lead — one chord tone every 2 bars, held ~2 bars."""
    evs = []
    for b in range(N_BARS):
        if b % 2 == 1:
            continue
        s = section_of_bar(b)
        tones = chord_tones(CHORD_PCS[s], 67, 84)
        st = b * BAR
        p = tones[(b // 2) % len(tones)]
        evs.append(MusicEvent(pitch=p, volume=60, start_tick=st,
                              end_tick=st + 2 * BAR - EIGHTH))
    return evs


def arp_events(phase_step_per_section):
    """16th arpeggio over the section chord, phase-shifted per section."""
    evs = []
    for si, (s, (slen, soff)) in enumerate(SECTION_TICKS.items()):
        tones = chord_tones(CHORD_PCS[s], 60, 84)
        phase = si * phase_step_per_section
        n = slen // SIXTEENTH
        for k in range(n):
            st = soff + ((k * SIXTEENTH + phase) % slen)
            p = tones[k % len(tones)]
            evs.append(MusicEvent(pitch=p, volume=52, start_tick=st,
                                  end_tick=st + SIXTEENTH))
    return evs


def pad_events():
    """Sustained chord block, whole section."""
    evs = []
    for s, (slen, soff) in SECTION_TICKS.items():
        tones = chord_tones(CHORD_PCS[s], 48, 72)
        for p in tones[:4]:
            evs.append(MusicEvent(pitch=p, volume=46, start_tick=soff,
                                  end_tick=soff + slen))
    return evs


def bass_events():
    """Root pedal, whole notes per bar."""
    evs = []
    for s, (slen, soff) in SECTION_TICKS.items():
        root = pc_to_pitch(CHORD_PCS[s][0], 36)
        for bar in range(slen // BAR):
            st = soff + bar * BAR
            evs.append(MusicEvent(pitch=root, volume=68, start_tick=st,
                                  end_tick=st + BAR))
    return evs


VOICES = [
    ("Lead", FLUTE.midi_program, 0),
    ("ArpA", GLOCKENSPIEL.midi_program, 1),
    ("ArpB", GLOCKENSPIEL.midi_program, 2),
    ("Pad", STRING_ENSEMBLE.midi_program, 3),
    ("Bass", DOUBLE_BASS.midi_program, 4),
]
events_by_voice = {
    "Lead": lead_events(),
    "ArpA": arp_events(0),
    "ArpB": arp_events(BEAT),       # +1 beat per section
    "Pad": pad_events(),
    "Bass": bass_events(),
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    composer.add_section(sname, bars=nbars)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        seg = sorted([e for e in evs if soff <= e.start_tick < soff + slen],
                     key=lambda e: (e.start_tick, e.pitch))
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
            if e.end_tick <= e.start_tick:
                e.end_tick = e.start_tick + 1
        composer.fill_voice_section(vname, sname, unit_from(seg, slen))

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Lead": FLUTE.humanize_dna,
    "ArpA": GLOCKENSPIEL.humanize_dna,
    "ArpB": GLOCKENSPIEL.humanize_dna,
    "Pad": STRING_ENSEMBLE.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "perfect", "grid-locked, no jitter"),
                          (humanized_path, "humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom {NAME}",
                     sources=["methods_db:026 DPSM (Phase-Shift Minimalism)",
                              f"style:{GENRE}", "phase:concrete",
                              f"humanize_seed:{hz_seed}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": FORM_NAME,
                                 "humanize": hz, "note": note,
                                 "axis_combo": "percussion=none, 1 lead + arp "
                                               "phase-drift, pad harmonization"})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE,
    "method": "026 DPSM (Phase-Shift Minimalism)",
    "layer": "concrete", "paradigm": "Nature-Led",
    "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "bars": N_BARS, "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "scale_pcs": SCALE_DEG_PCS,
    "chords": CHORD_PCS,
    "voices": [v for v, _, _ in VOICES],
    "percussion": "none",
    "humanize_seed": hz_seed,
    "axis_combo": ["layer=concrete-only", "paradigm=Nature-Led(DPSM)",
                   "percussion=none", "lead=1+arp-texture",
                   "harmonization=pad+arp", "form=6-section",
                   "humanization=ambient(6ms)"],
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
