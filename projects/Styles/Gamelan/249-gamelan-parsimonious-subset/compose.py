# -*- coding: utf-8 -*-
"""249 — Gamelan Parsimonious Subset Sequence (head-solos-head, 32 bars).

Autonomous nightly composition job (2026-10-17). Genre: Gamelan (Javanese,
slendro-like pentatonic). Method: ABS-104 "Parsimonious Subset Sequence
Composition" (PSSC) — abstract layer.

Two-phase architecture:
  Phase 1 (raw): single metallic voice, stochastic random walk over the
    D-pentatonic pitch-class pool, unquantized pitch + off-grid micro-timing,
    NO harmony -> 249-gamelan-parsimonious-subset-phase1.mid
  Phase 2 (rules): the abstract layer walks a parsimonious (P/L/R-style,
    minimal voice-leading) sequence through subsets of the D-pentatonic scale
    (PatternNetwork.walk). The concrete layer realizes each subset into a
    4-voice gamelan texture (glockenspiel balungan / vibraphone gender
    interlock / marimba colotomic kenong / kendang kit), chord-tone quantized,
    16th-grid snapped, voice-leading checked, then dual-version export
    (perfect grid-locked + seeded humanized).

Key: D pentatonic (slendro-like) = {D E F# A B} = pcs {2,4,6,9,11}.
Tempo 108 BPM, 4/4, 480 TPB, BAR = 1920. 4 sections x 8 bars = 32 bars.
"""
import json
import os
import random
import sys

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

from rules.patterns import Pattern
from rules.subset_network import PatternNetwork

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    GLOCKENSPIEL, VIBRAPHONE, MARIMBA, DRUM_KIT,
)

# ---- Concept ----------------------------------------------------------------
SEED = 249
STYLE = "gamelan"
METHOD_ID = "ABS-104"
METHOD_NAME = "Parsimonious Subset Sequence Composition (PSSC)"
METHOD_LAYER = "abstract"
FORM_NAME = "head-solos-head"
KEY_NAME = "D pentatonic (slendro-like)"
KEY_PCS = {2, 4, 6, 9, 11}      # D E F# A B
BPM = 108
TPB = 480
BPB = 4
BAR = TPB * BPB                 # 1920
EIGHTH = 240
SIXTEENTH = 120
QUARTER = 480

# ---- Form -------------------------------------------------------------------
# NOTE: section names MUST be unique — fill_voice_section() resolves by name,
# so a literal "head-solos-head" (two "Head") would collide.
SECTIONS = [("Head", 8), ("Solo1", 8), ("Solo2", 8), ("HeadReprise", 8)]
TOTAL_BARS = sum(b for _, b in SECTIONS)          # 32
TOTAL_TICKS = TOTAL_BARS * BAR                    # 61440

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


def section_start_abs(s):
    return SECTION_START_BARS[s] * BAR


def section_ticks(s):
    return SECTIONS[s][1] * BAR


# ---- Abstract layer: parsimonious subset walk (ABS-104) ---------------------
PCS_SORTED = sorted(KEY_PCS)                       # [2, 4, 6, 9, 11]

from itertools import combinations  # noqa: E402


def build_subset_library():
    pats = []
    for k in (2, 3, 4, 5):
        for comb in combinations(PCS_SORTED, k):
            sid = f"p{k}_" + "".join(str(x) for x in comb)
            pats.append(Pattern(sid, frozenset(comb),
                                roles=("harmony",), tags=("pentatonic",)))
    return pats


HOME_ID = "p3_269"   # {D F# A} = D-major sonority inside the pentatonic


def tension_curve_32():
    """Per-bar tension target: Head low, Solo1 rise, Solo2 peak, Head resolve."""
    curve = []
    for b in range(TOTAL_BARS):
        sec = section_of_bar(b)
        pos = b - SECTION_START_BARS[sec]          # 0..7 within section
        t = pos / 7.0
        if sec == 0:                                # Head: home, gentle
            val = 1.2 + 0.6 * t
        elif sec == 1:                              # Solo1: rise
            val = 2.0 + 1.2 * t
        elif sec == 2:                              # Solo2: peak
            val = 3.2 + 1.6 * t
        else:                                       # Head recapitulation: resolve
            val = 3.0 - 2.0 * t
        curve.append(round(val, 3))
    return curve


def subset_walk():
    lib = build_subset_library()
    net = PatternNetwork(lib)
    rng = random.Random(SEED)
    curve = tension_curve_32()
    walk = net.walk(HOME_ID, TOTAL_BARS, rng=rng, tension_curve=curve,
                    home=HOME_ID)
    # map ids -> subsets + tension
    by_id = {p.id: p for p in lib}
    subsets = []
    walk_detail = []
    for i, pid in enumerate(walk):
        p = by_id[pid]
        sub = frozenset(p.subset)
        subsets.append(sub)
        walk_detail.append({"bar": i, "pattern": pid,
                            "subset": sorted(sub),
                            "tension": round(p.tension, 3),
                            "target": curve[i]})
    return subsets, walk_detail


SUBSETS, WALK_DETAIL = subset_walk()

# per-bar chord-tone pcs (for the harmony audit) == the walked subset
CHORD_TONES = [sorted(s) for s in SUBSETS]


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
    start = section_start_abs(s)
    length = section_ticks(s)
    end = start + length
    cell = []
    for e in sorted(abs_events, key=lambda e: (e.start_tick, e.pitch)):
        # A note belongs to the section that contains its START. This prevents
        # a note whose tail crosses a section seam from being cloned into both
        # neighbours (the old end/start-clamp condition did that).
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


def pc_to_note(pc, center, anchor_pc=2):
    """Pitch class pc -> MIDI note at/above `center`, anchored on D."""
    return center + ((pc - (center % 12)) % 12)


# ---- Phase-1 raw draft (single voice, off-grid random walk) -----------------
def build_raw_events():
    rng = random.Random(SEED)
    out = []
    n_events = TOTAL_BARS * 8
    for i in range(n_events):
        pc = PCS_SORTED[rng.randrange(len(PCS_SORTED))]
        note = pc_to_note(pc, 74)                    # vibraphone register
        st = int(i * (TOTAL_TICKS / float(n_events))) + rng.randint(-90, 90)
        st = max(0, min(TOTAL_TICKS - 40, st))
        dur = 80 + rng.randint(0, 160)
        vel = 55 + rng.randint(0, 55)
        out.append(MusicEvent(pitch=note, volume=vel,
                              start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
LEAD_CENTER = 86     # D6 (glockenspiel sweet 84-100)
ELAB_CENTER = 74     # D5 (vibraphone sweet 60-84)
BASS_CENTER = 50     # D3 (marimba low)


def build_balungan():
    ev = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        tones = CHORD_TONES[bar]
        base = bar * BAR
        if sec in (0, 3):                            # Head: quarter-note balungan
            for i in range(4):
                pc = tones[i % len(tones)]
                st = base + i * QUARTER
                ev.append(MusicEvent(pitch=pc_to_note(pc, LEAD_CENTER), volume=92,
                                     start_tick=st, end_tick=st + 420))
        else:                                        # Solo: 8th-note balungan
            for i in range(8):
                pc = tones[i % len(tones)]
                st = base + i * EIGHTH
                ev.append(MusicEvent(pitch=pc_to_note(pc, LEAD_CENTER), volume=92,
                                     start_tick=st, end_tick=st + 210))
    return dedup(ev)


def build_gender():
    ev = []
    for bar in range(TOTAL_BARS):
        tones = CHORD_TONES[bar]
        base = bar * BAR
        # interlocking 16th pattern: cycle subset tones, alternate octave
        for i in range(16):
            pc = tones[i % len(tones)]
            note = pc_to_note(pc, ELAB_CENTER)
            if i % 2 == 1:
                note -= 12                            # lower octave interlock
            st = base + i * SIXTEENTH
            ev.append(MusicEvent(pitch=note, volume=58,
                                 start_tick=st, end_tick=st + 100))
    return dedup(ev)


def build_kenong():
    ev = []
    for bar in range(TOTAL_BARS):
        tones = CHORD_TONES[bar]
        root_pc = min(tones)
        base = bar * BAR
        vel = 100 if bar in SECTION_START_BARS else 82
        # colotomic: gong/kenong strikes on the downbeat, rings through
        ev.append(MusicEvent(pitch=pc_to_note(root_pc, BASS_CENTER),
                             volume=vel, start_tick=base, end_tick=base + 1560))
        if bar % 2 == 1:                             # kempul on beat 3 of odd bars
            fifth = tones[(len(tones) // 2) % len(tones)]
            ev.append(MusicEvent(pitch=pc_to_note(fifth, BASS_CENTER),
                                 volume=70, start_tick=base + 1440,
                                 end_tick=base + 1440 + 960))
    return dedup(ev)


def build_kendang():
    ev = []
    kick = MidiPercussion.BASS_DRUM
    lowtom = 41          # low floor tom
    hitom = 48           # high-mid tom
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        ev.append(MusicEvent(pitch=kick, volume=95,
                             start_tick=base, end_tick=base + 120))
        ev.append(MusicEvent(pitch=lowtom, volume=72,
                             start_tick=base + 960, end_tick=base + 1080))
        if sec in (1, 2):                            # Solo: kendang 8th interlock
            for i in range(8):
                p = hitom if i % 2 == 0 else lowtom
                ev.append(MusicEvent(pitch=p, volume=52,
                                     start_tick=base + i * EIGHTH,
                                     end_tick=base + i * EIGHTH + 90))
    return dedup(ev)


VOICES = ["Balungan", "Gender", "Kenong", "Kendang"]
VOICE_PROGRAMS = [GLOCKENSPIEL.midi_program, VIBRAPHONE.midi_program,
                  MARIMBA.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 9]
PITCHED_VOICES = ["Balungan", "Gender", "Kenong"]


def audit_voice(name, events, pitched):
    onsets = [e.start_tick for e in events if e.pitch != 0]
    off_grid = sum(1 for o in onsets if (o % 120 != 0 and o % 240 != 0))
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
    return {"name": name, "n_notes": len(onsets), "off_grid": off_grid,
            "out_scale": out_scale, "out_chord": out_chord}


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "249-gamelan-parsimonious-subset"
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
PERFECT_PATH = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
HUMANIZED_PATH = os.path.join(MIDI_DIR, BASE + "-humanized.mid")


def compose():
    # ---- Phase 1 ------------------------------------------------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawLead", program=VIBRAPHONE.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawLead", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2 ------------------------------------------------------------
    balungan = build_balungan()
    gender = build_gender()
    kenong = build_kenong()
    kendang = build_kendang()
    voice_events = {"Balungan": balungan, "Gender": gender,
                    "Kenong": kenong, "Kendang": kendang}

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
                             mode="D pentatonic (gamelan, parsimonious subsets)")

    # ---- dual-version export: perfect (grid-locked) + humanized -------------
    from workflows.humanize import export_dual
    hz_instruments = {
        "Balungan": GLOCKENSPIEL.humanize_dna,
        "Gender": VIBRAPHONE.humanize_dna,
        "Kenong": MARIMBA.humanize_dna,
        "Kendang": DRUM_KIT.humanize_dna,
    }
    hz = export_dual(composer, PERFECT_PATH, HUMANIZED_PATH,
                     style=STYLE, seed=SEED, bpm=BPM, instruments=hz_instruments)

    summary = {
        "project": BASE,
        "project_number": 249,
        "style": STYLE,
        "method_id": METHOD_ID,
        "method_name": METHOD_NAME,
        "method_layer": METHOD_LAYER,
        "form": FORM_NAME,
        "key": KEY_NAME,
        "key_pcs": sorted(KEY_PCS),
        "bpm": BPM,
        "ticks_per_beat": TPB,
        "beats_per_bar": BPB,
        "bar_ticks": BAR,
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS,
        "total_ticks": TOTAL_TICKS,
        "seed": SEED,
        "subset_walk": WALK_DETAIL,
        "voices": [{"name": n, "program": p, "channel": c,
                    "pitched": n in PITCHED_VOICES}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "inline_audit": inline_audit,
        "humanize": {k: {"seed": v["seed"],
                         "profile": v["profile"],
                         "n_notes": v["n_notes"],
                         "mean_abs_shift_ticks": v["mean_abs_shift_ticks"],
                         "max_abs_shift_ticks": v["max_abs_shift_ticks"],
                         "mean_abs_vel_delta": v["mean_abs_vel_delta"]}
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
    print("[OK] Subset walk (bar: pattern subset tension):")
    for w in WALK_DETAIL:
        print(f"     {w['bar']:2d} {w['pattern']:8s} {w['subset']} "
              f"tension={w['tension']} target={w['target']}")
    print("[OK] Inline grid/harmony audit (pre-humanize):")
    for vname, a in inline_audit.items():
        print(f"     {vname:9s} notes={a['n_notes']:4d} off_grid={a['off_grid']} "
              f"out_scale={a['out_scale']} out_chord={a['out_chord']}")
    print("[OK] Humanization (per voice):")
    for vname, h in hz.items():
        print(f"     {vname:9s} seed={h['seed']} mean_shift={h['mean_abs_shift_ticks']:.1f}t "
              f"max={h['max_abs_shift_ticks']}t vel_delta={h['mean_abs_vel_delta']:.1f}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="Gamelan parsimonious subsets - PRE-RULES raw draft "
                  "(D-pentatonic random walk)",
        parameters={"phase": 1, "key": KEY_NAME, "bpm": BPM, "seed": SEED,
                    "style": STYLE, "method": METHOD_ID,
                    "total_bars": TOTAL_BARS, "sections": len(SECTIONS)},
        notes="Phase 1 raw: single vibraphone voice, stochastic walk over the "
              "D-pentatonic pc pool, unquantized pitch + off-grid micro-timing, "
              "NO harmony, off-grid by design.")
    write_provenance(
        PERFECT_PATH, classification=AI_ASSISTED,
        generator="Gamelan parsimonious subset sequence (ABS-104) + musicom rules",
        parameters={"phase": 2, "version": "perfect", "key": KEY_NAME,
                    "bpm": BPM, "seed": SEED, "style": STYLE,
                    "method": METHOD_ID, "total_bars": TOTAL_BARS,
                    "sections": len(SECTIONS), "voices": VOICES},
        notes="Phase 2 perfect: grid-locked concrete layer (no humanization). "
              "Abstract parsimonious subset walk -> 4-voice gamelan texture, "
              "chord-tone quantized, 16th-grid snapped, zero-drift gated.")
    write_provenance(
        HUMANIZED_PATH, classification=AI_ASSISTED,
        generator="Gamelan parsimonious subset sequence (ABS-104) + musicom rules",
        parameters={"phase": 2, "version": "humanized", "key": KEY_NAME,
                    "bpm": BPM, "seed": SEED, "style": STYLE,
                    "method": METHOD_ID, "total_bars": TOTAL_BARS,
                    "sections": len(SECTIONS), "voices": VOICES,
                    "humanize_seed": SEED},
        notes="Phase 2 humanized: same concrete layer + style-derived seeded "
              "humanization (per-instrument DNA). Zero-drift safe.")
    print("[OK] Provenance sidecars written (phase1 + perfect + humanized).")
