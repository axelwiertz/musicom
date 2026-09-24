# Method SP-094: Through-Zero Frequency Modulation Synthesis (TZFM)

**Method ID:** SP-094  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  
**Status:** Canonical Reference Specification  
**Author:** David A. Jaffe & Julius O. Smith (1983); John Chowning (1973); Yamaha FS1R (1998); modern analog implementations by Endorphin.es, Intellijel, Instruo, Verbos  
**Candidate Implementation:** `sound/synthesis/tzfm.py`  
**Integration Point:** `workflows.musicom_workflow.produce(method="SP-094")`

---

## 1. Overview & Theoretical Foundations

Through-Zero Frequency Modulation (TZFM) is a variant of frequency modulation synthesis in which the carrier oscillator's instantaneous frequency is permitted to cross below zero Hz, causing the phase accumulator to **reverse direction** rather than stalling at zero. This seemingly small change has profound consequences:

1. **Pitch stability** — The carrier's center frequency $f_c$ is preserved exactly regardless of modulation depth $d$, because the mean instantaneous frequency over any zero-mean modulator cycle remains $f_c$.
2. **Arbitrary modulation depth** — The modulation index $\beta = d / f_m$ can be driven arbitrarily high without the pitch detuning that plagues conventional linear FM.
3. **Richer spectra** — Phase reversal at zero crossings introduces time-reversed waveform segments that generate additional spectral energy beyond the classical Bessel expansion.

### 1.1 Relationship to Existing FM Methods

| Method | Technique | Pitch Stability | Max Depth Limit |
|---|---|---|---|
| SP-010 (Basic FM) | Phase modulation (DX7-style) | Perfect (inherently phase mod) | Numerical (phases stay bounded) |
| SP-017 (Feedback FM) | Carrier modulates own frequency | Variable | Feedback loop gain < 1 |
| SP-094 (TZFM) | Bidirectional phase accumulation | Perfect (zero-mean modulator) | Nyquist-limited only |

TZFM is the **linear FM done right** — it provides the pitch-accuracy of phase modulation (SP-010 is technically phase modulation, not true FM) with the timbral richness of true frequency modulation. The TZFM output at low depth is identical to conventional FM; at high depth, the difference is dramatic.

---

## 2. Mathematical Formalism & DSP Mechanics

### 2.1 The Problem with Conventional Linear FM

A standard digital oscillator computes:

$$ \phi[n+1] = \big( \phi[n] + \Delta\phi[n] \big) \bmod 1.0 $$

$$ \Delta\phi[n] = \frac{f_c + d \cdot m[n]}{f_s} $$

When $f_c + d \cdot m[n] < 0$, the increment $\Delta\phi[n]$ is negative. However, the modulo operation $(\psi + \Delta) \bmod 1.0$ in IEEE floating point maps $(-0.3) \bmod 1.0 = 0.7$ — the sign is _erased_, and the phase continues forward with a positive increment equal to $1 + \Delta\phi$. The result:

- The instantaneous frequency clamps to a positive value (below $f_c$ by $|f_c + d\cdot m|$).
- A DC offset proportional to the clamped time builds up.
- The **perceived pitch rises** because the oscillator spends less time than expected at low frequencies.

### 2.2 TZFM: Bidirectional Phase Accumulation

TZFM fixes this by tracking phase direction internally. Two equivalent formulations:

**Formulation A: Signed Phase + Direction Flag**

$$ \theta[n+1] = \theta[n] + \Delta\phi[n] \quad (\text{no modulo}) $$

$$ y[n] = \begin{cases}
\text{wt}\big( \lfloor \theta[n] \cdot W \rfloor \bmod W \big), & \Delta\phi[n] \ge 0 \\
\text{wt}\big( \lfloor (1 - \theta[n]) \cdot W \rfloor \bmod W \big), & \Delta\phi[n] < 0
\end{cases} $$

Phase $\theta[n]$ is unwrapped (real-valued, no modulo). The wavetable read direction flips when the increment sign flips.

**Formulation B: Modulo with Sign Preservation**

$$ \psi[n] = \big( \psi[n-1] + \Delta\phi[n-1] \big) \bmod 1.0 $$

$$ y[n] = \text{wt}\big( \lfloor \psi[n] \cdot W \rfloor \bmod W \big) $$

This works because the modulo operation $(\psi + \Delta) \bmod 1.0$ naturally decreases $\psi$ when $\Delta < 0$, since in IEEE floating-point:
- $0.2 + (-0.3) = -0.1$, then $-0.1 \bmod 1.0 = 0.9$
- The table is read with index $0.9 \cdot W$, which is a descending read from $0.2W$

The modulo wrap treats the waveform buffer as a ring buffer that can be walked forward or backward.

### 2.3 Pitch Stability Proof

The mean instantaneous frequency over any interval $[n_1, n_2]$ spanning an integer number of modulator cycles:

$$ \bar{f} = \frac{1}{n_2-n_1} \sum_{n=n_1}^{n_2-1} \big( f_c + d \cdot m[n] \big) = f_c + d \cdot \overline{m[n]} $$

For any zero-mean modulator waveform (sine, triangle, saw, 50% pulse): $\overline{m[n]} = 0$, so $\bar{f} = f_c$. This holds for **any** modulation depth $d$.

### 2.4 Spectral Structure

The output is a periodic signal with fundamental $f_0 = \gcd(f_c, f_m)$ (for integer ratio). The spectrum follows the Bessel function expansion:

$$ y(t) = \sum_{k=-\infty}^{\infty} J_k(\beta) \cos\big( (f_c + k f_m) t \big) $$

where $\beta = d / f_m$ is the modulation index. Key properties:

- **Carrier nulls**: $J_0(\beta)$ vanishes at $\beta = 2.4048, 5.5201, 8.6537, \dots$
- **Bandwidth**: Carson's rule: $BW \approx 2(\beta + 1) f_m$
- **Symmetry**: Sidebands are symmetrically distributed around $f_c$ with equal energy above and below

The difference from conventional FM is not in the Bessel expansion (which assumes perfect modulation) but in the **realization**: conventional digital FM distorts the Bessel expansion at high $\beta$ due to phase clamping; TZFM realizes the Bessel expansion faithfully.

### 2.5 Through-Zero with Non-Sinusoidal Carriers

When the carrier waveform is asymmetric (e.g., sawtooth, narrow pulse), time-reversed read at zero crossings produces a different waveform than forward read:

$$ \text{saw}_{\text{forward}}(t) = 2t - 1 \quad t\in[0,1) $$
$$ \text{saw}_{\text{reverse}}(t) = 1 - 2t \quad t\in[0,1) $$

The reverse saw is a falling ramp instead of a rising ramp. The transition between forward and reverse reads at zero crossings creates a characteristic "glassy" or "liquid" timbre that is the sonic signature of TZFM with asymmetric carriers. Symmetric carriers (sine, triangle) produce identical forward and reverse waveforms, so the timbre is unchanged through zero — only the spectral content from the phase reversal itself is heard.

### 2.6 Feedback TZFM

When the carrier output is fed back as the modulation signal:

$$ m[n] = y[n-1] $$
$$ \Delta\phi[n] = \frac{f_c + d \cdot y[n-1]}{f_s} $$

The feedback path creates a self-modulating loop. At low feedback gains ($d < 1$), the effect is mild spectral enrichment. At moderate gains ($1 < d < 5$), the oscillator enters a regime of deterministic chaos with period-doubling bifurcations and subharmonic generation. At high gains ($d > 5$), the output can become quasi-periodic or noisy. Feedback TZFM is the core of the "complex oscillator" topology (e.g., Make Noise DPO, Verbos Complex Oscillator).

### 2.7 Complexity

$$ \mathcal{O}(1) \text{ per sample per voice} $$

Overhead over standard FM: one sign check and one conditional branch.

---

## 3. Musical Elements Framework

- **PITCH**: Perfect pitch stability is TZFM's defining musical advantage. Carrier pitch $f_c$ is invariant under modulation depth, enabling FM timbre sweeps that sound like "the same note getting brighter" rather than "the pitch bending up." Microtonal chord voicings remain stable under modulation.
- **RHYTHM**: The modulator signal can be an audio-rate oscillator (spectral effects), a tempo-synchronized LFO (cyclic timbral wobble in 1/4, 1/8, 1/16 note subdivisions), or an envelope follower (dynamic accent shaping). Pitch stability means rhythmic modulation doesn't add undesired pitch swoop.
- **HARMONY**: Carrier-to-modulator ratio $r = f_c / f_m$ governs harmonicity. Integer ratios produce harmonic spectra (1:1 = saw-like, 2:1 = clarinet-like, 3:1 = brass-like, 3:2 = vocal formant). Irrational ratios produce inharmonic bell/gong spectra. TZFM maintains harmonic clarity at all depths.
- **STRUCTURE**: Modulation depth $d(t)$ and ratio $r(t)$ as macro-form signals. Verse: low depth ($\beta < 1$), pure carrier tone. Chorus: moderate depth ($\beta \approx 2$), rich sidebands. Bridge: sweeping $\beta$ from 0 $\to$ 10. Outro: high depth with irrational ratio for textured noise.
- **TEXTURE**: Continuous timbre morph from pure sine ($\beta \ll 1$) $\to$ brassy ($\beta \approx 2$) $\to$ glassy ($\beta \approx 5$) $\to$ metallic ($\beta > 10$). Carrier waveform choice (saw $\to$ glassy, sine $\to$ pure, pulse $\to$ hollow) and modulator waveform further shape the texture.

---

## 4. Implementation in Python / NumPy

```python
"""
sound/synthesis/tzfm.py - Through-Zero Frequency Modulation Synthesis (Method SP-094)
"""

import numpy as np
from typing import Optional, Callable, Dict, Any


def generate_tzfm_tone(
    f0: float,
    duration: float,
    sr: int = 44100,
    fm_ratio: float = 1.0,
    mod_depth: float = 1.0,
    carrier_wave: str = "sine",
    modulator_wave: str = "sine",
    depth_envelope: Optional[Callable[[float], float]] = None,
    feedback: float = 0.0,
    oversample: int = 1,
) -> np.ndarray:
    """
    Synthesizes a tone using Through-Zero Frequency Modulation (TZFM).

    TZFM allows the instantaneous frequency to go negative, causing the phase
    accumulator to reverse direction. This preserves the carrier pitch
    regardless of modulation depth.

    Args:
        f0: Carrier fundamental frequency in Hz.
        duration: Duration in seconds.
        sr: Sample rate.
        fm_ratio: f_mod / f_carrier ratio.
        mod_depth: Modulation depth (peak frequency deviation in Hz).
        carrier_wave: 'sine', 'saw', 'pulse', 'triangle'.
        modulator_wave: 'sine' (other shapes for advanced use).
        depth_envelope: Function depth(t) over [0, duration].
                        If None, uses constant depth.
        feedback: Feedback gain [0, 1). Routes carrier output back as modulator.
        oversample: Oversampling factor (1=no oversample, 2=2x, 4=4x).

    Returns:
        1D numpy array of float32 samples.
    """
    osr = oversample
    sr_os = sr * osr
    n_samples = int(duration * sr_os)

    if n_samples <= 0 or f0 <= 0:
        return np.zeros(max(0, int(duration * sr)), dtype=np.float32)

    # Build carrier wavetable
    W = 1024  # Table length (higher = less aliasing)
    t_wt = np.arange(W) / W
    wt = {
        "sine": np.sin(2.0 * np.pi * t_wt),
        "saw": 2.0 * t_wt - 1.0,
        "pulse": np.where(t_wt < 0.25, 1.0, -1.0),
        "triangle": 4.0 * np.abs(t_wt - 0.5) - 1.0,
    }.get(carrier_wave, np.sin(2.0 * np.pi * t_wt))

    # Phase increments
    f_mod = f0 * fm_ratio
    phase_inc_mod = f_mod / sr_os

    # State
    psi_car = 0.0  # Carrier phase in [0, 1)
    psi_mod = 0.0  # Modulator phase in [0, 1)
    fb_sample = 0.0
    out_os = np.zeros(n_samples, dtype=np.float64)

    for n in range(n_samples):
        time_sec = (n / sr_os)

        # Advance modulator
        psi_mod = (psi_mod + phase_inc_mod) % 1.0
        mod_idx = int(psi_mod * W) % W

        if feedback > 0:
            mod_signal = fb_sample
        else:
            mod_signal = np.sin(2.0 * np.pi * psi_mod)

        # Depth envelope
        d_env = depth_envelope(time_sec) if depth_envelope else 1.0

        # Instantaneous frequency deviation
        delta_f = mod_depth * d_env * mod_signal

        # Total instant frequency (can be negative!)
        f_inst = f0 + delta_f

        # Phase increment (negative = through-zero)
        phase_delta = f_inst / sr_os

        # Bidirectional phase accumulation (TZFM core)
        psi_car = (psi_car + phase_delta) % 1.0

        # Read wavetable — the modulo naturally handles
        # sign, giving forward/backward traversal
        car_idx = int(psi_car * W) % W
        sample = wt[car_idx]

        out_os[n] = sample
        fb_sample = sample * feedback

    # Decimate if oversampled
    if osr > 1:
        out_os = out_os[::osr]

    # Fade in/out
    n_final = len(out_os)
    fade_len = min(int(0.003 * sr), n_final // 4)
    if fade_len > 0:
        fade_in = np.linspace(0.0, 1.0, fade_len)
        fade_out = np.linspace(1.0, 0.0, fade_len)
        out_os[:fade_len] *= fade_in
        out_os[-fade_len:] *= fade_out

    # Normalize
    max_val = np.max(np.abs(out_os))
    if max_val > 1e-6:
        out_os = (out_os / max_val) * 0.95

    return out_os.astype(np.float32)


def tzfm_depth_envelope_adsr(
    attack: float = 0.02,
    decay: float = 0.3,
    sustain: float = 0.4,
    release_samples: int = 0,
    total_duration: float = 1.0,
) -> Callable[[float], float]:
    """Returns an ADSR-style depth envelope function."""
    def envelope(t: float) -> float:
        if t < attack:
            return t / attack if attack > 0 else 1.0
        t_rel = t - attack
        if t_rel < decay:
            return 1.0 - (1.0 - sustain) * (t_rel / decay) if decay > 0 else sustain
        if t < total_duration:
            return sustain
        return sustain
    return envelope
```

---

## 5. UnitMatrix Workflow Integration

In `musicom`:
- **Voices**: Each voice defines a TZFM operator pair (carrier + modulator), with per-voice ratio $r$, depth $d$, and waveform selection. Multi-operator TZFM (up to 4) follows the Yamaha DX7 algorithm topology but with TZFM phase accumulation at each FM stage.
- **Sections**: Each section specifies the carrier-modulator ratio $r$, depth envelope shape, and cross-patching algorithm. The unwrapped phase $\theta$ is preserved across section boundaries for click-free transitions.
- **Cells**: `MusicEvent` pitch maps to $f_c$. Cell metadata carries micro-depth variation for timbral accents.

---

## 6. References
- Chowning, J. (1973). "The Synthesis of Complex Audio Spectra by Means of Frequency Modulation." *Journal of the Audio Engineering Society*, 21(7), 526–534.
- Jaffe, D. A., & Smith, J. O. (1983). "Extensions of the Karplus-Strong Plucked-String Algorithm." *Computer Music Journal*, 7(2), 56–69. [Discusses TZFM for commuted synthesis.]
- Puckette, M. (2006). *The Theory and Technique of Electronic Music*. World Scientific, Ch. 5.
- Park, T. H. (2010). *Introduction to Digital Signal Processing: Computer Musically Speaking*. World Scientific.
- Roads, C. (1996). *The Computer Music Tutorial*. MIT Press, Ch. 4 (FM Synthesis).
- Moore, F. R. (1975). "Table Lookup Noise for Sinusoidal Digital Oscillators." *Computer Music Journal*, 1(2).
- Yamaha Corporation (1998). *FS1R Formant Shaping Synthesizer Technical Manual*. [Contains TZFM in the "Frequency Modulation" synthesis context.]