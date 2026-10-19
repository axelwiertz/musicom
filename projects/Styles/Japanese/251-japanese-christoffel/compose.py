# -*- coding: utf-8 -*-
"""251 — Japanese Christoffel Word (rondo A-B-A-C-A, 20 bars).

Autonomous nightly composition job (2026-10-18). Genre: Japanese (koto /
shakuhachi / shamisen / taiko). Method: 069 Christoffel Word Combinatorial
Composition (CWCC) — concrete, Rules-Based.

Christoffel words are balanced binary words; here the method drives three
musical dimensions:
  * SCALE (height)  : step word C(3,2) = "aabab" over {whole-step=2, minor-3rd=3}
                      -> step pattern (2,2,3,2,3) -> E yo/major pentatonic
                      {4,6,8,11,1} = E F# G# B C#.
  * RHYTHM (time)   : Euclidean rhythms ARE Christoffel words over {onset,rest}.
                      Koto = E(5,8) ("aab aab ab"), shamisen = E(3,8) tresillo.
  * FORM (Sturmian) : the rondo A-B-A-C-A recurrence mirrors the Fibonacci/Sturmian
                      morphism A -> AB (A self-repeats as a recurrent block).
  * HARMONY (duality): the dual word C(2,3) ("babaa", a<->b swap) folds the home
                      sonority into its "dark twin" subsets that schedule the
                      episode (B/C) chords — all still subsets of the home scale.

Two-phase architecture:
  Phase 1 (raw): single koto voice, stochastic walk over the E-pentatonic pc
    pool, off-grid micro-timing, NO harmony -> *-phase1.mid
  Phase 2 (rules): Christoffel step-word contour mapped to per-bar chord-tone
    subsets (HOME E / LIFT C#m / TURN B / TENSE F#sus2), 8th-grid snapped,
    chord-tone quantized, then dual-version export (perfect grid-locked +
    seeded humanized).

Key: E yo pentatonic {4,6,8,11,1}. Tempo 88 BPM, 4/4, 480 TPB, BAR=1920.
"""
import json
import os
import random
import sys

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import KOTO, SHAKUCHACHI, SHAMISEN, TAIKO  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 251
STYLE = "japanese"
METHOD_ID = "069"
METHOD_NAME = "Christoffel Word Combinatorial Composition (CWCC)"
METHOD_LAYER = "concrete"
FORM_NAME = "rondo (A-B-A-C-A)"
KEY_NAME = "E yo pentatonic (major pentatonic)"
ROOT_PC = 4                     # E
BPM = 88
TPB = 480
BPB = 4
BAR = TPB * BPB                 # 1920
EIGHTH = 240
SIXTEENTH = 120
QUARTER = 480


# ---- Christoffel word (method core) ----------------------------------------
def christoffel(p, q):
    """Lower Christoffel word, p 'a'(=0) and q 'b'(=1), length p+q.

    word[i] = 1 iff floor((i+1)*q/n) - floor(i*q/n) == 1 (the classic
    Cayley / step-function construction). C(5,2) -> "aaabaab" (Lydian).
    """
    n = p + q
    return [1 if ((i + 1) * q // n - i * q // n) == 1 else 0 for i in range(n)]


def euclid_mask(k, n):
    """Euclidean rhythm (k onsets in n pulses) as a Christoffel word over
    {onset, rest}: onsets sit on the 'a' positions of C(k, n-k)."""
    w = christoffel(k, n - k)
    return [1 if s == 0 else 0 for s in w]


# scale from the step word C(3,2) = aabab  (a=2 semitones, b=3 semitones)
SCALE_STEP_WORD = christoffel(3, 2)                      # [0,0,1,0,1]
SCALE_STEPS = [2 if s == 0 else 3 for s in SCALE_STEP_WORD]   # [2,2,3,2,3]
_pcs = []
_cur = ROOT_PC
for _st in SCALE_STEPS:
    _pcs.append(_cur)
    _cur = (_cur + _st) % 12
KEY_PCS = set(_pcs)                                      # {4,6,8,11,1}
PCS_SORTED = sorted(KEY_PCS)                             # [1,4,6,8,11]

# rhythm masks (Christoffel/Euclidean)
MASK_KOTO = euclid_mask(5, 8)      # 5 onsets / 8 eighth-slots
MASK_SHAMI = euclid_mask(3, 8)     # tresillo (3 / 8)
KOTO_SLOTS = [i for i in range(8) if MASK_KOTO[i]]
SHAMI_SLOTS = [i for i in range(8) if MASK_SHAMI[i]]

# ---- Form (rondo, uniquified for the engine) -------------------------------
# form_to_sections("rondo") -> ["A","B","A","C","A"] x4 bars; rename duplicates.
SECTIONS = [("A1", 4), ("B", 4), ("A2", 4), ("C", 4), ("A3", 4)]
TOTAL_BARS = sum(b for _, b in SECTIONS)          # 20
TOTAL_TICKS = TOTAL_BARS * BAR                    # 38400

SECTION_START_BARS = []
_acc = 0
for _n, _b in SECTIONS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def section_of_bar(bar):
    sec = 0
    for s in range(len(SECTIONS)):
        if bar >= SECTION_START_BARS[s]:
            sec = s
    return sec


def section_ticks(s):
    return SECTIONS[s][1] * BAR


# ---- Harmony: per-bar chord-tone subsets (Christoffel duality schedule) -----
SUBSETS = {
    "E":      {"roman": "I",    "name": "E major",       "pcs": {4, 8, 11}},
    "C#m":    {"roman": "vi",   "name": "C# minor",      "pcs": {1, 4, 6}},
    "B":      {"roman": "V",    "name": "B sus",         "pcs": {11, 1, 4}},
    "F#sus2": {"roman": "ii",   "name": "F# sus2 (tense)", "pcs": {6, 8, 11}},
}
CHORD_TONES = []
CHORD_PATH = []
for bar in range(TOTAL_BARS):
    sec = section_of_bar(bar)
    pos = bar - SECTION_START_BARS[sec]
    if sec in (0, 2, 4):        # A1 / A2 / A3 rondo theme -> HOME
        key = "E"
    elif sec == 1:              # B -> LIFT then TURN
        key = "C#m" if pos < 2 else "B"
    else:                       # C -> TENSE then TURN
        key = "F#sus2" if pos < 2 else "B"
    CHORD_TONES.append(sorted(SUBSETS[key]["pcs"]))
    CHORD_PATH.append({"bar": bar, "section": SECTIONS[sec][0],
                       "roman": SUBSETS[key]["roman"],
                       "name": SUBSETS[key]["name"],
                       "pcs": sorted(SUBSETS[key]["pcs"])})


# ---- Helpers ----------------------------------------------------------------
def dedup(events):
    d, order = {}, []
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in d:
            d[key] = e
            order.append(key)
        elif (e.end_tick - e.start_tick) > (d[key].end_tick - d[key].start_tick):
            d[key] = e
    return [d[k] for k in order]


def split_abs_to_section(abs_events, s):
    start = SECTION_START_BARS[s] * BAR
    length = section_ticks(s)
    end = start + length
    cell = []
    for e in sorted(abs_events, key=lambda e: (e.start_tick, e.pitch)):
        if e.start_tick < start or e.start_tick >= end:
            continue
        st = e.start_tick - start
        et = min(length, e.end_tick - start)
        if et <= st:
            continue
        cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                               start_tick=st, end_tick=et))
    if not cell or cell[-1].end_tick < length:
        last = cell[-1].end_tick if cell else 0
        cell.append(MusicEvent(pitch=0, volume=0, start_tick=last, end_tick=length))
    cell.append(MusicEvent(pitch=0, volume=0, start_tick=length, end_tick=length))
    return MusicUnit(events=cell)


def pc_to_note(pc, center):
    return center + ((pc - (center % 12)) % 12)


# ---- Phase-1 raw draft (single voice, off-grid random walk) -----------------
def build_raw_events():
    rng = random.Random(SEED)
    out = []
    n_events = TOTAL_BARS * 6
    for i in range(n_events):
        pc = PCS_SORTED[rng.randrange(len(PCS_SORTED))]
        note = pc_to_note(pc, 76)
        st = int(i * (TOTAL_TICKS / float(n_events))) + rng.randint(-100, 100)
        st = max(0, min(TOTAL_TICKS - 40, st))
        dur = 70 + rng.randint(0, 160)
        vel = 50 + rng.randint(0, 55)
        out.append(MusicEvent(pitch=note, volume=vel, start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
KOTO_CENTER = 76     # E5
SHAKU_CENTER = 64    # E4
SHAMI_CENTER = 52    # E3


def koto_contour(bar):
    # Christoffel step-word contour (a=up,b=down) mapped onto chord-tone idx
    up = [0, 1, 2, 1, 2]
    down = [2, 1, 0, 1, 2]
    return down if bar % 2 == 1 else up


def build_koto():
    ev = []
    for bar in range(TOTAL_BARS):
        tones = sorted(CHORD_TONES[bar])
        sec = section_of_bar(bar)
        base = bar * BAR
        center = KOTO_CENTER + (12 if sec == 3 else 0)   # octave up at climax
        contour = koto_contour(bar)
        for k, slot in enumerate(KOTO_SLOTS):
            cti = contour[k % len(contour)]
            pc = tones[cti % len(tones)]
            st = base + slot * EIGHTH
            ev.append(MusicEvent(pitch=pc_to_note(pc, center), volume=88,
                                 start_tick=st, end_tick=st + 230))
    return dedup(ev)


def build_shakuhachi():
    ev = []
    for bar in range(TOTAL_BARS):
        tones = sorted(CHORD_TONES[bar])
        base = bar * BAR
        root = pc_to_note(tones[0], SHAKU_CENTER)
        ev.append(MusicEvent(pitch=root, volume=70, start_tick=base,
                             end_tick=base + 1560))
        upper = pc_to_note(tones[1] if len(tones) > 1 else tones[0], SHAKU_CENTER)
        ev.append(MusicEvent(pitch=upper, volume=62, start_tick=base + 960,
                             end_tick=base + 1560))
    return dedup(ev)


def build_shamisen():
    ev = []
    for bar in range(TOTAL_BARS):
        tones = sorted(CHORD_TONES[bar])
        base = bar * BAR
        for k, slot in enumerate(SHAMI_SLOTS):
            pc = tones[(k + bar) % len(tones)]
            st = base + slot * EIGHTH
            ev.append(MusicEvent(pitch=pc_to_note(pc, SHAMI_CENTER), volume=74,
                                 start_tick=st, end_tick=st + 200))
    return dedup(ev)


def build_taiko():
    ev = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        ev.append(MusicEvent(pitch=60, volume=100, start_tick=base,
                             end_tick=base + 100))
        ev.append(MusicEvent(pitch=60, volume=86, start_tick=base + 960,
                             end_tick=base + 1060))
        if sec == 3:      # C climax: 8th-note taiko interlock
            for i in range(8):
                ev.append(MusicEvent(pitch=62 if i % 2 == 0 else 60, volume=58,
                                     start_tick=base + i * EIGHTH,
                                     end_tick=base + i * EIGHTH + 70))
    return dedup(ev)


VOICES = ["Koto", "Shakuhachi", "Shamisen", "Taiko"]
VOICE_PROGRAMS = [KOTO.midi_program, SHAKUCHACHI.midi_program,
                  SHAMISEN.midi_program, TAIKO.midi_program]
VOICE_CHANNELS = [0, 1, 2, 3]
PITCHED_VOICES = ["Koto", "Shakuhachi", "Shamisen"]


def audit_voice(name, events, pitched):
    onsets = [e.start_tick for e in events if e.pitch != 0]
    off16 = sum(1 for o in onsets if o % SIXTEENTH != 0)
    off8 = sum(1 for o in onsets if o % EIGHTH != 0)
    out_scale = 0
    out_chord = 0
    if pitched:
        for e in events:
            if e.pitch == 0:
                continue
            pc = e.pitch % 12
            bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
            cpc = set(CHORD_TONES[bar])
            if pc not in KEY_PCS:
                out_scale += 1
            if pc not in cpc:
                out_chord += 1
    return {"name": name, "n_notes": len(onsets), "off16": off16,
            "off8": off8, "out_scale": out_scale, "out_chord": out_chord}


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "251-japanese-christoffel"
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
PERFECT_PATH = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
HUMANIZED_PATH = os.path.join(MIDI_DIR, BASE + "-humanized.mid")


def compose():
    # ---- Phase 1 ------------------------------------------------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawKoto", program=KOTO.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawKoto", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2 ------------------------------------------------------------
    koto = build_koto()
    shaku = build_shakuhachi()
    shami = build_shamisen()
    taiko = build_taiko()
    voice_events = {"Koto": koto, "Shakuhachi": shaku,
                    "Shamisen": shami, "Taiko": taiko}

    inline_audit = {v: audit_voice(v, voice_events[v], v in PITCHED_VOICES)
                    for v in VOICES}

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for name, bars in SECTIONS:
        composer.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        for vname in VOICES:
            composer.fill_voice_section(vname, name,
                                        split_abs_to_section(voice_events[vname], s))

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICES, bpm=BPM,
                             mode="E yo pentatonic (Christoffel step word C(3,2))")

    # ---- dual-version export: perfect + humanized ---------------------------
    from workflows.humanize import export_dual
    hz_instruments = {
        "Koto": KOTO.humanize_dna,
        "Shakuhachi": SHAKUCHACHI.humanize_dna,
        "Shamisen": SHAMISEN.humanize_dna,
        "Taiko": TAIKO.humanize_dna,
    }
    hz = export_dual(composer, PERFECT_PATH, HUMANIZED_PATH,
                     style=STYLE, seed=SEED, bpm=BPM, instruments=hz_instruments)

    summary = {
        "project": BASE,
        "project_number": 251,
        "style": STYLE,
        "method_id": METHOD_ID,
        "method_name": METHOD_NAME,
        "method_layer": METHOD_LAYER,
        "form": FORM_NAME,
        "key": KEY_NAME,
        "root_pc": ROOT_PC,
        "key_pcs": sorted(KEY_PCS),
        "scale_step_word": SCALE_STEP_WORD,
        "scale_steps": SCALE_STEPS,
        "koto_rhythm_mask": MASK_KOTO,
        "shamisen_rhythm_mask": MASK_SHAMI,
        "bpm": BPM,
        "ticks_per_beat": TPB,
        "beats_per_bar": BPB,
        "bar_ticks": BAR,
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS,
        "total_ticks": TOTAL_TICKS,
        "seed": SEED,
        "chord_path": CHORD_PATH,
        "voices": [{"name": n, "program": p, "channel": c,
                    "pitched": n in PITCHED_VOICES}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "inline_audit": inline_audit,
        "humanize": {k: {"seed": v["seed"],
                         "profile": v["profile"],
                         "n_notes": v["n_notes"],
                         "mean_abs_shift_ticks": v["mean_abs_shift_ticks"],
                         "max_abs_shift_ticks": v["max_abs_shift_ticks"],
                         "mean_abs_vel_delta": v["mean_abs_vel_delta"],
                         "timing_sigma_ticks": v["timing_sigma_ticks"]}
                     for k, v in hz.items()},
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, inline_audit, len(raw), hz, summary


if __name__ == "__main__":
    composer, ok1, inline_audit, n_raw, hz, summary = compose()

    size1 = os.path.getsize(PHASE1_PATH)
    size_p = os.path.getsize(PERFECT_PATH)
    size_h = os.path.getsize(HUMANIZED_PATH)
    assert size1 > 40 and size_p > 40 and size_h > 40

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes) zero-drift={ok1}")
    print(f"[OK] Perfect MIDI:  {PERFECT_PATH} ({size_p} bytes)")
    print(f"[OK] Humanized MIDI: {HUMANIZED_PATH} ({size_h} bytes)")
    print(f"[OK] Bars {TOTAL_BARS}, sections {len(SECTIONS)}, raw events {n_raw}")
    print("[OK] Scale step word C(3,2) =", SCALE_STEP_WORD, "-> steps", SCALE_STEPS)
    print("[OK] Koto mask (5/8):", MASK_KOTO, " Shamisen mask (3/8):", MASK_SHAMI)
    print("[OK] Inline grid/harmony audit (pre-humanize):")
    for vname, a in inline_audit.items():
        print(f"     {vname:10s} notes={a['n_notes']:4d} off16={a['off16']} "
              f"off8={a['off8']} out_scale={a['out_scale']} out_chord={a['out_chord']}")
    print("[OK] Humanization (per voice):")
    for vname, h in hz.items():
        print(f"     {vname:10s} seed={h['seed']} mean_shift={h['mean_abs_shift_ticks']:.1f}t "
              f"max={h['max_abs_shift_ticks']}t vel_delta={h['mean_abs_vel_delta']:.1f}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="Japanese Christoffel word - PRE-RULES raw draft "
                  "(E-pentatonic random walk)",
        parameters={"phase": 1, "key": KEY_NAME, "bpm": BPM, "seed": SEED,
                    "style": STYLE, "method": METHOD_ID,
                    "total_bars": TOTAL_BARS, "sections": len(SECTIONS)},
        notes="Phase 1 raw: single koto voice, stochastic walk over the "
              "E-yo-pentatonic pc pool, off-grid micro-timing, NO harmony.")
    write_provenance(
        PERFECT_PATH, classification=AI_ASSISTED,
        generator="Japanese Christoffel word (069 CWCC) + musicom rules",
        parameters={"phase": 2, "version": "perfect", "key": KEY_NAME,
                    "bpm": BPM, "seed": SEED, "style": STYLE,
                    "method": METHOD_ID, "total_bars": TOTAL_BARS,
                    "sections": len(SECTIONS), "voices": VOICES},
        notes="Phase 2 perfect: grid-locked concrete layer (no humanization). "
              "Christoffel step word -> E-pentatonic; Euclidean/Christoffel "
              "rhythms; chord-tone quantized, 8th-grid snapped, zero-drift gated.")
    write_provenance(
        HUMANIZED_PATH, classification=AI_ASSISTED,
        generator="Japanese Christoffel word (069 CWCC) + musicom rules",
        parameters={"phase": 2, "version": "humanized", "key": KEY_NAME,
                    "bpm": BPM, "seed": SEED, "style": STYLE,
                    "method": METHOD_ID, "total_bars": TOTAL_BARS,
                    "sections": len(SECTIONS), "voices": VOICES,
                    "humanize_seed": SEED},
        notes="Phase 2 humanized: same concrete layer + style-derived seeded "
              "humanization (per-instrument DNA). Zero-drift safe.")
    print("[OK] Provenance sidecars written (phase1 + perfect + humanized).")
