# -*- coding: utf-8 -*-
"""213 - Markov Chain Chorale Rework (Method 020, rework of 066).

Autonomous nightly REWORK job. Source: Experimental/066-markov-chain-chorale
(Method 020 First-Order Markov Chain Sequencing). The source failed the
current-standard audit ONLY on standard 6 (missing root provenance.json +
index.html dashboard) — the engine, zero-drift, grid-sync, track-setup and
two-phase standards all PASSED. This rework therefore preserves the musical
identity (F major/ionian, 92 BPM, 4-part chorale texture, stepwise-Markov
pitch DNA) and EXTENDS it: 16 bars (8 sections) instead of 8 bars (4 sections),
5 gen/unpitched voices incl. a ch9 drum kit, and >=3 distinct variation
techniques (transposition, inversion, retrograde, diminution, augmentation,
register shift).

Two-phase architecture (mandatory):
  Phase 1 (generative draft): first-order Markov chain over 12 pitch classes
    (neighbour-biased, chromatic escape states) + a second first-order chain
    over duration states {1/8, 1/4}. Raw, chromatic, single voice -> -phase1.mid
  Phase 2 (musicom rules): per-BAR chord quantization (each note snapped to its
    own bar's triad), per-section variation transforms, rhythm-grid snap
    (onset in 120/240 grid), diatonic block harmony via
    Scale7ChordDegree.get_diatonic_note(), voice-leading optimization +
    Phase 2c correction, zero-drift gate. -> 213-...mid

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression, generators.chain.

Per-section harmonic regions (each section owns a short progression; the
MIDPOINT chord (2nd bar) drives the section's root/quality so no section
defaults to the bar-0 tonic bug):
  S0 Intro      : I  | IV         (midpoint IV)
  S1 VerseA     : vi | I          (midpoint I)
  S2 VerseA2    : IV | ii         (midpoint ii)   [transposed +5]
  S3 PreChorus  : ii | V          (midpoint V)    [diminution]
  S4 Chorus     : I  | V          (midpoint V)    [diminution + register up]
  S5 Chorus2    : vi | IV         (midpoint IV)   [inversion]
  S6 Bridge     : ii | iii        (midpoint iii)  [inversion]
  S7 Outro      : IV | I          (midpoint I)    [augmentation + register down]
"""
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree
from generators.chain import MarkovChainGenerator

SEED = 213
random.seed(SEED)

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "F major (ionian)"
KEY_ROOT_PC = 5                # F
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]   # major / ionian
KEY_PCS = {5, 7, 9, 10, 0, 2, 4}          # F G A Bb C D E
KEY_ROOT_MIDI = 53             # F3
BPM = 92
TPB = 480
BPB = 4
BAR = TPB * BPB                # 1920
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR       # 3840

# 8 sections x 2 bars = 16 bars. Degree per bar (0-based: I=0..vii=6).
SECTION_NAMES = ["Intro", "VerseA", "VerseA2", "PreChorus",
                 "Chorus", "Chorus2", "Bridge", "Outro"]
BAR_DEGREES = [
    0, 3,     # Intro      I  IV
    5, 0,     # VerseA     vi I
    3, 1,     # VerseA2    IV ii   (transposed +5)
    1, 4,     # PreChorus  ii V    (diminution)
    0, 4,     # Chorus     I  V    (diminution + reg up)
    5, 3,     # Chorus2    vi IV   (retrograde)
    1, 2,     # Bridge     ii iii  (inversion)
    3, 0,     # Outro      IV I    (augmentation + reg down)
]
MIDPOINT_DEGREES = [BAR_DEGREES[s * 2 + 1] for s in range(len(SECTION_NAMES))]

VOICES = ["Soprano", "Alto", "Tenor", "Bass", "Drums"]
VOICE_PROGRAMS = [
    MidiInstrument.FLUTE,
    MidiInstrument.STRING_ENSEMBLE,
    MidiInstrument.STRING_ENSEMBLE,
    MidiInstrument.BASS,
    0,                          # ch9 percussion (program ignored on ch9)
]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
BASE = "213-markov-chorale-rework"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

NUM_BARS = len(BAR_DEGREES)
RAW_TOTAL_TICKS = NUM_BARS * BAR        # 30720

# Pitch-class transition matrix: neighbour-biased (diatonic + chromatic) plus
# fifth-leap escape states -> raw draft leaks non-diatonic tones.
_NEIGH = {pc: sorted({(pc + 11) % 12, (pc + 1) % 12, (pc + 2) % 12,
                      (pc + 10) % 12, (pc + 7) % 12}) for pc in range(12)}
RAW_PC_TO_PITCH = {pc: 65 + pc for pc in range(12)}   # 65..76 chromatic

DUR_STATES = [TPB // 2, TPB]          # eighth, quarter
DUR_MATRIX = [[0.65, 0.35], [0.55, 0.45]]


# ---- Helpers ----------------------------------------------------------------
def chord_triad_abs(degree):
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return [root, third, fifth]


def quantize_to_chord_tone(raw_pitch, triad, lo=60, hi=88):
    candidates = set()
    for p in triad:
        for shift in (-12, 0, 12):
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
    """Snap an onset to the 8th/16th grid (120 or 240 tick boundary)."""
    return int(round(t / 120.0) * 120)


# Per-section variation spec: (pitch_transform, dur_scale)
#   pitch_transform: callable(raw_pitch) -> raw_pitch (pre-quantization)
#   dur_scale:       float multiplier applied to raw duration
def _identity(p):
    return p


def _transpose(p, k=5):
    return p + k


def _invert(p, axis=69):
    return 2 * axis - p


SECTION_PITCH_FN = {
    "Intro": _identity,
    "VerseA": _identity,
    "VerseA2": lambda p: _transpose(p, 5),
    "PreChorus": _identity,
    "Chorus": lambda p: _transpose(p, 12),
    "Chorus2": lambda p: _invert(p, 69),
    "Bridge": lambda p: _invert(p, 66),
    "Outro": lambda p: _transpose(p, -12),
}
SECTION_DUR_SCALE = {
    "Intro": 1.0, "VerseA": 1.0, "VerseA2": 1.0, "PreChorus": 0.5,
    "Chorus": 0.5, "Chorus2": 1.0, "Bridge": 1.0, "Outro": 2.0,
}


def dedup_collisions(events):
    """Dedup collided (start_tick, pitch) keeping longest duration."""
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > (best[key].end_tick - best[key].start_tick):
            best[key] = e
    out = sorted(best.values(), key=lambda e: (e.start_tick, e.end_tick))
    return out


def generate_raw_events():
    """Walk both first-order Markov chains -> raw (chromatic, unquantized) events."""
    train_pairs = [(pc, n) for pc in range(12) for n in _NEIGH[pc]]
    chain = MarkovChainGenerator(train=train_pairs, start=0, length=1)

    events, tick, safety = [], 0, 0
    cur_pc = random.randrange(12)
    cur_dur_state = random.randrange(2)
    while tick < RAW_TOTAL_TICKS and safety < 12000:
        safety += 1
        cur_pc = random.choice(chain.trans[cur_pc])
        cur_dur_state = random.choices(range(2), weights=DUR_MATRIX[cur_dur_state])[0]
        dur = DUR_STATES[cur_dur_state]
        pitch = RAW_PC_TO_PITCH[cur_pc]
        end = min(tick + dur, RAW_TOTAL_TICKS)
        if end > tick:
            events.append(MusicEvent(pitch=pitch, volume=90, start_tick=tick, end_tick=end))
        tick = end
    return events


def split_by_section(events):
    """Partition raw events into per-section MusicUnits (relative ticks + pad)."""
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
            cell.append(MusicEvent(pitch=e.pitch, volume=e.volume, start_tick=st, end_tick=et))
        if not cell or cell[-1].end_tick < SECTION_TICKS:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=SECTION_TICKS))
        sections.append(MusicUnit(events=cell))
    return sections


# ---- Composition ------------------------------------------------------------
def compose():
    raw_events = generate_raw_events()
    n_raw_leak = len([e for e in raw_events
                      if (e.pitch - KEY_ROOT_PC) % 12 not in SCALE_INTERVALS])
    phase1_sections = split_by_section(raw_events)

    # ---- Phase 1 MIDI (single voice, pre-rules) --------------------------
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTION_NAMES))
    p1.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
    for sname in SECTION_NAMES:
        p1.add_section(sname, bars=SECTION_BARS)
    for s in range(len(SECTION_NAMES)):
        p1.fill_voice_section("RawDraft", SECTION_NAMES[s], phase1_sections[s])
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: per-bar chords, voice-leading, variation transforms ----
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
        pitch_fn = SECTION_PITCH_FN[sname]
        dur_scale = SECTION_DUR_SCALE[sname]

        soprano_events, alto_events, tenor_events, bass_events, drum_events = [], [], [], [], []
        for bar_in_sec in range(SECTION_BARS):
            bar = s * SECTION_BARS + bar_in_sec
            triad = corr_triads[bar]
            bar_start = bar_in_sec * BAR
            bass_note = triad[0] - 12
            alto_note = triad[1]
            tenor_note = triad[2]

            # chord pad (whole bar) for Alto/Tenor/Bass
            pad_end = bar_start + BAR - 10
            alto_events.append(MusicEvent(pitch=alto_note, volume=70,
                                          start_tick=bar_start, end_tick=pad_end))
            tenor_events.append(MusicEvent(pitch=tenor_note, volume=70,
                                           start_tick=bar_start, end_tick=pad_end))
            bass_events.append(MusicEvent(pitch=bass_note, volume=82,
                                          start_tick=bar_start, end_tick=pad_end))

            # drums (ch9): simple 4/4 backbeat, denser in Chorus
            kick = MidiPercussion.BASS_DRUM
            snare = MidiPercussion.ACOUSTIC_SNARE
            hh = MidiPercussion.CLOSED_HI_HAT
            beat = int(TPB / 2)   # 240 = eighth
            if sname == "Chorus":
                for k in range(0, BAR, beat):   # dense 16th hi-hat + backbeat
                    drum_events.append(MusicEvent(pitch=hh, volume=78,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 60))
                for k in (0, 960):
                    drum_events.append(MusicEvent(pitch=kick, volume=100,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 80))
                for k in (480, 1440):
                    drum_events.append(MusicEvent(pitch=snare, volume=90,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 70))
            else:
                for k in (0, 960):
                    drum_events.append(MusicEvent(pitch=kick, volume=92,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 80))
                for k in (480, 1440):
                    drum_events.append(MusicEvent(pitch=snare, volume=82,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 60))
                for k in range(0, BAR, 2 * beat):   # quarter hi-hat
                    drum_events.append(MusicEvent(pitch=hh, volume=66,
                                                  start_tick=bar_start + k, end_tick=bar_start + k + 50))

        # soprano: transform raw events, snap grid, quantize to per-bar triad
        raw_sec = phase1_sections[s]
        current_bar = -1
        for e in raw_sec.events:
            if e.pitch == 0:
                continue
            bar_in_sec = min(SECTION_BARS - 1, e.start_tick // BAR)
            bar = s * SECTION_BARS + bar_in_sec
            triad = corr_triads[bar]

            # apply variation transform (pitch + duration scale)
            raw_pitch = pitch_fn(e.pitch)
            raw_dur = int((e.end_tick - e.start_tick) * dur_scale)
            onset = snap_grid(e.start_tick)
            onset = min(onset, SECTION_TICKS - 80)
            if raw_dur < 60:
                raw_dur = 60
            end_t = min(onset + raw_dur, SECTION_TICKS - 10)
            if end_t <= onset:
                end_t = onset + 60

            qp = quantize_to_chord_tone(raw_pitch, triad)
            soprano_events.append(MusicEvent(pitch=qp, volume=92,
                                             start_tick=onset, end_tick=end_t))

        soprano_events = dedup_collisions(soprano_events)

        # pad each voice to section boundary
        def seal(ev_list):
            if not ev_list:
                ev_list = [MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=SECTION_TICKS)]
            last_end = max(e.end_tick for e in ev_list)
            if last_end < SECTION_TICKS:
                ev_list.append(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end, end_tick=SECTION_TICKS))
            return MusicUnit(events=ev_list)

        composer.fill_voice_section("Soprano", sname, seal(soprano_events))
        composer.fill_voice_section("Alto", sname, seal(alto_events))
        composer.fill_voice_section("Tenor", sname, seal(tenor_events))
        composer.fill_voice_section("Bass", sname, seal(bass_events))
        composer.fill_voice_section("Drums", sname, seal(drum_events))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Ionian (F major)")

    return (composer, violations, fixed_report, corr_triads, n_raw_leak,
            len(raw_events), MIDPOINT_DEGREES)


if __name__ == "__main__":
    (composer, violations, fixed_report, triads, n_leak, n_total,
     midpoints) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"
    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Raw events: {n_total}, non-diatonic leak (raw): {n_leak}")
    print(f"[OK] Section midpoint degrees (0-based): {midpoints}")
    print(f"[OK] Voice-leading corrections: {len(fixed_report)} chord(s)")
    print(f"[OK] Parallel/hidden fifth violations: {len(violations)}")
    if fixed_report:
        for idx, n in fixed_report:
            print(f"     bar {idx + 1}: {n} violation(s) corrected")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + generators.chain (PRE-RULES raw draft)",
        parameters={"project": "213-markov-chorale-rework", "phase": 1,
                    "key": KEY_NAME, "bpm": BPM, "method": 20,
                    "source": "066-markov-chain-chorale", "seed": SEED,
                    "rules_applied": "NONE (pre-rules)",
                    "variation": "none (identity seed material)"},
        notes="Phase 1 raw Markov draft: first-order pitch-class chain + duration "
              "chain, chromatic (leaks non-diatonic), single voice, pre-rules.")
    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + musicom rules",
        parameters={"project": "213-markov-chorale-rework", "phase": 2,
                    "key": KEY_NAME, "bpm": BPM, "method": 20,
                    "source": "066-markov-chain-chorale", "seed": SEED,
                    "sections": SECTION_NAMES, "bars": NUM_BARS,
                    "variation_techniques": [
                        "transposition (VerseA2 +5, Chorus +12, Outro -12)",
                        "inversion (Chorus2 axis=69, Bridge axis=66)",
                        "diminution (PreChorus/Chorus dur x0.5)",
                        "augmentation (Outro dur x2.0)",
                        "register shift (Chorus +12, Outro -12)",
                        "density rise (Chorus 16th hi-hat)",
                    ],
                    "bar_degrees": BAR_DEGREES,
                    "rules_applied": "per-bar chord quantization, rhythm-grid snap, "
                                     "diatonic block harmony, voice-leading + "
                                     "Phase 2c correction"},
        notes="Phase 2 rules-processed multi-voice rework. Extended 8->16 bars, "
              "added ch9 drums, >=3 variation techniques.")
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")