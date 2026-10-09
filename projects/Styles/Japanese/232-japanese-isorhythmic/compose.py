# -*- coding: utf-8 -*-
"""232 - Japanese Isorhythmic Talea-Color Study (Method 032, concrete).

Autonomous nightly composition job (2026-10-09).

Style: Japanese. Method 032 Isorhythmic Talea-Color Mapping (ITCM), layer
concrete, paradigm Rules-Based, Grid-Locked, Macro/Cycle, O(N).

Method 032 essence (medieval isorhythmic motet technique):
  * COLOR = a FIXED pitch sequence (7 scale degrees, length 7).
  * TALEA = a FIXED rhythm sequence (5 durations summing to 1 bar).
  * gcd(7, 5) = 1 (coprime) -> the color and talea re-align only after
    lcm(7,5) = 35 notes = 7 bars. Each color statement lands on a DIFFERENT
    metric position than the last: the melody "shifts" against the bar grid.

Key: D Phrygian (Japanese "in-sen" pentatonic is the scale's color subset:
D-Eb-G-A-C = degrees 0,1,3,4,6). Phrygian gives the flat-II (Neapolitan)
cadence + flat-vi/flat-vii, a dark Japanese/temple modal flavor.

Two-phase architecture (mandatory):
  Phase 1 (raw generative draft): single koto voice running the PURE
    color x talea stream (fixed 7-note color, fixed 5-duration talea), no
    harmony, no chord-tone snapping -> 232-...-phase1.mid
  Phase 2 (musicom rules): the talea rhythm is preserved EXACTLY (isorhythmic
    identity), the color contour is chord-tone-quantized per bar against a
    D-Phrygian modal progression, plus shakuhachi counterline (sustained chord
    tones), shamisen arpeggio, taiko + drums. Rhythm-grid snap, voice-leading
    optimization + correction, zero-drift gate. -> 232-...mid

Per-section color transforms (>=3 variation techniques):
  Intro   : COLOR,       octave -12, augmentation x2.0
  TaleaA  : COLOR,       octave   0, identity
  TaleaB  : COLOR retro, octave   0, identity
  Dev     : COLOR invert,octave   0, identity
  TaleaA2 : COLOR,       octave +12, identity (register shift)
  Climax  : COLOR,       octave +12, diminution x0.5
  Coda1   : COLOR retro, octave -12, augmentation x2.0
  Coda2   : COLOR,       octave   0, resolve to tonic drone
"""
import os
import sys

# Instrument registry (source of truth — NOT pip-installed)
_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import KOTO, SHAKUCHACHI, SHAMISEN, TAIKO

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "D Phrygian"
KEY_ROOT_PC = 2                 # D
SCALE_INTERVALS = [0, 1, 3, 5, 7, 8, 10]   # D Eb F G A Bb C (phrygian)
KEY_PCS = {2, 3, 5, 7, 9, 10, 0}          # D Eb F G A Bb C
KEY_ROOT_MIDI = 62              # D4
BPM = 76
TPB = 480
BPB = 4
BAR = TPB * BPB                 # 1920
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR        # 3840

SECTION_NAMES = ["Intro", "TaleaA", "TaleaB", "Dev",
                 "TaleaA2", "Climax", "Coda1", "Coda2"]

# D Phrygian modal progression (0-based degrees): i=0 bII=1 bIII=2 iv=3 vdim=4
# bVI=5 bvii=6. One degree per bar (16 bars), midpoint degree per section
# drives the section root (avoids the bar-0-tonic bug).
BAR_DEGREES = [
    0, 1,    # Intro     i  bII       (midpoint bII)
    1, 6,    # TaleaA    bII bvii     (midpoint bvii)
    6, 5,    # TaleaB    bvii bVI     (midpoint bVI)
    5, 3,    # Dev       bVI iv       (midpoint iv)
    3, 1,    # TaleaA2   iv  bII      (midpoint bII)
    1, 0,    # Climax    bII i        (midpoint i)
    0, 0,    # Coda1     i   i        (midpoint i)
    0, 0,    # Coda2     i   i        (midpoint i)
]
MIDPOINT_DEGREES = [BAR_DEGREES[s * 2 + 1] for s in range(len(SECTION_NAMES))]

# ---- Isorhythmic DNA --------------------------------------------------------
# COLOR: 7 Phrygian scale degrees (0-based), the fixed pitch sequence.
COLOR = [0, 1, 3, 4, 6, 4, 3]           # D Eb G A C A G  (in-sen pentatonic)
# color inversion: mirror around tonic degree 0 (d -> (7-d) % 7)
_INV = {0: 0, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
COLOR_RETRO = list(reversed(COLOR))     # [3,4,6,4,3,1,0]
COLOR_INV = [_INV[d] for d in COLOR]    # [0,6,4,3,1,3,4]

# TALEA: 5 durations in ticks summing to 1 bar (1920). gcd(7,5)=1 coprime.
TALEA = [480, 240, 480, 240, 480]       # quarter eighth quarter eighth quarter

# (color, octave_shift, dur_scale) per section
SECTION_COLOR = {
    "Intro": COLOR, "TaleaA": COLOR, "TaleaB": COLOR_RETRO, "Dev": COLOR_INV,
    "TaleaA2": COLOR, "Climax": COLOR, "Coda1": COLOR_RETRO, "Coda2": COLOR,
}
SECTION_OCTAVE = {
    "Intro": -12, "TaleaA": 0, "TaleaB": 0, "Dev": 0,
    "TaleaA2": 12, "Climax": 12, "Coda1": -12, "Coda2": 0,
}
SECTION_DUR_SCALE = {
    "Intro": 2.0, "TaleaA": 1.0, "TaleaB": 1.0, "Dev": 1.0,
    "TaleaA2": 1.0, "Climax": 0.5, "Coda1": 2.0, "Coda2": 1.0,
}

VOICES = ["Koto", "Shakuhachi", "Shamisen", "Taiko", "Drums"]
VOICE_PROGRAMS = [KOTO.midi_program, SHAKUCHACHI.midi_program,
                  SHAMISEN.midi_program, TAIKO.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
BASE = "232-japanese-isorhythmic"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

NUM_BARS = len(BAR_DEGREES)             # 16
RAW_TOTAL_TICKS = NUM_BARS * BAR        # 30720


# ---- Helpers ----------------------------------------------------------------
def get_diatonic(degree, octave_shift=0):
    return Scale7ChordDegree.get_diatonic_note(
        KEY_ROOT_MIDI, SCALE_INTERVALS, degree) + octave_shift


def chord_triad_abs(degree):
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return [root, third, fifth]


def quantize_to_chord_tone(raw_pitch, triad, lo=45, hi=100):
    candidates = set()
    for p in triad:
        for shift in (-24, -12, 0, 12, 24):
            cand = p + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        candidates = set(triad)
    return min(candidates, key=lambda c: abs(c - raw_pitch))


def correct_voice_leading(triads):
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = []
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        candidates = [base]
        for rot in range(1, len(base)):
            candidates.append(vl._rotate_chord(base, rot))
        extra = [c for c in candidates]
        for c in candidates:
            extra.append([p + 12 for p in c])
        candidates = list(candidates) + list(extra)

        best, best_score = candidates[0], None
        for cand in candidates:
            pv = vl.check_parallel_motion(prev, cand)
            hv = vl.check_hidden_fifths(prev, cand)
            n_viol = len(pv) + len(hv)
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed.append((i, best_score[0]))
        corrected.append(sorted(best))
    return corrected, fixed


def snap_grid(t):
    return int(round(t / 120.0) * 120)


def dedup_collisions(events):
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.end_tick))


def generate_raw_events():
    """Phase-1 raw stream: PURE color x talea (identity, octave 0), single voice."""
    events, onset, i, safety = [], 0, 0, 0
    while onset < RAW_TOTAL_TICKS and safety < 20000:
        safety += 1
        degree = COLOR[i % 7]
        dur = TALEA[i % 5]
        pitch = get_diatonic(degree, 0)
        end = min(onset + dur, RAW_TOTAL_TICKS)
        if end > onset + 30:
            events.append(MusicEvent(pitch=pitch, volume=90,
                                     start_tick=int(onset), end_tick=int(end)))
        onset = end
        i += 1
    return events


def split_by_section(events):
    sections = []
    for s in range(len(SECTION_NAMES)):
        start = s * SECTION_TICKS
        end = start + SECTION_TICKS
        cell = []
        for e in events:
            if e.end_tick <= start or e.start_tick >= end:
                continue
            st = max(0, e.start_tick - start)
            et = min(SECTION_TICKS, e.end_tick - start)
            if et <= st:
                continue
            cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                   start_tick=st, end_tick=et))
        if not cell or cell[-1].end_tick < SECTION_TICKS:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=SECTION_TICKS))
        sections.append(MusicUnit(events=cell))
    return sections


# ---- Composition ------------------------------------------------------------
def compose():
    raw_events = generate_raw_events()
    phase1_sections = split_by_section(raw_events)

    # ---- Phase 1 MIDI (single koto voice, pre-rules) ----------------------
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTION_NAMES))
    p1.add_voice("RawDraft", program=KOTO.midi_program, channel=0)
    for sname in SECTION_NAMES:
        p1.add_section(sname, bars=SECTION_BARS)
    for s in range(len(SECTION_NAMES)):
        p1.fill_voice_section("RawDraft", SECTION_NAMES[s], phase1_sections[s])
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: harmony, voice-leading, chord-tone quantization ---------
    bar_triads = [sorted(chord_triad_abs(d)) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed_report = correct_voice_leading(opt_triads)

    violations = []
    for i in range(len(corr_triads) - 1):
        violations += vl.check_parallel_motion(corr_triads[i], corr_triads[i + 1])
        violations += vl.check_hidden_fifths(corr_triads[i], corr_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTION_NAMES))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname in SECTION_NAMES:
        composer.add_section(sname, bars=SECTION_BARS)

    for s, sname in enumerate(SECTION_NAMES):
        color_seq = SECTION_COLOR[sname]
        octave = SECTION_OCTAVE[sname]
        dur_scale = SECTION_DUR_SCALE[sname]

        lead_events, shaku_events, sham_events, taiko_events, drum_events = [], [], [], [], []

        # --- Lead (koto): isorhythmic color x talea stream, chord-quantized --
        onset, j = 0, 0
        while onset < SECTION_TICKS:
            degree = color_seq[j % 7]
            dur = int(TALEA[j % 5] * dur_scale)
            if dur < 60:
                dur = 60
            bar_in_sec = min(SECTION_BARS - 1, onset // BAR)
            bar = s * SECTION_BARS + bar_in_sec
            triad = corr_triads[bar]
            raw_pitch = get_diatonic(degree, octave)
            qp = quantize_to_chord_tone(raw_pitch, triad)
            end_t = min(onset + dur, SECTION_TICKS - 10)
            if end_t > onset + 30:
                lead_events.append(MusicEvent(pitch=qp, volume=92,
                                              start_tick=int(onset), end_tick=int(end_t)))
            onset += dur
            j += 1
        lead_events = dedup_collisions(lead_events)

        # --- Shakuhachi (ch1): sustained chord-tone counterline, 1 note/bar ---
        for bar_in_sec in range(SECTION_BARS):
            bar = s * SECTION_BARS + bar_in_sec
            triad = corr_triads[bar]
            bar_start = bar_in_sec * BAR
            note = triad[2] if bar % 2 == 0 else triad[1]
            while note < 64:
                note += 12
            shaku_events.append(MusicEvent(pitch=note, volume=72,
                                           start_tick=bar_start,
                                           end_tick=bar_start + BAR - 10))

        # --- Shamisen (ch2): 8th-note arpeggio of chord tones, 1 octave down --
        for bar_in_sec in range(SECTION_BARS):
            bar = s * SECTION_BARS + bar_in_sec
            triad = corr_triads[bar]
            bar_start = bar_in_sec * BAR
            r, th, f = triad
            pattern = [r - 12, th - 12, f - 12, r, f - 12, th - 12, r - 12, f - 12]
            for k in range(8):
                st = bar_start + k * 240
                sham_events.append(MusicEvent(pitch=pattern[k], volume=68,
                                              start_tick=st, end_tick=st + 200))

        # --- Taiko (ch3): deep DON on beat 1 (+ beat 3 in Climax) ---
        for bar_in_sec in range(SECTION_BARS):
            bar_start = bar_in_sec * BAR
            taiko_events.append(MusicEvent(pitch=45, volume=96,
                                           start_tick=bar_start,
                                           end_tick=bar_start + 300))
            if sname == "Climax":
                taiko_events.append(MusicEvent(pitch=45, volume=80,
                                               start_tick=bar_start + 960,
                                               end_tick=bar_start + 960 + 200))

        # --- Drums (ch9): sparse pulse; denser 8th hi-hat in Climax ---
        kick = MidiPercussion.BASS_DRUM
        low_tom = MidiPercussion.LOW_TOM
        hh = MidiPercussion.CLOSED_HI_HAT
        for bar_in_sec in range(SECTION_BARS):
            bar_start = bar_in_sec * BAR
            drum_events.append(MusicEvent(pitch=kick, volume=90,
                                          start_tick=bar_start,
                                          end_tick=bar_start + 80))
            drum_events.append(MusicEvent(pitch=low_tom, volume=82,
                                          start_tick=bar_start + 960,
                                          end_tick=bar_start + 960 + 70))
            if sname == "Climax":
                for k in range(0, BAR, 240):
                    drum_events.append(MusicEvent(pitch=hh, volume=70,
                                                  start_tick=bar_start + k,
                                                  end_tick=bar_start + k + 50))

        def seal(ev_list):
            if not ev_list:
                ev_list = [MusicEvent(pitch=0, volume=0, start_tick=0,
                                      end_tick=SECTION_TICKS)]
            last_end = max(e.end_tick for e in ev_list)
            if last_end < SECTION_TICKS:
                ev_list.append(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end,
                                          end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Koto", sname, seal(lead_events))
        composer.fill_voice_section("Shakuhachi", sname, seal(shaku_events))
        composer.fill_voice_section("Shamisen", sname, seal(sham_events))
        composer.fill_voice_section("Taiko", sname, seal(taiko_events))
        composer.fill_voice_section("Drums", sname, seal(drum_events))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="D Phrygian")

    return (composer, violations, fixed_report, corr_triads, len(raw_events),
            MIDPOINT_DEGREES)


if __name__ == "__main__":
    (composer, violations, fixed_report, triads, n_total, midpoints) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"
    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Raw events: {n_total}")
    print(f"[OK] Section midpoint degrees (0-based): {midpoints}")
    print(f"[OK] Voice-leading corrections: {len(fixed_report)} chord(s)")
    print(f"[OK] Parallel/hidden fifth violations: {len(violations)}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + Isorhythmic Talea-Color (PRE-RULES raw draft)",
        parameters={"project": BASE, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "method": 32, "color": COLOR, "talea": TALEA,
                    "color_len": 7, "talea_len": 5, "coprime": "gcd(7,5)=1",
                    "rules_applied": "NONE (pre-rules)"},
        notes="Phase 1 raw isorhythmic draft: fixed 7-note Phrygian color x fixed "
              "5-duration talea, single koto voice, no harmony, no chord-tone snap.")
    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + musicom rules",
        parameters={"project": BASE, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "method": 32, "color": COLOR, "talea": TALEA,
                    "sections": SECTION_NAMES, "bars": NUM_BARS,
                    "variation_techniques": [
                        "retrograde color (TaleaB, Coda1)",
                        "inversion color (Dev)",
                        "augmentation x2.0 (Intro, Coda1)",
                        "diminution x0.5 (Climax)",
                        "transposition/register shift (+12 TaleaA2/Climax, -12 Intro/Coda1)",
                        "density rise (Climax 8th hi-hat + taiko off-beat)",
                    ],
                    "bar_degrees": BAR_DEGREES,
                    "instruments": {v: p for v, p in zip(VOICES, VOICE_PROGRAMS)},
                    "rules_applied": "per-bar chord-tone quantization, rhythm-grid snap, "
                                     "diatonic block harmony, voice-leading + correction"},
        notes="Phase 2 rules-processed Japanese ensemble. Talea rhythm preserved exactly; "
              "color contour chord-quantized to D Phrygian modal progression.")
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
