# Vector Synthesis (4-Corner Wavetable Crossfade) — Method SP-047

**Sound Production Method** — Synthesis Engines layer.
**Acronym**: VS-4C (Vector Synthesis, 4-Corner).

## One-line description
Mixes four single-cycle corner wavetables via bilinear interpolation driven by a 2D vector position (joystick / LFO / vector envelope / algorithmic driver); the 2D plane is a timbre map and the trajectory is the timbral macro-form.

## Source
Prophet VS (Sequential Circuits, 1986) → Korg Wavestation (1990, wave sequencing + vector envelope) → Yamaha SY22/TG33 (1990, FM hybrid). 2D counterpart to SP-041 (1D wavetable morph).

## Core equations

Bilinear blend of four corner wavetables $A, B, C, D$ at vector position $(x, y) \in [0,1]^2$:

$$w(n) = A(n)(1-x)(1-y) + B(n)\,x(1-y) + C(n)\,x\,y + D(n)(1-x)\,y$$

Phase-accumulator playback at pitch $f_0$:

$$\phi_{k+1} = \phi_k + \frac{f_0 \cdot N}{f_s} \pmod N, \qquad s_k = w(\lfloor \phi_k \rfloor)$$

Weights sum to 1 (convex combination), so no gain is added by the mix itself.

## Musical Elements Framework
- **PITCH**: phase increment $f_0 \cdot N / f_s$; fully decoupled from timbre.
- **RHYTHM**: note grid + vector-trajectory rate (fast = tremolo, slow = pad); vector envelope synced to bar grid = timbral sequencing.
- **HARMONY**: corner waveform choice shapes harmonic content (odd vs even vs inharmonic partials).
- **STRUCTURE**: 2D plane = timbre map; each section = a region/trajectory; the trajectory IS the structural arc.
- **TEXTURE**: corner set + trajectory speed/chaos + number of independent voices.

## UnitMatrix Integration
- Rows (Voices) = independent vector oscillators (own accumulator, corner set, trajectory).
- Columns (Sections) = vector trajectory / rate / corner swap; boundaries = trajectory jump or crossfade.
- Cells $U_{v,s}$ = {PITCH: MIDI→phase inc; RHYTHM: onset grid + env timing; TEXTURE: 4 corners + vector position + rate}.

## Python / NumPy implementation sketch

```python
import numpy as np

def make_wavetable(n=2048, kind="saw"):
    t = np.arange(n) / n
    if kind == "sine":      return np.sin(2*np.pi*t)
    if kind == "saw":       return 2*t - 1          # band-limit via mipmap/PolyBLEP (SP-041)
    if kind == "square":    return np.where(t < 0.5, 1.0, -1.0)
    if kind == "triangle":  return 1 - 4*np.abs(t - 0.5)
    if kind == "inharmonic":
        return (np.sin(2*np.pi*t) + 0.5*np.sin(2*np.pi*2.3*t)
                + 0.3*np.sin(2*np.pi*4.7*t))
    raise ValueError(kind)

def midi_to_hz(p):
    return 440.0 * 2 ** ((p - 69) / 12)

def render_vector_voice(midi_notes, corners, xtraj, ytraj, fs=44100, n=2048):
    A, B, C, D = corners["A"], corners["B"], corners["C"], corners["D"]
    total = int(sum(d for _, d, _ in midi_notes) * fs)
    out = np.zeros(total); phase = 0.0; t = 0
    for pitch, dur, vel in midi_notes:
        inc = midi_to_hz(pitch) * n / fs
        for _ in range(int(dur * fs)):
            i = int(phase) % n
            x, y = xtraj[t], ytraj[t]
            out[t] = vel * (A[i]*(1-x)*(1-y) + B[i]*x*(1-y)
                            + C[i]*x*y + D[i]*(1-x)*y)
            phase += inc; t += 1
    return out

def lissajous(n, fx=0.1, fy=0.13):
    tt = np.arange(n) / n
    return (0.5 + 0.5*np.sin(2*np.pi*fx*n*tt),
            0.5 + 0.5*np.sin(2*np.pi*fy*n*tt))
```

## Pitfalls (condensed)
1. Aliasing from naive single-cycle playback → mipmap/PolyBLEP (SP-041).
2. Phase misalignment across corners → comb filtering; normalize fundamental phase.
3. Energy dip at center → pre-normalize corners to equal RMS or energy-preserving crossfade.
4. Clicks from vector jumps → slew-limit / crossfade at boundaries.
5. DC offset accumulation → remove DC per corner + high-pass.
6. Per-sample random vector → zipper noise; keep control-rate.
7. Redundant corners → choose spectrally distinct waveforms.

## References
- Sequential Circuits Prophet VS (1986) operator's manual.
- Korg Wavestation (1990) owner's manual ("Advanced Vector Synthesis").
- Yamaha SY22 / TG33 (1990) owner's manual.
- Roads, C. (1996). *The Computer Music Tutorial*. MIT Press.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley.
- Smith, J. O. (2010). *Spectral Audio Signal Processing* (wavetable/band-limiting).
