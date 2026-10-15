# -*- coding: utf-8 -*-
"""243-world-melisma-rework - World style / Markov-Constraint Wavefront (M-022).

Rework of 072-world-melisma (audit failed: off-grid pitched onsets + missing
index.html). Rebuilt through canonical UnitMatrixComposer. Longer form
(8 sections x 4 bars = 32 bars) with 7 documented variation techniques.

Two-phase architecture:
  Phase 1: raw markov swimming melody, single voice (pre-rules).
  Phase 2: chord-tone quantization + voice-leading + rhythm-grid snap + dedup,
           full world texture (Lead / Counter / Pad / Bass / Perc ch9).

Key: D dorian. All pitched notes stay in KEY_PCS = {0,2,4,5,7,9,11}.
"""
import os
import random
import json

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from generators.markov_constraint import MarkovConstraintGenerator
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED, AI_GENERATED

random.seed(20261015)

# ---------------------------------------------------------------- paths
PROJ = "/opt/data/projects/Styles/World/243-world-melisma-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS                      # 1920
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}       # D dorian pitch classes
SCALE_STEP = [2, 4, 5, 7, 9, 11, 0]    # D dorian ascending pc order
SCALE = [62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]  # D4..C6
LEAD_LO, LEAD_HI = 60, 84

# chord-tone triads (D dorian diatonic degrees) + bass root (oct2) + lift (5th)
DEG = {
    "i":    (38, [62, 65, 69]),
    "ii":   (40, [64, 67, 71]),
    "III":  (41, [65, 69, 72]),
    "IV":   (43, [67, 71, 74]),
    "v":    (45, [69, 72, 76]),
    "vi°":  (47, [71, 74, 77]),
    "VII":  (48, [72, 76, 79]),
}
LIFT = {"i": 45, "ii": 47, "III": 48, "IV": 50, "v": 52, "vi°": 53, "VII": 55}

# ---------------------------------------------------------------- form
SECTIONS = ["Intro", "Verse", "Chorus", "Verse2", "Bridge", "Chorus2", "Drop", "Outro"]
BARS_PER = 4
N_SECTIONS = len(SECTIONS)
N_BARS = N_SECTIONS * BARS_PER               # 32 bars
SECTION_TICKS = BAR * BARS_PER               # 7680

# per-section harmonic regions (each its OWN progression; avoids bar-0 tonic bug)
PROG = [
    ["i", "i", "VII", "IV"],      # Intro
    ["i", "v", "III", "IV"],      # Verse
    ["IV", "v", "VII", "i"],      # Chorus
    ["i", "v", "III", "IV"],      # Verse2
    ["vi°", "ii", "v", "VII"],    # Bridge
    ["IV", "v", "VII", "i"],      # Chorus2
    ["i", "VII", "i", "v"],       # Drop
    ["i", "IV", "VII", "i"],      # Outro
]
CHORD_WALK = [d for sec in PROG for d in sec]   # 32 degree names
roots_per_bar = [DEG[d][0] for d in CHORD_WALK]
section_roots = [DEG[PROG[s][BARS_PER // 2]][0] for s in range(N_SECTIONS)]  # midpoint
print("roots_per_bar:", roots_per_bar)
print("section_roots (midpoint):", section_roots)

def chord_for_bar(abs_bar):
    return DEG[CHORD_WALK[abs_bar]][1]

def chord_pcs(abs_bar):
    return {t % 12 for t in chord_for_bar(abs_bar)}

# ---------------------------------------------------------------- helpers
def snap_scale(p):
    """Nearest MIDI note whose pitch class is in D dorian."""
    cands = [n for n in range(p - 6, p + 7) if n % 12 in KEY_PCS]
    return min(cands, key=lambda n: (abs(n - p), n))

def clamp(p, lo=LEAD_LO, hi=LEAD_HI):
    return snap_scale(max(lo, min(hi, p)))

def diatonic_shift(p, k):
    """Shift pitch by k scale degrees within D dorian (diatonic transposition)."""
    pc = p % 12
    idx = SCALE_STEP.index(pc)
    ni = idx + k
    oct = p // 12
    while ni >= 7:
        oct += 1
        ni -= 7
    while ni < 0:
        oct -= 1
        ni += 7
    return oct * 12 + SCALE_STEP[ni]

mk = MarkovConstraintGenerator(key_pitches=SCALE, default_pitch=74,
                               min_pitch=LEAD_LO, max_pitch=LEAD_HI)

def gen_raw(step, density, prev):
    u = mk.generate_voice_section(section_ticks=SECTION_TICKS, step_ticks=step,
                                  density=density, volume=92, previous_pitch=prev)
    evs = [e for e in u.events if e.pitch != 0]
    if evs:
        prev = evs[-1].pitch
    return evs, prev

# ---------------------------------------------------------------- phase 1
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=75, channel=0)   # Pan Flute
for n in SECTIONS:
    phase1.add_section(n, bars=BARS_PER)

prev = None
raw_by_section = []
for s, name in enumerate(SECTIONS):
    evs, prev = gen_raw(480, 0.55, prev)
    raw_by_section.append(evs)
    unit = MusicUnit(events=list(evs) + [MusicEvent(pitch=0, volume=0,
                        start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS)])
    phase1.set_unit(0, s, unit)

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "243-world-melisma-rework-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI)

# ---------------------------------------------------------------- motif + transforms
# Reference motif = raw Verse phrase (section 1)
motif = [(e.pitch, e.start_tick, e.end_tick) for e in raw_by_section[1]]

def identity(evs, hi=LEAD_HI):
    return [(clamp(e[0], LEAD_LO, hi), e[1], e[2]) for e in evs]

def octave_up(evs, hi=96):
    return [(clamp(e[0] + 12, 60, hi), e[1], e[2]) for e in evs]

def invert(evs, axis=62, hi=LEAD_HI):
    return [(clamp(snap_scale(2 * axis - e[0]), LEAD_LO, hi), e[1], e[2]) for e in evs]

def retrograde(evs):
    pitches = [e[0] for e in evs][::-1]
    return [(pitches[i], evs[i][1], evs[i][2]) for i in range(len(evs))]

def diminish(evs):
    out = []
    for p, s, e in evs:
        t0 = s // 2
        t1 = max(t0 + 1, e // 2)
        out.append((p, t0, min(t1, 2 * BAR - 1)))
        out.append((p, t0 + 2 * BAR, min(t1 + 2 * BAR, SECTION_TICKS)))
    return out

def augment(evs):
    out = []
    for p, s, e in evs:
        if s >= 2 * BAR:
            continue
        t0 = s * 2
        t1 = min(SECTION_TICKS, e * 2)
        out.append((p, t0, t1))
    return out

def diatonic_up(evs, hi=96):
    return [(clamp(diatonic_shift(e[0], 1), LEAD_LO, hi), e[1], e[2]) for e in evs]

# per-section lead transform (variation map)
LEAD_TRANSFORM = [
    ("identity", lambda evs: identity(evs)),            # Intro
    ("identity", lambda evs: identity(evs)),            # Verse (base motif)
    ("diminution", lambda evs: diminish(motif)),        # Chorus
    ("register-shift(+12)", lambda evs: octave_up(motif)),  # Verse2
    ("inversion(axis=D5)", lambda evs: invert(motif, axis=74)),  # Bridge
    ("diatonic-transposition(+1deg)", lambda evs: diatonic_up(motif)),  # Chorus2
    ("retrograde", lambda evs: retrograde(motif)),      # Drop
    ("augmentation", lambda evs: augment(motif)),       # Outro
]

# ---------------------------------------------------------------- phase 2
VOICES = [
    ("Lead",    75, 0),   # Pan Flute
    ("Counter", 48, 1),   # String Ensemble
    ("Pad",     89, 2),   # Synth Pad (warm)
    ("Bass",    35, 3),   # Fretless Bass
    ("Perc",     0, 9),   # percussion
]
N_V = len(VOICES)
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
vnames = [v[0] for v in VOICES]
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in SECTIONS:
    phase2.add_section(n, bars=BARS_PER)

def snap_grid(t):
    return max(0, int(round(t / 120.0)) * 120)

def finalize(events, total=SECTION_TICKS):
    """Clamp ticks, add terminal landmark (pitch 0) so len_ticks()==total."""
    for e in events:
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick > total:
            e.end_tick = total
        if e.end_tick <= e.start_tick:
            e.end_tick = e.start_tick + 1
    if not events or max(e.end_tick for e in events) < total:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=total - 1, end_tick=total))
    return MusicUnit(events=events)

# ---- lead: transform -> chord-quantize -> voice-leading -> snap -> dedup ----
lead_by_section = {}
for s, name in enumerate(SECTIONS):
    technique, fn = LEAD_TRANSFORM[s]
    src = [(e.pitch, e.start_tick, e.end_tick) for e in raw_by_section[0]] if name == "Intro" else motif
    evs = fn(src)
    # chord-quantize to each event's own bar (floor t // BAR -> absolute bar)
    q = []
    prev_p = None
    for (p, st, en) in evs:
        abs_bar = s * BARS_PER + (st // BAR)
        if abs_bar >= N_BARS:
            abs_bar = N_BARS - 1
        tones_pcs = chord_pcs(abs_bar)
        cands = [n for n in range(p - 12, p + 13)
                 if n % 12 in tones_pcs and LEAD_LO - 5 <= n <= LEAD_HI + 12]
        if not cands:
            cands = [n for n in range(48, 108) if n % 12 in tones_pcs]
        qp = min(cands, key=lambda n: (abs(n - p), n))
        # voice-leading: cap leap to <=8 semitones toward nearest chord tone
        if prev_p is not None and abs(qp - prev_p) > 8:
            qp = min(cands, key=lambda n: (abs(n - prev_p), n))
        q.append(MusicEvent(pitch=qp, volume=92, start_tick=st, end_tick=en))
        prev_p = qp
    # rhythm-grid snap + dedup (start_tick,pitch) keeping longest
    dedup = {}
    for e in q:
        st = snap_grid(e.start_tick)
        en = snap_grid(e.end_tick)
        key = (st, e.pitch)
        if key not in dedup or (en - st) > (dedup[key].end_tick - dedup[key].start_tick):
            dedup[key] = MusicEvent(pitch=e.pitch, volume=92, start_tick=st, end_tick=en)
    lead_by_section[s] = sorted(dedup.values(), key=lambda e: e.start_tick)
    phase2.set_unit(0, s, finalize(list(lead_by_section[s])))

# ---- counter: ostinato with per-section variation (all onsets on 120 grid) ----
DRUM_DENS = [0.35, 0.6, 1.0, 0.6, 0.5, 1.0, 0.2, 0.1]
for s, name in enumerate(SECTIONS):
    evs = []
    for b in range(BARS_PER):
        abs_bar = s * BARS_PER + b
        t0 = b * BAR
        tones = chord_for_bar(abs_bar)
        third, fifth = tones[1], tones[2]
        if name in ("Intro",):
            evs.append(MusicEvent(pitch=fifth, volume=58, start_tick=t0 + 960, end_tick=t0 + 1680))
        elif name in ("Verse", "Verse2"):
            evs.append(MusicEvent(pitch=fifth + 12, volume=70, start_tick=t0, end_tick=t0 + 360))
            evs.append(MusicEvent(pitch=third + 12, volume=66, start_tick=t0 + 960, end_tick=t0 + 1440))
        elif name in ("Chorus", "Chorus2"):
            up = 12 if name == "Chorus2" else 0
            pat = [tones[0], tones[1], tones[2], tones[1], tones[0], tones[1], tones[2], tones[1]]
            for k, tp in enumerate(pat):
                evs.append(MusicEvent(pitch=tp + up, volume=72, start_tick=t0 + k * 240,
                                      end_tick=t0 + k * 240 + 220))
        elif name == "Bridge":
            evs.append(MusicEvent(pitch=fifth, volume=64, start_tick=t0, end_tick=t0 + BAR - 60))
        elif name == "Drop":
            pass  # counter rests during drop
        elif name == "Outro":
            evs.append(MusicEvent(pitch=third + 12, volume=60, start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(1, s, finalize(evs))

# ---- pad: sustained triad per bar (onset at bar start) ----
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        abs_bar = s * BARS_PER + b
        t0 = b * BAR
        tones = chord_for_bar(abs_bar)
        for p in tones:
            evs.append(MusicEvent(pitch=p, volume=62, start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(2, s, finalize(evs))

# ---- bass: root drone + diatonic fifth lift on beat 3 ----
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        abs_bar = s * BARS_PER + b
        d = CHORD_WALK[abs_bar]
        root = DEG[d][0]
        lift = LIFT[d]
        t0 = b * BAR
        evs.append(MusicEvent(pitch=root, volume=96, start_tick=t0, end_tick=t0 + BAR))
        evs.append(MusicEvent(pitch=lift, volume=84, start_tick=t0 + 1440, end_tick=t0 + BAR))
    phase2.set_unit(3, s, finalize(evs))

# ---- drums: world percussion with density ramp (ch9, excluded from grid checks) ----
for s, name in enumerate(SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    if dens <= 0:
        phase2.set_unit(4, s, create_empty_unit(SECTION_TICKS))
        continue
    for b in range(BARS_PER):
        t0 = b * BAR
        # shaker 8ths when dens >= 0.6
        if dens >= 0.6:
            for k in range(0, BAR, 240):
                evs.append(MusicEvent(pitch=82, volume=52, start_tick=t0 + k, end_tick=t0 + k + 80))
        # low tom beats 1 & 3
        evs.append(MusicEvent(pitch=41, volume=92, start_tick=t0, end_tick=t0 + 140))
        evs.append(MusicEvent(pitch=41, volume=88, start_tick=t0 + 960, end_tick=t0 + 1100))
        # high tom off-beats in full sections
        if dens >= 1.0:
            evs.append(MusicEvent(pitch=50, volume=70, start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=50, volume=66, start_tick=t0 + 1440, end_tick=t0 + 1560))
        # kick on beats 1 (+3 in chorus/drop)
        if dens >= 1.0 or name == "Drop":
            evs.append(MusicEvent(pitch=35, volume=100, start_tick=t0, end_tick=t0 + 120))
        # cabasa light intro/outro
        if name in ("Intro", "Outro"):
            for k in range(0, BAR, 480):
                evs.append(MusicEvent(pitch=69, volume=44, start_tick=t0 + k, end_tick=t0 + k + 100))
    phase2.set_unit(4, s, finalize(evs))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok2, msg2

P2_MIDI = os.path.join(MIDI_DIR, "243-world-melisma-rework.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI)

# ---------------------------------------------------------------- sidecars
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM, mode="D Dorian / markov-harmony rework")
print("grid written", grid_path)

for mid, phase, note in (
    (P1_MIDI, "1", "raw markov melody, unquantized, single voice (pre-rules)"),
    (P2_MIDI, "2", "chord-tone quantized + voice-leading + grid-snap + dedup, full world texture"),
):
    write_provenance(
        mid, AI_GENERATED if phase == "1" else AI_ASSISTED,
        "MarkovConstraintGenerator (M-022) + musicom rules",
        parameters={
            "bpm": BPM, "key": "D dorian", "sections": N_SECTIONS, "bars": N_BARS,
            "phase": phase, "chord_walk": CHORD_WALK, "seed": 20261015,
            "source": "072-world-melisma", "rework": "redesign",
            "variation_techniques": [t[0] for t in LEAD_TRANSFORM],
        },
        notes=note,
    )
    print("provenance for phase", phase)

summary = {
    "project": "243-world-melisma-rework",
    "style": "World",
    "method": "markov-harmony (M-022 Markov-Constraint Wavefront)",
    "bpm": BPM, "key": "D Dorian",
    "bars": N_BARS, "sections": SECTIONS,
    "chord_walk": CHORD_WALK,
    "roots_per_bar": roots_per_bar,
    "section_roots_midpoint": section_roots,
    "voices": vnames,
    "variation_techniques": [t[0] for t in LEAD_TRANSFORM],
    "drum_density": dict(zip(SECTIONS, DRUM_DENS)),
    "source": "072-world-melisma",
    "decision": "redesign (off-grid onsets + missing index.html)",
    "phase1": os.path.basename(P1_MIDI),
    "phase2": os.path.basename(P2_MIDI),
    "grid": os.path.basename(grid_path),
    "seed": 20261015,
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("summary.json written")

# size asserts
for p in (P1_MIDI, P2_MIDI, grid_path, os.path.join(ANALYSIS_DIR, "summary.json")):
    assert os.path.getsize(p) > 40, f"too small: {p}"
print("ALL SIZE ASSERTS PASSED")
print("CHORD_WALK:", CHORD_WALK)
