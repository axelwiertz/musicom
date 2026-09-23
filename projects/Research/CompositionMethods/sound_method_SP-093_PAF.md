# Method SP-093: Phase-Aligned Formant Synthesis (PAF)

**Method ID:** SP-093  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  
**Status:** Canonical Reference Specification  
**Author:** Miller Puckette (IRCAM 1994 / JAES 1995; *The Theory and Technique of Electronic Music*, 2006)  
**Candidate Implementation:** `sound/synthesis/paf.py`  
**Integration Point:** `workflows.musicom_workflow.produce(method="SP-093")`

---

## 1. Overview & Theoretical Foundations

Phase-Aligned Formant (PAF) synthesis is an analytical distortion / waveshaping technique devised by Miller Puckette at IRCAM. It provides direct, independent, and continuous control over:
1. Fundamental pitch frequency ($f_0$)
2. Formant center frequency ($f_c$)
3. Formant bandwidth ($b_w$)

In traditional acoustic modeling and speech/vocal synthesis:
- **Subtractive formant synthesis** filters an excitation (e.g. pulse train or sawtooth) through narrow resonant IIR/biquad bandpass filters. This introduces phase rotation, frequency-dependent delay, filter ring-down smearing, and numerical instability under fast modulation.
- **FOF (Formant-Wave-Function) synthesis** (SP-025) sums decaying granular cosine wavepackets triggered at each fundamental pitch period. While highly authentic, FOF requires managing overlapping grain ring-buffers, window lookups, and grain lifecycle scheduling.
- **Phase Modulation / FM Formant synthesis** introduces asymmetric, complex sideband phase interactions, making multiple formant peaks difficult to superpose constructively without interference notches.

PAF overcomes these challenges by generating arbitrary spectral formant peaks directly in the time domain using memoryless waveshaping of an absolute half-frequency sinusoidal driver, modulated by a phase-aligned two-cosine carrier. Crucially, all partials are synthesized with strictly zero phase relative to the fundamental period, allowing multiple arbitrary formant peaks to be superposed additively with zero destructive phase cancellation.

---

## 2. Mathematical Formalism & DSP Mechanics

### 2.1 Core Formula

Given sample index $n$, sampling frequency $f_s$, and angular fundamental frequency $\omega_0 = 2\pi f_0 / f_s$, the discrete output $x[n]$ of a single PAF generator is:

$$x[n] = g\Big(a \cdot \big|\sin(\omega_0 n / 2)\big|\Big) \cdot \Big[ (1 - q)\cos(k \omega_0 n) + q\cos\big((k + 1)\omega_0 n\big) \Big]$$

Where:
- $g(u)$ is an even waveshaping transfer function.
- $a$ is the modulation index controlling bandwidth.
- $k \in \mathbb{Z}^+$ and $q \in [0, 1)$ are the integer harmonic index and fractional interpolation factor controlling formant center frequency.

### 2.2 Parameter Decomposition

Given desired formant center frequency $f_c$ and formant bandwidth $b_w$ (both in Hz):

1. **Center Frequency Mapping:**
   $$m = \frac{f_c}{f_0}$$
   $$k = \lfloor m \rfloor$$
   $$q = m - k = \text{frac}(m)$$
   $$p = 1 - q$$

   The carrier consists of two adjacent harmonic cosines: $\cos(k \omega_0 n)$ and $\cos((k + 1)\omega_0 n)$, weighted by $p$ and $q$. As $f_c$ varies continuously, the power shifts linearly between adjacent harmonics, placing the spectral centroid at $(k + q) f_0 = f_c$.

2. **Bandwidth & Modulation Index:**
   $$a = \frac{\pi \cdot b_w}{f_0}$$
   The modulation index scales the input amplitude to waveshaper $g(u)$. Higher values of $a$ steepen the pulse in the time domain, which expands the bandwidth in the frequency domain.

### 2.3 Waveshaping Functions

1. **Cauchy Waveshaping Function:**
   $$g_{\text{Cauchy}}(u) = \frac{1}{1 + u^2}$$
   The Fourier transform of the Cauchy distribution is a bilateral exponential decay $e^{-|\omega|}$. When viewed on a logarithmic decibel scale, the spectral skirts fall off linearly, matching measured acoustic vocal tract resonances.

2. **Gaussian Waveshaping Function:**
   $$g_{\text{Gauss}}(u) = \exp(-u^2)$$
   The Fourier transform of a Gaussian is also Gaussian. It features exceptionally rapid high-frequency attenuation, suppressing aliasing near Nyquist.

### 2.4 Half-Frequency Rectification

The pulse modulator requires an argument that pulses at fundamental frequency $f_0$. Computing $\sin(\omega_0 n / 2)$ produces a subharmonic at $f_0 / 2$. However, because $g(u)$ is strictly an even function ($g(-u) = g(u)$), taking the absolute value:
$$|\sin(\omega_0 n / 2)|$$
rectifies the waveform, yielding identical symmetric half-cycles repeating at fundamental rate $f_0$. This avoids needing a separate phase accumulator or resetting state.

### 2.5 Zero Phase Alignment & Superposition

Because the carrier cosines and the even waveshaping pulse have zero phase at the period boundary ($n\omega_0 = 2\pi M$), all resulting spectral partials are pure cosines with zero phase offset:
$$\cos((k \pm r)\omega_0 n)$$

For an arbitrary vocal vowel or instrument timbre specified by $F$ formants $\{(f_{c,j}, b_{w,j}, A_j)\}_{j=1}^F$:
$$x_{\text{multi}}[n] = \sum_{j=1}^F A_j \cdot C(a_j) \cdot x_j[n]$$
Where $C(a) \approx 1 + a$ normalizes the central formant peak height across varying bandwidths.

---

## 3. Musical Elements Framework

- **PITCH**: Determined strictly by master phase accumulator $\theta[n] = \omega_0 n \pmod{2\pi}$. Formant peaks stay stationary while $f_0$ moves, maintaining distinct vocal or instrument identity across vocal ranges, vibrato, and portamento glides.
- **RHYTHM**: Memoryless time-domain formulation provides sample-accurate attack transients without filter ring-up delays.
- **HARMONY**: Coherent additive nature allows pristine polyphonic vocal choirs and chord voicings without inter-voice phase clashing or distortion.
- **STRUCTURE**: Trajectories of formants $(F_1, F_2, F_3)$ map directly across UnitMatrix section columns to produce structured phonetic transformations (e.g. vowel transitions /a/ -> /o/ -> /u/).
- **TEXTURE**: From smooth flute-like purity ($a < 0.5$) to rich resonant brass buzz ($a > 4.0$). Adding non-integer phase offsets creates clangorous inharmonic bell spectra.

---

## 4. Implementation in Python / NumPy

```python
"""
sound/synthesis/paf.py - Phase-Aligned Formant Synthesis (Method SP-093)
"""

import numpy as np
from typing import List, Tuple, Dict, Any

def generate_paf_tone(
    f0: float,
    duration: float,
    formants: List[Tuple[float, float, float]], # list of (fc, bw, gain)
    sr: int = 44100,
    waveshaper: str = "cauchy"
) -> np.ndarray:
    """
    Synthesizes a multi-formant tone using Phase-Aligned Formant (PAF) synthesis.
    
    Args:
        f0: Fundamental frequency in Hz.
        duration: Duration in seconds.
        formants: List of tuples (fc, bw, gain) representing formant center (Hz),
                  bandwidth (Hz), and linear gain.
        sr: Sample rate.
        waveshaper: 'cauchy' or 'gaussian'.
        
    Returns:
        1D numpy array of float32 samples.
    """
    n_samples = int(duration * sr)
    if n_samples <= 0 or f0 <= 0:
        return np.zeros(max(0, n_samples), dtype=np.float32)
        
    t = np.arange(n_samples, dtype=np.float64)
    omega0 = 2.0 * np.pi * f0 / sr
    phi = omega0 * t
    half_phi = 0.5 * phi
    
    # Abs sin driver for the even waveshaper
    abs_sin = np.abs(np.sin(half_phi))
    
    out = np.zeros(n_samples, dtype=np.float64)
    
    for fc, bw, gain in formants:
        # Bandwidth index
        a = (np.pi * bw) / f0
        
        # Center frequency parameters
        m = fc / f0
        k = int(np.floor(m))
        q = float(m - k)
        p = 1.0 - q
        
        # Waveshaper pulse
        u = a * abs_sin
        if waveshaper == "cauchy":
            mod = 1.0 / (1.0 + u * u)
        elif waveshaper == "gaussian":
            mod = np.exp(-u * u)
        else:
            raise ValueError(f"Unknown waveshaper: {waveshaper}")
            
        # Two-cosine carrier
        carrier = p * np.cos(k * phi) + q * np.cos((k + 1.0) * phi)
        
        # Peak normalization
        norm_factor = 1.0 + a
        
        out += gain * norm_factor * (mod * carrier)
        
    # Apply standard smooth envelope to prevent edge clicks
    fade_len = min(int(0.005 * sr), n_samples // 4)
    if fade_len > 0:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        out[:fade_len] *= fade_in
        out[-fade_len:] *= fade_out
        
    # Scale output
    max_val = np.max(np.abs(out))
    if max_val > 1e-6:
        out = (out / max_val) * 0.95
        
    return out.astype(np.float32)
```

---

## 5. UnitMatrix Workflow Integration

In `musicom`:
- **Voices**: Assigned to vocal leads, synthesizer formants, or resonant acoustic instruments.
- **Sections**: Formant schedules ($[F_1, F_2, F_3]$) defined per section.
- **Cells**: Each `MusicUnit` contains note events rendered deterministically into sample buffers with zero track drift.

---

## 6. References
- Puckette, M. (1995). "Formant-based audio synthesis using nonlinear distortion." *Journal of the Audio Engineering Society*, 43(1–2), 40–47.
- Puckette, M. (2006). *The Theory and Technique of Electronic Music*. World Scientific Publishing Co., Chapter 6: Designer Spectra (Phase-Aligned Formant Generator).
- Roads, C. (1996). *The Computer Music Tutorial*. MIT Press.
