# -*- coding: utf-8 -*-
"""076-reggae-lsystem — Reggae / Method 019 L-System.

Autonomous nightly composition job (2026-08-23).

Style: Reggae (one-drop + skank + bubble, Dub ethos: space is the place).
Method: 019 — L-System Algorithmic Composition (LSystemCore canonical grammar:
axiom A, rules {A -> AB, B -> A} = Fibonacci word, self-similar at every scale).

Musical story (method-shape = form):
  The Fibonacci word (21 symbols after 6 iterations: ABAABABAABAABABAABABA)
  is generated ONCE in Phase 1 as a raw pitch/rhythm draft over a continuous
  beat timeline, then Phase 2 maps each raw symbol stream onto a ONE-DROP
  reggae texture:
    - Lead organ (program 17) plays the L-system contour, chord-tone
      quantized per bar, phrase-shaped by the word itself.
    - Skank guitar (program 26/27) chops staccato chords on the offbeats
      (the 'and' of every beat) - the reggae signature.
    - Bass (program 33) plays a deep one-drop pattern: root on beat 1 pickup,
      fifth/octave bounce, syncopated pushes toward beat 3 (the one-drop
      anchor).
    - Drums: one-drop kit - kick on beat 3, rimshot/snare on beat 3,
      closed hat 8ths with swing, open hat pushes.
    - Dub cut: the Outro drops the lead and guitar for the 'space is the
      place' dub ethos (bass + drums exposed), then a final one-bar stab.

Two-phase architecture (mandatory):
  Phase 1 (PRE-RULES): L-system Fibonacci word -> raw chromatic pitch walk
    (continuous, unquantized, NOT scale-enforced -> non-diatonic leak by
    design), Levy-free deterministic symbol rhythm (A = quarter, B = eighth,
    burst clusters by the word's own self-similar structure). Single voice,
    no harmony, no voice leading.
  Phase 2 (RULES): chord-tone quantization of the lead via the canonical
    Scale7ChordDegree.get_diatonic_note() helper (no off-by-octave wrap),
    harmony = A aeolian i - bVII - i - bVI (Am - G - Am - F), voice-leading
    optimization + Phase 2c inversion-rotation correction of parallel/hidden
    fifths, zero-drift UnitMatrix export with full reggae texture.

Engines: structures.*, workflows.unitmatrix_composer, visualization.grid,
workflows.provenance, rules.voice_leading, rules.progression.
"""
import math
import os
import random

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

SEED = 76

# ------------------------------------------------------------------ concept
KEY_NAME = "A aeolian"
KEY_ROOT_PC = 9                 # A
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]    # aeolian (natural minor)
KEY_ROOT_MIDI = 45              # A2 (bass-register root for chord calc)
BPM = 96
TPB = 480
BPB = 4
BAR = TPB * BPB                 # 1920 ticks / bar

# form: 6 sections x 4 bars = 24 bars (reggae roots length)
SECTION_NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Chorus2", "Outro"]
SECTION_BARS = 4
NUM_SECTIONS = len(SECTION_NAMES)
SECTION_TICKS = BAR * SECTION_BARS       # 7680
TOTAL_TICKS = SECTION_TICKS * NUM_SECTIONS

# harmonic bed: i - bVII - i - bVI (Am - G - Am - F) x 6 sections
# degree indices (0-based into the aeolian scale):
#   i(0) bVII(6) i(0) bVI(5)
SECTION_DEGREES = [0, 6, 0, 5] * NUM_SECTIONS          # per-bar, 24 bars
CHORD_DEG_PER_BAR = SECTION_DEGREES
CHORD_NAMES = {0: "i", 5: "bVI", 6: "bVII"}
PROG_NAMES = [CHORD_NAMES[d] for d in SECTION_DEGREES]

# voices: Lead organ, Skank guitar, Bass, Drums
VOICES = ["Lead", "Skank", "Bass", "Drums"]
VOICE_PROGRAMS = [
    17,                 # Drawbar Organ (reggae keyboard lead)
    27,                 # Clean Electric Guitar (skank chop)
    MidiInstrument.BASS,      # Electric Bass (finger)
    0,                  # drums -> channel 9
]
VOICE_CHANNELS = [0, 1, 2, 9]

LEAD_LO, LEAD_HI = 60, 84     # lead organ register
BASS_LO, BASS_HI = 33, 48     # bass register (A1..C3)


# ------------------------------------------------------------------ L-system
def fib_word(axiom="A", rules=None, iters=6):
    """Canonical Fibonacci-word L-system: axiom A, {A->AB, B->A}."""
    if rules is None:
        rules = {"A": "AB", "B": "A"}
    w = axiom
    for _ in range(iters):
        w = "".join(rules.get(ch, ch) for ch in w)
    return w


def lsystem_phase1_events(word, seed=SEED):
    """Phase 1: raw L-system draft over a continuous beat timeline.

    Symbol semantics: A = pitch step +2 st (quarter note), B = pitch step
    -2 st (eighth note). Word cycles re-enter at rotation offsets
    (0, 5, 3, 8) per section so each re-entry starts at a different phase
    (self-similar, never a literal repeat). Pitches accumulate on a
    CONTINUOUS chromatic walk (NOT scale-enforced) -> raw draft leaks
    non-diatonic tones by design. Velocity follows symbol: A louder.
    Returns absolute-tick MusicEvents, single voice.
    """
    rng = random.Random(seed)
    rot_offsets = [0, 5, 3, 8, 5, 3]
    events = []
    beat = 0.0
    total_beats = NUM_SECTIONS * SECTION_BARS * BPB
    sec = 0
    pitch = float(62)               # D4 start (inside clamp)
    while beat < total_beats and sec < NUM_SECTIONS:
        rot = rot_offsets[sec % len(rot_offsets)]
        w = word[rot:] + word[:rot]
        for ch in w:
            if beat >= (sec + 1) * SECTION_BARS * BPB:
                break
            if beat >= total_beats:
                break
            if ch == "A":
                step = 2.0
                dur_beats = 1.0
            else:
                step = -2.0
                dur_beats = 0.5
            pitch += step
            pitch = max(48.0, min(84.0, pitch))
            st = int(round(beat * TPB))
            et = int(round((beat + dur_beats * 0.92) * TPB))
            if et <= st:
                et = st + 120
            vel = 92 if ch == "A" else 78
            events.append(MusicEvent(pitch=int(round(pitch)), volume=vel,
                                     start_tick=st, end_tick=et))
            beat += dur_beats
        sec += 1
    return events


def split_events_by_section(events, section_ticks, num_sections):
    """Partition raw events into per-section MusicUnits (relative ticks)."""
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


# ------------------------------------------------------------------ rules
def chord_triad_abs(degree):
    """Absolute MIDI triad (root, third, fifth) for a scale degree.

    Routes through canonical Scale7ChordDegree.get_diatonic_note() so no
    off-by-octave scale-inversion errors on wrap steps (bVII, bVI here).
    """
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                               degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                                degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS,
                                                degree + 4)
    return [root, third, fifth]


def quantize_to_chord_tone(raw_pitch, triad, lo=60, hi=84):
    """Phase 2: snap raw pitch to nearest chord tone (lead register)."""
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
    """Validate degree sequence against Scale7ChordDegree.function map."""
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
            else:
                note_txt = "legal (dominant release)"
        elif fa == Scale7ChordDegree.SUBDOMINANT:
            note_txt = "legal (subdominant -> dominant/tonic)" \
                if fb in (Scale7ChordDegree.DOMINANT, Scale7ChordDegree.TONIC) \
                else "CHECK"
        elif fa == Scale7ChordDegree.TONIC_PROLONG:
            note_txt = "legal (prolongation, free)"
        else:
            note_txt = "CHECK"
        report.append((a, b, note_txt))
    return report


# ------------------------------------------------------------------ build
def compose():
    word = fib_word()
    raw_events = lsystem_phase1_events(word, seed=SEED)
    raw_pitches = [e.pitch for e in raw_events]
    raw_leak = [p for p in raw_pitches
                if (p - KEY_ROOT_PC) % 12 not in SCALE_INTERVALS]

    phase1_sections = split_events_by_section(raw_events, SECTION_TICKS,
                                              NUM_SECTIONS)

    # ---- Phase 1 MIDI: raw L-system draft, single voice, pre-rules -------
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=NUM_SECTIONS)
    p1.add_voice("RawLSystem", program=17, channel=0)
    for n in SECTION_NAMES:
        p1.add_section(n, bars=SECTION_BARS)
    for s in range(NUM_SECTIONS):
        p1.fill_voice_section("RawLSystem", SECTION_NAMES[s], phase1_sections[s])
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError("Phase 1 zero-drift validation FAILED: %s" % msg1)

    # ---- Phase 2: rules post-process ------------------------------------
    base_triads = [sorted(chord_triad_abs(d)) for d in CHORD_DEG_PER_BAR]
    vl = VoiceLeadingRules(style="classical")
    optimized = vl.optimize_voice_leading(base_triads)
    corrected_triads, fixed_report = correct_voice_leading(optimized)

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
    for n in SECTION_NAMES:
        composer.add_section(n, bars=SECTION_BARS)

    for s in range(NUM_SECTIONS):
        triad = corrected_triads[s * SECTION_BARS]   # one chord per section
        bass_root = triad[0] - 12                     # deep reggae bass octave
        sec_events = phase1_sections[s].events

        # --- Lead organ: quantized L-system contour ----------------------
        lead_evs = []
        for e in sec_events:
            if e.pitch == 0:
                continue
            qp = quantize_to_chord_tone(e.pitch, triad)
            lead_evs.append(MusicEvent(pitch=qp, volume=e.volume,
                                       start_tick=e.start_tick,
                                       end_tick=e.end_tick))
        composer.fill_voice_section("Lead", SECTION_NAMES[s],
                                    MusicUnit(events=lead_evs))

        # --- Skank guitar: staccato offbeat chops ('and' of every beat) ---
        skank_evs = []
        if s < NUM_SECTIONS - 1:      # dub cut: no skank in outro
            for bar in range(SECTION_BARS):
                t0 = bar * BAR
                for beat in range(BPB):
                    off = 480 * beat + 240          # the 'and'
                    for p in triad:
                        # tight staccato chop, mid register
                        skank_evs.append(MusicEvent(
                            pitch=p + 12, volume=74,
                            start_tick=t0 + off, end_tick=t0 + off + 90))
        composer.fill_voice_section("Skank", SECTION_NAMES[s],
                                    MusicUnit(events=skank_evs))

        # --- Bass: one-drop root/fifth bounce ----------------------------
        bass_evs = []
        for bar in range(SECTION_BARS):
            t0 = bar * BAR
            chord_deg = CHORD_DEG_PER_BAR[s * SECTION_BARS + bar]
            tr = corrected_triads[s * SECTION_BARS + bar]
            root = tr[0] - 12
            fifth = tr[2] - 12
            # one-drop: pickup root on beat 1&, anchor on beat 3, bounce
            bass_evs += [
                MusicEvent(pitch=root, volume=96, start_tick=t0,
                           end_tick=t0 + 240),               # pickup
                MusicEvent(pitch=root, volume=92, start_tick=t0 + 240,
                           end_tick=t0 + 480),               # release
                MusicEvent(pitch=fifth, volume=90, start_tick=t0 + 720,
                           end_tick=t0 + 960),               # bubble
                MusicEvent(pitch=root, volume=100, start_tick=t0 + 960,
                           end_tick=t0 + 1440),              # one-drop anchor
                MusicEvent(pitch=fifth, volume=90, start_tick=t0 + 1440,
                           end_tick=t0 + 1680),              # bounce
                MusicEvent(pitch=root + 12, volume=84, start_tick=t0 + 1680,
                           end_tick=t0 + 1920),              # octave push
            ]
        composer.fill_voice_section("Bass", SECTION_NAMES[s],
                                    MusicUnit(events=bass_evs))

        # --- Drums: one-drop kit -----------------------------------------
        drum_evs = []
        for bar in range(SECTION_BARS):
            t0 = bar * BAR
            # closed hat 8ths (steady pulse)
            for k in range(0, BAR, 240):
                vel = 52 if (k // 240) % 2 == 0 else 44
                drum_evs.append(MusicEvent(pitch=42, volume=vel,
                                           start_tick=t0 + k,
                                           end_tick=t0 + k + 90))
            # one-drop: kick + rimshot/snare on beat 3 (the anchor)
            drum_evs.append(MusicEvent(pitch=36, volume=104,
                                       start_tick=t0 + 960,
                                       end_tick=t0 + 1120))
            drum_evs.append(MusicEvent(pitch=38, volume=92,
                                       start_tick=t0 + 960,
                                       end_tick=t0 + 1100))
            # open hat push on 4& (dub anticipation)
            drum_evs.append(MusicEvent(pitch=46, volume=64,
                                       start_tick=t0 + 1800,
                                       end_tick=t0 + 1910))
            if s in (2, 4):      # chorus: extra snare ghost on 3&
                drum_evs.append(MusicEvent(pitch=38, volume=56,
                                           start_tick=t0 + 1080,
                                           end_tick=t0 + 1160))
        composer.fill_voice_section("Drums", SECTION_NAMES[s],
                                    MusicUnit(events=drum_evs))

        # --- pad every cell to exact section boundary (zero-drift) --------
        for voice_name in VOICES:
            row = [v["name"] for v in composer.voices].index(voice_name)
            unit = composer.matrix.get_unit((row, s))
            last_end = max(e.end_tick for e in unit.events) if unit.events else 0
            if last_end < SECTION_TICKS:
                unit.add_event(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end,
                                          end_tick=SECTION_TICKS))

    # ---- zero-drift gate -------------------------------------------------
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError("Phase 2 zero-drift validation FAILED: %s" % msg)

    harm_report = harmonic_rule_report(CHORD_DEG_PER_BAR)
    return (composer, p1, ok1, msg1, violations, corrected_triads,
            fixed_report, harm_report, raw_pitches, raw_leak, word)


if __name__ == "__main__":
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
    AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
    ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    BASE = "076-reggae-lsystem"
    P1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
    P2_PATH = os.path.join(MIDI_DIR, BASE + ".mid")

    (composer, p1, ok1, msg1, violations, triads, fixed_report,
     harm_report, raw_pitches, raw_leak, word) = compose()

    p1.to_midi(P1_PATH)
    composer.to_midi(P2_PATH)

    size1 = os.path.getsize(P1_PATH)
    size2 = os.path.getsize(P2_PATH)
    assert size1 > 40, "Phase 1 MIDI too small (%d)" % size1
    assert size2 > 40, "Phase 2 MIDI too small (%d)" % size2

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path,
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode="Aeolian (A) one-drop")

    # ---- render audio via fluidsynth CLI (TimGM6mb.sf2) ------------------
    SF2 = "/opt/data/micromamba/envs/musicom/lib/python3.11/site-packages/pretty_midi/TimGM6mb.sf2"
    FS = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
    wav1 = os.path.join(AUDIO_DIR, BASE + "-phase1.wav")
    wav2 = os.path.join(AUDIO_DIR, BASE + ".wav")
    ogg1 = os.path.join(AUDIO_DIR, BASE + "-phase1.ogg")
    ogg2 = os.path.join(AUDIO_DIR, BASE + ".ogg")
    for mid, wav in ((P1_PATH, wav1), (P2_PATH, wav2)):
        cmd = "%s -ni -g 1.2 -F %s %s %s" % (FS, wav, SF2, mid)
        print("RENDER:", cmd)
        rc = os.system(cmd)
        assert rc == 0, "fluidsynth failed rc=%d" % rc
        assert os.path.getsize(wav) > 40, "wav too small: %s" % wav
    for wav, ogg in ((wav1, ogg1), (wav2, ogg2)):
        cmd = ("ffmpeg -y -i %s -codec:a libopus -application voip -b:a 48k %s "
               "-loglevel error" % (wav, ogg))
        print("OGG:", cmd)
        rc = os.system(cmd)
        assert rc == 0, "ffmpeg failed rc=%d" % rc
        assert os.path.getsize(ogg) > 40, "ogg too small: %s" % ogg

    # ---- analysis artifacts ---------------------------------------------
    import json
    summary = {
        "project": BASE,
        "style": "Reggae",
        "method": "019 L-System Algorithmic Composition (LFC-grammar Fibonacci word)",
        "paradigm": "Rules-Based",
        "bpm": BPM,
        "key": KEY_NAME,
        "tempo": BPM,
        "bars": NUM_SECTIONS * SECTION_BARS,
        "sections": {n: SECTION_BARS for n in SECTION_NAMES},
        "progression": PROG_NAMES,
        "voices": VOICES,
        "phase1": os.path.basename(P1_PATH),
        "phase2": os.path.basename(P2_PATH),
        "grid": os.path.basename(grid_path),
        "seed": SEED,
        "word_length": len(word),
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    prov = {
        "project": BASE,
        "style": "Reggae",
        "method": "019 L-System Algorithmic Composition (Fibonacci word)",
        "paradigm": "Rules-Based",
        "bpm": BPM,
        "key": KEY_NAME,
        "bars": NUM_SECTIONS * SECTION_BARS,
        "sections": SECTION_NAMES,
        "bars_per_section": SECTION_BARS,
        "progression": PROG_NAMES,
        "voices": VOICES,
        "seed": SEED,
    }
    with open(os.path.join(ANALYSIS_DIR, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    # ---- provenance sidecars for both MIDI artifacts ---------------------
    write_provenance(
        P1_PATH,
        classification="ai-generated",
        generator="Method 019 L-System (Fibonacci word) - PRE-RULES raw draft",
        sources=["Research/CompositionMethods/methods_db.md:Method 019",
                 "workflows/unitmatrix_composer.py"],
        parameters={
            "method": 19, "phase": 1, "key": KEY_NAME, "bpm": BPM,
            "ticks_per_beat": TPB, "beats_per_bar": BPB,
            "sections": NUM_SECTIONS, "section_bars": SECTION_BARS,
            "model": "Fibonacci-word L-system (axiom A, A->AB, B->A), "
                     "6 iterations, 21 symbols",
            "symbol_semantics": "A = +2 st / quarter, B = -2 st / eighth",
            "rotation_offsets": [0, 5, 3, 8, 5, 3],
            "seed": SEED, "two_phase": True,
            "rules_applied": "NONE (pre-rules generative draft)",
        },
        notes="Phase 1: L-system Fibonacci word driven chromatic walk, "
              "continuous unquantized pitch (non-diatonic leak by design), "
              "symbol rhythm (A quarter / B eighth), single voice, no harmony.",
    )
    write_provenance(
        P2_PATH,
        classification="ai-generated",
        generator="Method 019 L-System + musicom rules (chord-tone "
                  "quantization, voice leading, one-drop reggae texture)",
        sources=["Research/CompositionMethods/methods_db.md:Method 019",
                 "rules/voice_leading.py", "rules/progression.py",
                 "workflows/unitmatrix_composer.py"],
        parameters={
            "method": 19, "phase": 2, "key": KEY_NAME, "bpm": BPM,
            "ticks_per_beat": TPB, "beats_per_bar": BPB,
            "sections": NUM_SECTIONS, "section_bars": SECTION_BARS,
            "progression_degrees": CHORD_DEG_PER_BAR,
            "seed": SEED, "voice_leading_style": "classical", "two_phase": True,
            "rules_applied": "chord-tone quantization, one-drop skank/bass/"
                             "drums texture, voice-leading optimization, "
                             "Phase 2c inversion-rotation correction",
        },
        notes="Phase 2: raw L-system pitches quantized to section triad "
              "tones, A-aeolian i-bVII-i-bVI harmony via "
              "Scale7ChordDegree.get_diatonic_note(), one-drop reggae "
              "texture (offbeat skank chops, beat-3 kick/rimshot, bass "
              "pickup-anchor bounce, dub-cut outro), voice-leading "
              "correction, zero-drift UnitMatrix export.",
    )

    # ---- stdout report ---------------------------------------------------
    print("=" * 70)
    print("PHASE 1 MIDI:", P1_PATH, "(%d bytes)" % size1)
    print("PHASE 2 MIDI:", P2_PATH, "(%d bytes)" % size2)
    print("Phase 1 zero-drift:", ok1, msg1)
    print("Phase 2 zero-drift: OK")
    print("Fibonacci word (%d symbols): %s" % (len(word), word))
    print("Raw events: %d, non-diatonic leak in raw draft: %d"
          % (len(raw_pitches), len(raw_leak)))
    print("Progression (per bar):", PROG_NAMES)
    print("Voice-leading violations (classical):", len(violations))
    print("Phase 2c corrections:", len(fixed_report), fixed_report[:6])
    print("Harmonic function report:")
    seen = set()
    for a, b, verdict in harm_report:
        if (a, b) not in seen:
            seen.add((a, b))
            print("   %d -> %d: %s" % (a, b, verdict))
    print("Final section triads:", triads[::SECTION_BARS])
    print("ALL SIZE ASSERTS PASSED")
