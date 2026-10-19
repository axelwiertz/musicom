# SP-119 — Auto-Pan / Dynamic Stereo Modulation Synthesis (APMS)

- **Method ID:** SP-119
- **Acronym:** APMS (Auto-Pan / Modulation Synthesis)
- **Layer:** absolute (sound production)
- **Category:** Post-Processing / DSP (spatialization / stereo field modulation)
- **Candidate code path:** `sound/effects/autopan.py`

## One-line description

Continuously varies the stereo pan position of a mono (or stereo) signal via LFO-driven constant-power panning law (sine/cosine amplitude distribution), with multiple waveforms (sine, triangle, square, sawtooth, random S&H), stereo phase offset for rotary/wide effects, and tempo-synced rate.

## The sound / effect character

Auto-pan creates the perception of a sound source moving left-right across the stereo image. It is the four-quadrant spatial counterpart of tremolo (SP-102): where tremolo modulates volume equally in both channels, auto-pan modulates volume in opposite proportion (one channel rises as the other falls). The LFO waveform determines the motion character: sine = natural pendulum (softer, musical), triangle = constant-velocity sweep (uniform coverage), square = hard L/R ping-pong jump (aggressive), sawtooth = slow sweep with fast snap-back, random S&H = stepped unpredictable hopping.

## The math (extended)

### 1. Constant-Power Panning Law

The core requirement for natural-sounding panning is constant perceived loudness regardless of pan position. The sine/cosine law achieves this:

$$\theta[n] = \frac{\pi}{4}(1 + D \cdot p[n])$$

where $p[n] \in [-1, 1]$ is the LFO output at sample $n$ and $D \in [0, 1]$ is the depth. The panning gains:

$$g_L[n] = \cos(\theta[n]), \qquad g_R[n] = \sin(\theta[n])$$

Since $\cos^2\theta + \sin^2\theta = 1$, the power $g_L^2 + g_R^2 = 1$ is constant. At center ($p=0$): $\theta=\pi/4$, both channels at $-3$ dB. At hard right ($p=1$): $\theta=\pi/2$, $g_L=0$, $g_R=1$. At hard left ($p=-1$): $\theta=0$, $g_L=1$, $g_R=0$.

Alternative laws:
- **Square-root law**: $g_L = \sqrt{(1-p)/2}, \quad g_R = \sqrt{(1+p)/2}$ — numerically cheaper, slightly different center perception
- **Tangent law** (Bauer 1969): $g_L = 1, \quad g_R = \tan(\theta)$ with constant-power normalization — psychoacoustically optimal for $60^\circ$ stereo base angle
- **Linear (constant-gain)**: $g_L = 0.5(1-p), \quad g_R = 0.5(1+p)$ — produces $-3$ dB center dip, deprecated

### 2. LFO Waveforms

The LFO $w(\phi)$ generates the pan trajectory over normalised phase $\phi[n] = 2\pi f_m n/f_s + \phi_0$:

| Waveform | Equation $w(\phi)$ | Fourier series | Character |
|---|---|---|---|
| Sine | $\sin(\phi)$ | Single term | Smooth, natural, musical |
| Triangle | $\frac{8}{\pi^2}\sum_{k=0}^{\infty}(-1)^k\frac{\sin((2k+1)\phi)}{(2k+1)^2}$ | Odd harmonics only, $1/n^2$ rolloff | Uniform velocity sweep |
| Square | $\frac{4}{\pi}\sum_{k=0}^{\infty}\frac{\sin((2k+1)\phi)}{2k+1}$ | Odd harmonics, $1/n$ rolloff | Hard L/R jumps |
| Sawtooth (down) | $-\frac{2}{\pi}\sum_{k=1}^{\infty}\frac{\sin(k\phi)}{k}$ | All harmonics, $1/n$ rolloff | Slow→snap sweep |
| Random S&H | $p_{\text{SH}}[n] = r_{\lfloor n f_m/f_s\rfloor}$ | White spectrum | Unpredictable hopping |

The triangle wave is unique: it provides equal time at every pan position — unlike sine which dwells at the extremes (slower zero-crossing). This makes triangle preferable for rhythmic auto-pan where even spatial coverage is desired.

### 3. Stereo Phase Offset

For stereo processing, the left and right LFOs can have a phase offset $\Delta\phi$:

$$p_L[n] = D \cdot w(\phi[n]), \qquad p_R[n] = D \cdot w(\phi[n] + \Delta\phi)$$

Alternatively, for M/S mode:
$$M[n] = (x_L + x_R)/2, \qquad S[n] = (x_L - x_R)/2$$
$$S'[n] = S[n] \cdot (1 - D \cdot |w(\phi[n])|)$$
$$y_L = M + S', \quad y_R = M - S'$$

### 4. Tempo Sync

The modulation rate in Hz is derived from BPM $T$ and note division $d$:

$$f_m = \frac{T}{60 \cdot d}$$

For dotted: $f_m = 1.5T/(60d)$. For triplet: $f_m = T/(60) \cdot 3/d$ (three events per beat).

### 5. Equivalent circuit: 4-quadrant amplitude modulator

Conceptually, auto-pan is equivalent to:
- Two amplitude modulators (one per channel) driven by out-of-phase LFOs
- A constant-power law replaces the simple modulator $m(t) = [1 + m \cos(\omega_m t)]/2$ with trigonometric gains
- The stereo field position $s[n] \in [-1, 1]$ is the control parameter; the pan law maps $s \to (g_L, g_R)$

This $O(1)$ structure per sample makes auto-pan the cheapest spatialization effect, comparable to SP-102 AMS.

## Python / NumPy implementation sketch

```python
import numpy as np

class AutoPanProcessor:
    """LFO-driven auto-pan with multiple waveforms and pan laws."""
    
    WAVEFORM = {'sine', 'triangle', 'square', 'sawdown', 'sawup', 'random_sh'}
    PANLAW   = {'sine', 'sqrt', 'linear'}
    
    def __init__(self, rate=0.3, depth=1.0, phase=0.0,
                 waveform='sine', pan_law='sine'):
        self.rate = rate
        self.depth = depth
        self.phase = np.radians(phase)
        self.waveform = waveform
        self.pan_law = pan_law
        
    def _lfo(self, phases):
        """Compute LFO waveform value from phase array."""
        if self.waveform == 'sine':
            return np.sin(phases)
        elif self.waveform == 'triangle':
            return 2*np.abs(2*((phases+np.pi)/(2*np.pi) % 1) - 1) - 1
        elif self.waveform == 'square':
            return np.where(np.sin(phases) >= 0, 1.0, -1.0)
        elif self.waveform == 'sawdown':
            return 1 - 2*((phases+np.pi)/(2*np.pi) % 1)
        elif self.waveform == 'sawup':
            return 2*((phases+np.pi)/(2*np.pi) % 1) - 1
        elif self.waveform == 'random_sh':
            idx = np.floor(phases / (2*np.pi)).astype(int)
            rng = np.random.RandomState(seed=42)
            vals = 2 * rng.rand(int(idx.max())+1) - 1
            return vals[idx]
    
    def _gains(self, p):
        """Panning gains for position p in [-1,1]."""
        if self.pan_law == 'sine':
            theta = np.pi/4 * (1 + p)
            return np.cos(theta), np.sin(theta)
        elif self.pan_law == 'sqrt':
            return np.sqrt(0.5*(1-p)), np.sqrt(0.5*(1+p))
        else:  # linear
            return 0.5*(1-p), 0.5*(1+p)
    
    def process(self, x, sr=48000):
        """Mono -> stereo auto-pan."""
        t = np.arange(len(x)) / sr
        phases = 2*np.pi*self.rate*t + self.phase
        p = self._lfo(phases) * self.depth
        gL, gR = self._gains(p)
        return np.stack([gL * x, gR * x])
    
    def process_stereo_ms(self, left, right, sr=48000):
        """Stereo auto-pan via mid-side modulation."""
        n = len(left)
        t = np.arange(n) / sr
        phases = 2*np.pi*self.rate*t + self.phase
        p = self._lfo(phases) * self.depth
        
        M = (left + right) / 2
        S = (left - right) / 2
        S_mod = S * (1 - np.abs(p))
        
        out_L = M + S_mod
        out_R = M - S_mod
        return np.stack([out_L, out_R])
```

## References

[1] Tarr, E. (2018-2022). "Auto Pan." *Hack Audio*. https://hackaudio.com/digital-signal-processing/stereo-audio/auto-pan/

[2] Zölzer, U. (2011). *DAFX: Digital Audio Effects* (2nd ed.). John Wiley & Sons. — Chapter 7: Modulation Effects.

[3] Behrens, S. (2024). "Audio Signal Processing in Python: Panning and Stereo Width." https://www.sbehrens4d.com/posts/python_dsp_1_panning.html

[4] CMU Music Informatics. "Pan Laws." https://www.cs.cmu.edu/~music/icm-online/readings/panlaws/

[5] Bauer, B. B. (1969). "Phantom Sound Source Localization." *Journal of the Audio Engineering Society*.

[6] OxiMedia. (2026). "auto_pan — Automatic panning effect." Rust DSP lib. https://docs.rs/oximedia-effects/latest/oximedia_effects/auto_pan/