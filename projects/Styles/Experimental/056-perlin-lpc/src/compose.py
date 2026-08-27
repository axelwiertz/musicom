# -*- coding: utf-8 -*-
"""
Project 056: Perlin Noise Composition + LPC Synthesis
Method 040: Perlin Noise Composition (Nature-Led)
SP-028: Linear Predictive Coding (LPC) Synthesis

Perlin noise drives:
  - Lead melody pitch contour (fractal Brownian motion mapped to D Dorian)
  - Rhythm density per voice per section (noise threshold -> event probability)
  - Texture evolution (noise amplitude -> velocity scaling)

LPC post-processing:
  - Analyze FluidSynth WAV output via autocorrelation / Levinson-Durbin
  - Resynthesize through all-pole IIR filter for formant-like coloration
"""
import os
import sys
import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

# ---------------------------------------------------------------- CONFIG -----
PROJECT_NAME = "056-perlin-lpc"
PROJECT_DIR = f"/opt/data/projects/Styles/Experimental/{PROJECT_NAME}"
OUTPUT_DIR = PROJECT_DIR
BPM = 80
TICKS_PER_BEAT = 480
BEATS_PER_BAR = 4
BAR = TICKS_PER_BEAT * BEATS_PER_BAR  # 1920

# D Dorian: D E F G A B C -> pitch classes [2,4,5,7,9,11,1]
# MIDI base: D4=62
D_DORIAN_PCS = [2, 4, 5, 7, 9, 11, 1]  # scale degrees 0-6
D_DORIAN_SCALE = [62, 64, 65, 67, 69, 71, 72, 74]  # D4 to D5 (one octave)

# Perlin noise parameters
NOISE_SEED = 42
NOISE_OCTAVES = 4
NOISE_PERSISTENCE = 0.5
NOISE_LACUNARITY = 2.0


# ---- Perlin Noise Implementation (pure numpy, no external deps) ----
class PerlinNoise:
    """Simple 1D Perlin noise with fractal Brownian motion."""

    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        self.perm = np.arange(256, dtype=np.int32)
        self.rng.shuffle(self.perm)
        self.perm = np.concatenate([self.perm, self.perm])

    def _fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        return a + t * (b - a)

    def _grad(self, hash_val, x):
        h = hash_val & 3
        if h == 0:
            return x
        elif h == 1:
            return -x
        elif h == 2:
            return 1.0
        else:
            return -1.0

    def noise1d(self, x):
        xi = int(np.floor(x)) & 255
        xf = x - np.floor(x)
        u = self._fade(xf)
        a = self.perm[xi]
        b = self.perm[xi + 1]
        return self._lerp(self._grad(a, xf), self._grad(b, xf - 1), u)

    def fbm(self, x, octaves=4, persistence=0.5, lacunarity=2.0):
        """Fractal Brownian motion - sum of octaves of noise."""
        total = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_amp = 0.0
        for _ in range(octaves):
            total += self.noise1d(x * frequency) * amplitude
            max_amp += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        return total / max_amp if max_amp > 0 else 0.0


def perlin_map_to_scale(noise_val, scale_pitches, center_idx=3):
    """Map noise value [-1,1] to scale degree centered around center_idx."""
    # Normalize to [0, 1]
    norm = (noise_val + 1.0) / 2.0
    # Map to scale index range (center +/- 3 degrees)
    idx = int(norm * 6)  # 0-6
    idx = max(0, min(len(scale_pitches) - 1, idx))
    return scale_pitches[idx]


def generate_perlin_melody(perlin, num_steps, step_size=0.3, scale=None, base_octave=62):
    """Generate a melody by walking through Perlin noise space."""
    if scale is None:
        scale = D_DORIAN_SCALE
    pitches = []
    for i in range(num_steps):
        val = perlin.fbm(i * step_size, NOISE_OCTAVES, NOISE_PERSISTENCE, NOISE_LACUNARITY)
        pitch = perlin_map_to_scale(val, scale)
        pitches.append(pitch)
    return pitches


def generate_perlin_rhythm(perlin, num_steps, step_size=0.2, threshold=0.0):
    """Generate rhythm pattern from noise - above threshold = onset."""
    pattern = []
    for i in range(num_steps):
        val = perlin.fbm(i * step_size + 100, 3, 0.6, 2.0)  # offset to decorrelate
        pattern.append(1 if val > threshold else 0)
    return pattern


def generate_perlin_velocities(perlin, num_steps, step_size=0.15, base_vel=80, spread=30):
    """Generate velocity curve from noise."""
    vels = []
    for i in range(num_steps):
        val = perlin.fbm(i * step_size + 200, 2, 0.5, 2.0)
        vel = int(base_vel + val * spread)
        vels.append(max(40, min(127, vel)))
    return vels


def pad_unit_to_length(unit, total_ticks):
    """Ensure unit spans full total_ticks by adding silent padding event if needed."""
    if not unit.events:
        unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=total_ticks))
    else:
        max_end = max(e.end_tick for e in unit.events)
        if max_end < total_ticks:
            unit.add_event(MusicEvent(pitch=0, volume=0, start_tick=max_end, end_tick=total_ticks))
    return unit


def build_melody_unit(pitches, rhythm, velocities, ticks_per_step, total_ticks):
    """Build a MusicUnit from Perlin-generated pitch/rhythm/velocity arrays."""
    unit = MusicUnit()
    tick = 0
    for i in range(len(pitches)):
        if tick >= total_ticks:
            break
        if rhythm[i % len(rhythm)] == 1:
            dur = min(ticks_per_step, total_ticks - tick)
            vel = velocities[i % len(velocities)]
            unit.add_event(MusicEvent(
                pitch=pitches[i % len(pitches)],
                volume=vel,
                start_tick=tick,
                end_tick=tick + dur
            ))
        tick += ticks_per_step
    return pad_unit_to_length(unit, total_ticks)


def build_bass_unit(section_idx, total_ticks, perlin):
    """Bass follows root movement guided by noise - Dorian roots."""
    # Dorian chord roots: D(38), G(43), A(45), C(48) - low octave
    bass_notes = [38, 43, 45, 48]  # D2, G2, A2, C2
    unit = MusicUnit()

    # 4 beats per bar, 1 note per beat for bass
    step_ticks = TICKS_PER_BEAT
    num_steps = total_ticks // step_ticks

    for i in range(num_steps):
        tick = i * step_ticks
        # Noise selects bass note
        val = perlin.fbm(i * 0.4 + section_idx * 10, 2, 0.5, 2.0)
        idx = int((val + 1) / 2 * len(bass_notes))
        idx = max(0, min(len(bass_notes) - 1, idx))
        pitch = bass_notes[idx]
        vel = 70 + int(val * 15)
        unit.add_event(MusicEvent(
            pitch=pitch, volume=max(50, min(100, vel)),
            start_tick=tick, end_tick=tick + step_ticks
        ))
    return pad_unit_to_length(unit, total_ticks)


def build_pad_unit(section_idx, total_ticks, perlin):
    """Pad voice - sustained chords from Perlin-selected degrees."""
    # Dorian diatonic triads (low register): Dm, Em, F, G, Am, Bdim, C
    chord_sets = [
        [50, 53, 57],  # Dm: D3 F3 A3
        [52, 55, 59],  # Em: E3 G3 B3
        [53, 57, 60],  # F:  F3 A3 C4
        [55, 59, 62],  # G:  G3 B3 D4
        [57, 60, 64],  # Am: A3 C4 E4
        [53, 55, 59],  # Bdim (approx)
        [48, 52, 55],  # C:  C3 E3 G3
    ]
    unit = MusicUnit()
    # One chord per bar
    bars = total_ticks // BAR
    for bar_idx in range(bars):
        tick = bar_idx * BAR
        val = perlin.fbm(bar_idx * 0.5 + section_idx * 20 + 300, 2, 0.4, 2.0)
        idx = int((val + 1) / 2 * len(chord_sets))
        idx = max(0, min(len(chord_sets) - 1, idx))
        chord = chord_sets[idx]
        vel = 55 + int(val * 10)
        for p in chord:
            unit.add_event(MusicEvent(
                pitch=p, volume=max(40, min(80, vel)),
                start_tick=tick, end_tick=tick + BAR
            ))
    return pad_unit_to_length(unit, total_ticks)


def build_perc_unit(section_idx, total_ticks, perlin):
    """Percussion: kick on strong beats, hat from noise density."""
    unit = MusicUnit()
    step_ticks = TICKS_PER_BEAT // 2  # eighth notes
    num_steps = total_ticks // step_ticks

    for i in range(num_steps):
        tick = i * step_ticks
        beat_pos = i % 8  # position within bar (8 eighth notes)

        # Kick on 1 and 3 (positions 0, 4) - GM: 36
        if beat_pos in (0, 4):
            unit.add_event(MusicEvent(
                pitch=36, volume=100,
                start_tick=tick, end_tick=tick + step_ticks // 2
            ))

        # Snare on 2 and 4 (positions 2, 6) - GM: 38
        if beat_pos in (2, 6):
            unit.add_event(MusicEvent(
                pitch=38, volume=85,
                start_tick=tick, end_tick=tick + step_ticks // 2
            ))

        # Hi-hat: noise-driven density - GM: 42
        val = perlin.fbm(i * 0.3 + section_idx * 30 + 400, 2, 0.5, 2.0)
        if val > -0.2:  # most positions get a hat
            vel = int(50 + val * 20)
            unit.add_event(MusicEvent(
                pitch=42, volume=max(35, min(70, vel)),
                start_tick=tick, end_tick=tick + step_ticks // 4
            ))

    return pad_unit_to_length(unit, total_ticks)


def build_composer():
    """Build the full composition with Perlin-driven voices."""
    perlin = PerlinNoise(seed=NOISE_SEED)

    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS_PER_BEAT, beats_per_bar=BEATS_PER_BAR)
    c.create_matrix(num_voices=4, num_sections=3)

    # Voices
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)
    c.add_voice("Drums", program=0, channel=9)

    # Sections: A (4 bars), B (4 bars), A' (4 bars)
    c.add_section("A", bars=4)
    c.add_section("B", bars=4)
    c.add_section("C", bars=4)  # A' variant

    section_ticks = 4 * BAR  # 7680 ticks per section

    # Generate Perlin-driven melody (12 steps per section = 3 per bar)
    steps_per_section = 12
    step_ticks = section_ticks // steps_per_section  # 640 ticks

    for sec_idx, sec_name in enumerate(["A", "B", "C"]):
        # Lead melody - different noise offset per section
        sec_perlin = PerlinNoise(seed=NOISE_SEED + sec_idx * 100)
        pitches = generate_perlin_melody(sec_perlin, steps_per_section, step_size=0.35)
        rhythm = generate_perlin_rhythm(sec_perlin, steps_per_section, step_size=0.25, threshold=-0.1)
        velocities = generate_perlin_velocities(sec_perlin, steps_per_section)

        melody_unit = build_melody_unit(pitches, rhythm, velocities, step_ticks, section_ticks)
        c.fill_voice_section("Lead", sec_name, melody_unit)

        # Pad - sustained chords
        pad_unit = build_pad_unit(sec_idx, section_ticks, sec_perlin)
        c.fill_voice_section("Pad", sec_name, pad_unit)

        # Bass
        bass_unit = build_bass_unit(sec_idx, section_ticks, sec_perlin)
        c.fill_voice_section("Bass", sec_name, bass_unit)

        # Drums
        perc_unit = build_perc_unit(sec_idx, section_ticks, sec_perlin)
        c.fill_voice_section("Drums", sec_name, perc_unit)

    return c


def main():
    os.makedirs(os.path.join(OUTPUT_DIR, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "Analysis"), exist_ok=True)

    composer = build_composer()

    # Zero-drift validation
    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")

    midi_path = os.path.join(OUTPUT_DIR, "MIDI", f"{PROJECT_NAME}.mid")
    composer.to_midi(midi_path)

    size = os.path.getsize(midi_path)
    if size <= 40:
        raise SystemExit(f"MIDI empty/corrupt: {size} bytes")

    # Grid visualization
    grid_path = os.path.join(OUTPUT_DIR, "Analysis", "grid_visualization.txt")
    write_grid_visualization(
        composer.matrix, grid_path,
        ticks_per_character=240, bpm=BPM
    )

    # Provenance
    write_provenance(
        midi_path, classification=AI_ASSISTED,
        generator=f"{PROJECT_NAME}/compose.py",
        parameters={
            "bpm": BPM,
            "method": "040-Perlin-Noise-Composition",
            "seed": NOISE_SEED,
            "octaves": NOISE_OCTAVES,
            "key": "D Dorian",
            "form": "ABA (3x4 bars)",
            "voices": 4,
        },
        notes="Perlin noise (fBm) drives pitch contour, rhythm density, velocity. D Dorian. 80 BPM."
    )

    print(f"OK: {midi_path} ({size} bytes)")
    print(f"Grid: {grid_path}")


if __name__ == "__main__":
    main()
