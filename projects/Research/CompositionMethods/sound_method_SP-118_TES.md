# Sound Production Method SP-118 — Transient Envelope Synthesis (TES)

## Overview

**Acronym**: TES  
**Full Name**: Transient Envelope Synthesis  
**Layer**: absolute — Post-Processing / DSP  
**Code Path**: `sound/effects/transient_shaper.py`  
**SP ID**: SP-118 (next free: SP-119)  

**One-line description**: Level-independent transient and sustain envelope shaping via Differential Envelope Technology (DET) — two envelope followers with fast (~1ms) and slow (~15ms) attack time constants whose difference isolates transient onsets and sustain decay regions for independent gain control.

---

## Extended Theory

### Differential Envelope Technology (DET)

The core insight (Tilgner 1998, SPL Audio) is to measure the *rate of change* of the amplitude envelope rather than the absolute level. This makes the processor **level-independent**: a quiet snareand a loud snare produce the same shaped control signal, scaled proportionally, with no threshold parameter.

**Two envelope followers in parallel:**

- **Fast envelope** $e_f[n]$: attack $\tau_f \approx 1$ ms, tracks instantaneous peaks
- **Slow envelope** $e_s[n]$: attack $\tau_s \approx 15$ ms, tracks running average level

Both use the same one-pole recursive filter:
$$e[n] = \alpha \cdot e[n-1] + (1-\alpha) \cdot |x[n|]$$
$$\alpha = e^{-1/(\au \cdot f_s)}$$

**Attack control signal**: $d_a[n] = \max(e_f[n] - e_s[n], 0)$
- Positive during transient onsets
- Near-zero at steady-state

**Sustain control signal** $d_s[n] = \max(e_s[n] - e_f[n], 0)$
- Positive during decays
- near-zero during attacks

**Gain application**:
$$g[n] = (1 + A cdot \hat{d}_a[n]) \cot (1 + S \cdot \hat{d}_s[n])$$
$y[n] = x[n} \cdot g_{\text{smooth}}[n]$$

Where $\hat{d}_a$ and $\hat{d}_s$ ar normalised to $[0,1]$ by a running pek tracker, $A \in [-1,1]$ is the attack control, $S \in [-1,1]$ is the sustain control, and $g_{\text{smooth}}$ is a one pole LPF on $g$ with $\tau_r \approx 1$ ms.

### Multiband Extension

For frequency-selective transient shaping, split the signal into $B =24$ Bark-scale frequency bands (Gammatone or biquad fiterbank). Run independent DET per band and sum. Cost scales $\mathcal{O}(B)$ per sample.

---

## Python/NumPy Implementation

### Single-band transient shaper

```python
import numpy as np

class TransientShaper:
    """
    Single-band transient shaper using Differential Envelope Technology (DET).
    Level-independent attack/sustain shaping.
    """
    def __init__(self, sr=44100):
        self.sr = sr
        self.attack_time_fast = 0.001    # 1 ms
        self.attack_time_slow = 0.015   # 15 ms
        self.release_time = 0.001       # 1 ms

        self.alpha_f = np.exp(-1.0 / (self.attack_time_fast * self.sr))
        self.alpha_s = np.exp(-1.0 / (self.attack_time_slow * self.sr))
        self.gamma = np.exp(-1.0 / (self.release_time * self.sr))

        self.env_fast = 0.0
        self.env_slow = 0.0
        self.gain_smooth = 1.0
        self.peak_norm = 1e-6
        self.attack = 0.0
        self.sustain = 0.0

    def process(self, x):
        n = len(x)
        y = np.empty_like(x)
        for i in range(n):
            s = abs(x[i])
            self.env_fast = self.alpha_f * self.env_fast + (1 - self.alpha_f) * s
            self.env_slow = self.alpha_s * self.env_slow + (1 - self.alpha_s) * s

            d_a = max(self.env_fast - self.env_slow, 0.0)
            d_s = max(self.env_slow - self.env_fast, 0.0)

            self.peak_norm = max(0.999 * self.peak_norm + 0.001 * (d_a + d_s), 1e-12)

            nd_a = d_a / self.peak_norm
            nd_s = d_s / self.peak_norm
            g = (1.0 + self.attack * nd_a) * (1.0 + self.sustain * nd_s)

            self.gain_smooth = self.gamma * self.gain_smooth + (1.0 - self.gamma) * g
            y[i] = x[i] * self.gain_smooth
        return y
```

### Multiband (Bark-scale) transient shaper

```python
from scipy.signal import butter, sosfilt

class MultibandTransientShaper:
    def __init__(self, sr=44100, n_bands=24):
        self.sr = sr
        self.n_bands = n_bands
        self.bands = [TransientShaper(sr) for _ in range(n_bands)]
        self.bark_freqs = [
            50, 150, 250, 350, 450, 570, 700, 840, 1000, 1170,
            1370, 1600, 1850, 2150, 2500, 2900, 3400, 4000, 4800,
            5800, 7000, 8500, 10500, 13500
        ]
        self._build_filterbank()

    def _build_filterbank(self):
        self._sos = []
        freqs = [0] + self.bark_freqs + [self.sr/2]
        for i in range(self.n_bands):
            low = freqs[i]
            high = freqs[i+2]
            sos = butter(2, [low / (self.sr/2), high / (self.sr/2)],
                         btype='band', output='sos')
            self._sos.append(sos)

    def process(self, x):
        y = np.zeros_like(x)
        zi = [np.zeros((sos.shape[0], 2)) for sos in self._sos]
        for b in range(self.n_bands):
            band, zi[b] = sosfilt(self._sos[b], x, zi=zi[b])
            y += self.bands[b].process(band)
        return y
```

---

## Musical Elements Framework Summary

| Element | TES Role |
|:---|:---|
| **PITCH** | No pitch alteration. Spectral content preserved. |
| **RHYTHM** | Reshapes transient/sustain ratio → crisp/smooth/tight/legato feel |
| **HARMONY** | Temporal shaping of harmonic components; reduces mud via sustain cut |
| **STRUCTURE** | Per-section $(A,S)$ automation → macro-form from envelope alone |
| **TEXTURE** | Four quadrants: punchy, smooth, aggressive, restrained |

## UnitMatrix Integration

- **Voices**: Independent $(A_v, S_v)$ per voice in DSP chain.
- **Sections**: Per-section $\theta_m = (A^{(m)}, S^{(m)})$ interpolated across boundaries.
- **Cell filleing**: Apply TES to rendered audio buffer $b_{v,m}[n]$ → $b'_{v,m}[n]$ (buffer length unchanged → zero-drift invariant holds).

## Complexity

| Stage | Cost | Notes |
|:---|:---:|:---|
| Single-band DET | $\sim12$ mult + $6$ add/sample | No FFT, sample-by-sample |
| Multiband 24-band | $\sim24\times$ | Bark filterbank + per-band DET |

All operations $\mathcal{O}(1)$ per sample, zero latency.

---

## References

1. Tilgner, R. (1998). "Transient Designer." SPL Audio / elysia GmbH. Differential Envelope Technology (DET).
2. SPL Transient Designer 2 Manual (9946). https://spl.audio/wp-content/uploads/transient_designer_2_9946_manual.pdf
3. elysia GmbH. "The Transient Designer Story, Part 1 & 2." https://www.elysia.com/transient-designer-story/
4. Audio Toolkit Blog. (2015–2016). "Anatomy of a Transient Shaper." Parts 1 & 2. https://blog.audio-tk.com/
5. HackAudio. (2017). "Transient Shaper." *HackAudio Textbook*, Chapter 17.
6. Zölzer, U. (2011). *DAFX: Digital Audio Effects* (2nd ed.). John Wiley & Sons. — Ch. 3.
7. Sadik, A. & Oklobdzija, V. G. (2011). "Transient Shaper for Audio Signals." *IEEE ISCAS*, 1203–1206.
8. Sevagh. (2020). "Bark-scale multi-band transient shaper." https://github.com/sevagh/multiband-transient-shaper