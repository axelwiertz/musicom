# -*- coding: utf-8 -*-
"""262-harmonic-chorale-variations — Experimental rework of 067-harmonic-chorale.

Rework agent: source 067-harmonic-chorale FAILED audit standard 6 (missing
index.html) -> full rebuild through the canonical UnitMatrixComposer, preserving
identity (F major, 92 BPM, SATB chorale, Method 023 Harmonic-Series overtone
staircase of G3), then extended into a LONGER, MORE VARIED piece.

Two-phase architecture (mandatory):
  Phase 1 = raw generative draft: natural overtone staircase (12-TET partials
            1..16 of G3 = 55), walked per section with a variation transform,
            single voice, unquantized chromatic pitches, off-grid onsets, NO
            harmony. Exported as -phase1.mid.
  Phase 2 = musicom rules post-processing: chord-tone quantization per bar,
            smooth voice-leading (nearest-octave block harmony), 16th-grid onset
            snap, register/range enforcement, dual-version export (perfect +
            humanized).

Form: 6 sections x 4 bars = 24 bars (source = 4 x 2 = 8 bars -> 3x longer).
Variation techniques (>= 3 required): retrograde, transposition (up a 5th),
inversion, diminution (+register shift up), augmentation.
"""
import json
import math
import os
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)  # not pip-installed (registry package)
from instrument_registry import FLUTE, STRING_ENSEMBLE, CELLO, DOUBLE_BASS  # noqa: E402

# ---------------- concept ----------------------------------------------------
GENRE = "Experimental"
NAME = "262-harmonic-chorale-variations"
METHOD = "023 Harmonic Series / Overtone Composition"
LAYER = "concrete"
PARADIGM = "Deterministic physics"
TONIC = 5                        # F
KEY_NAME = "F major (ionian)"
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
SCALE_PCS = set((TONIC + o) % 12 for o in SCALE_INTERVALS)
KEY_ROOT_MIDI = 53               # F3 (base for get_diatonic_note)
BPM = 92
TPB = 480
BAR = TPB * 4                    # 1920
BEAT = TPB                       # 480
EIGHTH = TPB // 2                # 240
SIXTEENTH = TPB // 4             # 120
SEED = 262
HZ_SEED = SEED + 1
SECTION_BARS = 4
SECTION_TICKS = SECTION_BARS * BAR   # 7680

ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

# ---------------- form + harmony --------------------------------------------
# (section name, per-bar degrees, variation transform, soprano register)
# degree index = roman-1 (0=I, 1=ii, 2=iii, 3=IV, 4=V, 5=vi, 6=vii)
FORM = [
    ("A Theme",      [0, 5, 3, 4], "theme",      "I vi IV V", (60, 88)),
    ("B Retrograde", [4, 3, 5, 0], "retrograde", "V IV vi I", (60, 88)),
    ("C Transposed", [4, 0, 1, 4], "transpose",  "V I ii V",  (60, 88)),
    ("D Inversion",  [3, 1, 4, 0], "invert",     "IV ii V I", (60, 88)),
    ("E Diminution", [0, 3, 1, 4], "diminish",   "I IV ii V", (72, 88)),
    ("F Coda Augm",  [3, 4, 0, 0], "augment",    "IV V I I",  (60, 84)),
]
N_BARS = sum(SECTION_BARS for _ in FORM)         # 24
TOTAL_TICKS = N_BARS * BAR                        # 46080
CHORD_DEGREE_BY_BAR = [d for _, dg, _, _, _ in FORM for d in dg]

# ---------------- overtone staircase motif ----------------------------------
# natural harmonic series of G3 (55): partial n -> round(55 + 12*log2(n)).
# Differences between consecutive partials = the overtone staircase motif.
_PARTIALS = [round(55 + 12 * math.log2(n)) for n in range(1, 17)]
MOTIF = tuple(_PARTIALS[i + 1] - _PARTIALS[i] for i in range(len(_PARTIALS) - 1))
# rhythm DNA: partial n (n = i+2) -> odd partial quarter, even partial eighth
DUR_BASE = tuple(BEAT if i % 2 == 1 else EIGHTH for i in range(len(MOTIF)))


def transform_for(kind):
    if kind == "theme":
        return MOTIF, DUR_BASE, 72
    if kind == "retrograde":
        return MOTIF[::-1], DUR_BASE[::-1], 72
    if kind == "transpose":
        return MOTIF, DUR_BASE, 79            # up a perfect 5th
    if kind == "invert":
        return tuple(-i for i in MOTIF), DUR_BASE, 72
    if kind == "diminish":
        return MOTIF, tuple(d // 2 for d in DUR_BASE), 72
    if kind == "augment":
        return MOTIF, tuple(d * 2 for d in DUR_BASE), 72
    raise ValueError(kind)


def fold(p, lo=60, hi=88):
    while p > hi:
        p -= 12
    while p < lo:
        p += 12
    return p


def chord_triad_abs(degree):
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return [root, third, fifth]


def chord_pcs(degree):
    return set(p % 12 for p in chord_triad_abs(degree))


def quantize_to_chord_tone(raw_pitch, triad, lo, hi):
    candidates = set()
    for p in triad:
        for shift in (-24, -12, 0, 12, 24):
            cand = p + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        return fold(min(triad, key=lambda c: abs(c - raw_pitch)), lo, hi)
    return min(candidates, key=lambda c: abs(c - raw_pitch))


# ---------------- Phase 1: raw generative draft ------------------------------
rng = random.Random(SEED)


def raw_events():
    evs = []
    for s_idx, (sname, degrees, kind, rom, _reg) in enumerate(FORM):
        sec_start = s_idx * SECTION_TICKS
        ivs, durs, start = transform_for(kind)
        p = start
        k = 0
        t = 0.0
        while t < SECTION_TICKS:
            iv = ivs[k % len(ivs)]
            d = durs[k % len(durs)] + rng.randint(-40, 40)
            d = max(60, d)
            p = fold(p + iv)
            jitter = rng.randint(-30, 30)
            st = int(round(t + jitter))
            if st < 0:
                st = 0
            en = int(round(t + jitter + d))
            if en > SECTION_TICKS:
                en = SECTION_TICKS
            if en <= st:
                en = st + 60
            evs.append(MusicEvent(pitch=p, volume=80,
                                  start_tick=sec_start + st,
                                  end_tick=sec_start + en))
            t += d
            k += 1
    return evs


# ---------------- Phase 2: rules post-processing -----------------------------
def soprano_events():
    evs = []
    for s_idx, (sname, degrees, kind, rom, reg) in enumerate(FORM):
        lo, hi = reg
        sec_start = s_idx * SECTION_TICKS
        ivs, durs, start = transform_for(kind)
        p = start
        k = 0
        t = 0
        while t < SECTION_TICKS:
            iv = ivs[k % len(ivs)]
            d = max(SIXTEENTH, int(round(durs[k % len(durs)] / SIXTEENTH)) * SIXTEENTH)
            raw_p = fold(p + iv)
            bar_abs = (sec_start + t) // BAR
            deg = CHORD_DEGREE_BY_BAR[bar_abs]
            triad = chord_triad_abs(deg)
            qp = quantize_to_chord_tone(raw_p, triad, lo, hi)
            st = sec_start + t
            en = min(st + d, sec_start + SECTION_TICKS)
            evs.append(MusicEvent(pitch=qp, volume=90, start_tick=st, end_tick=en))
            p = raw_p
            t += d
            k += 1
    # dedup collided (start_tick, pitch) keeping longest duration
    best = {}
    for e in evs:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def smooth_line(tone_fn, lo, hi):
    """Nearest-octave voice-leading over the 24-bar degree sequence."""
    prev = None
    out = []
    for deg in CHORD_DEGREE_BY_BAR:
        base = tone_fn(deg)
        if prev is None:
            c = base
            while c < lo:
                c += 12
            while c > hi:
                c -= 12
        else:
            best = None
            for sh in (-12, 0, 12):
                c = base + sh
                if lo <= c <= hi:
                    dist = abs(c - prev)
                    if best is None or dist < best[1]:
                        best = (c, dist)
            c = best[0] if best else base
        out.append(c)
        prev = c
    return out


def block_events(tone_fn, lo, hi, volume):
    line = smooth_line(tone_fn, lo, hi)
    evs = []
    for bar_abs, pitch in enumerate(line):
        st = bar_abs * BAR
        evs.append(MusicEvent(pitch=pitch, volume=volume, start_tick=st,
                              end_tick=st + BAR))
    return evs


BASS_TONE = lambda d: chord_triad_abs(d)[0] - 12      # noqa: E731
TENOR_TONE = lambda d: chord_triad_abs(d)[1]           # noqa: E731
ALTO_TONE = lambda d: chord_triad_abs(d)[2]            # noqa: E731


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))     # zero-drift landmark
    return u


def fill(composer, evs_by_voice, voices):
    for vname, _, _ in voices:
        evs = evs_by_voice[vname]
        for s_idx, (sname, degrees, kind, rom, _reg) in enumerate(FORM):
            soff = s_idx * SECTION_TICKS
            seg = []
            for e in evs:
                if soff <= e.start_tick < soff + SECTION_TICKS:
                    st = e.start_tick - soff
                    en = e.end_tick - soff
                    if en > SECTION_TICKS:
                        en = SECTION_TICKS
                    if en <= st:
                        en = st + 1
                    seg.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                          start_tick=st, end_tick=en))
            seg.sort(key=lambda e: (e.start_tick, e.pitch))
            composer.fill_voice_section(vname, sname, unit_from(seg, SECTION_TICKS))


# ---------------- build + export --------------------------------------------
# Phase 1: single-voice raw draft
phase1_composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase1_composer.create_matrix(num_voices=1, num_sections=len(FORM))
phase1_composer.add_voice("RawDraft", program=FLUTE.midi_program, channel=0)
for sname, dg, kind, rom, _reg in FORM:
    phase1_composer.add_section(sname, bars=SECTION_BARS)
fill(phase1_composer, {"RawDraft": raw_events()},
     [("RawDraft", FLUTE.midi_program, 0)])
ok1, msg1 = phase1_composer.validate()
assert ok1, f"phase1 validate failed: {msg1}"
phase1_path = ROOT / "MIDI" / f"{NAME}-phase1.mid"
phase1_composer.to_midi(str(phase1_path))
write_provenance(
    str(phase1_path), "ai-generated", f"musicom {NAME}",
    sources=["generators/harmonics.py (overtone staircase, 12-TET)",
             "methods_db:023 Harmonic Series / Overtone Composition",
             f"style:{GENRE}", "phase:1-raw"],
    parameters={"phase": "1", "seed": SEED, "key": KEY_NAME, "bpm": BPM,
                "bars": N_BARS, "fundamental": 55, "variations": [f[2] for f in FORM],
                "note": "raw generative draft: unquantized chromatic overtone "
                        "staircase, off-grid onsets, single voice, no harmony"})
print("phase1 midi:", phase1_path, phase1_path.stat().st_size, "bytes")

# Phase 2: full SATB chorale, dual-version export
VOICES = [
    ("Soprano", FLUTE.midi_program, 0),
    ("Alto", STRING_ENSEMBLE.midi_program, 1),
    ("Tenor", CELLO.midi_program, 2),
    ("Bass", DOUBLE_BASS.midi_program, 3),
]
EVENTS = {
    "Soprano": soprano_events(),
    "Alto": block_events(ALTO_TONE, 55, 79, 72),
    "Tenor": block_events(TENOR_TONE, 48, 72, 72),
    "Bass": block_events(BASS_TONE, 36, 60, 84),
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, dg, kind, rom, _reg in FORM:
    composer.add_section(sname, bars=SECTION_BARS)
fill(composer, EVENTS, VOICES)

hz_instruments = {
    "Soprano": FLUTE.humanize_dna,
    "Alto": STRING_ENSEMBLE.humanize_dna,
    "Tenor": CELLO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)

for path, phase, note in (
        (perfect_path, "perfect", "grid-locked, no jitter"),
        (humanized_path, "humanized", "style+instrument humanized")):
    write_provenance(
        str(path), "ai-generated", f"musicom {NAME}",
        sources=["methods_db:023 Harmonic Series / Overtone Composition",
                 "rules/progression.py (Scale7ChordDegree.get_diatonic_note)",
                 f"style:{GENRE}", "phase:2-rules", f"humanize_seed:{HZ_SEED}"],
        parameters={"phase": phase, "seed": SEED, "key": KEY_NAME, "bpm": BPM,
                    "bars": N_BARS, "humanize": hz, "note": note,
                    "method": METHOD, "layer": LAYER, "paradigm": PARADIGM,
                    "variations": [f[2] for f in FORM],
                    "redesign": "rebuild of 067-harmonic-chorale (audit fail: missing index.html)"})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---------------- grid viz + summary -----------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:  # noqa: BLE001
    print("grid viz skipped:", exc)

raw = raw_events()
raw_offgrid = sum(1 for e in raw if not (e.start_tick % 120 == 0 or e.start_tick % 240 == 0))
raw_scale_viol = sum(1 for e in raw if (e.pitch % 12) not in SCALE_PCS)

summary = {
    "project": NAME, "genre": GENRE, "method": METHOD, "layer": LAYER,
    "paradigm": PARADIGM, "key": KEY_NAME, "bpm": BPM, "bars": N_BARS,
    "sections": [f[0] for f in FORM], "total_ticks": TOTAL_TICKS,
    "tonic": TONIC, "scale_pcs": sorted(SCALE_PCS),
    "chord_degree_by_bar": CHORD_DEGREE_BY_BAR,
    "variations": {f[0]: f[2] for f in FORM},
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": HZ_SEED, "composition_seed": SEED,
    "humanize_profiles": hz,
    "raw_events": len(raw), "raw_offgrid": raw_offgrid,
    "raw_scale_violations": raw_scale_viol,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("DONE compose")
print("raw events:", len(raw), "off-grid:", raw_offgrid,
      "scale viol:", raw_scale_viol)
print("soprano notes:", len(EVENTS["Soprano"]),
      "alto:", len(EVENTS["Alto"]), "tenor:", len(EVENTS["Tenor"]),
      "bass:", len(EVENTS["Bass"]))
print("humanize per-voice:", {k: (v["mean_abs_shift_ticks"], v["max_abs_shift_ticks"])
                              for k, v in hz.items()})
