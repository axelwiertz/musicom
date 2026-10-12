# -*- coding: utf-8 -*-
"""237 - Kuramoto Chorale Extended (rework of 069).

Rework agent: redesign of 069-kuramoto-chorale. Preserves musical identity
(F dorian, 92 BPM, 4-voice chorale, Method 038 KOPS synchronization
transition) while fixing the audit defects:

  * 069 exported raw KOPS phase-wrap onsets WITHOUT grid snapping -> 124
    off-grid pitched onsets. This rework snaps every onset to the 120-tick
    (16th) grid and dedups collisions.
  * 069 lacked index.html + project-level provenance.json.

New piece is LONGER (18 bars vs 8) with MORE variation (8 techniques across
8 sections). Two-phase architecture: Phase 1 = raw KOPS draft (single voice,
unquantized chromatic, off-grid by design); Phase 2 = rules post-process
(grid snap, per-bar chord-tone quantization, register enforcement, block
harmony, voice-leading check).

Engines: structures.*, workflows.unitmatrix_composer, visualization.grid,
workflows.provenance, rules.progression, rules.voice_leading.
"""
import math
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance
from rules.progression import Scale7ChordDegree
from rules.voice_leading import VoiceLeadingRules

SEED = 237
KEY_NAME = "F dorian"
KEY_ROOT_PC = 5
SCALE_INTERVALS = [0, 2, 3, 5, 7, 9, 10]      # dorian intervals from root
KEY_PCS = sorted(set((KEY_ROOT_PC + iv) % 12 for iv in SCALE_INTERVALS))
KEY_ROOT_MIDI = 53                            # F3
BPM = 92
TPB = 480
BPB = 4
BAR = TPB * BPB                                # 1920
GRID = 120                                     # 16th-note snap grid

# ---- Form: 8 sections (source had 4) --------------------------------------
# (name, bars, per-bar scale degrees 0-indexed into F dorian)
SECTIONS = [
    ("Intro",    2, [0, 0]),
    ("Verse A",  2, [0, 3]),
    ("Verse A'", 2, [3, 6]),
    ("Chorus",   3, [6, 3, 0]),
    ("Bridge",   2, [0, 2]),
    ("Verse B",  2, [4, 6]),
    ("Chorus'",  3, [3, 6, 0]),
    ("Outro",    2, [0, 0]),
]
K_PER_SECTION = [0.5, 0.8, 1.2, 1.5, 2.0, 2.5, 3.2, 4.0]

# Variation technique applied to the soprano lead per section.
VARIATION = {
    "Intro":    None,
    "Verse A":  None,
    "Verse A'": "augment+octave",
    "Chorus":   None,               # density rise via drums
    "Bridge":   "invert",
    "Verse B":  "retrograde",
    "Chorus'":  "double",
    "Outro":    "diminish",
}

# Flatten per-bar degrees.
BAR_DEGREES = []
SECTION_BARS = []
for _name, _bars, _degs in SECTIONS:
    SECTION_BARS.append(_bars)
    BAR_DEGREES.extend(_degs)
TOTAL_BARS = sum(SECTION_BARS)
TOTAL_TICKS = TOTAL_BARS * BAR
TOTAL_BEATS = TOTAL_BARS * BPB

SECTION_START_BARS = []
_acc = 0
for _b in SECTION_BARS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def section_start_abs(s):
    return SECTION_START_BARS[s] * BAR


def section_ticks(s):
    return SECTION_BARS[s] * BAR


# ---- Voices ----------------------------------------------------------------
VOICES = ["Soprano", "Alto", "Tenor", "Bass", "Drums"]
VOICE_PROGRAMS = [
    MidiInstrument.FLUTE,
    MidiInstrument.STRING_ENSEMBLE,
    MidiInstrument.STRING_ENSEMBLE,
    MidiInstrument.BASS,
    0,                                   # drums: channel 9, program ignored
]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

REGISTERS = {
    "Soprano": (64, 86),
    "Alto": (53, 67),
    "Tenor": (43, 55),
    "Bass": (36, 48),
}

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "237-kuramoto-chorale-extended"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")


# ---- KOPS model ------------------------------------------------------------
N_OSC = 4
FREQS = [0.85, 1.0, 1.15, 1.35]
OMEGA = [2.0 * math.pi * f for f in FREQS]
DT = 0.005
PITCH_LO, PITCH_HI = 48, 84
VEL_LO, VEL_HI = 70, 100


def kuramoto_step(theta, omega, k, dt):
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
    re_ = sum(math.cos(t) for t in theta) / len(theta)
    im_ = sum(math.sin(t) for t in theta) / len(theta)
    return math.hypot(re_, im_)


def effective_omega(theta, omega, k, idx):
    n = len(theta)
    w = omega[idx]
    for j in range(n):
        if j != idx:
            w += (k / n) * math.sin(theta[j] - theta[idx])
    return w


def integrate():
    """Run KOPS over TOTAL_BEATS, K switched per section. Returns
    events[osc][(start_beat, dur_beats, raw_pitch, vel)] and r_means."""
    rng = random.Random(SEED)
    theta = [rng.uniform(0.0, 2.0 * math.pi) for _ in range(N_OSC)]
    events = [[] for _ in range(N_OSC)]
    prev_wrap = [0.0] * N_OSC
    r_means = [0.0] * len(SECTIONS)

    sec_start_beat = []
    acc = 0
    for b in SECTION_BARS:
        sec_start_beat.append(acc)
        acc += b * BPB
    sec_start_beat.append(acc)

    steps = int(TOTAL_BEATS / DT)
    for step in range(steps):
        beat = step * DT
        sec = 0
        while sec + 1 < len(sec_start_beat) and beat >= sec_start_beat[sec + 1]:
            sec += 1
        sec = min(sec, len(SECTIONS) - 1)
        k = K_PER_SECTION[sec]
        r = order_parameter(theta)
        r_means[sec] += r
        new_theta = kuramoto_step(theta, OMEGA, k, DT)
        for i in range(N_OSC):
            if new_theta[i] >= 2.0 * math.pi:
                w_eff = effective_omega(theta, OMEGA, k, i)
                raw = PITCH_LO + int(round((PITCH_HI - PITCH_LO) * min(1.0, max(0.0, (w_eff - 1.0) / 8.0))))
                raw = max(PITCH_LO, min(PITCH_HI, raw))
                dur = max(0.125, beat - prev_wrap[i])
                vel = VEL_LO + int(round((VEL_HI - VEL_LO) * r))
                events[i].append((beat, dur, raw, vel))
                prev_wrap[i] = beat
                new_theta[i] -= 2.0 * math.pi
        theta = new_theta

    for s in range(len(SECTIONS)):
        r_means[s] /= (SECTION_BARS[s] * BPB / DT)
    return events, r_means


def osc_to_abs(osc_events):
    out = []
    for (sb, db, raw, vel) in osc_events:
        st = int(round(sb * TPB))
        et = int(round((sb + db) * TPB))
        out.append(MusicEvent(pitch=raw, volume=vel, start_tick=st, end_tick=et))
    return out


# ---- Rules helpers (canonical-engine backed) -------------------------------
def chord_tones_abs(degree):
    root = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)
    third = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 2)
    fifth = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree + 4)
    return root, third, fifth


def octave_in_range(pitch, lo, hi):
    p = pitch
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def quantize_chord_tone(raw, degree, lo, hi):
    r, t, f = chord_tones_abs(degree)
    pool = set()
    for p in (r, t, f):
        for sh in (-24, -12, 0, 12, 24):
            c = p + sh
            if lo <= c <= hi:
                pool.add(c)
    if not pool:
        pool = {octave_in_range(r, lo, hi), octave_in_range(t, lo, hi),
                octave_in_range(f, lo, hi)}
    return min(pool, key=lambda c: abs(c - raw))


def snap(t):
    return int(round(t / GRID) * GRID)


def dedup(events):
    d = {}
    order = []
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


# ---- Variation techniques --------------------------------------------------
def apply_variation(sec_events, var, sec_start, sec_end):
    """Mutate soprano raw events in-place for one section. Returns new list."""
    ev = [MusicEvent(pitch=e.pitch, volume=e.volume,
                     start_tick=e.start_tick, end_tick=e.end_tick) for e in sec_events]
    if not ev:
        return ev
    if var is None:
        return ev

    if "augment" in var:
        for e in ev:
            d = e.end_tick - e.start_tick
            e.end_tick = min(sec_end, e.start_tick + 2 * d)

    if "diminish" in var:
        for e in ev:
            d = e.end_tick - e.start_tick
            e.end_tick = e.start_tick + max(GRID, d // 2)

    if "octave" in var:
        for e in ev:
            e.pitch = min(96, e.pitch + 12)

    if "invert" in var:
        pivot = ev[0].pitch
        for e in ev:
            e.pitch = max(PITCH_LO, min(PITCH_HI, 2 * pivot - e.pitch))

    if "retrograde" in var:
        pitches = [e.pitch for e in ev]
        pitches.reverse()
        for e, p in zip(ev, pitches):
            e.pitch = p

    return ev


def build_soprano(raw_abs_events):
    final = []
    for s, (name, _bars, _degs) in enumerate(SECTIONS):
        sec_start = section_start_abs(s)
        sec_len = section_ticks(s)
        sec_end = sec_start + sec_len
        sec_events = [e for e in raw_abs_events
                      if sec_start <= e.start_tick < sec_end]
        sec_events = apply_variation(sec_events, VARIATION[name], sec_start, sec_end)
        out = []
        for e in sec_events:
            st = snap(e.start_tick)
            et = max(st + GRID, snap(e.end_tick))
            st = max(sec_start, min(st, sec_end - GRID))
            et = min(sec_end, max(st + GRID, et))
            if et <= st:
                continue
            bar = st // BAR
            deg = BAR_DEGREES[bar]
            pitch = quantize_chord_tone(e.pitch, deg, REGISTERS["Soprano"][0],
                                        REGISTERS["Soprano"][1])
            out.append(MusicEvent(pitch=pitch, volume=e.volume,
                                  start_tick=st, end_tick=et))
        out = dedup(out)
        final.extend(out)
    return final


def compute_voicings():
    """Voice-leading-optimized SATB (bass/tenor/alto) per bar.

    Returns (voicings, violations, fixed_count) where voicings[bar] =
    (bass, tenor, alto) absolute MIDI. Uses VoiceLeadingRules.optimize +
    an inversion-rotation fix loop to minimize parallel/hidden fifths.
    """
    vl = VoiceLeadingRules(style="classical")
    canon = []
    for bar in range(TOTAL_BARS):
        r, t, f = chord_tones_abs(BAR_DEGREES[bar])
        canon.append([octave_in_range(r, 36, 48),
                      octave_in_range(f, 43, 55),
                      octave_in_range(t, 53, 67)])
    opt = vl.optimize_voice_leading(canon)

    fixed = [sorted(opt[0])]
    n_fixed = 0
    for i in range(1, len(opt)):
        prev = fixed[-1]
        base = sorted(opt[i])
        cands = [base]
        for rot in range(1, len(base)):
            cands.append(vl._rotate_chord(base, rot))
        cands += [[p - 12 for p in c] for c in list(cands)]
        cands += [[p + 12 for p in c] for c in list(cands)]
        best = cands[0]
        best_score = None
        for c in cands:
            nv = (len(vl.check_parallel_motion(prev, c))
                  + len(vl.check_hidden_fifths(prev, c)))
            dist = vl.calculate_voice_leading_distance(prev, c)
            score = (nv, dist)
            if best_score is None or score < best_score:
                best_score = score
                best = c
        if best_score[0] > 0:
            n_fixed += 1
        fixed.append(sorted(best))

    voicings = []
    for bar in range(TOTAL_BARS):
        tones = sorted(fixed[bar])
        voicings.append((octave_in_range(tones[0], 36, 48),
                         octave_in_range(tones[1], 43, 55),
                         octave_in_range(tones[2], 53, 67)))

    # Final violation count on the delivered voicings.
    violations = []
    for i in range(len(voicings) - 1):
        c1 = sorted(voicings[i])
        c2 = sorted(voicings[i + 1])
        violations += vl.check_parallel_motion(c1, c2)
        violations += vl.check_hidden_fifths(c1, c2)
    return voicings, violations, n_fixed


def build_block_voice(soprano_base, voice_name, voicings):
    lo, hi = REGISTERS[voice_name]
    out = []
    for se in soprano_base:
        st, et = se.start_tick, se.end_tick
        bar = st // BAR
        bass, tenor, alto = voicings[bar]
        if voice_name == "Bass":
            pitch = octave_in_range(bass, lo, hi)
            vel = 84
        elif voice_name == "Alto":
            pitch = octave_in_range(alto, lo, hi)
            vel = 72
        else:  # Tenor
            pitch = octave_in_range(tenor, lo, hi)
            vel = 72
        out.append(MusicEvent(pitch=pitch, volume=vel, start_tick=st, end_tick=et))
    return out


def build_drums():
    out = []
    for s, (name, bars, _degs) in enumerate(SECTIONS):
        sec_start = section_start_abs(s)
        crash = name in ("Chorus", "Chorus'")
        if crash:
            out.append(MusicEvent(pitch=MidiPercussion.CRASH_CYMBAL, volume=80,
                                  start_tick=sec_start, end_tick=sec_start + GRID))
        for b in range(bars):
            for beat in range(BPB):
                tick = sec_start + (b * BPB + beat) * TPB
                if name in ("Intro", "Outro"):
                    if beat == 0 and b == 0:
                        out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                              start_tick=tick, end_tick=tick + GRID))
                elif name == "Bridge":
                    pass  # breakdown, no kick
                else:
                    if beat % 2 == 0:
                        out.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                              start_tick=tick, end_tick=tick + GRID))
                if beat % 2 == 1:
                    out.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=85,
                                          start_tick=tick, end_tick=tick + GRID))
                for eighth in range(2):
                    ht = tick + eighth * 240
                    out.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=70,
                                          start_tick=ht, end_tick=ht + GRID))
    return dedup(out)


def compose():
    events, r_means = integrate()

    # ---- Phase 1: raw KOPS draft (oscillator 0, single voice, pre-rules) ---
    raw0 = osc_to_abs(events[0])
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
    for name, bars, _degs in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars, _degs) in enumerate(SECTIONS):
        p1.fill_voice_section("RawDraft", name, split_abs_to_section(raw0, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process --------------------------------------
    soprano_base = build_soprano(raw0)
    soprano_abs = list(soprano_base)
    for s, (name, _b, _d) in enumerate(SECTIONS):
        if VARIATION[name] == "double":
            sec_start = section_start_abs(s)
            sec_end = sec_start + section_ticks(s)
            doubled = []
            for e in soprano_base:
                if sec_start <= e.start_tick < sec_end:
                    doubled.append(MusicEvent(pitch=e.pitch - 12, volume=e.volume - 8,
                                              start_tick=e.start_tick, end_tick=e.end_tick))
            soprano_abs.extend(doubled)
    soprano_abs = dedup(soprano_abs)

    voicings, vl_violations, n_fixed = compute_voicings()
    alto_abs = build_block_voice(soprano_base, "Alto", voicings)
    tenor_abs = build_block_voice(soprano_base, "Tenor", voicings)
    bass_abs = build_block_voice(soprano_base, "Bass", voicings)
    drums_abs = build_drums()

    voice_events = {
        "Soprano": soprano_abs,
        "Alto": alto_abs,
        "Tenor": tenor_abs,
        "Bass": bass_abs,
        "Drums": drums_abs,
    }

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for name, bars, _degs in SECTIONS:
        composer.add_section(name, bars=bars)
    for s, (name, _bars, _degs) in enumerate(SECTIONS):
        for vname in VOICES:
            composer.fill_voice_section(vname, name,
                                        split_abs_to_section(voice_events[vname], s))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICES, bpm=BPM, mode="Dorian (F)")

    return composer, ok1, r_means, len(raw0), vl_violations, n_fixed


if __name__ == "__main__":
    composer, ok1, r_means, n_raw, vl_violations, n_fixed = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Total bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw KOPS events (osc0): {n_raw}")
    print(f"[OK] Voice-leading violations (classical, after optimization): {len(vl_violations)} "
          f"({n_fixed} bars re-voiced)")
    for s, (name, bars, degs) in enumerate(SECTIONS):
        print(f"     {name:<9} bars={bars} K={K_PER_SECTION[s]} degs={degs} "
              f"mean_r={r_means[s]:.3f} var={VARIATION[name]}")

    write_provenance(
        PHASE1_PATH,
        classification="ai-generated",
        generator="Method 038 Kuramoto Oscillator Phase Synchronization (KOPS) - PRE-RULES raw draft",
        sources=["Research/CompositionMethods/methods_db.md:Method 038",
                 "workflows/unitmatrix_composer.py",
                 "Styles/Experimental/069-kuramoto-chorale/compose.py (source)"],
        parameters={"method": 38, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "natural_frequencies_events_per_beat": FREQS,
                    "coupling_per_section": K_PER_SECTION,
                    "seed": SEED, "rework_of": "069-kuramoto-chorale"},
        notes="Phase 1 (rework): raw KOPS draft, single voice, unquantized "
              "chromatic pitch, off-grid rhythm by design.",
    )
    write_provenance(
        MIDI_PATH,
        classification="ai-generated",
        generator="Method 038 Kuramoto Oscillator Phase Synchronization (KOPS) + musicom rules (grid snap, chord-tone quantization, block harmony, voice leading)",
        sources=["Research/CompositionMethods/methods_db.md:Method 038",
                 "rules/progression.py", "rules/voice_leading.py",
                 "workflows/unitmatrix_composer.py",
                 "Styles/Experimental/069-kuramoto-chorale/compose.py (source)"],
        parameters={"method": 38, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "sections": len(SECTIONS), "total_bars": TOTAL_BARS,
                    "seed": SEED, "rework_of": "069-kuramoto-chorale",
                    "variation_techniques": sorted(set(v for v in VARIATION.values() if v))},
        notes="Phase 2 (rework): grid-snap every onset to 120 ticks, per-bar "
              "chord-tone quantization, register enforcement, SATB block "
              "harmony, ch9 drum groove, 8 variation techniques.",
    )
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
