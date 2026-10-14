# -*- coding: utf-8 -*-
"""242 — Trap Phase (Method 026: Deconstructive Phase-Shift Minimalism).

Nightly composition job (2026-10-14). Style = Trap, form = cinematic-build
(Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars), key = D natural
minor (aeolian on D), 140 BPM.

Method 026 (concrete, Rules-Based): "Multiple identical looping voice streams
with dynamic phase offsets to create complex phasing and emergent rhythms."

Implementation (MIDI is discrete, so "phase shift" is expressed as):
  1. IDENTICAL LOOP — a one-bar 8-event motif (a 4-tone 7th-chord arpeggio
     contour) is the single melodic cell.
  2. DYNAMIC PHASE OFFSETS — up to four copies of the SAME loop play with
     bar-by-bar phase offsets (in 8th-note units); one voice drifts a full
     cycle over a section (Reich-style), Peak spreads 0/2/4/6, Resolve
     converges to unison.
  3. EMERGENT RHYTHM — the interference between offset copies produces the
     phasing texture (the point of the method), not new notes.
Every loop/bass/pad note is a chord tone of its own bar AND in D natural minor.

Two-phase architecture:
  Phase 1 (raw): single deconstructive loop — a theremin-style pitch sweep +
    jitter, unquantized onsets (off-grid by design), no harmony.
  Phase 2 (rules): grid-snap (8th = 240 ticks), per-bar chord-tone
    quantization, 4 phase-shifted loop voices (Rhodes), sub bass (Electric
    Bass), cinematic pad (Synth Pad), trap drum kit (ch9).

Engines: structures.*, workflows.unitmatrix_composer, visualization.grid,
workflows.provenance, rules.voice_leading (validation), instrument registry.
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
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import RHODES, ELECTRIC_BASS, SYNTH_PAD  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 242
KEY_NAME = "D minor"
KEY_ROOT_PC = 2            # D
KEY_ROOT_MIDI = 50         # D3
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]     # aeolian from D
KEY_PCS = set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS)
BPM = 140
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
GRID = 120                 # 16th-note reference
EIGHTH = 240               # phase loop slot width (8th note)

# ---- Form: cinematic-build (unique section names) ---------------------------
SECTIONS = [("Intro", 4), ("Build", 8), ("Rise", 8), ("Peak", 8), ("Resolve", 4)]
TOTAL_BARS = sum(b for _, b in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# ---- Chord plan (32 bars) — all diatonic 7th chords in D natural minor ------
# (roman, name, root_pc, chord_tone_pcs[4])
_DM7 = ("i", "Dm7", 2, [2, 5, 9, 0])
_BBM7 = ("VI", "Bbmaj7", 10, [10, 2, 5, 9])
_FM7 = ("III", "Fmaj7", 5, [5, 9, 0, 4])
_C7 = ("VII", "C7", 0, [0, 4, 7, 10])

CHORDS = [
    # Intro (0-3): tonic drone
    _DM7, _DM7, _DM7, _DM7,
    # Build (4-11): i VI i VI i VII i VII
    _DM7, _BBM7, _DM7, _BBM7, _DM7, _C7, _DM7, _C7,
    # Rise (12-19): VI III VI III VII VI VII III
    _BBM7, _FM7, _BBM7, _FM7, _C7, _BBM7, _C7, _FM7,
    # Peak (20-27): III VII i VI VII i VI VII
    _FM7, _C7, _DM7, _BBM7, _C7, _DM7, _BBM7, _C7,
    # Resolve (28-31): tonic
    _DM7, _DM7, _DM7, _DM7,
]
assert len(CHORDS) == TOTAL_BARS


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


def section_start_abs(s):
    return SECTION_START_BARS[s] * BAR


def section_ticks(s):
    return SECTIONS[s][1] * BAR


def section_of_bar(bar):
    sec = 0
    for s in range(len(SECTIONS)):
        if bar >= SECTION_START_BARS[s]:
            sec = s
    return sec


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


# ---- DPSM phase schedule ----------------------------------------------------
# One-bar loop = 8 events on the 8th-note grid. Phase offset (0..7) rotates the
# loop by whole 8th notes, so every onset stays a multiple of 240 ticks.
CONTOUR = [0, 1, 2, 3, 2, 1, 3, 0]


def phase_offset(voice_idx, bar):
    """Return phase offset (8th-note units) for loop voice idx (0..3) at bar,
    or None if that voice is inactive in the bar's section."""
    sec = section_of_bar(bar)
    if voice_idx == 0:
        return 0                       # Loop1 = reference phase, always on
    if sec == 0 or sec == 4:           # Intro / Resolve: single unison loop
        return None
    if sec == 1:                       # Build: Loop2 drifts a full phase cycle
        return (bar - 4) % 8 if voice_idx == 1 else None
    if sec == 2:                       # Rise: Loop2 frozen, Loop3 drifts
        if voice_idx == 1:
            return 4
        if voice_idx == 2:
            return (bar - 12) % 8
        return None
    if sec == 3:                       # Peak: static maximal spread
        return [0, 2, 4, 6][voice_idx]
    return None


# ---- Phase-1 raw draft (single deconstructive loop) -------------------------
def build_raw_events():
    rng = random.Random(SEED)
    out = []
    n_events = TOTAL_BARS * 8
    for i in range(n_events):
        frac = i / float(n_events)
        center = 62 + 12 * math.sin(2 * math.pi * frac)   # D4 <-> D5 sweep
        pitch = int(round(center + rng.uniform(-3.0, 3.0)))
        st = int(i * (TOTAL_TICKS / float(n_events))) + rng.randint(-60, 60)
        st = max(0, min(TOTAL_TICKS - 60, st))
        dur = rng.randint(60, 200)
        vel = rng.randint(60, 90)
        out.append(MusicEvent(pitch=pitch, volume=vel,
                              start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
def build_loops(chords):
    """Four identical loops with dynamic phase offsets (the DPSM core)."""
    out = {f"Loop{i + 1}": [] for i in range(4)}
    for bar, (roman, name, root, pcs) in enumerate(chords):
        base = bar * BAR
        tones = chord_tones_midi(pcs, 62, 86)
        for vi in range(4):
            off = phase_offset(vi, bar)
            if off is None:
                continue
            for k in range(8):
                slot = (k + off) % 8
                st = base + slot * EIGHTH
                pitch = tones[CONTOUR[k]]
                vel = 94 if slot == 0 else 80
                out[f"Loop{vi + 1}"].append(
                    MusicEvent(pitch=pitch, volume=vel,
                               start_tick=st, end_tick=st + EIGHTH))
    return out


def build_bass(chords):
    """Trap 808-style sub bass (Electric Bass) following the chord roots."""
    out = []
    for bar, (roman, name, root, pcs) in enumerate(chords):
        base = bar * BAR
        sec = section_of_bar(bar)
        r = pitch_in(root, 26, 38)
        fifth = pitch_in((root + 7) % 12, 26, 38)
        if sec == 0:
            continue                      # Intro: no bass (sparse)
        elif sec == 1:
            out.append(MusicEvent(pitch=r, volume=96, start_tick=base,
                                  end_tick=base + 480))
            out.append(MusicEvent(pitch=r, volume=88, start_tick=base + 960,
                                  end_tick=base + 1440))
        elif sec == 2:
            out.append(MusicEvent(pitch=r, volume=100, start_tick=base,
                                  end_tick=base + 480))
            out.append(MusicEvent(pitch=fifth, volume=92, start_tick=base + 960,
                                  end_tick=base + 1440))
        elif sec == 3:                    # Peak: driving 8th pulse
            for k in range(8):
                p = r if k % 2 == 0 else fifth
                out.append(MusicEvent(pitch=p, volume=100 if k == 0 else 88,
                                      start_tick=base + k * EIGHTH,
                                      end_tick=base + k * EIGHTH + 200))
        elif sec == 4:                    # Resolve: held tonic
            out.append(MusicEvent(pitch=r, volume=90, start_tick=base,
                                  end_tick=base + BAR))
    return dedup(out)


def build_pad(chords):
    """Cinematic swell pad (Synth Pad) — sustained 7th chords, section dynamics."""
    out = []
    vel = {0: 58, 1: 64, 2: 72, 3: 80, 4: 56}
    for bar, (roman, name, root, pcs) in enumerate(chords):
        base = bar * BAR
        sec = section_of_bar(bar)
        tones = chord_tones_midi(pcs, 50, 69)
        for p in tones:
            out.append(MusicEvent(pitch=p, volume=vel[sec],
                                  start_tick=base, end_tick=base + BAR))
    return dedup(out)


def build_drums():
    """Trap kit (ch9) — half-time kick/clap, hi-hat rolls, cinematic density."""
    out = []
    for s, (name, bars) in enumerate(SECTIONS):
        for b in range(bars):
            bar = SECTION_START_BARS[s] + b
            base = bar * BAR
            if s <= 1:                    # Intro/Build: 8th hats
                for k in range(8):
                    vel = 56 if k % 2 == 0 else 38
                    out.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT,
                                          volume=vel, start_tick=base + k * EIGHTH,
                                          end_tick=base + k * EIGHTH + 60))
            else:                         # Rise/Peak: 16th hat rolls
                for k in range(16):
                    vel = 50 if k % 2 == 0 else 32
                    if k % 4 == 2:
                        vel = 62
                    out.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT,
                                          volume=vel, start_tick=base + k * GRID,
                                          end_tick=base + k * GRID + 60))
            if s >= 1:                    # half-time kick (beats 1 & 3)
                out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                      start_tick=base, end_tick=base + 120))
                out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                      start_tick=base + 960, end_tick=base + 1080))
            if s >= 2:                    # trap clap backbeat on 3
                out.append(MusicEvent(pitch=MidiPercussion.HAND_CLAP, volume=88,
                                      start_tick=base + 960, end_tick=base + 1080))
            if s == 3:                    # Peak: snare roll into beat 4
                for k in (14, 15):
                    out.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE,
                                          volume=68, start_tick=base + k * GRID,
                                          end_tick=base + k * GRID + 60))
            if s == 4:                    # Resolve: sparse single kick
                out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=80,
                                      start_tick=base, end_tick=base + 120))
    return dedup(out)


# ---- Compose ----------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "242-trap-phase"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

VOICES = ["Loop1", "Loop2", "Loop3", "Loop4", "Bass", "Pad", "Drums"]
VOICE_PROGRAMS = [RHODES.midi_program, RHODES.midi_program, RHODES.midi_program,
                  RHODES.midi_program, ELECTRIC_BASS.midi_program,
                  SYNTH_PAD.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 4, 5, 9]


def compose():
    # ---- Phase 1: raw single-voice deconstructive loop ----------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawLoop", program=RHODES.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawLoop", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process ----------------------------------------
    loops = build_loops(CHORDS)
    bass = build_bass(CHORDS)
    pad = build_pad(CHORDS)
    drums = build_drums()

    voice_events = {"Loop1": loops["Loop1"], "Loop2": loops["Loop2"],
                    "Loop3": loops["Loop3"], "Loop4": loops["Loop4"],
                    "Bass": bass, "Pad": pad, "Drums": drums}

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
                             voice_names=VOICES, bpm=BPM, mode="Minor (D)")

    # ---- inline grid + harmony audit (event lists, pre-export) --------------
    def audit_voice(name, events):
        onsets = [e.start_tick for e in events if e.pitch != 0]
        off16 = sum(1 for o in onsets if o % 120 != 0)
        off8 = sum(1 for o in onsets if o % 240 != 0)
        out_scale = 0
        out_chord = 0
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
        if vname == "Drums":
            continue
        inline_audit[vname] = audit_voice(vname, voice_events[vname])

    # voice-leading check on the sustained pad chords (informational)
    vl = VoiceLeadingRules(style="classical")
    pad_voicings = [chord_tones_midi(c[3], 50, 69) for c in CHORDS]
    vl_violations = []
    for i in range(1, len(pad_voicings)):
        vl_violations += vl.check_parallel_motion(pad_voicings[i - 1], pad_voicings[i])
        vl_violations += vl.check_hidden_fifths(pad_voicings[i - 1], pad_voicings[i])

    phase_schedule = {}
    for vi in range(4):
        phase_schedule[f"Loop{vi + 1}"] = {
            SECTIONS[s][0]: (phase_offset(vi, SECTION_START_BARS[s])
                             if phase_offset(vi, SECTION_START_BARS[s]) is not None
                             else None)
            for s in range(len(SECTIONS))
        }

    summary = {
        "key": KEY_NAME, "root_pc": KEY_ROOT_PC, "scale_intervals": SCALE_INTERVALS,
        "bpm": BPM, "ticks_per_beat": TPB, "beats_per_bar": BPB, "bar_ticks": BAR,
        "grid": GRID, "eighth": EIGHTH, "form": "cinematic-build",
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "voices": [{"name": n, "program": p, "channel": c}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "chord_path": [
            {"bar": i, "roman": CHORDS[i][0], "name": CHORDS[i][1],
             "root_pc": CHORDS[i][2], "chord_tone_pcs": CHORDS[i][3]}
            for i in range(TOTAL_BARS)],
        "contour": CONTOUR,
        "phase_schedule": phase_schedule,
        "vl_violations": vl_violations,
        "inline_audit": inline_audit,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, inline_audit, phase_schedule, vl_violations, len(raw)


if __name__ == "__main__":
    composer, ok1, inline_audit, phase_schedule, vl_violations, n_raw = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw loop events: {n_raw}")
    print("[OK] Inline grid/harmony audit (pitched voices):")
    for vname, a in inline_audit.items():
        print(f"     {vname:6s} notes={a['n_notes']:3d} off16={a['off16']} "
              f"off8={a['off8']} out_scale={a['out_scale']} "
              f"out_chord={a['out_chord']}")
    print("[OK] Phase schedule:")
    for vi in range(4):
        offs = phase_schedule[f"Loop{vi + 1}"]
        print(f"     Loop{vi + 1}: " + " ".join(f"{k}={v}" for k, v in offs.items()))
    print(f"[OK] Voice-leading violations (pad, informational): {len(vl_violations)}")

    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 026 Deconstructive Phase-Shift Minimalism (DPSM) - PRE-RULES raw draft",
        sources=["Research/CompositionMethods/methods_db.md:Method 026",
                 "workflows/unitmatrix_composer.py"],
        parameters={"method": 26, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Trap", "form": "cinematic-build"},
        notes="Phase 1: single deconstructive loop (sine contour + jitter), "
              "unquantized onsets, off-grid by design, no harmony.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 026 Deconstructive Phase-Shift Minimalism (DPSM) + musicom rules",
        sources=["Research/CompositionMethods/methods_db.md:Method 026",
                 "rules/voice_leading.py", "workflows/unitmatrix_composer.py",
                 "projects/Instruments/instrument_registry.py"],
        parameters={"method": 26, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Trap", "form": "cinematic-build",
                    "voices": VOICES},
        notes="Phase 2: four identical 8-event loops (Rhodes) with dynamic "
              "phase offsets (8th-note units; drift/peak/converge), electric "
              "bass sub, synth-pad swell, trap drum kit. Onset grid-snap at "
              "8th-note (240 ticks), per-bar chord-tone quantization.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
