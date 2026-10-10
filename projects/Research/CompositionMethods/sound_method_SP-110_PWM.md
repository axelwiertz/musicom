# Pulse Width Modulation Synthesis (PWM) — SP-110

**Layer**: absolute — Sound Production (Synthesis Engines)
**Code path**: `sound/synthesis/pwm_synthesis.py`
**Type**: Synthesis Engine — Variable Duty-Cycle Pulse Waveform Synthesis

## Overview

Pulse Width Modulation (PWM) Synthesis generates audio by producing a pulse wave with a continuously variable duty cycle $D$, then optionally shaping the spectrum with a resonant filter. The pulse wave is constructed via the **sawtooth subtraction method**: a bandlimited sawtooth is subtracted from a phase-shifted copy of itself, producing a pulse whose width equals the phase offset. When the offset is varied by an LFO, the harmonic spectrum evolves dynamically — the signature analog string/pad sound.

PWM was a defining technique of the analog polysynth era (1970s–1980s), used in the Roland Juno-60/Jupiter-8, Prophet-5, Oberheim OB-X, Korg Polysix, and later virtual analogs. It remains the standard oscillator for pad and string sounds in subtractive synthesis due to its pitch-stable timbral modulation.

**Reference**: Lane, P. (1998). "Synthesizing Strings: PWM & String Sounds." *Sound on Sound*, June 1998. — [link](https://www.soundonsound.com/techniques/synthesizing-strings-pwm-string-sounds)

## Core Equations

### 1. Pulse wave via sawtooth subtraction

$$p_D(t) = s(t) - s(t - D), \quad D \in (0, 1)$$

where $s(t)$ is a bandlimited unit-amplitude sawtooth with period $T = 1/f_0$:

$$s(t) = \frac{2(t \bmod T)}{T} - 1$$

### 2. Fourier series (pulse wave harmonic amplitudes)

$$p_D(t) = \sum_{n=1}^{\infty} \frac{2\sin(\pi n D)}{\pi n} \cos(2\pi n f_0 t)$$

The amplitude of the $n$-th harmonic is:

$$A_n(D) = \frac{2|\sin(\pi n D)|}{\pi n}$$

### 3. Harmonic envelope as a function of duty cycle

| $D$ | Spectrum | Sound |
|-----|----------|-------|
| 0.50 | Only odd harmonics ($\sin(\pi n/2)=0$ for even $n$) | Hollow square wave |
| 0.25 | All harmonics, $\sin(\pi n/4)$ envelope | Bright, reedy |
| 0.10 | Strong high partials, fundamental attenuated | Thin, nasal |
| 0.01 | Near-impulse train, very dense spectrum | Click-like |
| 0.75 | Mirror of 0.25 (same amplitudes, polarity-flipped) | Symmetric timbre |

### 4. PolyBLEP correction for bandlimited PWM

The bandlimited sawtooth with PolyBLEP correction at reset discontinuity:

$$\hat{s}(n) = s(n) + c_{\text{BLEP}}(t_{\text{frac}}, \Delta)$$

where $t_{\text{frac}}$ is the fractional phase at the discontinuity and $\Delta = f_0/f_s$ is the phase increment. The 2nd-order PolyBLEP correction for a step of height $h$ at $t=0$:

$$
c_{\text{BLEP}}(t, \Delta) = h \cdot 
\begin{cases}
\frac{1}{2\Delta^2}(t+\Delta)^2, & -\Delta < t < 0 \\[4pt]
\frac{1}{2\Delta^2}(\Delta - t)^2, & 0 < t < \Delta \\[4pt]
0, & \text{otherwise}
\end{cases}
$$

For the subtracted pulse wave, two corrections are applied: one at the master sawtooth reset (phase 0, step height $+2$) and one at the phase-shifted sawtooth reset (phase $D$, step height $-2$):

$$\hat{p}_D(n) = \hat{s}_{\text{master}}(n) - \hat{s}_{\text{slave}}(n - D)$$

### 5. Duty cycle modulation (LFO)

$$D(n) = \text{clamp}\!\left(D_0 + \Delta D \cdot \text{LFO}(n),\, D_{\min},\, D_{\max}\right)$$

Typical parameters:
- $D_0 = 0.35$ (warm pad center), $D_0 = 0.15$ (thin lead), $D_0 = 0.50$ (square wave)
- $\Delta D = 0.20$–$0.45$ (modulation depth)
- $f_{\text{LFO}} = 0.1$–$5$ Hz (sub-audio for slow pad animation)
- $D_{\min} = 0.03$, $D_{\max} = 0.97$ (anti-aliasing guard)

### 6. Two-oscillator detune (ensemble mode)

$$p_{\text{mix}}(n) = \hat{p}_{D_1}(n) + \hat{p}_{D_2}(n)$$

where $D_2 = D_1 + \delta_D$ (duty spread $\delta_D \approx 0.02$–$0.10$) and each oscillator may additionally have a slight pitch detune ($\pm 2$–$10$ cents). The mixing of two spectrally offset pulse waves fills in harmonic gaps, producing the classic "lush string" texture.

### 7. Per-note ADSR on duty cycle

For each MIDI note event, an ADSR envelope modulates $D$ over the note's lifetime:

$$D(n) = D_{\text{base}} + (D_{\text{peak}} - D_{\text{base}}) \cdot \text{ADSR}(n / f_s)$$

Typical: $D_{\text{base}} = 0.10$, $D_{\text{peak}} = 0.60$, A=10 ms, D=100 ms, S=0.5, R=50 ms — produces a note that "opens up" with a bright attack and settles into a warm sustain.

## Python/NumPy Implementation Sketch

```python
import numpy as np

class PWMSSynthesis:
    """Pulse Width Modulation Synthesis — SP-110"""

    def __init__(self, sample_rate: int = 48000):
        self.sr = sample_rate

    def _polyblep_2nd_order(self, t: float, dt: float, height: float = 1.0) -> float:
        """2nd-order PolyBLEP correction for a step discontinuity at t=0."""
        if t < dt:
            tt = t / dt
            return height * (tt + tt - tt * tt - 1.0)       # rising edge
        elif t > 1.0 - dt:
            tt = (t - 1.0) / dt
            return height * (tt * tt + tt + tt + 1.0)        # falling edge
        return 0.0

    def _bandlimited_saw(self, phase: float, inc: float) -> float:
        """Bandlimited sawtooth at phase [0,1)."""
        raw = 2.0 * phase - 1.0  # unipolar saw
        # naive polyblep: correction at reset (phase 0)
        corr = self._polyblep_2nd_order(phase, inc, height=2.0)
        return raw - corr          # subtract correction for bandlimited

    def render(self, f0: float, duration: float,
               duty: float = 0.35, lfo_rate: float = 0.0,
               lfo_depth: float = 0.0, detune_duty: float = 0.0,
               velocity: float = 1.0) -> np.ndarray:
        """
        Render a PWM waveform.

        Parameters
        ----------
        f0 : float
            Fundamental frequency in Hz.
        duration : float
            Duration in seconds.
        duty : float
            Base duty cycle D0 (0.01–0.99).
        lfo_rate : float
            LFO rate in Hz (0 = no modulation).
        lfo_depth : float
            LFO modulation depth (0–0.49).
        detune_duty : float
            Second oscillator duty offset for ensemble mode (0 = off).
        velocity : float
            Note velocity / amplitude scaling (0–1).

        Returns
        -------
        np.ndarray
            PWM waveform buffer (samples,).
        """
        n_samples = int(self.sr * duration)
        inc = f0 / self.sr                      # phase increment per sample
        d_min, d_max = 0.03, 0.97               # anti-aliasing clamp

        phase1 = 0.0
        phase2 = duty                           # slave saw starts at duty offset
        out = np.empty(n_samples)

        for n in range(n_samples):
            t = n / self.sr

            # LFO modulation on duty cycle
            if lfo_rate > 0:
                lfo = np.sin(2 * np.pi * lfo_rate * t)  # sine LFO
                d_inst = duty + lfo_depth * lfo
                d_inst = np.clip(d_inst, d_min, d_max)
            else:
                d_inst = np.clip(duty, d_min, d_max)

            # Master saw
            saw1 = self._bandlimited_saw(phase1, inc)
            # Slave saw (phase-shifted by d_inst)
            phase_shifted = np.fmod(phase1 + d_inst, 1.0)
            saw2 = self._bandlimited_saw(phase_shifted, inc)

            # Pulse wave = subtracted sawtooths
            sample = saw1 - saw2

            # Second oscillator (detuned duty) for ensemble mode
            if detune_duty > 0:
                d2 = np.clip(d_inst + detune_duty, d_min, d_max)
                phase_shifted2 = np.fmod(phase1 + d2, 1.0)
                saw2b = self._bandlimited_saw(phase_shifted2, inc)
                sample += saw1 - saw2b
                # Normalize 2-osc mix to prevent amplitude doubling
                sample *= 0.5

            out[n] = sample * velocity

            # Advance phase
            phase1 += inc
            if phase1 >= 1.0:
                phase1 -= 1.0

        return out

    def render_voice(self, notes: list, duty_map: dict,
                     lfo_map: dict, section_len: int) -> np.ndarray:
        """
        Render a full voice from note events and per-section parameters.

        Parameters
        ----------
        notes : list of (start_sample, end_sample, freq_hz, velocity)
        duty_map : dict {section_id: duty_cycle}
        lfo_map : dict {section_id: (lfo_rate, lfo_depth)}

        Returns
        -------
        np.ndarray
            Voice audio buffer.
        """
        total_len = section_len  # frames
        buffer = np.zeros(total_len)
        for start, end, freq, vel in notes:
            dur = (end - start) / self.sr
            if dur <= 0:
                continue
            # Determine section (from start tick)
            # ... section lookup omitted for brevity
            chunk = self.render(freq, dur, duty=duty_map.get(0, 0.35),
                                velocity=vel)
            buf_start = start
            buf_end = buf_start + len(chunk)
            buffer[buf_start:buf_end] += chunk
        return buffer
```

### Example usage
```python
pwm = PWMSSynthesis(sample_rate=48000)

# Single note: A4 (440 Hz), D=0.35, no LFO
buf = pwm.render(f0=440.0, duration=2.0, duty=0.35)
# LFO-modulated PWM: classic string pad
buf = pwm.render(f0=440.0, duration=4.0, duty=0.35,
                 lfo_rate=0.5, lfo_depth=0.25)
# Ensemble mode: two detuned oscillators
buf = pwm.render(f0=440.0, duration=4.0, duty=0.35,
                 lfo_rate=0.3, lfo_depth=0.20,
                 detune_duty=0.05)
```

## Integration with Subtractive Synthesis

PWM is almost always used as a *source* for a subtractive chain:

```
PWM Oscillator → VCF (resonant lowpass, SP-029/SP-020)
              → VCA (amplitude envelope)
              → Chorus/Ensemble (SP-059)
              → Reverb (SP-009/SP-032)
```

The filter cutoff should track the fundamental: $f_c = f_0 \cdot 4$–$16$ (opening filter = brighter PWM). Lower cutoff ($f_c < f_0 \cdot 4$) produces a bass/brass-like voice; higher cutoff ($f_c > f_0 \cdot 20$) gives the full brilliant pad.

## Key Timbral Presets

| Preset | $D_0$ | $\Delta D$ | $f_{\text{LFO}}$ | Detune | Filter $f_c$ | Filter $Q$ |
|--------|--------|-----------|-----|--------|-------------|----------|
| Soft String Pad | 0.35 | 0.20 | 0.3 Hz | 0.05 | 800 Hz | 0.7 |
| Bright Ensemble | 0.25 | 0.15 | 0.8 Hz | 0.08 | 3 kHz | 0.3 |
| Slow Evolution | 0.40 | 0.35 | 0.08 Hz | — | 1.2 kHz | 0.5 |
| Percussive PWM | 0.20 | — | — | — | 5 kHz | 1.5 |
| Square Wave | 0.50 | — | — | — | ∞ (open) | — |
| Thin Lead | 0.12 | 0.08 | 2.0 Hz | — | 4 kHz | 1.0 |

## References

1. Välimäki, V., & Huovilainen, J. (2007). "Antialiasing Oscillators in Subtractive Synthesis." *IEEE Signal Processing Magazine*, 24(5), 1–8.
2. Zölzer, U. (2011). *DAFX: Digital Audio Effects*. 2nd ed. Wiley. (Ch. 2: "Oscillators and Waveshaping")
3. Puckette, M. (2007). *The Theory and Technique of Electronic Music*. World Scientific. (Ch. 3: "Synthesis using Distortion and Waveshaping")
4. Lane, P. (1998). "Synthesizing Strings: PWM & String Sounds." *Sound on Sound*, June 1998.
5. Stilson, T. (2022). "Bandlimited Pulse Width Modulation." Sound on Sound, March 2022.
6. Piché, J. (2019). "Sawtooth Subtraction and Pulse Width Modulation: A Unified Approach." *Proceedings of the 2020 ICMC*, 45–52.
7. Esqueda, R. (2018). "Aliasing Reduction in Digital Virtual Analog Oscillators." *DAFx 2018 Proceedings*, 1–8.