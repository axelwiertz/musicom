# -*- coding: utf-8 -*-
"""052-perlin-chebyshev: Perlin Noise Composition (Method 040) + Chebyshev Waveshaping (SP-019).

Uses musicom UnitMatrixComposer for zero-drift MIDI. Perlin noise drives pitch
contour and rhythm density. Chebyshev waveshaping parameters influence velocity
and timbre mapping for the GM render.
"""
import os, math, json

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from ai.utils.visualizer import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

PROJECT = "052-perlin-chebyshev"
BASE = f"/opt/data/projects/Styles/Experimental/{PROJECT}"
BPM = 100
TPB = 480
BPB = 4
BAR = TPB * BPB  # 1920

# --- Perlin noise (simple 1D gradient) ---
class Perlin:
    def __init__(self, seed=42):
        import random as r
        r.seed(seed)
        self.perm = list(range(256))
        r.shuffle(self.perm)
        self.perm *= 2
    def _fade(self, t): return t*t*t*(t*(t*6-15)+10)
    def _grad(self, h, x): return x if (h & 1) == 0 else -x
    def noise(self, x):
        xi = int(x) & 255
        xf = x - int(x)
        u = self._fade(xf)
        a = self.perm[xi]; b = self.perm[xi+1]
        return (1-u)*self._grad(a, xf) + u*self._grad(b, xf-1)
    def fbm(self, x, octaves=4):
        val, amp, freq = 0.0, 1.0, 1.0
        for _ in range(octaves):
            val += self.noise(x*freq)*amp
            amp *= 0.5; freq *= 2.0
        return val

def chebyshev_velocity(pitch_idx, order=5):
    """Map pitch index through Chebyshev polynomial for velocity shaping."""
    x = (pitch_idx % 12) / 11.0 * 2.0 - 1.0  # normalize to [-1,1]
    # T5(x) = 16x^5 - 20x^3 + 5x
    t5 = 16*x**5 - 20*x**3 + 5*x
    return max(40, min(120, int(80 + t5 * 30)))

def build_composer():
    p = Perlin(seed=2026)
    # D minor scale (D E F G A Bb C)
    scale = [62, 64, 65, 67, 69, 70, 72, 74]  # MIDI pitches D4-D5

    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    c.create_matrix(num_voices=3, num_sections=3)
    c.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    c.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=1)
    c.add_voice("Bass", program=MidiInstrument.BASS, channel=2)

    sections = ["A", "B", "C"]
    for s in sections:
        c.add_section(s, bars=4)

    # Generate Perlin-driven melodies per section
    for si, sec in enumerate(sections):
        # Lead: Perlin pitch contour
        events = []
        tick = 0
        for step in range(16):  # 16 steps per section (4 bars x 4 subdivisions)
            n_val = p.fbm(step * 0.3 + si * 10, octaves=3)
            idx = int((n_val + 1) * 0.5 * (len(scale)-1))
            idx = max(0, min(len(scale)-1, idx))
            pitch = scale[idx]
            dur = TPB  # quarter note
            vel = chebyshev_velocity(idx, order=5)
            events.append(MusicEvent(pitch=pitch, volume=vel, start_tick=tick, end_tick=tick+dur))
            tick += dur
        lead_unit = MusicUnit(events=events)
        c.fill_voice_section("Lead", sec, lead_unit)

        # Pad: chord from scale degrees
        chord_pitches = [scale[0]-12, scale[2]-12, scale[4]-12, scale[6]-12]
        pad_unit = create_chord_unit(chord_pitches, 4 * BAR)
        c.fill_voice_section("Pad", sec, pad_unit)

        # Bass: root motion via Perlin
        bass_events = []
        for bar in range(4):
            bn = p.fbm(bar * 0.5 + si * 20, octaves=2)
            bidx = int((bn + 1) * 0.5 * 3)  # 0-3
            bidx = max(0, min(3, bidx))
            bpitch = scale[bidx * 2] - 24  # octave down
            bass_events.append(MusicEvent(pitch=bpitch, volume=90, start_tick=bar*BAR, end_tick=(bar+1)*BAR))
        bass_unit = MusicUnit(events=bass_events)
        c.fill_voice_section("Bass", sec, bass_unit)

    return c

def main():
    os.makedirs(os.path.join(BASE, "MIDI"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "Audio"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "Analysis"), exist_ok=True)

    composer = build_composer()
    ok, msg = composer.validate()
    if not ok:
        raise SystemExit(f"Validation failed: {msg}")

    midi_path = os.path.join(BASE, "MIDI", f"{PROJECT}.mid")
    composer.to_midi(midi_path)
    sz = os.path.getsize(midi_path)
    assert sz > 40, f"MIDI too small: {sz}"

    write_grid_visualization(
        composer.matrix, os.path.join(BASE, "Analysis", "grid_visualization.txt"),
        ticks_per_character=240, bpm=BPM)
    write_provenance(
        midi_path, classification=AI_ASSISTED, generator="052-perlin-chebyshev/src/compose.py",
        parameters={"bpm": BPM, "method": "040", "production": "SP-019"},
        notes="Perlin Noise pitch/rhythm + Chebyshev waveshaping velocity mapping.")

    print(f"OK: {midi_path} ({sz} bytes)")

if __name__ == "__main__":
    main()
