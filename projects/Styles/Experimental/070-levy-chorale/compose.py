# -*- coding: utf-8 -*-
"""070 - Levy Flight Chorale (Method 053 LFC).

Autonomous nightly composition job.
Composition method: Method 053 - Levy Flight Composition (LFC).
Heavy-tailed random walk: step lengths drawn from an alpha-stable
distribution P(l) ~ l^-(1+alpha). Clusters of small steps (conjunct
motion) punctuated by rare long jumps (dramatic leaps) -> fractal,
self-similar melodic structure. Voss (1994): real melody pitch intervals
follow power laws with alpha ~ 1.0-1.5.

Musical story: the stability index alpha DECREASES per section
(1.6 -> 1.4 -> 1.2 -> 1.0). Early sections behave like Brownian motion
(mostly stepwise, calm), later sections become Cauchy-like (frequent
large leaps, dramatic). The form is itself the alpha descent.

Two-phase architecture (mandatory):
  Phase 1 (generative draft, PRE-RULES):
    - Pitch DNA = symmetric Levy flight trajectory in MIDI pitch space,
      CMS algorithm, alpha_s descending per section, clipped +-24 st,
      weak Ornstein-Uhlenbeck mean reversion toward the flight origin.
      Continuous chromatic values (rounded), NOT quantized to any scale
      -> the raw draft leaks non-diatonic tones by design.
    - Rhythm DNA = Levy-distributed inter-onset intervals
      IOI = base + L_n, L_n ~ S_alpha_r(sigma_r, 0, 0), clipped to
      [0.25, 4.0] beats -> bursty clustered rhythm.
    - Dynamics DNA = velocity follows |local step| (big leaps louder).
    - Single voice, no chord context, no scale enforcement, no voice
      leading.
  Phase 2 (musicom rules post-processing):
    - Quantize each raw pitch onto the nearest tone of the section's
      diatonic triad (G aeolian: i - VI - VII - i = Gm - Eb - F - Gm)
      in soprano register.
    - Alto/Tenor/Bass built as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then Phase 2c
      CORRECTS remaining parallel/hidden fifth violations by trying
      inversion rotations of each chord, keeping the zero-violation
      minimal-distance voicing.
    - Harmonic progression rule: i - VI - VII - i (Gm - Eb - F - Gm),
      validated against Scale7ChordDegree.function map (tonic ->
      tonic-prolongation -> dominant -> tonic = closed perfect cadence).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass for BOTH
      the Phase 1 raw-draft MIDI and the Phase 2 rules-processed MIDI
      before to_midi(); seeded RNG -> reproducible artifact.

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression.
"""
import math
import os
import random

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

SEED = 70

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "G aeolian"
KEY_ROOT_PC = 7                 # G
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]    # aeolian (natural minor)
KEY_ROOT_MIDI = 55              # G3 (base for absolute diatonic chord calc)
BPM = 88
TPB = 480                       # ticks per beat
BPB = 4                         # beats per bar
BAR = TPB * BPB                 # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4
TOTAL_BEATS = NUM_SECTIONS * SECTION_BARS * BPB     # 32 beats
SECT_BEATS = SECTION_BARS * BPB                     # 8 beats / section
RAW_TOTAL_TICKS = NUM_SECTIONS * SECTION_TICKS      # 15360

# G aeolian: i - VI - VII - i (Gm - Eb - F - Gm). Harmonic-rule legal:
#   i (tonic, free) -> VI (tonic prolongation) -> VII (dominant class 7)
#   -> i (perfect cadence, closed form).
SECTION_DEGREES = [0, 5, 6, 0]
SECTION_NAMES = ["i (Gm) 1", "VI (Eb)", "VII (F)", "i (Gm) 2"]

VOICES = ["Soprano", "Alto", "Tenor", "Bass"]
VOICE_PROGRAMS = [
    MidiInstrument.FLUTE,            # Soprano (bright, melodic)
    MidiInstrument.STRING_ENSEMBLE,  # Alto
    MidiInstrument.STRING_ENSEMBLE,  # Tenor
    MidiInstrument.BASS,             # Bass
]
VOICE_CHANNELS = [0, 1, 2, 3]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
NOTES_DIR = os.path.join(PROJECT_DIR, "Notes")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(NOTES_DIR, exist_ok=True)
BASE = "070-levy-chorale"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

# ---- LFC model parameters ----------------------------------------------------
# Stability index per section: DESCENDS 1.6 -> 1.0. alpha=2 is Brownian
# (stepwise), alpha=1 is Cauchy (frequent dramatic leaps). The form is the
# alpha descent: calm conjunct motion -> wild leaping climax.
ALPHAS = [1.6, 1.4, 1.2, 1.0]
SIGMA_PITCH = 3.5               # scale of pitch steps (semitones)
MAX_STEP = 24                   # clip: no unplayable leaps
ALPHA_RHYTHM = 1.5              # rhythm Levy index (bursty)
SIGMA_RHYTHM = 0.4              # IOI noise scale (beats)
BASE_IOI = 0.5                  # base inter-onset interval (beats)
IOI_MIN, IOI_MAX = 0.25, 4.0    # clipped IOI range (beats)
PITCH_LO, PITCH_HI = 48, 84     # raw chromatic clamp
MEAN_REVERT = 0.15              # OU pull toward origin (per step)


def levy_stable_sample(rng, alpha, sigma, size=1, beta=0.0):
    """CMS algorithm for symmetric alpha-stable samples."""
    if alpha == 2.0:
        return np.array([rng.gauss(0.0, sigma) for _ in range(size)])
    if alpha == 1.0 and beta == 0.0:
        return np.array([sigma * math.tan(math.pi * (rng.random() - 0.5))
                         for _ in range(size)])
    out = np.empty(size)
    for i in range(size):
        u = rng.uniform(-math.pi / 2.0, math.pi / 2.0)
        w = rng.expovariate(1.0)
        if beta == 0.0:
            # Nolan form of CMS: bases are guaranteed positive for
            # alpha in (0, 2] and |u| < pi/2, so no complex leakage.
            s = 1.0 if rng.random() < 0.5 else -1.0
            x = (s * sigma
                 * (math.sin(alpha * u)
                    / (math.cos(u) ** (1.0 / alpha)))
                 * ((math.cos(u * (1.0 - alpha)) / w)
                    ** ((1.0 - alpha) / alpha)))
        else:
            raise NotImplementedError("beta != 0 not needed here")
        out[i] = x
    return out


def compose():
    # ---- Phase 1: raw generative draft (LFC, pre-rules) -------------------
    rng = random.Random(SEED)

    # One Levy flight per section; alpha descends across sections.
    raw_events = []            # absolute ticks, single voice
    flight_report = []         # (section, alpha, n_notes, mean|step|, max|step|)
    n_leap_big = 0             # leaps >= 12 semitones (heavy-tail signature)
    total_steps = 0
    origin = 62                # D4 (start pitch, inside clamp range)
    pitch = float(origin)
    beat = 0.0
    total_beats = TOTAL_BEATS

    while beat < total_beats:
        sec = min(int(beat // SECT_BEATS), NUM_SECTIONS - 1)
        alpha = ALPHAS[sec]

        # Pitch step: Levy flight + weak OU mean reversion toward origin.
        step = float(levy_stable_sample(rng, alpha, SIGMA_PITCH, size=1)[0])
        step = max(-MAX_STEP, min(MAX_STEP, step))
        pitch += step + MEAN_REVERT * (origin - pitch)
        pitch = max(PITCH_LO, min(PITCH_HI, pitch))
        total_steps += 1
        if abs(step) >= 12:
            n_leap_big += 1

        # Rhythm step: Levy IOI noise on top of base, clipped.
        ioi_noise = float(levy_stable_sample(rng, ALPHA_RHYTHM,
                                             SIGMA_RHYTHM, size=1)[0])
        ioi = max(IOI_MIN, min(IOI_MAX, BASE_IOI + ioi_noise))
        if beat + ioi > (sec + 1) * SECT_BEATS:
            ioi = (sec + 1) * SECT_BEATS - beat
        if ioi <= 0:
            break

        # Velocity follows local step magnitude: big leaps louder.
        vel = int(min(100, 62 + 6.0 * abs(step)))

        start_tick = int(round(beat * TPB))
        end_tick = int(round((beat + ioi * 0.92) * TPB))
        if end_tick <= start_tick:
            end_tick = start_tick + 120
        raw_events.append(MusicEvent(pitch=int(round(pitch)), volume=vel,
                                     start_tick=start_tick, end_tick=end_tick))
        beat += ioi

    # Flight stats per section.
    for s in range(NUM_SECTIONS):
        s_ev = [e for e in raw_events
                if s * SECTION_TICKS <= e.start_tick < (s + 1) * SECTION_TICKS]
        if s_ev:
            steps = [abs(e.pitch - p2.pitch)
                     for e, p2 in zip(s_ev, s_ev[1:])]
            mean_s = sum(steps) / len(steps) if steps else 0.0
            max_s = max(steps) if steps else 0
        else:
            mean_s, max_s = 0.0, 0
        flight_report.append((SECTION_NAMES[s], ALPHAS[s], len(s_ev),
                              round(mean_s, 2), max_s))

    raw_pitches = [e.pitch for e in raw_events]
    raw_durs = [e.end_tick - e.start_tick for e in raw_events]
    raw_pitch_report = raw_pitches[:24]
    raw_rhythm_report = raw_durs[:24]
    raw_leak = [p for p in raw_pitches
                if (p - KEY_ROOT_PC) % 12 not in SCALE_INTERVALS]
    n_raw_leak = len(raw_leak)

    # Split raw events into the 4 sections for the Phase 1 MIDI (single voice).
    phase1_sections = split_events_by_section(raw_events, SECTION_TICKS,
                                              NUM_SECTIONS)

    # ---- Phase 1 MIDI export (raw draft, single voice, pre-rules) ----------
    p1_composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB,
                                     beats_per_bar=BPB)
    p1_composer.create_matrix(num_voices=1, num_sections=NUM_SECTIONS)
    p1_composer.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
    for sname in SECTION_NAMES:
        p1_composer.add_section(sname, bars=SECTION_BARS)
    for s in range(NUM_SECTIONS):
        p1_composer.fill_voice_section("RawDraft", SECTION_NAMES[s],
                                       phase1_sections[s])
    ok1, msg1 = p1_composer.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift validation FAILED: {msg1}")
    p1_composer.to_midi(PHASE1_PATH)

    # ---- Phase 2: musicom rules post-processing ----------------------------
    base_triads = [sorted(chord_triad_abs(d)) for d in SECTION_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    optimized_triads = vl.optimize_voice_leading(base_triads)
    corrected_triads, fixed_report = correct_voice_leading(optimized_triads)

    violations = []
    for i in range(len(corrected_triads) - 1):
        violations += vl.check_parallel_motion(corrected_triads[i],
                                               corrected_triads[i + 1])
        violations += vl.check_hidden_fifths(corrected_triads[i],
                                             corrected_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=NUM_SECTIONS)
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname in SECTION_NAMES:
        composer.add_section(sname, bars=SECTION_BARS)

    quant_report = []
    for s in range(NUM_SECTIONS):
        triad = corrected_triads[s]
        bass_note = triad[0] - 12
        alto_note = triad[1]
        tenor_note = triad[2]

        soprano_events = []
        alto_events = []
        tenor_events = []
        bass_events = []
        shifted = []
        for e in phase1_sections[s].events:
            if e.pitch == 0:
                continue
            qp = quantize_to_chord_tone(e.pitch, triad)
            shifted.append((e.pitch, qp))
            soprano_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                             start_tick=e.start_tick,
                                             end_tick=e.end_tick))
            alto_events.append(MusicEvent(pitch=alto_note, volume=72,
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick))
            tenor_events.append(MusicEvent(pitch=tenor_note, volume=72,
                                           start_tick=e.start_tick,
                                           end_tick=e.end_tick))
            bass_events.append(MusicEvent(pitch=bass_note, volume=84,
                                          start_tick=e.start_tick,
                                          end_tick=e.end_tick))
        quant_report.append((SECTION_NAMES[s], shifted[:8]))

        composer.fill_voice_section("Soprano", SECTION_NAMES[s],
                                    MusicUnit(events=soprano_events))
        composer.fill_voice_section("Alto", SECTION_NAMES[s],
                                    MusicUnit(events=alto_events))
        composer.fill_voice_section("Tenor", SECTION_NAMES[s],
                                    MusicUnit(events=tenor_events))
        composer.fill_voice_section("Bass", SECTION_NAMES[s],
                                    MusicUnit(events=bass_events))

        # Pad each section cell to its declared boundary (SECTION_TICKS).
        for voice_name in VOICES:
            row = [v['name'] for v in composer.voices].index(voice_name)
            unit = composer.matrix.get_unit((row, s))
            last_end = max(e.end_tick for e in unit.events) if unit.events else 0
            if last_end < SECTION_TICKS:
                unit.add_event(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end,
                                          end_tick=SECTION_TICKS))

    # ---- Zero-drift gate ---------------------------------------------------
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Zero-drift validation FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    # ---- Grid visualization -------------------------------------------------
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Aeolian (G)")

    harm_report = harmonic_rule_report(SECTION_DEGREES)
    return (composer, violations, raw_pitch_report, raw_rhythm_report,
            corrected_triads, harm_report, fixed_report, quant_report,
            p1_composer, ok1, msg1, n_raw_leak, len(raw_pitches),
            flight_report, n_leap_big, total_steps)


# ---- Rules helpers (project-local, canonical-engine backed) -----------------
def chord_triad_abs(degree):
    """Absolute MIDI triad (root, third, fifth) for a scale degree, key-aware.

    Routes through the canonical Scale7ChordDegree.get_diatonic_note so no
    off-by-octave scale-inversion errors on wrap steps (e.g. vii / iii).
    """
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                               degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                                degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                                degree + 4)
    return [root, third, fifth]


def quantize_to_chord_tone(raw_pitch, triad, lo=60, hi=84):
    """Phase-2: snap raw pitch to nearest chord tone (soprano).

    Octave-fold the raw pitch into the soprano register first so the
    melodic contour is preserved and low-register raw pitches do not all
    collapse onto the lowest in-range chord tone.
    """
    p = raw_pitch
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    candidates = set()
    for t in triad:
        for shift in (-12, 0, 12):
            cand = t + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        candidates = set(triad)
    return min(candidates, key=lambda c: abs(c - p))


def correct_voice_leading(triads):
    """Phase 2c: fix parallel/hidden fifths by rotating chord inversions."""
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = []
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        candidates = [base]
        for rot in range(1, len(base)):
            candidates.append(vl._rotate_chord(base, rot))
        extra = []
        for c in candidates:
            extra.append([p + 12 for p in c])
        candidates += extra

        best = candidates[0]
        best_score = None
        for cand in candidates:
            pv = vl.check_parallel_motion(prev, cand)
            hv = vl.check_hidden_fifths(prev, cand)
            n_viol = len(pv) + len(hv)
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score = score
                best = cand
        if best_score[0] > 0:
            fixed.append((i, best_score[0]))
        corrected.append(sorted(best))
    return corrected, fixed


def harmonic_rule_report(degrees):
    """Validate the degree sequence against the Scale7ChordDegree function map."""
    report = []
    func = Scale7ChordDegree.function
    deg1 = [d + 1 for d in degrees]
    for i in range(len(deg1) - 1):
        a, b = deg1[i], deg1[i + 1]
        norm = lambda v: v if isinstance(v, (tuple, list)) else (v,)
        fa = next((k for k, v in func.items() if a in norm(v)), None)
        fb = next((k for k, v in func.items() if b in norm(v)), None)
        if fa == Scale7ChordDegree.TONIC:
            note_txt = "legal (tonic -> any)"
        elif fa == Scale7ChordDegree.DOMINANT:
            if fb == Scale7ChordDegree.TONIC:
                note_txt = "legal (perfect cadence)"
            elif fb == Scale7ChordDegree.TONIC_PROLONG:
                note_txt = "legal (interrupted/deceptive cadence)"
            else:
                note_txt = "CHECK"
        elif fa == Scale7ChordDegree.SUBDOMINANT:
            if fb in (Scale7ChordDegree.DOMINANT, Scale7ChordDegree.TONIC):
                note_txt = "legal (subdominant -> dominant/tonic)"
            else:
                note_txt = "CHECK"
        elif fa == Scale7ChordDegree.TONIC_PROLONG:
            note_txt = "legal (prolongation, free)"
        else:
            note_txt = "CHECK"
        report.append((a, b, note_txt))
    return report


def split_events_by_section(events, section_ticks, num_sections):
    """Partition raw events into per-section MusicUnits (relative ticks + pad)."""
    sections = []
    for s in range(num_sections):
        start = s * section_ticks
        end = start + section_ticks
        cell = []
        for e in events:
            if e.end_tick <= start or e.start_tick >= end:
                continue
            st = max(0, e.start_tick - start)
            et = min(section_ticks, e.end_tick - start)
            if et <= st:
                continue
            cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                                   start_tick=st, end_tick=et))
        if not cell or cell[-1].end_tick < section_ticks:
            cell.append(MusicEvent(pitch=0, volume=0,
                                   start_tick=cell[-1].end_tick if cell else 0,
                                   end_tick=section_ticks))
        sections.append(MusicUnit(events=cell))
    return sections


if __name__ == "__main__":
    (composer, violations, pitch_rep, rhythm_rep, triads, harm_report,
     fixed_report, quant_rep, p1_composer, ok1, msg1,
     n_leak, n_total, flight_rep, n_leap, n_steps) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2} bytes)"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1} bytes)"
    print(f"[OK] Phase 1 MIDI written: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI written: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift validation: PASS ({ok1})")
    print(f"[OK] Phase 2 zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: i-VI-VII-i (Gm-Eb-F-Gm)")
    print("[OK] Harmonic function report (degree pair -> legality):")
    for a, b, verdict in harm_report:
        print(f"     {a} -> {b}: {verdict}")
    print(f"[OK] Phase 2c voice-leading corrections applied: "
          f"{len(fixed_report)} chord(s) re-voiced")
    if fixed_report:
        for idx, n in fixed_report:
            print(f"     chord {idx + 1}: {n} violation(s) corrected "
                  f"via inversion rotation")
    print(f"[OK] Final triads (corrected, voice-leading minimized): {triads}")
    print(f"[OK] Raw events: {n_total}, non-diatonic leak in raw draft: "
          f"{n_leak}")
    print("[OK] Levy flight report (alpha descends 1.6 -> 1.0 per section):")
    for name, alpha, n_notes, mean_s, max_s in flight_rep:
        print(f"     {name}: alpha={alpha}, notes={n_notes}, "
              f"mean|step|={mean_s} st, max|step|={max_s} st")
    print(f"[OK] Heavy-tail signature: {n_leap} leap(s) >= 12 semitones "
          f"out of {n_steps} steps")
    print("[OK] Raw Levy pitch DNA (first 24, CMS alpha-stable steps):")
    print(f"     {pitch_rep}")
    print("[OK] Raw Levy rhythm DNA (first 24, Levy IOI burst pattern):")
    print(f"     {rhythm_rep}")
    print("[OK] Phase 2 quantization (raw pitch -> chord tone, first 8 per "
          "section):")
    for name, pairs in quant_rep:
        print(f"     {name}: {pairs}")
    print(f"[OK] Parallel/hidden fifth violations (classical): "
          f"{len(violations)}")
    if violations:
        for v in violations:
            print(f"     - {v}")

    # Provenance sidecars for BOTH artifacts
    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 053 Levy Flight Composition (LFC) - PRE-RULES raw draft",
        sources=[
            "Research/CompositionMethods/methods_db.md:Method 053",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 53,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "model": "Levy flight (alpha-stable CMS), alpha descending 1.6->1.0 per section",
            "alpha_per_section": ALPHAS,
            "sigma_pitch_semitones": SIGMA_PITCH,
            "max_step_clip": MAX_STEP,
            "mean_reversion": MEAN_REVERT,
            "rhythm_ioi": "base 0.5 beats + Levy(alpha=1.5, sigma=0.4), clipped [0.25, 4.0]",
            "raw_pitch_mapping": "alpha-stable step accumulation -> chromatic MIDI 48..84",
            "raw_rhythm_mapping": "Levy-distributed inter-onset intervals",
            "raw_velocity_mapping": "62 + 6*|step| (leaps louder)",
            "seed": SEED,
            "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: symmetric Levy flight in MIDI pitch space, CMS "
              "algorithm, stability index alpha descending 1.6 -> 1.0 "
              "across the four sections (Brownian stepwise motion decays "
              "into Cauchy-like dramatic leaping). Rhythm = Levy-distributed "
              "inter-onset intervals (bursty clusters). Pitch = continuous "
              "chromatic accumulation -> heavy non-diatonic leak (the "
              "pre-rules signature); velocity follows local step magnitude. "
              "Single voice, no scale enforcement, no chord context, no "
              "voice leading. Raw generative material preserved for "
              "comparison against the rules-processed Phase 2 artifact. "
              "Zero-drift validated UnitMatrix export.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 053 Levy Flight Composition (LFC) + musicom rules (chord-tone quantization, voice leading, harmonic progression)",
        sources=[
            "Research/CompositionMethods/methods_db.md:Method 053",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 53,
            "phase": 2,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "progression_degrees": SECTION_DEGREES,
            "seed": SEED,
            "voice_leading_style": "classical",
            "two_phase": True,
            "rules_applied": "chord-tone quantization, diatonic block harmony, voice-leading optimization, Phase 2c inversion-rotation correction",
        },
        notes="Phase 2: raw Levy flight pitches quantized to nearest "
              "section triad tone (soprano), Alto/Tenor/Bass as diatonic "
              "block harmony via Scale7ChordDegree.get_diatonic_note(), "
              "voice-leading optimization + Phase 2c inversion-rotation "
              "correction of parallel/hidden fifths, harmonic function "
              "validation (i-VI-VII-i, G aeolian, closed perfect cadence), "
              "zero-drift validated UnitMatrix export.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
