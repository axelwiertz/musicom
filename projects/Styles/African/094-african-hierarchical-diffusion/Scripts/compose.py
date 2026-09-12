# -*- coding: utf-8 -*-
"""094-african-hierarchical-diffusion -- African style / CONCRETE layer.

Method 010 Hierarchical Diffusion (multi-level, markov base)
    -> generators.chain.MarkovChainGenerator  (registry implementation)

PHASE 1 (raw generative draft, single voice, NO harmony)
    The Markov base of the method walks a 7-state pitch space; the sequence is
    realized by the engine's `generate_unit_from_sequence()` at a FRACTIONAL
    onset interval of 417 ticks -- deliberately NOT a multiple of the 16th
    (120) or 8th (240) grid -- and through a pitch_map whose entries include
    out-of-scale tones (C#, G#). The raw draft is therefore off-grid AND
    unquantized by construction: that is the phase-1 fingerprint.

PHASE 2 (musicom rules post-process)
    The SAME method is run strictly hierarchically, top-down, four levels:
      L4 macro  : density/en register state per SECTION (Markov walk, 6 states)
      L3 phrase : each section expands to 4 BAR states (Markov child step)
      L2 cell   : each bar expands to 4 BEAT states (Markov child step)
      L1 event  : each beat state expands to 1/2/3 onsets inside the beat
                  -> every onset lands on the 16th grid (120 @ 480 TPB)
    then the rules layer:
      * chord-tone quantization per bar routed through the canonical
        `Scale7ChordDegree.get_diatonic_note` (no local `% 7` wrappers)
      * 16th-grid lock (078 mandatory rule): 0 off-grid onsets
      * voice-leading check/correction (rules.voice_leading) on outer voices
      * full 6-voice kora/balafon/djembe texture

Engine only: structures + workflows.unitmatrix_composer + generators.chain
+ rules.progression + rules.voice_leading. mido is never imported here.
"""
import json
import os
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)

# method 010 registry implementation (Markov base)
from generators.chain import MarkovChainGenerator
from rules.progression import Scale7ChordDegree      # canonical diatonic helper
from rules.voice_leading import VoiceLeadingRules

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    MARIMBA, KALIMBA, FLUTE, ACOUSTIC_GUITAR, DOUBLE_BASS, DRUM_KIT,
)
from Percussion.drum_kit.drum_kit import KIT  # noqa: E402

SEED = 20260912
rng = np.random.default_rng(SEED)

PROJ = ("/opt/data/repos/musicom/projects/Styles/African/"
        "094-african-hierarchical-diffusion")
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
SCRIPTS_DIR = os.path.join(PROJ, "Scripts")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR, SCRIPTS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- concept
BPM = 112
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120
GRID8 = 240
BARS_PER = 4
NAMES = ["Intro", "KoraVerse", "BalafonChorus", "Bridge", "Chorus2", "Outro"]
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER   # 24
SECTION_TICKS = BAR * BARS_PER   # 7680

# A dorian (kora/mande tuning colour): A B C D E F# G
KEY_ROOT = 69
DORIAN = [0, 2, 3, 5, 7, 9, 10]
SCALE_PCS = {(KEY_ROOT + i) % 12 for i in DORIAN}
assert SCALE_PCS == {9, 11, 0, 2, 4, 6, 7}, SCALE_PCS
SCALE_PITCHES = [p for p in range(36, 97) if p % 12 in SCALE_PCS]


def degree_note(d):
    """Canonical diatonic pitch for a (possibly octave-shifted) degree index."""
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT, DORIAN, d)


def degree_pc(d):
    return degree_note(d) % 12


def degree_tetrad_pcs(d):
    """Diatonic 7th-chord tones of degree d (triad + diatonic 7th)."""
    return {degree_note(d + k) % 12 for k in (0, 2, 4, 6)}


def degree_triad_pcs(d):
    return {degree_note(d + k) % 12 for k in (0, 2, 4)}


# 24-bar A-dorian mande loop (0-based degrees: 0=i 2=III 3=IV 4=v 6=VII)
PROG_DEG = ([0, 0, 3, 6] +      # Intro        i  i  IV VII
            [0, 3, 6, 0] +      # KoraVerse    i  IV VII i
            [2, 6, 0, 4] +      # BalafonChor  III VII i v
            [3, 4, 0, 6] +      # Bridge       IV v  i  VII
            [2, 6, 0, 4] +      # Chorus2      III VII i v
            [0, 3, 0, 0])       # Outro        i  IV i  i
assert len(PROG_DEG) == N_BARS

DEG_NAME = {0: "i7", 1: "ii7", 2: "III", 3: "IV", 4: "v", 5: "vi°", 6: "VII"}
PC_NAME = {9: "A", 11: "B", 0: "C", 2: "D", 4: "E", 6: "F#", 7: "G"}
BAR_LABELS = [PC_NAME[degree_pc(d)] + DEG_NAME[d] for d in PROG_DEG]


def chord_tones(deg, lo, hi, seventh=True):
    """Chord tones of degree `deg` inside [lo, hi] (registry-safe range)."""
    pcs = degree_tetrad_pcs(deg) if seventh else degree_triad_pcs(deg)
    return sorted(p for p in range(lo, hi + 1) if p % 12 in pcs)


# ---------------------------------------------------------------- method 010
STATES = np.array([0, 1, 2], dtype=int)          # density states: sparse/mid/dense


def _dist(rows):
    """Row-normalize a raw weight matrix -> Markov transition matrix."""
    m = np.array(rows, dtype=float)
    return m / m.sum(axis=1, keepdims=True)


# L4 macro transition (section-to-section energy)
M4 = _dist([[0.55, 0.35, 0.10],
            [0.20, 0.55, 0.25],
            [0.08, 0.32, 0.60]])
# L3 phrase transition (bar-to-bar inside a section)
M3 = _dist([[0.45, 0.40, 0.15],
            [0.25, 0.50, 0.25],
            [0.12, 0.38, 0.50]])
# L2 cell transition (beat-to-beat inside a bar)
M2 = _dist([[0.50, 0.35, 0.15],
            [0.22, 0.50, 0.28],
            [0.10, 0.34, 0.56]])

# L1 onset expansion: beat state -> tick offsets inside the beat (16th grid)
L1_ONSETS = {
    0: [[0], [0], [0, 240]],
    1: [[0, 240], [0, 240], [0, 360], [0, 120]],
    2: [[0, 120, 240, 360], [0, 240, 360], [0, 120, 360], [0, 240]],
}


def markov_walk(seed, length, states=STATES, matrix=M4):
    """One Markov chain walk (the method's base generator)."""
    gen = MarkovChainGenerator([], 0, length=length)
    gen.np_generator = np.random.Generator
    return gen.generate_sequence(length=length, states=states,
                                 distribution=matrix)


def diffuse_voice(seed, n_sections, rot=0):
    """Full 4-level hierarchical diffusion -> per-beat onset lists.

    Returns (L4 macro states, L3 bar states, L2 beat states, onsets) where
    `onsets[bar][beat]` is the list of tick offsets inside that beat.
    """
    r = np.random.default_rng(seed)
    l4 = markov_walk(seed, n_sections)
    l3, l2, onsets = [], [], []
    for s in range(n_sections):
        # L3: the section's macro state seeds the bar-level walk
        bars_states = markov_walk(seed + 100 + s, BARS_PER,
                                  matrix=M3 if l4[s] else M3)
        bars_states = [max(0, min(2, st + (0 if l4[s] else -1)))
                       for st in bars_states]
        l3.append(bars_states)
        for b, bst in enumerate(bars_states):
            beats = markov_walk(seed + 200 + s * 10 + b, BEATS, matrix=M2)
            beats = [max(0, min(2, st + (1 if bst == 2 else 0))) for st in beats]
            l2.append(beats)
            row = []
            for beat, k in enumerate(beats):
                opts = L1_ONSETS[k]
                pick = opts[int(r.integers(len(opts)))]
                row.append([((o + (rot % 4) * GRID16) % TPB) for o in pick])
            onsets.append([sorted(set(x)) for x in row])
    return l4, l3, l2, onsets


# ---------------------------------------------------------------- PHASE 1
P1_STATES = np.array([0, 1, 2, 3, 4, 5, 6], dtype=int)
P1_MATRIX = _dist([
    [0.22, 0.30, 0.18, 0.10, 0.08, 0.06, 0.06],
    [0.14, 0.24, 0.28, 0.16, 0.08, 0.06, 0.04],
    [0.08, 0.16, 0.24, 0.26, 0.14, 0.08, 0.04],
    [0.05, 0.08, 0.16, 0.24, 0.25, 0.14, 0.08],
    [0.04, 0.06, 0.09, 0.17, 0.25, 0.24, 0.15],
    [0.03, 0.05, 0.07, 0.11, 0.19, 0.28, 0.27],
    [0.06, 0.10, 0.12, 0.14, 0.18, 0.22, 0.18],
])
# Raw pitch map: unquantized, deliberately includes C# (73) and G# (80),
# which are OUTSIDE A dorian -- the phase-1 pre-rules fingerprint.
P1_PITCH_MAP = {0: 66, 1: 69, 2: 73, 3: 76, 4: 78, 5: 80, 6: 84}
P1_UNIT = 417          # fractional onset interval: 417 % 120 = 57 (off-grid)
P1_N = {0: 14, 1: 18, 2: 19, 3: 18, 4: 19, 5: 14}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("KalimbaRaw", program=KALIMBA.midi_program, channel=0)

p1_note_count = 0
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    seq = markov_walk(SEED + s, P1_N[s], states=P1_STATES, matrix=P1_MATRIX)
    unit = MarkovChainGenerator([], 0).generate_unit_from_sequence(
        sequence=seq,
        pitch_map=P1_PITCH_MAP,
        duration=P1_UNIT - 60,      # slight gap -> no legato lock
        onset_interval=P1_UNIT,     # fractional -> off-grid
        volume=86,
    )
    evs = list(unit.events)
    p1_note_count += len([e for e in evs if e.pitch > 0])
    # clip the raw walk to the section boundary (raw rhythm keeps its
    # off-grid character; only the overflow tail is trimmed)
    kept = []
    for e in evs:
        if e.start_tick >= SECTION_TICKS:
            continue
        if e.end_tick > SECTION_TICKS:
            e.end_tick = SECTION_TICKS
        kept.append(e)
    evs = kept
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                              end_tick=SECTION_TICKS))
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
print("PHASE1 validate:", ok1, msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "094-african-hierarchical-diffusion-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written", P1_MIDI, os.path.getsize(P1_MIDI), "bytes",
      p1_note_count, "notes")

# ---------------------------------------------------------------- PHASE 2
VOICES = [
    ("Kalimba", KALIMBA.midi_program, 0),           # thumb piano — lead
    ("Balafon", MARIMBA.midi_program, 1),           # balafon (marimba GM)
    ("Flute",   FLUTE.midi_program, 2),             # fula flute counterline
    ("Kora",    ACOUSTIC_GUITAR.midi_program, 3),   # kora arpeggio (nylon gtr)
    ("Bass",    DOUBLE_BASS.midi_program, 4),       # double bass root pulse
    ("Drums",   DRUM_KIT.midi_program, 9),          # djembe kit (ch 9)
]
N_V = len(VOICES)

phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for n in NAMES:
    phase2.add_section(n, bars=BARS_PER)

# per-voice registers (inside each registry range)
REG = {
    "Kalimba": (60, 84),      # range 48-96, sweet 62-81
    "Balafon": (60, 88),      # range 45-96, sweet 60-84
    "Flute":   (67, 89),      # range 60-96
    "Kora":    (52, 76),      # range 40-84
    "Bass":    (33, 50),      # range 28-74, sweet 40-55
}
# L1 rotation per voice -> interlocking (African hocket between the two leads)
ROT = {"Kalimba": 0, "Balafon": 2, "Flute": 1, "Kora": 3}
DUR = {"Kalimba": 200, "Balafon": 300, "Flute": 660, "Kora": 150}


def realize_voice(voice, seed, contour_steps, center):
    """Realize one voice from the 4-level diffusion + the rules layer.

    Pitches are chord tones of the bar (diatonic tetrad), reached by a
    scale-degree contour walk -> 0 out-of-scale, 0 out-of-chord.
    """
    lo, hi = REG[voice]
    _, _, _, onsets = diffuse_voice(seed, N_SECTIONS, rot=ROT[voice])
    evs = []
    prev = center
    gi = 0
    for bar in range(N_BARS):
        deg = PROG_DEG[bar]
        tones = chord_tones(deg, lo, hi) or [degree_note(deg) + 24]
        t0 = bar * BAR
        for beat in range(BEATS):
            for off in onsets[bar][beat]:
                step = contour_steps[gi % len(contour_steps)]
                gi += 1
                target = prev + step
                q = min(tones, key=lambda c: (abs(c - target), c))
                if abs(q - prev) > 12:            # cap leaps to <= 1 octave
                    candidates = [t for t in tones if abs(t - prev) <= 12]
                    if candidates:
                        q = min(candidates, key=lambda c: (abs(c - target), c))
                st = t0 + beat * TPB + off
                accent = 0 if off % TPB == 0 else (1 if off % 240 == 0 else 2)
                vel = (96, 84, 74)[accent]
                dur = DUR[voice]
                if voice == "Flute":
                    dur = min(660, TPB)           # long fula-flute held notes
                evs.append(MusicEvent(pitch=int(q), volume=vel,
                                      start_tick=st, end_tick=st + dur))
                prev = int(q)
    evs.sort(key=lambda e: e.start_tick)
    for i in range(len(evs) - 1):                 # monophonic legato safety
        if evs[i].end_tick > evs[i + 1].start_tick:
            evs[i].end_tick = evs[i + 1].start_tick
        if evs[i].end_tick <= evs[i].start_tick:
            evs[i].end_tick = evs[i].start_tick + 60
    return evs


CONTOUR = {
    "Kalimba": [0, 2, -1, 3, -2, 1, -3, 2, 0, -2, 4, -1],
    "Balafon": [2, -2, 3, -1, -3, 1, 0, 2, -4, 3, -1, 0],
    "Flute":   [0, 3, 1, -2, 2, -1, 4, -3, 0, 2, -2, 1],
    "Kora":    [4, -2, -1, 3, -4, 2, -2, 1, 3, -3, 2, -1],
}
CENTER = {"Kalimba": 72, "Balafon": 72, "Flute": 79, "Kora": 64}

def slice_section(evs, lo_t, hi_t):
    """Absolute-tick events -> NEW events with ticks relative to the section.

    UnitMatrix cells are per-section coordinate spaces (each cell starts at
    tick 0), so absolute ticks MUST be rebased here -- forgetting the rebase
    clamps every event of sections > 0 to SECTION_TICKS-10, which is both
    off-grid and collides notes on export.
    """
    out = []
    for e in evs:
        if not (lo_t <= e.start_tick < hi_t):
            continue
        st = e.start_tick - lo_t
        en = min(e.end_tick - lo_t, SECTION_TICKS)
        if st >= SECTION_TICKS:
            st = SECTION_TICKS - 10
        if en <= st:
            en = min(SECTION_TICKS, st + 60)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    if not out:
        out = [MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS)]
    return out


for v, (voice, prog, ch) in enumerate(VOICES):
    if voice not in CONTOUR:          # Drums + Bass are written separately
        continue
    evs = realize_voice(voice, SEED + 1000 + v * 37, CONTOUR[voice],
                        CENTER[voice])
    # explicit chord-tone quantization pass (rules layer, canonical helper)
    quant_fixed = 0
    for e in evs:
        bar = min(e.start_tick // BAR, N_BARS - 1)
        tones = chord_tones(PROG_DEG[bar], REG[voice][0], REG[voice][1])
        if e.pitch % 12 not in {t % 12 for t in tones}:
            e.pitch = int(min(tones, key=lambda c: (abs(c - e.pitch), c)))
            quant_fixed += 1
    print("%-8s notes=%3d chord_quantized=%d" % (voice, len(evs), quant_fixed))
    # split into sections
    for s in range(N_SECTIONS):
        lo_t, hi_t = s * SECTION_TICKS, (s + 1) * SECTION_TICKS
        phase2.set_unit(v, s, MusicUnit(events=slice_section(evs, lo_t, hi_t)))

# --- Bass: root pulse, hierarchical (L2 beat states decide root vs octave)
bass_evs = []
_, _, l2_bass, _ = diffuse_voice(SEED + 4242, N_SECTIONS, rot=0)
for bar in range(N_BARS):
    deg = PROG_DEG[bar]
    tones = chord_tones(deg, 33, 52, seventh=False) or [40]
    root = min(tones, key=lambda c: abs(c - 40))
    t0 = bar * BAR
    for beat, st in enumerate(l2_bass[bar]):
        if st == 0 and beat % 2 == 1:
            continue                                   # sparse: leaves rests
        if beat % 2 == 0 or st < 2:
            p = root
        else:                                          # octave must ALSO be a
            oct_c = [t for t in tones if t > root]     # chord tone (audit rule)
            p = min(oct_c, key=lambda c: abs(c - (root + 12))) if oct_c else root
        bass_evs.append(MusicEvent(pitch=int(p),
                                   volume=98 if beat == 0 else 80,
                                   start_tick=t0 + beat * TPB,
                                   end_tick=t0 + beat * TPB + 200))
for s in range(N_SECTIONS):
    lo_t, hi_t = s * SECTION_TICKS, (s + 1) * SECTION_TICKS
    phase2.set_unit(4, s,
                    MusicUnit(events=slice_section(bass_evs, lo_t, hi_t)))

# --- Drums: djembe-oriented kit, dundun bell timeline E(7,16)
DRUM_PLAN = {
    0: dict(bell=64, shaker=None, djembe=88,  crash=True),
    1: dict(bell=80, shaker=48,   djembe=104, crash=False),
    2: dict(bell=92, shaker=58,   djembe=118, crash=True),
    3: dict(bell=76, shaker=44,   djembe=100, crash=False),
    4: dict(bell=92, shaker=58,   djembe=118, crash=True),
    5: dict(bell=64, shaker=None, djembe=84,  crash=True),
}
BELL_ONSETS = [0, 240, 480, 600, 840, 1080, 1320, 1440, 1680]   # 7-in-16 feel
SHAKER_ONSETS = list(range(0, BAR, GRID16))
DJEMBE_ONSETS = [0, 360, 720, 1080, 1440, 1680]

for s in range(N_SECTIONS):
    plan = DRUM_PLAN[s]
    evs = []
    for b in range(BARS_PER):
        t0 = b * BAR
        for off in BELL_ONSETS:
            if off >= BAR:
                continue
            evs.append(MusicEvent(pitch=KIT["claves"], volume=plan["bell"],
                                  start_tick=t0 + off, end_tick=t0 + off + 70))
        if plan["shaker"] is not None:
            for i, off in enumerate(SHAKER_ONSETS):
                if off >= BAR:
                    continue
                evs.append(MusicEvent(pitch=KIT["maracas"],
                                      volume=plan["shaker"] + (6 if i % 2 == 0 else 0),
                                      start_tick=t0 + off, end_tick=t0 + off + 50))
        for i, off in enumerate(DJEMBE_ONSETS):
            p = KIT["kick"] if i % 3 == 0 else (KIT["tom_mid"] if i % 3 == 1
                                                else KIT["tom_high"])
            evs.append(MusicEvent(pitch=p, volume=plan["djembe"] - 6 * (i % 3),
                                  start_tick=t0 + off, end_tick=t0 + off + 120))
        if plan["crash"] and b == 0:
            evs.append(MusicEvent(pitch=KIT["crash"], volume=96,
                                  start_tick=t0, end_tick=t0 + 240))
        if s in (2, 4) and b == 3:
            evs.append(MusicEvent(pitch=KIT["snare"], volume=104,
                                  start_tick=t0 + 1440, end_tick=t0 + 1560))
    phase2.set_unit(5, s, MusicUnit(events=evs))

# --- voice-leading check (outer voices: bass root vs lead first note per bar)
vlc = VoiceLeadingRules(style="classical")
vl_flags = []


def bass_root_of(bar):
    tones = chord_tones(PROG_DEG[bar], 33, 50, seventh=False) or [40]
    return int(min(tones, key=lambda c: abs(c - 40)))


def lead_first_of(bar):
    s, b = divmod(bar, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    for e in sorted(u.events, key=lambda x: x.start_tick):
        if e.pitch > 0 and e.start_tick >= b * BAR:
            return e
    return None


for bar in range(N_BARS - 1):
    a, b = bass_root_of(bar), bass_root_of(bar + 1)
    e1, e2 = lead_first_of(bar), lead_first_of(bar + 1)
    if e1 is None or e2 is None:
        continue
    viol = vlc.check_parallel_motion([a, e1.pitch], [b, e2.pitch])
    if viol:
        vl_flags.append((bar, "parallel", viol))
    hid = vlc.check_hidden_fifths([a, e1.pitch], [b, e2.pitch])
    if hid:
        vl_flags.append((bar, "hidden", hid))
print("VL flags (bass+lead, classical):", len(vl_flags))

n_fixed = 0
for (bar, _k, _v) in vl_flags:
    tgt_bar = min(bar + 1, N_BARS - 1)
    s, b = divmod(tgt_bar, BARS_PER)
    u = phase2.matrix.get_unit((0, s))
    evs = list(u.events)
    target = None
    for e in sorted(evs, key=lambda x: x.start_tick):
        if e.pitch > 0 and e.start_tick >= b * BAR:
            target = e
            break
    if target is None:
        continue
    tones = chord_tones(PROG_DEG[tgt_bar], REG["Kalimba"][0], REG["Kalimba"][1])
    bass = bass_root_of(tgt_bar)
    cands = [t for t in tones
             if (t - bass) % 12 not in (0, 7) and abs(t - target.pitch) <= 10]
    if not cands:
        continue
    target.pitch = int(min(cands, key=lambda c: (abs(c - target.pitch), c)))
    phase2.set_unit(0, s, MusicUnit(events=sorted(evs,
                                                  key=lambda e: e.start_tick)))
    n_fixed += 1
print("VL fixes applied:", n_fixed)


# --- normalize every cell to the exact section boundary (zero-drift invariant)
def normalize_cell(unit, total_ticks):
    evs = list(unit.events)
    for e in evs:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 10
        if e.start_tick < 0:
            e.start_tick = 0
        if e.end_tick <= e.start_tick:
            e.end_tick = min(total_ticks, e.start_tick + 60)
    if not evs or evs[-1].end_tick < total_ticks:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    return MusicUnit(events=sorted(evs, key=lambda e: (e.start_tick, e.pitch)))


for s in range(N_SECTIONS):
    for v in range(N_V):
        u = phase2.matrix.get_unit((v, s))
        if u is None:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
            continue
        phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", ok2, msg2)
assert ok2, msg2
P2_MIDI = os.path.join(MIDI_DIR, "094-african-hierarchical-diffusion.mid")
phase2.to_midi(P2_MIDI)
print("phase2 written", P2_MIDI, os.path.getsize(P2_MIDI), "bytes")

# ---------------------------------------------------------------- provenance
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

write_provenance(P1_MIDI, classification=AI_ASSISTED,
                 generator="generators.chain.MarkovChainGenerator (method 010)",
                 parameters={"phase": 1, "seed": SEED, "bpm": BPM,
                             "key": "A dorian", "onset_interval_ticks": P1_UNIT,
                             "pitch_map": {str(k): v for k, v in P1_PITCH_MAP.items()},
                             "method": "010 Hierarchical Diffusion (raw draft)"},
                 notes="Raw Markov draft: engine MarkovChainGenerator sequence "
                       "realized at a fractional (off-grid) 417-tick onset "
                       "interval with a pitch map containing out-of-scale "
                       "tones. Single voice, no harmony, no quantization.")
write_provenance(P2_MIDI, classification=AI_ASSISTED,
                 generator="generators.chain + musicom rules layer (method 010)",
                 parameters={"phase": 2, "seed": SEED, "bpm": BPM,
                             "key": "A dorian", "grid": "16th (120 @ 480 TPB)",
                             "hierarchy": ["L4 section", "L3 bar", "L2 beat",
                                           "L1 onset"],
                             "progression": BAR_LABELS,
                             "voices": [v[0] for v in VOICES],
                             "vl_flags": len(vl_flags), "vl_fixes": n_fixed,
                             "method": "010 Hierarchical Diffusion + rules"})
print("provenance written")

# ---------------------------------------------------------------- grid viz
from visualization.grid import write_grid_visualization  # noqa: E402
write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                         ticks_per_character=120, bpm=BPM,
                         mode="A dorian / hierarchical diffusion")
print("grid_visualization.txt written")

with open(os.path.join(ANALYSIS_DIR, "concept.json"), "w") as f:
    json.dump({"project": "094-african-hierarchical-diffusion",
               "genre": "African", "method": "010 Hierarchical Diffusion",
               "layer": "concrete", "seed": SEED, "bpm": BPM,
               "key": "A dorian", "bars": N_BARS,
               "sections": NAMES, "grid_16th": GRID16,
               "progression": BAR_LABELS,
               "voices": [{"name": v[0], "program": v[1], "channel": v[2]}
                          for v in VOICES],
               "vl_flags": len(vl_flags), "vl_fixes": n_fixed,
               "phase1_notes": p1_note_count}, f, indent=2)
print("DONE")
