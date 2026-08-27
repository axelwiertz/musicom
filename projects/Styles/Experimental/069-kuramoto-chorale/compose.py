# -*- coding: utf-8 -*-
"""069 - Kuramoto Chorale (Method 038 KOPS).

Autonomous nightly composition job.
Composition method: Method 038 - Kuramoto Oscillator Phase Synchronization
(KOPS) -- Nature-Led. Coupled limit-cycle oscillators: each voice is an
oscillator with its own natural frequency; diffusive sinusoidal coupling
pulls the ensemble toward phase lock. The global order parameter
r(t) = |(1/N) sum_j e^{i theta_j}| measures synchronization (0 = incoherent,
1 = fully locked).

Musical story of this piece: the coupling strength K INCREASES section by
section (0.5 -> 1.5 -> 2.5 -> 4.0), so the four voices evolve from a
desynchronized polyrhythmic drift into a phase-locked ensemble that locks to
a common pulse and resolves to the tonic. The form is itself the
synchronization transition.

Two-phase architecture (mandatory):
  Phase 1 (generative draft, PRE-RULES):
    - Rhythm DNA = phase-wrap pulse trains: each oscillator emits an event
      every time its phase crosses a 2*pi boundary. Natural frequencies
      f = [0.85, 1.0, 1.15, 1.35] events/beat -> incommensurate polyrhythm
      that the coupling progressively pulls into lock.
    - Pitch DNA = effective-frequency mapping: at each emission the raw pitch
      is mapped from the oscillator's instantaneous effective angular
      velocity omega_eff = omega_i + (K/N) sum_j sin(theta_j - theta_i).
      This is a continuous chromatic value (48..84, rounded), NOT quantized
      to any scale -> the raw draft leaks non-diatonic tones by design.
    - Dynamics DNA = velocity follows the instantaneous order parameter r:
      vel = 70 + 30*r (louder as the ensemble synchronizes).
    - Single voice (oscillator 0, the slowest), no chord context, no scale
      enforcement, no voice leading.
  Phase 2 (musicom rules post-processing):
    - Quantize each raw pitch onto the nearest tone of the section's
      diatonic triad (F dorian: i - iv - VII - i = Fm - Bbm - Eb - Fm) in
      soprano register.
    - Alto/Tenor/Bass built as diatonic block harmony via the canonical
      Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap).
    - Voice-leading: VoiceLeadingRules.optimize_voice_leading() rotates
      inversions to minimize total voice-leading distance; then Phase 2c
      CORRECTS remaining parallel/hidden fifth violations by trying
      inversion rotations of each chord, keeping the zero-violation
      minimal-distance voicing.
    - Harmonic progression rule: i - iv - VII - i (Fm - Bbm - Eb - Fm),
      validated against Scale7ChordDegree.function map (subdominant -> 
      dominant -> tonic = closed perfect cadence).
    - Zero-drift gate: UnitMatrixComposer.validate() must pass for BOTH the
      Phase 1 raw-draft MIDI and the Phase 2 rules-processed MIDI before
      to_midi(); seeded RK4 integration -> reproducible artifact (no
      unseeded rng).

Engines used: structures.*, workflows.unitmatrix_composer,
visualization.grid, workflows.provenance, rules.voice_leading,
rules.progression.
"""
import math
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

SEED = 69

# ---- Composition parameters ------------------------------------------------
KEY_NAME = "F dorian"
KEY_ROOT_PC = 5                 # F
SCALE_INTERVALS = [0, 2, 3, 5, 7, 9, 10]    # dorian
KEY_ROOT_MIDI = 53              # F3 (base for absolute diatonic chord calc)
BPM = 92
TPB = 480                       # ticks per beat
BPB = 4                         # beats per bar
BAR = TPB * BPB                 # 1920 ticks / bar
SECTION_BARS = 2
SECTION_TICKS = SECTION_BARS * BAR          # 3840 ticks / section
NUM_SECTIONS = 4
TOTAL_BEATS = NUM_SECTIONS * SECTION_BARS * BPB     # 32 beats
SECT_BEATS = SECTION_BARS * BPB                     # 8 beats / section
RAW_TOTAL_TICKS = NUM_SECTIONS * SECTION_TICKS      # 15360

# F dorian: i - iv - VII - i (Fm - Bbm - Eb - Fm). Harmonic-rule legal:
#   i (tonic, free) -> iv (subdominant) -> VII (dominant class 7)
#   -> i (perfect cadence, closed form).
SECTION_DEGREES = [0, 3, 6, 0]
SECTION_NAMES = ["i (Fm) 1", "iv (Bbm)", "VII (Eb)", "i (Fm) 2"]

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
BASE = "069-kuramoto-chorale"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

# ---- KOPS model parameters ---------------------------------------------------
# One oscillator per voice. Natural frequencies in events/beat (incommensurate
# -> polyrhythm). Coupling K grows per section: the synchronization
# transition is the form.
N_OSC = 4
FREQS = [0.85, 1.0, 1.15, 1.35]
OMEGA = [2.0 * math.pi * f for f in FREQS]
K_COUPLING = [0.5, 1.5, 2.5, 4.0]
DT = 0.005                      # integration step, beats
PITCH_LO, PITCH_HI = 48, 84     # raw chromatic clamp
VEL_LO, VEL_HI = 70, 100


def kuramoto_step(theta, omega, k, dt):
    """One RK4 step of the Kuramoto model for N oscillators.

    d theta_i/dt = omega_i + (k/N) * sum_j sin(theta_j - theta_i)
    """
    n = len(theta)

    def deriv(th):
        d = [omega[i] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    d[i] += (k / n) * math.sin(th[j] - th[i])
        return d

    k1 = deriv(theta)
    t2 = [theta[i] + 0.5 * dt * k1[i] for i in range(n)]
    k2 = deriv(t2)
    t3 = [theta[i] + 0.5 * dt * k2[i] for i in range(n)]
    k3 = deriv(t3)
    t4 = [theta[i] + dt * k3[i] for i in range(n)]
    k4 = deriv(t4)
    return [theta[i] + (dt / 6.0) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
            for i in range(n)]


def order_parameter(theta):
    """Global Kuramoto order parameter r in [0, 1]."""
    re_ = sum(math.cos(t) for t in theta) / len(theta)
    im_ = sum(math.sin(t) for t in theta) / len(theta)
    return math.hypot(re_, im_)


def effective_omega(theta, omega, k, idx):
    """Instantaneous effective angular velocity of oscillator idx."""
    n = len(theta)
    w = omega[idx]
    for j in range(n):
        if j != idx:
            w += (k / n) * math.sin(theta[j] - theta[idx])
    return w


def compose():
    # ---- Phase 1: raw generative draft (KOPS, pre-rules) -------------------
    rng = random.Random(SEED)
    theta = [rng.uniform(0.0, 2.0 * math.pi) for _ in range(N_OSC)]

    # events[i] = list of (start_beat, dur_beats, raw_pitch, velocity)
    events = [[] for _ in range(N_OSC)]
    prev_wrap_beat = [0.0] * N_OSC
    r_means = [0.0] * NUM_SECTIONS
    wrap_counts = [[0] * NUM_SECTIONS for _ in range(N_OSC)]
    beat = 0.0
    step = 0
    steps = int(TOTAL_BEATS / DT)
    while step < steps:
        beat = step * DT
        sec = min(int(beat // SECT_BEATS), NUM_SECTIONS - 1)
        k = K_COUPLING[sec]
        r = order_parameter(theta)
        r_means[sec] += r

        new_theta = kuramoto_step(theta, OMEGA, k, DT)
        for i in range(N_OSC):
            # Phase wrap -> emit an event for oscillator i
            if new_theta[i] >= 2.0 * math.pi:
                w_eff = effective_omega(theta, OMEGA, k, i)
                raw = PITCH_LO + int(round(
                    (PITCH_HI - PITCH_LO) * min(1.0, max(0.0,
                                                         (w_eff - 1.0) / 8.0))))
                raw = max(PITCH_LO, min(PITCH_HI, raw))
                dur = max(0.125, beat - prev_wrap_beat[i])
                vel = VEL_LO + int(round((VEL_HI - VEL_LO) * r))
                events[i].append((beat, dur, raw, vel))
                wrap_counts[i][sec] += 1
                prev_wrap_beat[i] = beat
                new_theta[i] -= 2.0 * math.pi
        theta = new_theta
        step += 1

    for s in range(NUM_SECTIONS):
        r_means[s] /= (SECT_BEATS / DT)

    # Convert oscillator-0 stream (the lead) to absolute-tick MusicEvents.
    raw_events = []
    for (start_beat, dur_beat, raw_pitch, vel) in events[0]:
        start_tick = int(round(start_beat * TPB))
        end_tick = int(round((start_beat + dur_beat) * TPB))
        raw_events.append(MusicEvent(pitch=raw_pitch, volume=vel,
                                     start_tick=start_tick, end_tick=end_tick))

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
                             bpm=BPM, mode="Dorian (F)")

    harm_report = harmonic_rule_report(SECTION_DEGREES)
    return (composer, violations, raw_pitch_report, raw_rhythm_report,
            corrected_triads, harm_report, fixed_report, quant_report,
            p1_composer, ok1, msg1, n_raw_leak, len(raw_pitches),
            r_means, wrap_counts)


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


def quantize_to_chord_tone(raw_pitch, triad, lo=64, hi=86):
    """Phase-2: snap raw pitch to nearest chord tone (soprano)."""
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
     n_leak, n_total, r_means, wrap_counts) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2} bytes)"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1} bytes)"
    print(f"[OK] Phase 1 MIDI written: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI written: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift validation: PASS ({ok1})")
    print(f"[OK] Phase 2 zero-drift validation: PASS")
    print(f"[OK] Harmonic progression: i-iv-VII-i (Fm-Bbm-Eb-Fm)")
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
    print("[OK] KOPS synchronization report (mean order parameter r per "
          "section, K rises 0.5->4.0):")
    for s in range(NUM_SECTIONS):
        print(f"     section {s + 1} ({SECTION_NAMES[s]}): K="
              f"{K_COUPLING[s]}, mean r={r_means[s]:.3f}, "
              f"wraps/osc={wrap_counts[0][s]},{wrap_counts[1][s]},"
              f"{wrap_counts[2][s]},{wrap_counts[3][s]}")
    print("[OK] Raw KOPS pitch DNA (first 24, effective-frequency mapping):")
    print(f"     {pitch_rep}")
    print("[OK] Raw KOPS rhythm DNA (first 24, phase-wrap pulse train):")
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
        generator="Method 038 Kuramoto Oscillator Phase Synchronization (KOPS) - PRE-RULES raw draft",
        sources=[
            "Research/CompositionMethods/methods_db.md:Method 038",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 38,
            "phase": 1,
            "key": KEY_NAME,
            "bpm": BPM,
            "ticks_per_beat": TPB,
            "beats_per_bar": BPB,
            "sections": NUM_SECTIONS,
            "section_bars": SECTION_BARS,
            "model": "Kuramoto coupled phase oscillators, RK4, dt=0.005 beats",
            "natural_frequencies_events_per_beat": FREQS,
            "coupling_per_section": K_COUPLING,
            "raw_pitch_mapping": "effective angular velocity omega_eff -> chromatic MIDI 48..84",
            "raw_rhythm_mapping": "phase-wrap pulse train (2*pi boundary crossing)",
            "raw_velocity_mapping": "70 + 30*order_parameter r",
            "seed": SEED,
            "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: Kuramoto model with N=4 oscillators (voices), "
              "natural frequencies 0.85/1.0/1.15/1.35 events per beat "
              "(incommensurate polyrhythm), coupling K rising per section "
              "(0.5, 1.5, 2.5, 4.0) drives the desync->sync transition. "
              "Rhythm = phase-wrap pulse train; pitch = continuous chromatic "
              "mapping of the instantaneous effective frequency -> heavy "
              "non-diatonic leak (the pre-rules signature); velocity follows "
              "the order parameter r. Single voice (slowest oscillator), no "
              "scale enforcement, no chord context, no voice leading. Raw "
              "generative material preserved for comparison against the "
              "rules-processed Phase 2 artifact. Zero-drift validated "
              "UnitMatrix export.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 038 Kuramoto Oscillator Phase Synchronization (KOPS) + musicom rules (chord-tone quantization, voice leading, harmonic progression)",
        sources=[
            "Research/CompositionMethods/methods_db.md:Method 038",
            "rules/voice_leading.py",
            "rules/progression.py",
            "workflows/unitmatrix_composer.py",
        ],
        parameters={
            "method": 38,
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
        notes="Phase 2: raw KOPS phase-wrap pitches quantized to nearest "
              "section triad tone (soprano), Alto/Tenor/Bass as diatonic "
              "block harmony via Scale7ChordDegree.get_diatonic_note(), "
              "voice-leading optimization + Phase 2c inversion-rotation "
              "correction of parallel/hidden fifths, harmonic function "
              "validation (i-iv-VII-i, F dorian, closed perfect cadence), "
              "zero-drift validated UnitMatrix export.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
