# Tonewheel Electromagnetic Modeling Synthesis (TWEMS) — SP-095

**Layer:** absolute (sound production — synthesis engines)
**Candidate code path:** `sound/synthesis/twems.py`
**Produce dispatch:** `produce(midi_path, method="SP-095", params={"registration": [8,8,8,8,0,0,0,0,0], "leslie_speed": "fast", "vib_chorus": "C3", "percussion": "3rd"})`

## Overview

TWEMS digitally replicates the Hammond tonewheel organ generator — the earliest electromechanical polyphonic synthesizer (Laurens Hammond, 1935). Unlike general-purpose additive synthesis (SP-039), TWEMS models the specific 91-tonewheel physical generator with its mechanical constraints: harmonic foldback, key-click from 9-pole busbar contact bounce, 5 Hz synchronous-motor tremolo, 6-position scanner vibrato/chorus phase-shift network, drawbar registration with fixed harmonic ratios, and the companion Leslie rotating speaker cabinet.

## Technical Mechanics

### 1. Tonewheel Generator

91 rotating toothed steel disks (tonewheels) mounted on a common synchronous shaft. Each wheel's teeth pass a magnetic pickup coil, inducing a sinusoidal voltage. The 91 tonewheels span 7 octaves of the 12-tone scale (approximate equal temperament).

For each key pressed, nine drawbar harmonics are summed:

$$ y_{key}[n] = \sum_{k=1}^{9} g_k \cdot \sin(2\pi \cdot r_k \cdot f_0 \cdot n / f_s) $$

**Drawbar ratios $r_k$:**
| Drawbar | Footage | Ratio $r_k$ | Harmonic |
|---------|---------|-------------|----------|
| 1 | 16' | 0.5 | Sub-octave |
| 2 | 5⅓' | 1.5 | Fifth above |
| 3 | 8' | 1.0 | Fundamental |
| 4 | 4' | 2.0 | Octave |
| 5 | 2⅔' | 3.0 | Twelfth |
| 6 | 2' | 4.0 | Double octave |
| 7 | 1⅗' | 5.0 | Seventeenth |
| 8 | 1⅓' | 6.0 | Nineteenth |
| 9 | 1' | 8.0 | Triple octave |

**Amplitude:** $g_k = d_k / 8$, where $d_k \in \{0,1,\dots,8\}$ is the drawbar position. Optional magnetic pickup compensation: $a_k = 1/\sqrt{k}$.

### 2. Harmonic Foldback

Only 91 tonewheels exist. When a requested harmonic exceeds the range, it foldback repeats from a lower octave:

$$ \text{pitch}_{k,\text{key}} = \begin{cases}
f_0 \cdot r_k, & \text{tonewheel index} \le 91 \\
f_0 \cdot r_k \cdot 2^{-m}, & \text{otherwise, } m = \text{foldback octaves}
\end{cases} $$

The foldback table for C2–C7 (61 notes):
- Drawbar 5 (3rd): folds from C6 down when tonewheel > 91
- Drawbar 7 (5th): folds from tonewheel 52 (G)
- Drawbar 8 (6th): partial foldback
- Drawbar 9 (8th): folds from tonewheel 44 (G)

### 3. Key-Click Transient

The 9-key contacts switch audio-level signals, producing a percussive transient:

$$ y_{click}[n] = w[n] \cdot \left( \sum_{k=1}^{9} \sigma_k \cdot \sin(2\pi \cdot 6f_0 \cdot n/f_s) \right) \cdot e^{-n/\tau} $$

- $w[n]$: Bernoulli-switched contact bounce (~1 kHz, 5 ms)
- $\sigma_k$: staggered contact closure (lower→higher drawbars, 2–5 ms)
- $\tau$: click decay (~10 ms)

6th harmonic emphasis matches the classic Hammond key-click spectral peak (Pekonen et al. 2011).

### 4. Synchronous Motor Tremolo

$$ y_{trem}[n] = y_{key}[n] \cdot \left(1 + m \cdot \sin(2\pi \cdot f_{trem} \cdot n/f_s)\right) $$

- $f_{trem} = 5.0$ Hz (60 Hz mains) or 6.25 Hz (50 Hz mains)
- $m \approx 0.1$ (classic depth)

### 5. Scanner Vibrato/Chorus

Time-varying phase-shift delay line (12–18 taps scanned by rotating contact):

$$ y_{vib}[n] = (1 - \alpha) \cdot y_{in}[n] + \alpha \cdot y_{in}[n - \delta[n]] $$
$$ \delta[n] = \delta_{base} + \Delta\delta \cdot \sin(2\pi \cdot f_{vib} \cdot n/f_s) $$

- V-1/V-2/V-3: increasing vibrato depth (no dry mix)
- C-1/C-2/C-3: chorused (50/50 dry/wet mix)

$f_{vib} \approx 6.5$ Hz.

### 6. Leslie Rotating Speaker Cabinet

Two counter-rotating elements: horn (treble, ~400 RPM fast/~40 RPM slow) and drum (bass, ~340 RPM/~40 RPM slow).

**Doppler effect (time-varying delay):**
$$ y_{dopp}[n] = x[n - D[n]] $$
$$ D[n] = D_0 + \Delta D \cdot \sin(2\pi \cdot f_{rot} \cdot n/f_s) $$

**Instantaneous pitch shift:**
$$ f_{out} = f_{in} \cdot \left(1 - \frac{d}{dt} D[n]\right) $$

**Tremolo from directional horn pattern:**
$$ y_{leslie}[n] = y_{dopp}[n] \cdot A_{horn}(\theta[n]) $$
$$ A_{horn}(\theta) = G_0 + \Delta G \cdot \cos(\theta) $$
$$ \theta[n] = 2\pi \cdot f_{rot} \cdot n/f_s $$

Signal split at ~800 Hz crossover, horn and drum processed independently, then summed with stereo panning.

### 7. Percussion Circuit (B3 only)

Transient 2nd or 3rd harmonic burst at note-on:

$$ y_{perc}[n] = \begin{cases}
A_{perc} \cdot \sin(2\pi \cdot p \cdot f_0 \cdot n/f_s) \cdot e^{-n/\tau_{perc}}, & n < N_{perc} \\
0, & \text{otherwise}
\end{cases} $$

- $p \in \{2, 3\}$: soft (2nd) or normal (3rd)
- $\tau_{perc} \approx 150$ ms decay

## Python/NumPy Implementation Sketch

```python
import numpy as np
from typing import List, Tuple

class TonewheelVoice:
    """Single voice (key) of the TWEMS tonewheel generator."""

    DRAWBAR_RATIOS = [0.5, 1.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]

    def __init__(self, f0: float, registration: List[float],
                 samplerate: int = 44100, mains_hz: int = 60):
        self.f0 = f0
        self.registration = np.array(registration) / 8.0  # normalize 0-8 to 0-1
        self.fs = samplerate
        self.phase = np.zeros(9)          # per-partial phase accumulator
        self.vel = 0.0                    # envelope velocity
        self.trem_phase = 0.0
        self.trem_rate = 5.0 if mains_hz == 60 else 6.25
        self.active = False

    def process(self, n: int) -> float:
        if not self.active:
            return 0.0
        # Accumulate 9 partials
        y = 0.0
        for k in range(9):
            if self.registration[k] > 0:
                inc = 2 * np.pi * self.DRAWBAR_RATIOS[k] * self.f0 / self.fs
                self.phase[k] += inc
                y += self.registration[k] * np.sin(self.phase[k])
        # Tremolo
        self.trem_phase += 2 * np.pi * self.trem_rate / self.fs
        y *= (1.0 + 0.1 * np.sin(self.trem_phase))
        return y / 9.0  # normalize


class VibratoChorus:
    """Scanner vibrato/chorus with time-varying delay."""

    def __init__(self, samplerate: int = 44100, max_delay: float = 0.005):
        self.fs = samplerate
        self.max_delay_s = max_delay
        self.buf_size = int(max_delay * samplerate) + 4
        self.buf = np.zeros(self.buf_size)
        self.write_idx = 0
        self.vib_rate = 6.5  # Hz
        self.vib_depth = 0.001  # seconds
        self.mix = 0.0  # 0 = dry only, 0.5 = chorus

    def process(self, x: float, n: int) -> float:
        self.buf[self.write_idx] = x
        delay_s = self.vib_depth * np.sin(2 * np.pi * self.vib_rate * n / self.fs)
        delay_s += self.vib_depth  # center at depth, range [0, 2*depth]
        delay_samp = delay_s * self.fs
        int_part = int(delay_samp)
        frac = delay_samp - int_part
        read_idx = (self.write_idx - int_part) % self.buf_size
        # Linear interpolation
        y_del = (1 - frac) * self.buf[read_idx] + frac * self.buf[(read_idx - 1) % self.buf_size]
        self.write_idx = (self.write_idx + 1) % self.buf_size
        # Mix: vibrato = only delayed; chorus = equal dry+delayed
        if self.mix > 0:
            return (1 - self.mix) * x + self.mix * y_del
        return y_del


class LeslieSpeaker:
    """Rotating speaker effect with Doppler + tremolo + crossover."""

    def __init__(self, samplerate: int = 44100):
        self.fs = samplerate
        self.crossover_hz = 800
        # Horn (treble): fast ~400 RPM (6.67 Hz), slow ~40 RPM (0.67 Hz)
        self.horn_rpm = 400.0
        self.horn_angle = 0.0
        # Drum (bass): fast ~340 RPM (5.67 Hz)
        self.drum_rpm = 340.0
        self.drum_angle = 0.0
        # Doppler delay parameters
        self.delay_base = 0.001  # 1 ms
        self.delay_mod = 0.0005  # ±0.5 ms
        # Horn directional gain
        self.gain_base = 0.7
        self.gain_mod = 0.3

    def set_speed(self, speed: str):
        """'stop', 'slow', 'fast'"""
        if speed == 'fast':
            self.horn_rpm, self.drum_rpm = 400.0, 340.0
        elif speed == 'slow':
            self.horn_rpm, self.drum_rpm = 40.0, 40.0
        else:
            self.horn_rpm, self.drum_rpm = 0.0, 0.0

    def process(self, x: float, n: int) -> Tuple[float, float]:
        # Simple crossover (1-pole)
        alpha = self.crossover_hz / (self.crossover_hz + self.fs / (2 * np.pi))
        # Integrate angles
        self.horn_angle += 2 * np.pi * self.horn_rpm / 60.0 / self.fs
        self.drum_angle += 2 * np.pi * self.drum_rpm / 60.0 / self.fs
        # Doppler delay
        d_horn = self.delay_base + self.delay_mod * np.sin(self.horn_angle)
        d_drum = self.delay_base + self.delay_mod * np.sin(self.drum_angle)
        # Simple pitch-shift via fractional delay (Thiran approx omitted for brevity)
        # Horn gain
        g_horn = self.gain_base + self.gain_mod * np.cos(self.horn_angle)
        g_drum = self.gain_base + self.gain_mod * np.cos(self.drum_angle)
        # Split and remix
        # (full implementation would use proper fractional delay interpolation)
        y_horn = x * g_horn
        y_drum = x * g_drum
        return (y_horn + y_drum) * 0.5  # simplified mono return
```

## Musical Elements Framework

| Element | TWEMS Expression |
|---------|-----------------|
| **PITCH** | Drawbar registration (9 fixed ratios), foldback artifacts, scanner vibrato pitch modulation (±5 cents) |
| **RHYTHM** | Key-click transient (6th harmonic + contact bounce), percussion circuit transient, Leslie speed-switching |
| **HARMONY** | Drawbar registration controls chord voicing; Hammond temperamento; Leslie chorusing (ensemble shimmer) |
| **STRUCTURE** | Preset key / registration changes = sections; Leslie speed = section energy; foldback = pitch boundary |
| **TEXTURE** | P partials per note × polyphony; Leslie spatial movement; scanner chorus thickening; key-click granularity |

## UnitMatrix Integration

- **Voices** → Hammond manuals (upper/lower/pedal), each with independent registration
- **Sections** → registration change, Leslie speed switch, vibrato/chorus selector, percussion toggle
- **Cells** → drawbar vector **d** ∈ [0,8]⁹ + Leslie speed + vib/chorus selector + percussion mode
- **Produce**: `produce(midi_path, method="SP-095", params={...})`

## References

1. Pekonen, J., Pihlajamäki, T., & Välimäki, V. (2011). "Computationally efficient Hammond organ synthesis." *Proc. DAFx-11*, Paris, pp. 19–23.
2. Smith, J. O. (2010). *Physical Audio Signal Processing*. https://ccrma.stanford.edu/~jos/pasp/ — Ch. 7: Doppler simulation and the Leslie.
3. Puckette, M. (2006). *The Theory and Technique of Electronic Music*. Ch. 2 (additive synthesis).
4. Savolainen, S. (2010). "Emulating a Combo Organ Using Faust."
5. Electric Druid. "Technical aspects of the Hammond Organ." https://electricdruid.net/technical-aspects-of-the-hammond-organ/
6. Hammond Organ Company (1935). US Patent 1,956,350: Electrical Musical Instrument.
7. Välimäki, V., & Laakso, T. I. (1995). "Fractional delay filter design for the Leslie effect." *IEEE Workshop on Applications of Signal Processing to Audio and Acoustics*.