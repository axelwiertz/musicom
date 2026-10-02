# -*- coding: utf-8 -*-
"""
Project 217: Perlin x D Dorian -- Extended Suite (extension of 102).

AUDIT of 102-perlin-dorian-bridge-mirror: ALL 6 standards PASS.
  -> decision = EXTENSION (no redesign). Keep musical identity,
     use 102 as the DNA seed, compose a NEW LONGER + MORE VARIED piece.

Preserved musical identity: Experimental genre, D Dorian, 80 BPM,
  Perlin-fBm driven pitch/rhythm/velocity, Flute/Strings/Bass/Drums.

Extension (vs 102):
  form:     6 sections x 4 bars (24 bars)  ->  8 sections x 4 bars (32 bars)
  voices:   4 (Lead/Pad/Bass/Drums)       ->  5 (+ Counter canon line)
  variation: 5 transforms                 ->  8 techniques (incl. diminution,
             canon/imitative counterline, register + density split)

Two-phase architecture:
  Phase 1 = raw generative draft (Perlin fBm -> scale-degree + rhythm),
            single lead voice, diatonic-only, NOT chord-quantized.
  Phase 2 = musicom rules: per-bar chord-tone quantization, rhythm-grid snap
            (120/240), key discipline, register clamp, per-section variation
            (ALL transforms in scale-degree space -> never leaves key).
"""
import os
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.unitmatrix_composer import UnitMatrixComposer

# ------------------------------------------------------------- CONFIG ----
GENRE = "Experimental"
PROJECT_NAME = "217-perlin-dorian-mirror-suite"
PROJECT_DIR = f"/opt/data/projects/Styles/{GENRE}/{PROJECT_NAME}"

BPM = 80
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920
GRID = 120  # 8th/16th snap resolution

NOISE_SEED = 42

# D Dorian (CORRECT): D E F G A B C -> pcs {0,2,4,5,7,9,11}
KEY_NAME = "D Dorian"
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}
# scale degree 0..6 -> semitone offset from D4 (62)
SCALE_STEPS = [0, 2, 3, 5, 7, 9, 10]   # D E F G A B C

# chord degree -> pitch classes (D Dorian triads); every set subset of KEY_PCS
DEG_PCS = {
    0: {2, 5, 9},     # i    Dm
    1: {4, 7, 11},    # ii   Em
    2: {5, 9, 0},     # III  F
    3: {7, 11, 2},    # IV   G
    4: {9, 0, 4},     # v    Am
    5: {11, 2, 5},    # vi°  Bdim
    6: {0, 4, 7},     # VII  C
}
DEG_NAME = {0: "i-Dm", 1: "ii-Em", 2: "III-F", 3: "IV-G",
            4: "v-Am", 5: "vio-Bdim", 6: "VII-C"}
DEG_QUALITY = {0: "minor", 1: "minor", 2: "major", 3: "major",
               4: "minor", 5: "diminished", 6: "major"}
DEG_ROOT = {0: 38, 1: 40, 2: 41, 3: 43, 4: 45, 5: 47, 6: 48}

# section -> (id, label, 4 chord degrees per bar, transform, note)
# 8 sections, each with its OWN harmonic region (never bar-0 tonic trap).
SECTIONS = [
    ("A", "Intro",       [0, 6, 0, 3], "none",       "motif exposed, sparse"),
    ("B", "Verse",       [0, 3, 4, 0], "transpose",  "motif up a 4th (+3 deg)"),
    ("C", "Verse2",      [4, 0, 3, 0], "diminution", "rhythm compressed, faster"),
    ("D", "Chorus",      [3, 0, 6, 3], "octave_up",  "register +8ve, dense"),
    ("E", "Bridge",      [5, 2, 4, 6], "retrograde", "pitch sequence reversed"),
    ("F", "Development", [0, 0, 3, 3], "invert",     "contour inverted + canon"),
    ("G", "Climax",      [3, 6, 0, 0], "octave_up",  "register + density + canon"),
    ("H", "Outro",       [0, 6, 3, 0], "augment",    "augmented + register down"),
]

# step ticks (grid), rhythm threshold
SECTION_PARAMS = {
    "A": {"step": 480, "thr": 0.15},
    "B": {"step": 240, "thr": -0.10},
    "C": {"step": 120, "thr": -0.15},
    "D": {"step": 120, "thr": -0.35},
    "E": {"step": 240, "thr": -0.15},
    "F": {"step": 120, "thr": -0.30},
    "G": {"step": 120, "thr": -0.40},
    "H": {"step": 960, "thr": 0.30},
}


# ------------------------------------------------------------- perlin ----
class PerlinNoise:
    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        self.perm = np.arange(256, dtype=np.int32)
        self.rng.shuffle(self.perm)
        self.perm = np.concatenate([self.perm, self.perm])

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        return a + t * (b - a)

    def _grad(self, h, x):
        h = h & 3
        return {0: x, 1: -x, 2: 1.0, 3: -1.0}[h]

    def noise1d(self, x):
        xi = int(np.floor(x)) & 255
        xf = x - np.floor(x)
        u = self._fade(xf)
        a, b = self.perm[xi], self.perm[xi + 1]
        return self._lerp(self._grad(a, xf), self._grad(b, xf - 1), u)

    def fbm(self, x, octaves=4, persistence=0.5, lacunarity=2.0):
        total, amp, freq, maxamp = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.noise1d(x * freq) * amp
            maxamp += amp
            amp *= persistence
            freq *= lacunarity
        return total / maxamp if maxamp > 0 else 0.0


def degree_to_midi(deg, oct_shift=0, base=62):
    """scale degree 0..6 -> MIDI (D Dorian from D4=62), with octave shift."""
    d = deg % 7
    octv = deg // 7
    return base + SCALE_STEPS[d] + 12 * octv + 12 * oct_shift


def chord_tones(deg_id, lo=48, hi=108):
    return [m for m in range(lo, hi + 1) if (m % 12) in DEG_PCS[deg_id]]


def nearest_in(pitches, target):
    return min(pitches, key=lambda p: abs(p - target))


# ------------------------------------------------------- phase-1 raw -----
def raw_lead(section, sec_idx):
    """Phase 1: Perlin fBm -> scale degree int + rhythm mask + velocity."""
    name, label, degrees, transform, _note = section
    p = SECTION_PARAMS[name]
    step, thr = p["step"], p["thr"]
    n = (4 * BAR) // step
    sec_perlin = PerlinNoise(seed=NOISE_SEED + sec_idx * 100)
    out = []
    for i in range(n):
        tick = i * step
        val = sec_perlin.fbm(i * 0.35 + sec_idx * 1.7, 4, 0.5, 2.0)
        rval = sec_perlin.fbm(i * 0.25 + sec_idx * 1.7 + 100, 3, 0.6, 2.0)
        if rval <= thr:
            continue
        deg = int(((val + 1.0) / 2.0) * 7)
        deg = max(0, min(6, deg))
        vel = max(45, min(120, int(80 + val * 25)))
        out.append({"tick": tick, "deg": deg, "oct": 0, "vel": vel, "dur": step})
    return out


# ------------------------------------------------------- phase-2 rules ---
def apply_transform(events, transform, total=4 * BAR):
    if transform == "none":
        return events
    if transform == "transpose":
        for e in events:
            e["deg"] += 3  # up a 4th = +3 scale degrees
        return events
    if transform == "octave_up":
        for e in events:
            e["oct"] += 1
        return events
    if transform == "diminution":
        # compress rhythm toward start (same contour, double speed),
        # halve durations; grid snap happens in quantize()
        base = min((e["tick"] for e in events), default=0)
        for e in events:
            e["tick"] = base + int((e["tick"] - base) * 0.5)
            e["dur"] = max(120, e["dur"] // 2)
        return events
    if transform == "retrograde":
        degs = [e["deg"] for e in reversed(events)]   # reverse pitch seq
        octs = [e["oct"] for e in reversed(events)]
        for e, d, o in zip(events, degs, octs):
            e["deg"], e["oct"] = d, o
        return events
    if transform == "invert":
        for e in events:
            e["deg"] = 6 - e["deg"]  # reflect scale index (around G)
        return events
    if transform == "augment":
        for e in events:
            e["oct"] -= 1          # register down an octave
            e["dur"] = max(e["dur"], 2 * 960)  # augmented duration
        return events
    return events


def quantize(events, degrees, lo=52, hi=88):
    """Phase 2 rule: chord-tone quantize per bar (floor t//BAR), grid snap,
    register clamp, dedup collided (tick,pitch) keeping longest duration."""
    tones_per_bar = [chord_tones(d, 48, 108) for d in degrees]
    seen = {}
    for e in events:
        tick = int(round(e["tick"] / GRID) * GRID)   # snap to 8th/16th grid
        bar = tick // BAR                             # floor, not round
        if bar >= 4:
            continue
        midi_raw = degree_to_midi(e["deg"], e["oct"])
        chor = nearest_in(tones_per_bar[bar], midi_raw)  # chord-tone quantize
        chor = max(lo, min(hi, chor))                    # register clamp
        key = (tick, chor)
        if key in seen:
            seen[key] = max(seen[key], e["dur"])
        else:
            seen[key] = e["dur"]
    out = []
    for (tick, pitch), dur in sorted(seen.items()):
        out.append((tick, pitch, 90, dur))
    return out


def _unit_from_quantized(q, total):
    unit = MusicUnit()
    for (t, p, v, d) in q:
        unit.add_event(MusicEvent(pitch=p, volume=v, start_tick=t, end_tick=min(t + d, total)))
    return _pad(unit, total)


def build_lead_unit(section, sec_idx):
    name, label, degrees, transform, _ = section
    raw = raw_lead(section, sec_idx)
    raw = apply_transform(raw, transform)
    q = quantize(raw, degrees, lo=52, hi=88)
    return _unit_from_quantized(q, 4 * BAR)


def build_counter_unit(section, sec_idx):
    """Canon / imitative counterline. Only in Development + Climax:
    echo the lead contour delayed one beat, transposed up a 3rd."""
    name, label, degrees, transform, _ = section
    total = 4 * BAR
    if name not in ("F", "G"):
        return _pad(MusicUnit(), total)
    raw = raw_lead(section, sec_idx)
    raw = apply_transform(raw, transform)
    delayed = []
    for e in raw:
        tick = e["tick"] + TICKS_PER_BEAT  # one-beat canon delay
        if tick + 120 > total:
            continue
        delayed.append({"tick": tick, "deg": e["deg"] + 2, "oct": e["oct"],
                        "vel": max(40, e["vel"] - 10), "dur": e["dur"]})
    q = quantize(delayed, degrees, lo=60, hi=96)   # sits above the lead
    return _unit_from_quantized(q, total)


def build_pad_unit(section, sec_idx):
    name, label, degrees, transform, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for bar in range(4):
        d = degrees[bar]
        tones = chord_tones(d, 48, 72)
        triad = sorted(tones, key=lambda x: abs(x - 60))[:3]
        for pp in sorted(triad):
            unit.add_event(MusicEvent(
                pitch=pp, volume=58,
                start_tick=bar * BAR, end_tick=(bar + 1) * BAR))
    return _pad(unit, total)


def build_bass_unit(section, sec_idx):
    name, label, degrees, transform, _ = section
    total = 4 * BAR
    unit = MusicUnit()
    for bar in range(4):
        d = degrees[bar]
        root = DEG_ROOT[d]
        # root on beats 1&3, octave on beats 2&4 (always chord tones + diatonic)
        for beat, note in ((0, root), (1, root + 12), (2, root), (3, root + 12)):
            tick = bar * BAR + beat * TICKS_PER_BEAT
            unit.add_event(MusicEvent(
                pitch=note, volume=72,
                start_tick=tick, end_tick=tick + TICKS_PER_BEAT))
    return _pad(unit, total)


def build_drums_unit(section, sec_idx):
    name, label, degrees, transform, _ = section
    p = SECTION_PARAMS[name]
    total = 4 * BAR
    unit = MusicUnit()
    dense = p["step"] <= 120
    step = TICKS_PER_BEAT // 2
    n = total // step
    for i in range(n):
        tick = i * step
        pos = i % 8
        if pos in (0, 4):
            unit.add_event(MusicEvent(pitch=36, volume=100, start_tick=tick, end_tick=tick + step // 2))
        if pos in (2, 6):
            unit.add_event(MusicEvent(pitch=38, volume=82, start_tick=tick, end_tick=tick + step // 2))
        if pos % 2 == 0 or dense:
            unit.add_event(MusicEvent(pitch=42, volume=60, start_tick=tick, end_tick=tick + step // 4))
    return _pad(unit, total)


def _pad(unit, total):
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total))
    else:
        mx = max(e.end_tick for e in unit.events)
        if mx < total:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=mx, end_tick=total))
    return unit


# ------------------------------------------------------- phase-1 export --
def export_phase1(out_path):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    for (name, label, degrees, transform, note) in SECTIONS:
        c.add_section(name, bars=4)
    for idx, section in enumerate(SECTIONS):
        name = section[0]
        raw = raw_lead(section, idx)
        total = 4 * BAR
        unit = MusicUnit()
        for e in raw:
            midi = degree_to_midi(e["deg"], e["oct"])
            unit.add_event(MusicEvent(
                pitch=midi, volume=e["vel"],
                start_tick=e["tick"], end_tick=min(e["tick"] + e["dur"], total)))
        c.fill_voice_section("Lead", name, _pad(unit, total))
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    c.to_midi(out_path)
    return c


# ------------------------------------------------------------- main ------
def main():
    for sub in ("MIDI", "Audio", "Analysis"):
        os.makedirs(os.path.join(PROJECT_DIR, sub), exist_ok=True)

    p1_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}-phase1.mid")
    export_phase1(p1_path)
    write_provenance(
        p1_path, classification=AI_ASSISTED,
        generator="040-Perlin-Noise-Composition + musicom rules",
        parameters={"phase": 1, "bpm": BPM, "key": KEY_NAME,
                    "seed": NOISE_SEED, "voices": 1,
                    "note": "raw generative draft, diatonic, pre-rules"},
    )

    c2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c2.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    c2.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c2.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    c2.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    c2.add_voice("Counter", program=MidiInstrument.TRUMPET, channel=3)
    c2.add_voice("Drums", program=0, channel=9)
    for (name, label, degrees, transform, note) in SECTIONS:
        c2.add_section(name, bars=4)

    for idx, section in enumerate(SECTIONS):
        name = section[0]
        c2.fill_voice_section("Lead", name, build_lead_unit(section, idx))
        c2.fill_voice_section("Pad", name, build_pad_unit(section, idx))
        c2.fill_voice_section("Bass", name, build_bass_unit(section, idx))
        c2.fill_voice_section("Counter", name, build_counter_unit(section, idx))
        c2.fill_voice_section("Drums", name, build_drums_unit(section, idx))

    ok, msg = c2.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")

    midi_path = os.path.join(PROJECT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    c2.to_midi(midi_path)
    assert os.path.getsize(midi_path) > 40, "empty phase2"
    assert os.path.getsize(p1_path) > 40, "empty phase1"

    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator="040-Perlin-Noise-Composition + musicom rules",
        parameters={"phase": 2, "bpm": BPM, "key": KEY_NAME,
                    "seed": NOISE_SEED, "voices": 5,
                    "form": "8 sections x 4 bars = 32 bars",
                    "variations": "transpose(+4th), diminution, octave_up, "
                                  "retrograde, invert, canon(counterline), augment"},
        notes="Extension of 102-perlin-dorian-bridge-mirror (all standards passed). "
              "8-section suite, +Counter canon voice, chord-tone quantized, "
              "grid-snapped, key-disciplined.",
    )

    grid_path = os.path.join(PROJECT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240, bpm=BPM)

    print("PHASE1", p1_path, os.path.getsize(p1_path))
    print("PHASE2", midi_path, os.path.getsize(midi_path))
    print("GRID", grid_path)


if __name__ == "__main__":
    main()
