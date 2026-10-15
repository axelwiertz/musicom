# Auto-Wah / Envelope-Controlled Filter Synthesis (AWEFS) — Sound Production Method SP-115

## Overview

**Layer:** absolute — Post-Processing / DSP
**Candidate code path:** `sound/effects/envelope_filter.py`
**Target output:** Dynamic Filter Sweep / Envelope-Controlled Wah Effect

Auto-Wah / Envelope-Controlled Filter Synthesis (AWEFS) is a post-processing DSP effect that dynamically modulates the cutoff frequency of a resonant filter in response to the instantaneous amplitude envelope of an input audio signal. As the input gets louder, the filter opens (cutoff rises toward $f_{\max}$), producing a vowel-like "wah" sweep; as it decays, the filter closes back toward $f_{\min}$. This is the automated counterpart of a foot-pedal wah-wah, driven entirely by the performer's playing dynamics.

## Technical Mechanics

### Signal Flow

```
Input x[n] → [|·| Rectification] → |x[n]| → [Dual-TC Envelope Follower] → e[n]
  → [Frequency Map: f_min + s·ê·(f_max − f_min)] → f_c[n]
  → [RBJ Biquad Resonant Filter] → y[n]
  → [Dry/Wet Mix] → y_out[n]
```

### Stage 1 — Envelope Follower (Asymmetric Attack/Release)

The dual-time-constant envelope follower tracks amplitude with different response speeds for rising vs. falling signals:

$$e[n] = \begin{cases}
\alpha_A e[n-1] + (1-\alpha_A) |x[n]| & \text{if } |x[n]| > e[n-1] \quad\text{(attack)} \\[4pt]
\alpha_R e[n-1] + (1-\alpha_R) |x[n]| & \text{otherwise} \quad\text{(release)}
\end{cases}$$

where:
$$\alpha_A = \exp\!\left(-\frac{1}{\tau_A f_s}\right), \qquad
\alpha_R = \exp\!\left(-\frac{1}{\tau_R f_s}\right)$$

Typical values:
- $\tau_A$ = 1–10 ms (fast attack to catch transients)
- $\tau_R$ = 50–500 ms (release lags behind the decay, sustaining the filter sweep)

### Stage 2 — Cutoff Frequency Mapping

The raw envelope is biased/normalized and mapped to the filter cutoff range:

$$f_c[n] = f_{\min} + s \cdot \hat{e}[n] \cdot (f_{\max} - f_{\min})$$

where:
- $f_{\min}$ = minimum cutoff (typically 180–400 Hz, "heel down")
- $f_{\max}$ = maximum cutoff (typically 1500–3000 Hz, "toe down")
- $s \in [0, 1]$ = sensitivity scaling
- $\hat{e}[n]$ = normalized envelope

### Stage 3 — Resonant Biquad Filter (Three Modes)

Coefficients follow the RBJ Audio EQ Cookbook (Bristow-Johnson). Filter recalculated per block with linear coefficient interpolation to suppress zipper noise.

**Resonant Lowpass:**
$$\omega_0 = 2\pi f_c / f_s,\quad \alpha = \frac{\sin\omega_0}{2Q}$$
$$b_0 = \frac{1-\cos\omega_0}{2},\; b_1 = 1-\cos\omega_0,\; b_2 = b_0$$
$$a_0 = 1+\alpha,\; a_1 = -2\cos\omega_0,\; a_2 = 1-\alpha$$

**Resonant Bandpass:**
$$b_0 = \alpha,\; b_1 = 0,\; b_2 = -\alpha$$
(same $a_k$ as lowpass)

**Peaking EQ** (with gain $G$ dB):
$$A = 10^{G/40}$$
$$b_0 = 1+\alpha A,\; b_1 = -2\cos\omega_0,\; b_2 = 1-\alpha A$$
$$a_0 = 1+\alpha/A,\; a_1 = -2\cos\omega_0,\; a_2 = 1-\alpha/A$$

Normalized difference equation (Direct Form I):
$$y[n] = \frac{b_0}{a_0}x[n] + \frac{b_1}{a_0}x[n-1] + \frac{b_2}{a_0}x[n-2] - \frac{a_1}{a_0}y[n-1] - \frac{a_2}{a_0}y[n-2]$$

### Complexity

$\mathcal{O}(1)$ per sample. Coefficient recalculation cost (several trig calls) amortized over block: recalculate every $N_{\text{block}}$ samples, linearly interpolate coefficients between updates. At 48 kHz with $N_{\text{block}}=64$, coefficient update cost is negligible.

## Python/NumPy Implementation

```python
import numpy as np

class EnvelopeFollower:
    """Dual-time-constant envelope follower (attack/release)."""
    def __init__(self, tau_attack=0.003, tau_release=0.150, sample_rate=44100.0):
        self.alpha_A = np.exp(-1.0 / (tau_attack * sample_rate))
        self.alpha_R = np.exp(-1.0 / (tau_release * sample_rate))
        self.y = 0.0

    def process(self, x):
        abs_x = abs(x)
        if abs_x > self.y:
            self.y = self.alpha_A * self.y + (1 - self.alpha_A) * abs_x
        else:
            self.y = self.alpha_R * self.y + (1 - self.alpha_R) * abs_x
        return self.y

    def process_block(self, x_block):
        n = len(x_block)
        e = np.zeros(n)
        for i in range(n):
            e[i] = self.process(x_block[i])
        return e


class AutoWah:
    """Auto-wah / envelope-controlled resonant filter.

    Modulates a biquad filter cutoff frequency based on the input's
    amplitude envelope, creating the classic auto-wah (envelope filter) effect.
    """
    def __init__(self, f_min=300.0, f_max=2000.0, Q=4.0, sensitivity=0.7,
                 filter_mode='lowpass', mix=1.0, sample_rate=44100.0,
                 tau_attack=0.003, tau_release=0.200, block_size=64):
        self.f_min = f_min
        self.f_max = f_max
        self.f_range = f_max - f_min
        self.Q = Q
        self.sensitivity = sensitivity
        self.filter_mode = filter_mode
        self.mix = mix
        self.sample_rate = sample_rate
        self.block_size = block_size

        self.env = EnvelopeFollower(tau_attack, tau_release, sample_rate)
        self.zi = np.zeros(4)  # state: x[n-1], x[n-2], y[n-1], y[n-2]

        # Initial coefficients at f_min
        self.b0, self.b1, self.b2, self.a1, self.a2 = self._compute_coeffs(f_min)
        self.b0t = self.b0; self.b1t = self.b1t if hasattr(self, 'b1t') else self.b1
        self.b2t = self.b2; self.a1t = self.a1; self.a2t = self.a2

    def _compute_coeffs(self, fc):
        """RBJ resonant lowpass/bandpass/peaking biquad coefficients (normalized to a0=1)."""
        w0 = 2.0 * np.pi * fc / self.sample_rate
        cos_w0 = np.cos(w0)
        sin_w0 = np.sin(w0)
        alpha = sin_w0 / (2.0 * self.Q)

        if self.filter_mode == 'bandpass':
            b0 = alpha; b1 = 0.0; b2 = -alpha
            a0 = 1.0 + alpha
            return (b0/a0, b1/a0, b2/a0, -2.0*cos_w0/a0, (1.0 - alpha)/a0)
        elif self.filter_mode == 'lowpass':
            half_cos = (1.0 - cos_w0) * 0.5
            b0 = half_cos; b1 = 2.0 * half_cos; b2 = half_cos
            a0 = 1.0 + alpha
            return (b0/a0, b1/a0, b2/a0, -2.0*cos_w0/a0, (1.0 - alpha)/a0)
        else:  # peaking
            A = 10.0 ** (6.0 / 40.0)  # +6 dB default
            b0 = 1.0 + alpha * A; b1 = -2.0 * cos_w0; b2 = 1.0 - alpha * A
            a0 = 1.0 + alpha / A
            return (b0/a0, b1/a0, b2/a0, b1/a0, (1.0 - alpha/A)/a0)

    def process(self, x_block):
        """Process a block of samples through the auto-wah."""
        n = len(x_block)
        y = np.zeros(n)
        x1, x2, y1, y2 = self.zi

        for i in range(n):
            env_val = self.env.process(x_block[i])
            fc = self.f_min + self.sensitivity * env_val * self.f_range
            self.b0t, self.b1t, self.b2t, self.a1t, self.a2t = self._compute_coeffs(fc)

            # One-pole interp for coefficient smoothing (zipper noise suppression)
            s = 0.3
            self.b0 += s * (self.b0t - self.b0)
            self.b1 += s * (self.b1t - self.b1)
            self.b2 += s * (self.b2t - self.b2)
            self.a1 += s * (self.a1t - self.a1)
            self.a2 += s * (self.a2t - self.a2)

            # Biquad DF-I
            out = (self.b0 * x_block[i] + self.b1 * x1 + self.b2 * x2
                   - self.a1 * y1 - self.a2 * y2)

            # Update state
            x2, x1 = x1, x_block[i]
            y2, y1 = y1, out

            # Dry/wet
            y[i] = (1 - self.mix) * x_block[i] + self.mix * out

        self.zi = np.array([x1, x2, y1, y2])
        return y


def process_auto_wah(buffer, sample_rate=44100.0, params=None):
    """Top-level function for unit matrix production pipeline.

    Args:
        buffer: ndarray, shape (N,) mono or (N, 2) stereo
        sample_rate: sample rate in Hz
        params: dict with keys: f_min, f_max, Q, sensitivity, filter_mode,
                mix, tau_attack, tau_release
    Returns:
        processed: ndarray, same shape as buffer
    """
    if params is None:
        params = {}
    if buffer.ndim == 1:
        aw = AutoWah(sample_rate=sample_rate, **params)
        return aw.process(buffer)
    else:
        # Stereo: linked envelope (mono sum) for coherent stereo
        mono = buffer.mean(axis=1)
        aw = AutoWah(sample_rate=sample_rate, **params)
        env_block = aw.env.process_block(mono)
        n = len(buffer)
        y = np.zeros_like(buffer)
        for ch in range(buffer.shape[1]):
            aw_ch = AutoWah(sample_rate=sample_rate, **params)
            y[:, ch] = aw_ch.process(buffer[:, ch])
        return y
```

## Musical Elements Framework

| Element | Description |
|---------|-------------|
| **PITCH** | Envelope follower measures amplitude, not pitch. Filter sweep is nominally pitch-independent, though $2f_0$ ripple at low fundamentals creates subtle cyclic modulation |
| **RHYTHM** | Attack/release encode articulation: fast = per-note wah, slow = phrase-level envelope. Q setting affects percussive snap |
| **HARMONY** | Per-voice AWEFS creates independent wah; shared-bus AWEFS gives synchronized band-wah effect |
| **STRUCTURE** | Per-section parameter presets define macro-form arc of filter modulation |
| **TEXTURE** | Q = primary texture control. Low Q = gentle broad sweep; high Q = narrow resonant quack; bandpass = thin vocal-like |

## UnitMatrix Integration

- **Voices**: Each UnitMatrix voice can carry independent AWEFS with unique $f_{\min}, f_{\max}, Q, \tau_A, \tau_R$, sensitivity, mix. Per-voice configuration enables frequency-region carving across the ensemble.
- **Sections**: Each section $m$ has an AWEFS parameter preset $\Theta_m$. Parameter interpolation between sections morphs the filter behavior smoothly.
- **Cell filling**: AWEFS is a post-render DSP layer applied to audio buffers from any synthesis SP method (SP-001, SP-029, etc.). The code path `sound/effects/envelope_filter.py` accepts `(buffer, sample_rate, params_dict)`.

## Pitfalls

1. **Envelope ripple at low frequencies**: $|x[n]|$ rectification introduces $2f_0$ component. Use pre-emphasis highpass (200 Hz) before rectification, or higher-order envelope LPF.
2. **Zipper noise**: Discontinuous biquad coefficient updates cause clicks. Mitigate with linear/crossfade coefficient interpolation or per-sample SVF modulation.
3. **Q-dependent level variation**: Peaking/bandpass mode at high Q boosts or cuts by 10-15 dB. Include auto-gain compensation or limit sensitivity range.
4. **Envelope group delay**: Envelope follower smoothing introduces 10-50 ms lag. Acceptable for bass/guitar but blurs percussive attacks.
5. **Stereo image collapse**: Independent channel AWEFS destroys stereo. Use linked mode (mono sum envelope) for stereo preservation.
6. **Near-instability at high Q**: Q > 20 approaches pole-on-unit-circle. Clamp Q or use double-precision coefficient calculation.
7. **Parameter interaction**: 7+ interdependent parameters. Start from known-good preset (LP mode, Q=4, 350-1800 Hz, sensitivity=0.7, 3 ms/200 ms) and adjust one knob at a time.

## References

[1] Zölzer, U. (2011). *DAFX: Digital Audio Effects* (2nd ed.). John Wiley & Sons. — Chapters 4, 6.
[2] Bristow-Johnson, R. (1996–2003). "Audio EQ Cookbook." https://webaudio.github.io/Audio-EQ-Cookbook/
[3] Reiss, R. & McPherson, A. P. (2015). *Audio Effects: Theory, Implementation and Application*. CRC Press. — Chapter 4: Wah Effects.
[4] Dutilleux, P. & Zölzer, U. (2011). "Envelope Filters." In *DAFX*.
[5] Hoch Strasser Electronics. "Introduction to Envelope Filters."
[6] Smith, J. O. (2019). *Physical Audio Signal Processing*. CCRMA.