# -*- coding: utf-8 -*-
"""240 — Ragtime Glide (Method 029: Continuous Polyphonic Portamento Glide).

Nightly composition job (2026-10-13). Style = Ragtime, form = rondo
(A B A C A, 20 bars), key = F major.

Method 029 (concrete, Rules-Based): "Smoothly interpolates (glides) pitch and
voicings of polyphonic chords between successive sections instead of
jump-cutting, creating a theremin-style continuous choral warp."

Implementation (MIDI is discrete, so "portamento" is expressed as:
  1. MIN-MOTION voice-leading — a 4-voice string-ensemble choir (7th chords)
     re-voices every bar with the smallest total motion; voices frequently
     move by a semitone/tone (the "slide").
  2. CONTINUOUS RE-VOICING — each bar's chord is re-articulated as four
     quarter-note inversions, so the top line "warps" through the chord
     instead of sitting as a block.
  3. GLISSANDO TRANSITIONS — at every rondo section boundary the lead piano
     runs a fast 16th-note chord-tone arpeggio sweep (2 octaves) that "glides"
     into the next section.
Every note is a chord tone of its own bar AND in the key scale (0 violations).

Two-phase architecture:
  Phase 1 (raw): single-voice continuous portamento glide — a theremin-style
    pitch sweep (sine contour + jitter) with unquantized onsets, off-grid by
    design, no harmony.
  Phase 2 (rules): grid-snap (120 ticks), per-bar chord-tone quantization,
    min-motion glide choir (String Ensemble), syncopated ragtime lead +
    stride left hand (Piano), light brushed drum kit (ch9).

Engines: structures.*, workflows.unitmatrix_composer, visualization.grid,
workflows.provenance, rules.voice_leading (validation), instrument registry.
"""
import itertools
import json
import math
import os
import random
import sys

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import PIANO, STRING_ENSEMBLE  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 240
KEY_NAME = "F major"
KEY_ROOT_PC = 5            # F
KEY_ROOT_MIDI = 53         # F3
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]     # ionian from F
KEY_PCS = set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS)
BPM = 100
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
GRID = 120                 # 16th-note snap grid

# ---- Form: rondo A B A C A --------------------------------------------------
# NOTE: section names MUST be unique (the composer looks up sections by name;
# duplicate "A" sections would collide and only the first gets filled).
SECTIONS = [("A1", 4), ("B", 4), ("A2", 4), ("C", 4), ("A3", 4)]
SECTION_ROLE = {"A1": "A", "A2": "A", "A3": "A", "B": "B", "C": "C"}
TOTAL_BARS = sum(b for _, b in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# ---- Chord plan (20 bars) — all diatonic 7th chords in F major ---------------
# (roman, root_pc, chord_tone_pcs)
CHORDS = [
    ("I",   5, [5, 9, 0, 4]),     # Fmaj7
    ("vi",  2, [2, 5, 9, 0]),     # Dm7
    ("ii",  7, [7, 10, 2, 5]),    # Gm7
    ("V7",  0, [0, 4, 7, 10]),    # C7
    ("IV", 10, [10, 2, 5, 9]),    # Bbmaj7
    ("I",   5, [5, 9, 0, 4]),     # Fmaj7
    ("ii",  7, [7, 10, 2, 5]),    # Gm7
    ("V7",  0, [0, 4, 7, 10]),    # C7
    ("I",   5, [5, 9, 0, 4]),     # Fmaj7
    ("vi",  2, [2, 5, 9, 0]),     # Dm7
    ("ii",  7, [7, 10, 2, 5]),    # Gm7
    ("V7",  0, [0, 4, 7, 10]),    # C7
    ("vi",  2, [2, 5, 9, 0]),     # Dm7   (C section)
    ("IV", 10, [10, 2, 5, 9]),    # Bbmaj7
    ("ii",  7, [7, 10, 2, 5]),    # Gm7
    ("V7",  0, [0, 4, 7, 10]),    # C7
    ("I",   5, [5, 9, 0, 4]),     # Fmaj7  (A' coda)
    ("vi",  2, [2, 5, 9, 0]),     # Dm7
    ("ii",  7, [7, 10, 2, 5]),    # Gm7
    ("I",   5, [5, 9, 0, 4]),     # Fmaj7  (tonic close)
]
assert len(CHORDS) == TOTAL_BARS


# ---- Pitch helpers ----------------------------------------------------------
def pitch_in(pc, lo, hi, center=None):
    """Return a MIDI pitch with pitch-class pc inside [lo,hi], nearest center."""
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


def snap(t):
    return int(round(t / GRID) * GRID)


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


# ---- CPPG voicing: min-motion 4-voice choir ---------------------------------
def voice_progression(chords, lo=55, hi=84):
    """Voice the 20 seventh-chords with greedy min-motion (portamento slide)."""
    voicings = []
    prev = None
    for (roman, root, pcs) in chords:
        if prev is None:
            cand = sorted(set(pitch_in(p, lo, hi) for p in pcs))
            while len(cand) < 4:
                cand.append(cand[-1] + 12)
            voicings.append(sorted(cand[:4]))
        else:
            best, bestd = None, None
            for perm in itertools.permutations(pcs):
                cand = []
                ok = True
                for j, pc in enumerate(perm):
                    n = pitch_in(pc, lo, hi, center=prev[j])
                    if n is None:
                        ok = False
                        break
                    cand.append(n)
                if not ok or len(set(cand)) < 4:
                    continue
                dist = sum(abs(prev[j] - cand[j]) for j in range(4))
                if bestd is None or dist < bestd:
                    bestd, best = dist, sorted(cand)
            if best is None:
                best = sorted(set(pitch_in(p, lo, hi) for p in pcs))
                while len(best) < 4:
                    best.append(best[-1] + 12)
                best = best[:4]
            voicings.append(sorted(best))
        prev = voicings[-1]
    return voicings


# ---- Phase-1 raw draft (single voice, continuous portamento glide) ----------
def build_raw_events():
    rng = random.Random(SEED)
    out = []
    n_events = TOTAL_BARS * 8        # ~8 gliding events per bar
    for i in range(n_events):
        frac = i / float(n_events)
        # theremin-style sweep: F4 (65) -> F6 (89) -> F4 (65) over the piece
        center = 65 + 24 * (0.5 - 0.5 * math.cos(2 * math.pi * frac))
        pitch = int(round(center + rng.uniform(-2.0, 2.0)))
        st = int(i * (TOTAL_TICKS / float(n_events))) + rng.randint(-40, 40)
        st = max(0, min(TOTAL_TICKS - 60, st))
        dur = rng.randint(60, 240)
        vel = rng.randint(60, 90)
        out.append(MusicEvent(pitch=pitch, volume=vel,
                              start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
def chord_tones_midi(pcs, lo, hi):
    t = sorted(set(pitch_in(p, lo, hi) for p in pcs))
    while len(t) < 4:
        t.append(t[-1] + 12)
    return t[:4]


TRANSITION_BARS = {3, 7, 11, 15, 19}
# Ragtime syncopation on the 8th-note grid (even 16th slots only) so every
# onset is a multiple of 240 ticks (off8 == 0, per the grid-sync rule).
LEAD_TEMPLATES = {
    "A": [0, 2, 6, 8, 10, 14],
    "B": [0, 4, 6, 10, 12, 14],
    "C": [0, 2, 8, 10, 14],
}
CONTOUR = [0, 2, 1, 3, 2, 0]


def build_lead(chords):
    """Syncopated ragtime melody (Piano) + chord-tone glissando transitions."""
    out = []
    for bar, (roman, root, pcs) in enumerate(chords):
        sec = section_of_bar(bar)
        sec_name = SECTIONS[sec][0]
        role = SECTION_ROLE[sec_name]
        base = bar * BAR
        t = chord_tones_midi(pcs, 60, 84)
        if bar in TRANSITION_BARS:
            # glissando sweep across 2 octaves of chord tones (the "glide"),
            # on the 8th-note grid (even 16th slots).
            seq = []
            for o in (0, 12):
                for x in t:
                    seq.append(x + o)
            descend = (bar == TOTAL_BARS - 1)
            if descend:
                seq = list(reversed(seq))
            for i in range(8):
                st = base + i * 2 * GRID
                p = seq[i % len(seq)]
                vel = 88 + (i * 3 if not descend else (7 - i) * 3)
                out.append(MusicEvent(pitch=p, volume=min(120, vel),
                                      start_tick=st, end_tick=st + 2 * GRID))
        else:
            slots = LEAD_TEMPLATES[role]
            for i, slot in enumerate(slots):
                st = base + slot * GRID
                idx = CONTOUR[i % len(CONTOUR)]
                p = t[idx]
                if i == 0 and slot == 0:
                    p = min(p + 12, 88)          # octave sparkle on the downbeat
                dur = GRID * 4 if slot % 4 == 0 else GRID * 2
                vel = 96 if role in ("A", "B") else 90
                out.append(MusicEvent(pitch=p, volume=vel,
                                      start_tick=snap(st),
                                      end_tick=min(base + BAR, snap(st) + dur)))
    return dedup(out)


def build_glide(chords, voicings):
    """CPPG core: 4-voice string-ensemble choir, min-motion + quarter-note
    inversion re-voicing (the continuous polyphonic 'warp')."""
    out = []
    for bar, (roman, root, pcs) in enumerate(chords):
        base = bar * BAR
        v = voicings[bar]                       # ascending 4-note voicing
        for q in range(4):                      # quarter-note inversions
            st = base + q * 4 * GRID
            if q == 0:
                inv = v
            elif q == 1:
                inv = [v[1], v[2], v[3], v[0] + 12]
            elif q == 2:
                inv = [v[2], v[3], v[0] + 12, v[1] + 12]
            else:
                inv = [v[3], v[0] + 12, v[1] + 12, v[2] + 12]
            for p in inv:
                out.append(MusicEvent(pitch=p, volume=72,
                                      start_tick=st,
                                      end_tick=min(base + BAR, st + 4 * GRID)))
    return dedup(out)


def build_stride(chords):
    """Ragtime stride left hand (Piano): bass on 1&3, offbeat chord on 2&4."""
    out = []
    for bar, (roman, root, pcs) in enumerate(chords):
        base = bar * BAR
        root_lo = pitch_in(root, 36, 48)
        fifth = pitch_in((root + 7) % 12, 36, 48)
        chord = sorted(set(pitch_in(p, 48, 62) for p in pcs))[:3]
        # beat 1: bass root
        out.append(MusicEvent(pitch=root_lo, volume=98,
                              start_tick=base, end_tick=base + 2 * GRID))
        # beat 2: offbeat chord
        for p in chord:
            out.append(MusicEvent(pitch=p, volume=70,
                                  start_tick=base + 4 * GRID,
                                  end_tick=base + 6 * GRID))
        # beat 3: bass fifth (or root for a walking feel)
        bass3 = root_lo if bar % 2 == 0 else fifth
        out.append(MusicEvent(pitch=bass3, volume=96,
                              start_tick=base + 8 * GRID,
                              end_tick=base + 10 * GRID))
        # beat 4: offbeat chord (slightly higher inversion)
        for p in chord:
            out.append(MusicEvent(pitch=p, volume=72,
                                  start_tick=base + 12 * GRID,
                                  end_tick=base + 14 * GRID))
    return dedup(out)


def build_drums():
    """Light brushed kit (ch9) — soft hi-hat, gentle kick/snare on B/C only."""
    out = []
    for s, (name, bars) in enumerate(SECTIONS):
        sec_start = section_start_abs(s)
        role = SECTION_ROLE[name]
        for b in range(bars):
            base = sec_start + b * BAR
            # closed hi-hat — 8th notes in B/C, quarter notes in A
            if role in ("B", "C"):
                slots = list(range(0, 16, 2))
            else:
                slots = [0, 4, 8, 12]
            for slot in slots:
                out.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT,
                                      volume=52,
                                      start_tick=base + slot * GRID,
                                      end_tick=base + slot * GRID + GRID))
            # soft kick on 1 & 3 in B/C
            if role in ("B", "C"):
                for slot in (0, 8):
                    out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM,
                                          volume=64,
                                          start_tick=base + slot * GRID,
                                          end_tick=base + slot * GRID + GRID))
            # brushed snare backbeat (C section "trio" only)
            if role == "C":
                for slot in (4, 12):
                    out.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE,
                                          volume=58,
                                          start_tick=base + slot * GRID,
                                          end_tick=base + slot * GRID + GRID))
    return dedup(out)


# ---- Compose ----------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "240-ragtime-glide"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

VOICES = ["Lead", "Glide", "Stride", "Drums"]
VOICE_PROGRAMS = [PIANO.midi_program, STRING_ENSEMBLE.midi_program,
                  PIANO.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 9]


def compose():
    voicings = voice_progression(CHORDS)

    # ---- Phase 1: raw single-voice portamento glide -------------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawGlide", program=PIANO.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawGlide", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process ----------------------------------------
    lead = build_lead(CHORDS)
    glide = build_glide(CHORDS, voicings)
    stride = build_stride(CHORDS)
    drums = build_drums()

    voice_events = {"Lead": lead, "Glide": glide, "Stride": stride,
                    "Drums": drums}

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
                             voice_names=VOICES, bpm=BPM, mode="Major (F)")

    # voice-leading check on the glide choir
    vl = VoiceLeadingRules(style="classical")
    vl_violations = []
    for i in range(1, len(voicings)):
        vl_violations += vl.check_parallel_motion(voicings[i - 1], voicings[i])
        vl_violations += vl.check_hidden_fifths(voicings[i - 1], voicings[i])

    # portamento step census (per-voice motion between bars)
    steps = []
    for i in range(1, len(voicings)):
        moves = [voicings[i][j] - voicings[i - 1][j] for j in range(4)]
        steps.append(moves)

    summary = {
        "key": KEY_NAME, "root_pc": KEY_ROOT_PC, "scale_intervals": SCALE_INTERVALS,
        "bpm": BPM, "ticks_per_beat": TPB, "beats_per_bar": BPB, "bar_ticks": BAR,
        "grid": GRID, "form": "rondo",
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "voices": [{"name": n, "program": p, "channel": c}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "chord_path": [
            {"bar": i, "roman": CHORDS[i][0], "root_pc": CHORDS[i][1],
             "chord_tone_pcs": CHORDS[i][2]}
            for i in range(TOTAL_BARS)],
        "voicings": voicings,
        "portamento_steps": steps,
        "vl_violations": vl_violations,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, voicings, steps, vl_violations, len(raw)


if __name__ == "__main__":
    composer, ok1, voicings, steps, vl_violations, n_raw = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw glide events: {n_raw}")
    print(f"[OK] Voice-leading violations (classical): {len(vl_violations)}")
    print(f"[OK] Chord degrees per bar:")
    degs = [c[0] for c in CHORDS]
    print("     " + " ".join(f"{d:>4}" for d in degs[:10]))
    print("     " + " ".join(f"{d:>4}" for d in degs[10:]))
    # portamento census
    semis = [abs(m) for st in steps for m in st]
    if semis:
        print(f"[OK] Portamento step census: {len(semis)} voice-moves, "
              f"max={max(semis)}, mean={sum(semis)/len(semis):.2f} semitones")

    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 029 Continuous Polyphonic Portamento Glide (CPPG) - PRE-RULES raw draft",
        sources=["Research/CompositionMethods/methods_db.md:Method 029",
                 "workflows/unitmatrix_composer.py"],
        parameters={"method": 29, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Ragtime", "form": "rondo"},
        notes="Phase 1: single-voice theremin-style portamento glide (sine "
              "contour + jitter), unquantized onsets, off-grid by design, "
              "no harmony.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 029 Continuous Polyphonic Portamento Glide (CPPG) + musicom rules",
        sources=["Research/CompositionMethods/methods_db.md:Method 029",
                 "rules/voice_leading.py", "workflows/unitmatrix_composer.py",
                 "projects/Instruments/instrument_registry.py"],
        parameters={"method": 29, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "style": "Ragtime", "form": "rondo",
                    "voices": VOICES},
        notes="Phase 2: min-motion 4-voice string-ensemble glide choir "
              "(quarter-note inversion re-voicing), syncopated ragtime piano "
              "lead with chord-tone glissando transitions at rondo section "
              "boundaries, stride left hand, light brushed kit. Grid-snap "
              "120 ticks, per-bar chord-tone quantization.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
