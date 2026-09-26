# Hard Sync Oscillator Synthesis (HSOS) — SP-096

**Layer:** absolute (sound production — synthesis engines)
**Candidate code path:** `sound/synthesis/hard_sync.py`
**Produce dispatch:** `produce(midi_path, method="SP-096", params={"default_r": 3.0, "sync_mode": "hard", "master_wave": "saw", "slave_wave": "saw", "blep": True, "filter_cutoff": 8000, "filter_resonance": 0.7})`

## Overview

HSOS digitally replicates the analog oscillator hard-sync effect — the classic "tearing" or "screaming" lead/bass sound synonymous with the Minimoog, Sequential Prophet-5, and Roland SH-101. One oscillator (the master) runs at the pitch frequency; a second oscillator (the slave) runs at a higher frequency and is forced to reset its phase every master cycle. The perceived pitch = master frequency; the harmonic spectrum is determined by the ratio $r = f_{\text{slave}} / f_{\text{master}}$ alone. This decoupling of pitch from timbre makes HSOS a uniquely expressive sound: sweeping $r$ with an envelope or LFO produces dramatic spectral animation without changing the note.

Three sync modes are supported: **hard sync** (phase reset — the classic "sync sweep"), **soft sync** (phase-reverse — milder, triangle-core variant), and **comb-filter approximation** (Timoney et al. 2012 — computationally efficient model for high $r$). Bandlimited antialiasing via the PolyBLEP method (Välimäki & Huovilainen 2007) eliminates the aliasing artifacts that plague naive digital phase-reset implementations.

## Technical Mechanics

### 1. The Phase-Reset Algorithm (Naive)

Master phase accumulator:

$$\phi_m[n+1] = \phi_m[n] + \frac{2\pi f_m}{f_s}$$

Slave phase accumulator:

$$\phi_s[n+1] = \phi_s[n] + \frac{2\pi f_s}{f_s}$$

On master zero-crossing ($\phi_m \ge 2\pi$):

$$\phi_m := \phi_m - 2\pi \quad \text{(wrap master)}$$
$$\phi_s := \phi_s \bmod 2\pi \quad \text{(reset slave phase)}$$

Output (bipolar sawtooth slave):

$$y_{\text{naive}}[n] = \frac{2\phi_s[n]}{2\pi} - 1 = 2\theta_s[n] - 1, \quad \theta_s \in [0,1)$$

The phase reset creates a discontinuity (jump) in the slave waveform each master period. The jump magnitude depends on the slave's residual phase at reset time:

$$\Delta_k = 2\theta_s(t_k^-) \quad \text{(from +1 direction to the residual value)}$$

### 2. Fourier Series (Timoney et al. 2012)

For a hard-synced sawtooth with ratio $r = f_s/f_m$, the $k$-th harmonic amplitude is:

$$|H_k| = \frac{2}{k\pi} \frac{|\sin(k\pi/r)|}{\sin(\pi/r)}$$

The spectrum is:
- **Integer $r$** ($r = 2,3,4,\dots$): harmonics only at multiples of $r$, producing pure octave-doubling or twelfth-doubling effects.
- **Non-integer $r$**: all harmonics are present, yielding a dense, inharmonic buzz.
- **High $r$** ($r > 5$): the spectrum approaches a dense sawtooth-like harmonic series, and the sync effect becomes less perceptible (many resets per master cycle → the slave waveform is mostly complete segments).

### 3. Comb-Filter Approximation

Rather than explicit phase reset, hard sync can be modeled as a comb filter applied to the master sawtooth (Timoney et al. 2012):

$$H(z) = \frac{1 - z^{-\lfloor r \rfloor}}{1 + z^{-\lfloor r \rfloor}}$$

This produces an equivalent spectrum without per-sample phase tracking, at reduced computational cost. The filter's periodic nulls at frequencies $k f_m / \lfloor r \rfloor$ recreate the spectral gaps of integer-ratio hard sync.

### 4. PolyBLEP Anti-Aliasing (Välimäki & Huovilainen 2007)

Each phase reset is a step discontinuity of magnitude $\Delta_k$. The BLEP method replaces the discontinuity with a bandlimited transition. PolyBLEP uses a 4-sample polynomial approximation:

$$y_{\text{blep}}[n] = y_{\text{naive}}[n] + \sum_k \Delta_k \cdot \text{PolyBLEP}\left( \frac{n - n_k}{f_s} \right)$$

where the PolyBLEP residual for sample offset $t$ (in samples, $t \in \mathbb{R}$ relative to the discontinuity at sample $n_k$) is:

$$p(t) = \begin{cases}
0 & t < -2 \text{ or } t > 2 \\
\frac{1}{2}\left(\frac{t+2}{2}\right)^2 & -2 \le t < -1 \\
\frac{3}{4} - \left(\frac{t+1}{2}\right)^2 - \frac{t}{2} & -1 \le t < 0 \\
\frac{3}{4} - \left(\frac{t}{2}\right)^2 + \frac{t}{2} & 0 \le t < 1 \\
\frac{1}{2}\left(-\frac{t+2}{2}\right)^2 + 1 & 1 \le t \le 2
\end{cases}$$

The residual is subtracted on the left of the discontinuity and added on the right, smoothly bridging the jump.

### 5. Sine Hard Sync Antialiasing (La Pastina & D'Angelo 2022)

For sine slaves, the discontinuity is of infinite order (all derivatives discontinuous). The residual must be computed via FIR kernel convolution:

$$y_{\text{sine-sync}}[n] = \sin(\theta_s[n]) + \sum_k \text{Res}\left(\theta_s[n] - \theta_{\text{res}}^{(k)}\right)$$

Using a triangular kernel with support $[-K, K]$ samples ($K = 4$ recommended for 44.1 kHz):

$$\text{Res}_{\text{tri}}(\theta) = \frac{2}{K^2 \omega_0^2} \left[ \cos(\omega_0 \theta/f_s) - 1 + \frac{\omega_0 K}{2 f_s} \sin\left(\frac{\omega_0 K}{2 f_s}\right) \cos\left(\frac{\omega_0 \theta}{f_s}\right) - \frac{\omega_0 \theta}{f_s} \sin\left(\frac{\omega_0 \theta}{f_s}\right) \right]$$

This eliminates aliasing for sine hard sync at $\mathcal{O}(K)$ per sample — much cheaper than 4–8× oversampling.

### 6. Soft Sync (Phase-Reverse)

In the triangle-core soft sync variant, the slave oscillator's direction reverses at each master reset rather than resetting to zero:

$$y_{\text{soft}}[n] = \begin{cases}
y_{\text{slave}}[n] & \text{between resets} \\
-y_{\text{slave}}[n] & \text{after reversal}
\end{cases}$$

The output waveform is continuous (no DC jump), so aliasing is naturally lower — but the harmonic effect is less dramatic, producing a gentler octave-doubling or subharmonic timbre.

## Musical Elements Framework

| Element | Contribution |
|---------|-------------|
| **PITCH** | Master frequency = perceived fundamental. Slave frequency = timbre control only. Master tracks MIDI note number exactly (12-TET). Per-voice/section $r$ sweep with envelope/LFO for dynamic timbre. |
| **RHYTHM** | Master oscillator gated by note-on/off provides rhythmic articulation. Audio-rate master gating produces pitched rhythm/hocket. |
| **HARMONY** | Integer $r$ = octave/twelfth/double-octave layering. Non-integer $r$ = inharmonic bell/gong spectra. Multiple voices with different $r$ = chordal layering. |
| **STRUCTURE** | Per-section $r$ and sync mode define macro-form: verse = integer $r$ (clean), chorus = high non-integer $r$ (aggressive), bridge = modulated $r$ (sweep). Master waveform type adds palette variation. |
| **TEXTURE** | Low $r$ (1–2) = sparse partials, high $r$ (7+) = dense buzz. LFO/envelope $r$ modulation = evolving texture. Multi-voice pairs = orchestral thickness. |

## UnitMatrix Integration

- **Voices (rows)**: Each voice = one HSOS pair or shared-master chain. Independent $r$, sync_mode, waveform types per voice. Shared master pattern: one master at harmonic anchor, per-voice slaves sync to it.
- **Sections (columns)**: Per-section parameters: $r$, sync_mode, master_wave, slave_wave, filter cutoff/resonance, BLEP on/off.
- **Cells (MusicUnit)**: pitch→master_freq, r→slave/master ratio (float≥1.0), sync_mode, master_wave, slave_wave, velocity→gain.
- **Produce**: `produce(midi_path, method="SP-096", params={"default_r": 3.0, "sync_mode": "hard", "master_wave": "saw", "slave_wave": "saw", "blep": True, ...})`
- **Post-processing**: HSOS buffer → subtractive filter (SP-029/SP-020) + ADSR envelope. HSOS is the exciter; filter+envelope shape the final tone.

## Python/NumPy Implementation Sketch

```python
import numpy as np

def hard_sync_saw(r, f_m, duration, sr=44100, antialias=True):
    """Generate hard-synced sawtooth with PolyBLEP antialiasing.
    
    Args:
        r: slave/master frequency ratio (float >= 1.0)
        f_m: master frequency (Hz)
        duration: output duration (seconds)
        sr: sample rate (Hz)
        antialias: apply PolyBLEP correction
    Returns:
        numpy array of samples (-1 to +1)
    """
    N = int(sr * duration)
    y = np.zeros(N)
    
    phi_m = 0.0
    phi_s = 0.0
    dphi_m = 2 * np.pi * f_m / sr
    dphi_s = 2 * np.pi * f_m * r / sr
    
    for n in range(N):
        # Phase accumulators
        phi_m += dphi_m
        phi_s += dphi_s
        
        # Detect master zero-crossing
        if phi_m >= 2 * np.pi:
            phi_m -= 2 * np.pi
            residual = phi_s  # save residual before reset
            phi_s = 0.0
            
            if antialias:
                # Apply PolyBLEP correction around the discontinuity
                # (simplified: 2-sample BLEP, 1 each side)
                frac = residual / (2 * np.pi)  # normalized residual [0,1)
                jump = 2 * frac  # discontinuity magnitude
                if n >= 2:
                    # Left side correction (subtract)
                    t = 1.0  # one sample before
                    if t >= 0 and t < 1:
                        corr = 0.5 * t * t
                    elif t >= 1 and t <= 2:
                        corr = 1.0 - 0.5 * (2 - t) * (2 - t)
                    else:
                        corr = 0.0
                    y[n-1] -= jump * corr
                    
                    # Right side correction (add after reset)
                    y[n] += jump * 0.5  # first post-reset sample
        
        # Naive sawtooth output
        theta_s = phi_s / (2 * np.pi)  # [0, 1)
        y[n] += 2 * theta_s - 1
    
    return np.clip(y, -1.0, 1.0)

def hard_sync_fourier_spectrum(r, n_harmonics=20):
    """Compute theoretical harmonic amplitudes for hard-synced sawtooth."""
    k = np.arange(1, n_harmonics + 1)
    numerator = np.abs(np.sin(k * np.pi / r))
    denominator = k * np.pi * np.sin(np.pi / r)
    return 2 * numerator / denominator
```

## References

1. Brandt, E. (2001). Hard Sync Without Aliasing. *Proc. 2001 Intl. Computer Music Conf. (ICMC'01)*, Havana, Cuba, pp. 365–368. — The BLEP method for alias-free hard sync.
2. Timoney, J., Lazzarini, V., Hodgkinson, M., Kleimola, J., Pekonen, J., & Välimäki, V. (2012). Virtual analog oscillator hard synchronisation: Fourier series and an efficient implementation. *Proc. 15th Intl. Conf. Digital Audio Effects (DAFx-12)*, York, UK. — Fourier series derivation and comb-filter model.
3. Välimäki, V. & Huovilainen, A. (2007). Antialiasing oscillators in subtractive synthesis. *IEEE Signal Processing Magazine*, 24, 116–125. — PolyBLEP method.
4. La Pastina, P.P. & D'Angelo, S. (2022). A general antialiasing method for sine hard sync. *Proc. 25th Intl. Conf. Digital Audio Effects (DAFx-20in22)*, Vienna, Austria. — FIR kernel antialiasing for sine hard sync.
5. Zavalishin, V. (2018). *The Art of VA Filter Design* (2nd ed.). Native Instruments. Ch. 8: Sync oscillators.
6. Stilson, T.S. & Smith, J.O. (1996). Alias-free digital synthesis of classic analog waveforms. *Proc. 1996 Intl. Computer Music Conf. (ICMC'96)*, Hong Kong, pp. 332–335. — BLIT method foundation.
7. Kleimola, J. & Välimäki, V. (2012). Reducing aliasing from synthetic audio signals using polynomial transition regions. *IEEE Signal Processing Letters*, 19(2), 67–70. — PTR method.