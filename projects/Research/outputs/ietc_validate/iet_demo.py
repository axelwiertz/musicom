"""IETC demo: 4 voices x 3 sections, zero-drift UnitMatrix -> MIDI.

Interval Exchange Transformation Composition (method 121).
Run:  $MUSICOM_PYTHON iet_demo.py
"""
import os
import numpy as np
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

BAR = 1920

def cum(lam):
    return np.concatenate(([0.0], np.cumsum(lam)))

def iet(x, lam, pi):
    a = cum(lam)
    aimg = np.array([lam[pi < pi[i]].sum() for i in range(len(lam))])
    k = int(np.clip(np.searchsorted(a, x, side="right") - 1, 0, len(lam) - 1))
    return (x - a[k] + aimg[k]) % 1.0, k

# --- exchange data: 7 intervals, tonic region widest (tonal gravity by width) ---
LAM = np.array([0.26, 0.17, 0.06, 0.13, 0.09, 0.21, 0.08])
assert abs(LAM.sum() - 1) < 1e-12
PI = np.array([6, 1, 2, 3, 4, 5, 0])          # irreducible (Keane condition)

# 12-slot diatonic quantizer: pitch slot -> semitone offset (duplicates = chord tones)
SLOT = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19]

VOICES = [
    ("Lead",   MidiInstrument.FLUTE,       72, 0.041),
    ("Counter",MidiInstrument.TRUMPET,     60, 0.377),
    ("Pad",    MidiInstrument.STRING_ENSEMBLE, 48, 0.618),
    ("Bass",   MidiInstrument.BASS,        36, 0.909),
]

def orbit_cell(x0, n_steps, section_len, octave_shift=0, vel_base=88):
    """One UnitMatrix cell = n_steps orbit steps laid out in absolute section ticks."""
    ev, x, t = [], x0, 0
    for _ in range(n_steps):
        u = x
        slot = int(u * 12) % 12
        pitch = octave_shift + SLOT[slot]
        _, k = iet(x, LAM, PI)                  # region the point currently sits in
        dur = int(BAR / 4) * (1 + k % 3)        # region -> rhythmic value class
        dur = max(120, dur)
        if t + dur > section_len:
            dur = section_len - t
        if dur <= 0:
            break
        vel = int(np.clip(vel_base + 12 * (u - 0.5), 40, 120))
        ev.append(MusicEvent(pitch=pitch, volume=vel, start_tick=t, end_tick=t + dur))
        t += dur
        x = iet(x, LAM, PI)[0]
        if t >= section_len:
            break
    if not ev:
        raise RuntimeError("empty cell")
    # zero-drift: terminal landmark at section_len
    last = ev[-1]
    if last.end_tick < section_len:
        ev[-1] = MusicEvent(pitch=last.pitch, volume=last.volume,
                            start_tick=last.start_tick, end_tick=section_len)
    return MusicUnit(events=ev)

composer = UnitMatrixComposer(bpm=96, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=3)
for name, prog, shift, _ in VOICES:
    composer.add_voice(name, program=prog, channel=VOICES.index((name, prog, shift, _)))
for s in ("A", "B", "C"):
    composer.add_section(s, bars=2)
SEC_LEN = 2 * BAR

for vi, (name, prog, shift, x0) in enumerate(VOICES):
    x = x0
    for si, sec in enumerate(("A", "B", "C")):
        # section renormalization: advance the orbit by a section-length jump
        unit = orbit_cell(x, n_steps=SEC_LEN // 240, section_len=SEC_LEN,
                          octave_shift=shift, vel_base=84 - 4 * si)
        composer.fill_voice_section(name, sec, unit)
        for _ in range(12):                      # orbit carries across the seam
            x = iet(x, LAM, PI)[0]

ok, msg = composer.validate()
print(f"validate() -> {ok}: {msg}")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ietc_demo.mid")
composer.to_midi(out)
size = os.path.getsize(out)
assert size > 40, f"empty/corrupt MIDI ({size} B)"
print(f"wrote {out} ({size} bytes, {composer.get_track_length_bars()} bars)")
print("done")
