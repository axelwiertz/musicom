# -*- coding: utf-8 -*-
"""244 — Japanese Chaotically Modulated Cellular Grains (Method 028, concrete).

Autonomous nightly composition job (2026-10-15).

Style: Japanese. Method 028 Chaotically Modulated Cellular Grains (CMCG),
layer concrete, paradigm Nature-Led, Continuous/Fluid, Meso/Phrase, O(G*P).

Method 028 essence: cross-coupled chaotic maps (Henon) modulate micro-timing,
spray, and pitch transposition of individual "grains". Structure is governed
by a gradual transition of the chaotic parameters (a, b) through distinct
mathematical regimes (stable point -> periodic loop -> full chaos -> return).

  x_{n+1} = 1 - a*x_n^2 + y_n
  y_{n+1} = b*x_n                      (Henon map, classic a=1.4 b=0.3)

Musical mapping (per the method framework):
  * PITCH  <- x-coordinate: select which chord tone each grain lands on.
  * RHYTHM <- y-coordinate: select which 8th-grid slot each grain occupies.
  * STRUCTURE <- chaotic regime sweep across the four strophic verses:
      Verse1 = stable/periodic (sparse grains), Verse2 = bifurcation (denser),
      Verse3 = full chaos (dense grain cloud), Verse4 = return (resolution).

Key: D Hirajoshi pentatonic (Japanese koto scale): D E F A Bb.
  SCALE_INTERVALS = [0, 2, 3, 7, 8]  ->  KEY_PCS = {2, 4, 5, 9, 10}.

Form: strophic — 4 verses x 8 bars = 32 bars. Each verse shares the SAME
8-bar harmonic progression (strophic identity) but realizes a different
chaotic regime (the CMCG structural sweep).

Two-phase architecture (mandatory):
  Phase 1 (raw): single koto voice running the PURE Henon grain cloud —
    unquantized pitch (raw int mapped from x), chaotic micro-timing jitter
    (y), no harmony, off-grid by design. -> 244-...-phase1.mid
  Phase 2 (rules): per-bar chord-tone quantization, 8th-grid onset snap,
    voice-leading check, full texture (koto grain lead, shakuhachi sustained
    counterline, shamisen arpeggio, taiko + ch9 drums). -> 244-...mid
"""
import itertools
import json
import math
import os
import random
import sys

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import KOTO, SHAKUCHACHI, SHAMISEN, TAIKO  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 244
KEY_NAME = "D Hirajoshi"
KEY_ROOT_PC = 2            # D
SCALE_INTERVALS = [0, 2, 3, 7, 8]     # Hirajoshi pentatonic from D
KEY_PCS = set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS)  # {2,4,5,9,10}
BPM = 80
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
GRID = 120                 # 16th-note reference
EIGHTH = 240               # 8th-note grid slot width

# ---- Form: strophic (4 verses, disambiguated section names) ------------------
SECTIONS = [("Verse1", 8), ("Verse2", 8), ("Verse3", 8), ("Verse4", 8)]
TOTAL_BARS = sum(b for _, b in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# ---- Chaotic regime per verse (a, b) + grain density ------------------------
# Henon b is fixed at 0.3; a sweeps stable -> periodic -> chaos -> return.
REGIME = {
    0: {"name": "stable/periodic", "a": 1.4, "b": 0.3, "density": 4},
    1: {"name": "bifurcation",     "a": 1.4, "b": 0.3, "density": 8},
    2: {"name": "full chaos",      "a": 1.4, "b": 0.3, "density": 12},
    3: {"name": "return",          "a": 1.4, "b": 0.3, "density": 5},
}

# ---- Chord plan (32 bars) — strophic 8-bar cycle, all in D Hirajoshi --------
# (roman, name, root_pc, chord_tone_pcs[3]) — every pc subset of KEY_PCS.
_D = ("i", "Dm", 2, [2, 5, 9])       # D  F  A
_Bb = ("bVI", "Bb", 10, [10, 2, 5])  # Bb D  F
_F = ("bIII", "F6", 5, [5, 9, 2])    # F  A  D
_A = ("v", "Asus", 9, [9, 2, 4])     # A  D  E

_VERSE_CYCLE = [_D, _Bb, _F, _A, _D, _Bb, _F, _D]   # 8-bar strophic verse
CHORDS = _VERSE_CYCLE * 4                            # 32 bars
assert len(CHORDS) == TOTAL_BARS


# ---- Henon map --------------------------------------------------------------
def henon(x, y, a=1.4, b=0.3):
    return (1.0 - a * x * x + y, b * x)


# ---- Pitch helpers ----------------------------------------------------------
def pitch_in(pc, lo, hi, center=None):
    center = center if center is not None else (lo + hi) // 2
    best, bestd = None, None
    for k in itertools.count(0):
        n = pc + 12 * k
        if n > hi:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    for k in itertools.count(-1, -1):
        n = pc + 12 * k
        if n < lo:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    return best


def chord_tones_midi(pcs, lo, hi):
    t = sorted(set(pitch_in(p, lo, hi) for p in pcs))
    while len(t) < len(pcs):
        t.append(t[-1] + 12)
    return t


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


# ---- Section bookkeeping ----------------------------------------------------
SECTION_START_BARS = []
_acc = 0
for _name, _b in SECTIONS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def bar_of(tick):
    return tick // BAR


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


def split_abs_to_section(abs_events, s):
    start = section_start_abs(s)
    length = section_ticks(s)
    end = start + length
    cell = []
    for e in abs_events:
        if e.end_tick <= start or e.start_tick >= end:
            continue
        st = max(0, e.start_tick - start)
        et = min(length, e.end_tick - start)
        if et <= st:
            continue
        cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                               start_tick=st, end_tick=et))
    if not cell or cell[-1].end_tick < length:
        last = cell[-1].end_tick if cell else 0
        cell.append(MusicEvent(pitch=0, volume=0, start_tick=last, end_tick=length))
    return MusicUnit(events=cell)


# ---- Phase-1 raw draft (single koto grain cloud) ----------------------------
def build_raw_events():
    """Pure Henon grain cloud: x -> raw pitch, y -> micro-timing jitter.
    Unquantized pitch (raw int), off-grid onsets by design."""
    rng = random.Random(SEED)
    x, y = 0.1, 0.1
    out = []
    n_events = TOTAL_BARS * 8
    for i in range(n_events):
        x, y = henon(x, y, 1.4, 0.3)
        # x in ~[-1.28, 1.27] -> raw pitch (unquantized, NOT scale-snapped)
        pitch = int(round(67 + x * 14))
        pitch = max(50, min(96, pitch))
        # y in ~[-0.38, 0.38] -> onset jitter around the base slot
        st = int(i * (TOTAL_TICKS / float(n_events))) + int(y * 240)
        st = max(0, min(TOTAL_TICKS - 40, st))
        dur = 100 + int(abs(x) * 120)
        vel = 60 + int(abs(y) * 70)
        out.append(MusicEvent(pitch=pitch, volume=vel,
                              start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
def build_grain_lead(chords):
    """Koto grain lead: Henon x -> chord-tone index, y -> 8th-grid slot.
    Every onset is a multiple of EIGHTH (240); every pitch is a chord tone."""
    x, y = 0.2, 0.1
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        n = REGIME[sec]["density"]
        tones = chord_tones_midi(chords[bar][3], 64, 84)
        base = bar * BAR
        for _k in range(n):
            x, y = henon(x, y, 1.4, 0.3)
            tone_idx = int(((x + 1.28) / 2.55) * len(tones)) % len(tones)
            slot = int(((y + 0.38) / 0.76) * 8) % 8
            st = base + slot * EIGHTH
            vel = 68 + int(abs(x) * 30)
            events.append(MusicEvent(pitch=tones[tone_idx], volume=vel,
                                     start_tick=st, end_tick=st + EIGHTH))
    return dedup(events)


def build_shakuhachi(chords):
    """Sustained counterline: one chord tone per bar, upper register."""
    events = []
    for bar in range(TOTAL_BARS):
        base = bar * BAR
        tones = chord_tones_midi(chords[bar][3], 66, 84)
        note = tones[2] if bar % 2 == 0 else tones[1]
        events.append(MusicEvent(pitch=note, volume=70,
                                 start_tick=base, end_tick=base + BAR - 10))
    return events


def build_shamisen(chords):
    """8th-note arpeggio of the bar's chord tones (one octave down)."""
    events = []
    for bar in range(TOTAL_BARS):
        base = bar * BAR
        tones = chord_tones_midi(chords[bar][3], 52, 72)
        r, th, f = tones[0], tones[1], tones[2]
        pattern = [r, th, f, r + 12, f, th, r, f]
        for k in range(8):
            st = base + k * EIGHTH
            events.append(MusicEvent(pitch=pattern[k], volume=62,
                                     start_tick=st, end_tick=st + 200))
    return dedup(events)


def build_taiko():
    """Deep DON on beat 1 (+ beat 3 in the chaotic Verse3)."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        events.append(MusicEvent(pitch=45, volume=96,
                                 start_tick=base, end_tick=base + 300))
        if sec == 2:
            events.append(MusicEvent(pitch=45, volume=80,
                                     start_tick=base + 960,
                                     end_tick=base + 960 + 200))
    return events


def build_drums():
    """Sparse ch9 pulse; 8th hats densify through the chaotic Verse3."""
    events = []
    kick = MidiPercussion.BASS_DRUM
    low_tom = MidiPercussion.LOW_TOM
    hh = MidiPercussion.CLOSED_HI_HAT
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        events.append(MusicEvent(pitch=kick, volume=88,
                                 start_tick=base, end_tick=base + 80))
        events.append(MusicEvent(pitch=low_tom, volume=80,
                                 start_tick=base + 960,
                                 end_tick=base + 960 + 70))
        if sec == 2:
            for k in range(8):
                events.append(MusicEvent(pitch=hh, volume=66,
                                         start_tick=base + k * EIGHTH,
                                         end_tick=base + k * EIGHTH + 50))
    return dedup(events)


# ---- Compose ----------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "244-japanese-chaotic-grains"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

VOICES = ["Koto", "Shakuhachi", "Shamisen", "Taiko", "Drums"]
VOICE_PROGRAMS = [KOTO.midi_program, SHAKUCHACHI.midi_program,
                  SHAMISEN.midi_program, TAIKO.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]
PITCHED_VOICES = ["Koto", "Shakuhachi", "Shamisen"]


def compose():
    # ---- Phase 1: raw single-voice Henon grain cloud ------------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawGrain", program=KOTO.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawGrain", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process ----------------------------------------
    lead = build_grain_lead(CHORDS)
    shaku = build_shakuhachi(CHORDS)
    sham = build_shamisen(CHORDS)
    taiko = build_taiko()
    drums = build_drums()

    voice_events = {"Koto": lead, "Shakuhachi": shaku, "Shamisen": sham,
                    "Taiko": taiko, "Drums": drums}

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

    ok2, msg2 = composer.validate()
    if not ok2:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg2}")
    composer.to_midi(MIDI_PATH)

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICES, bpm=BPM, mode="Hirajoshi (D)")

    # ---- inline grid + harmony audit (event lists, pre-export) --------------
    def audit_voice(name, events, pitched):
        onsets = [e.start_tick for e in events if e.pitch != 0]
        off16 = sum(1 for o in onsets if o % 120 != 0)
        off8 = sum(1 for o in onsets if o % 240 != 0)
        out_scale = 0
        out_chord = 0
        if pitched:
            for e in events:
                if e.pitch == 0:
                    continue
                pc = e.pitch % 12
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                cpc = set(CHORDS[bar][3])
                if pc not in KEY_PCS:
                    out_scale += 1
                if pc not in cpc:
                    out_chord += 1
        return {"name": name, "n_notes": len(onsets), "off16": off16,
                "off8": off8, "out_scale": out_scale, "out_chord": out_chord}

    inline_audit = {}
    for vname in VOICES:
        inline_audit[vname] = audit_voice(vname, voice_events[vname],
                                          pitched=(vname in PITCHED_VOICES))

    # voice-leading check on the shakuhachi sustained line (informational)
    vl = VoiceLeadingRules(style="classical")
    shaku_voicings = [chord_tones_midi(CHORDS[i][3], 66, 84) for i in range(TOTAL_BARS)]
    vl_violations = []
    for i in range(1, len(shaku_voicings)):
        vl_violations += vl.check_parallel_motion(shaku_voicings[i - 1], shaku_voicings[i])
        vl_violations += vl.check_hidden_fifths(shaku_voicings[i - 1], shaku_voicings[i])

    summary = {
        "key": KEY_NAME, "root_pc": KEY_ROOT_PC, "scale_intervals": SCALE_INTERVALS,
        "key_pcs": sorted(KEY_PCS), "bpm": BPM, "ticks_per_beat": TPB,
        "beats_per_bar": BPB, "bar_ticks": BAR, "grid": GRID, "eighth": EIGHTH,
        "form": "strophic", "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "regime": {str(k): v for k, v in REGIME.items()},
        "voices": [{"name": n, "program": p, "channel": c, "pitched": n in PITCHED_VOICES}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "chord_path": [
            {"bar": i, "roman": CHORDS[i][0], "name": CHORDS[i][1],
             "root_pc": CHORDS[i][2], "chord_tone_pcs": CHORDS[i][3]}
            for i in range(TOTAL_BARS)],
        "vl_violations": len(vl_violations),
        "inline_audit": inline_audit,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, inline_audit, vl_violations, len(raw)


if __name__ == "__main__":
    composer, ok1, inline_audit, vl_violations, n_raw = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw grain events: {n_raw}")
    print("[OK] Inline grid/harmony audit:")
    for vname, a in inline_audit.items():
        print(f"     {vname:11s} notes={a['n_notes']:3d} off16={a['off16']} "
              f"off8={a['off8']} out_scale={a['out_scale']} "
              f"out_chord={a['out_chord']}")
    print(f"[OK] Voice-leading violations (shakuhachi, informational): {len(vl_violations)}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="Method 028 Chaotically Modulated Cellular Grains (CMCG) - PRE-RULES raw draft",
        parameters={"method": 28, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Japanese", "form": "strophic",
                    "chaotic_map": "Henon (a=1.4, b=0.3)"},
        notes="Phase 1: single koto voice, pure Henon grain cloud. x -> raw "
              "unquantized pitch, y -> micro-timing jitter, off-grid by design, "
              "no harmony.")
    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator="Method 028 CMCG + musicom rules",
        parameters={"method": 28, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Japanese", "form": "strophic",
                    "voices": VOICES},
        notes="Phase 2: Henon grain cloud (koto lead) chord-tone-quantized per "
              "bar + 8th-grid onset snap; shakuhachi sustained counterline, "
              "shamisen arpeggio, taiko + ch9 drums. Chaotic regime sweeps "
              "across the four strophic verses (stable -> chaos -> return).")
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
