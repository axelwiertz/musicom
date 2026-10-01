# Digital Waveguide Synthesis (DWS) — Sound Method SP-101

**ID:** SP-101 · **Acronym:** DWS · **Layer:** absolute (sound production — synthesis engine)
**Target output:** Physical-Modeling String / Wind / Percussion Timbre
**Candidate code path:** `sound/synthesis/digital_waveguide.py`
**Produce dispatch:** `produce(midi_path, method="SP-101", params={"mode": "string", "loop_gain": 0.999, "stiffness_B": 0, "pickup_position": 0.85})`

## Overview

Digital Waveguide Synthesis (DWS) models one-dimensional acoustic wave propagation as the superposition of two traveling waves — right-going $y^+$ and left-going $y^-$ — in a pair of digital delay lines. This framework, formalized by Julius O. Smith III (CCRMA, 1985–2010), generalizes the Karplus-Strong algorithm to arbitrary terminations, spatially distributed excitations, nonlinear reed/bow interactions, and multi-waveguide networks with scattering junctions. DWS is the dominant physical-modeling synthesis paradigm, powering the Yamaha VL-series synthesizers and the STK (Synthesis ToolKit).

## Core Mathematics

### 1. Wave Equation and D'Alembert's Solution

The ideal vibrating string obeys the one-dimensional wave equation:

$$ \frac{\partial^2 y}{\partial t^2} = c^2 \frac{\partial^2 y}{\partial x^2} $$

where $c = \sqrt{T/\mu}$ (tension $T$, linear density $\mu$). D'Alembert's solution (1747) factors the wave into two arbitrary traveling functions:

$$ y(x,t) = y^+(t - x/c) + y^-(t + x/c) $$

where $y^+$ travels rightward and $y^-$ leftward at speed $c$. No energy is lost in an ideal medium — only boundaries and lumped filters introduce loss.

### 2. Sampled Digital Waveguide

Sampling at $x = mX$, $t = nT$ with $X = cT$ (spatial sampling interval = one sample's wave travel), the discrete waveguide at position $m$, time $n$ is:

$$ y(m,n) = y^+(n - m) + y^-(n + m) $$

The two traveling waves are stored in a **bidirectional delay line**: two arrays of length $K$ (the number of spatial samples, $K = \lfloor f_s / (2 f_0) \rfloor$). For a string at $f_0 = 110$ Hz, $f_s = 44100$ Hz: $K = \lfloor 44100 / 220 \rfloor = 200$.

### 3. Loop Structure

The two delay lines are looped back through termination reflections:

- **Fixed end** (clamped): $y^+[n] = -y^-[n-K]$ at $m=0$ (inverting reflection — zero displacement at boundary).
- **Free end** (open tube): $y^+[n] = y^-[n-K]$ (non-inverting — maximum displacement).
- **Lossy termination**: $y^+[n] = H_L(z) \cdot (-y^-[n-K])$, where $H_L(z)$ is the loop filter.
- **Fractional delay termination**: $y^+[n] = F(z) \cdot (-y^-[n-K])$, where $F(z)$ is the fractional-delay allpass.

The complete loop equation (fixed ends, lossy, fractional-delay):

$$ y^+[n] = H_L(z) \cdot F(z) \cdot (-H_L(z) \cdot F(z) \cdot y^+[n-2K]) $$$$ y^+[n] = -H_L^2(z) \cdot F^2(z) \cdot y^+[n-2K] $$

The loop length $2K$ (samples) sets the fundamental: $f_0 = f_s / (2K + 2\delta)$ with fractional delay $\delta$.

### 4. Loop Filter $H_L(z)$

The loop filter models frequency-dependent decay (higher frequencies attenuate faster in real strings):

$$ H_L(z) = \frac{g(1-a)}{1 - a z^{-1}} $$

Parameters:
- $g \in (0,1)$: loop gain. T60: $T_{60} \approx -3K / (f_s \cdot \log_{10} g)$ seconds.
- $a \in [0,1)$: lowpass coefficient. $a \to 1$ → rapid high-frequency decay (felt-muted). $a = 0$ → flat decay (bright).

Normalized so $|H_L(e^{j0})| = 1$ when $g = 1$.

### 5. Fractional-Delay Filter $F(z)$

For exact equal-temperament tuning, the delay length must be a fractional sample. A Thiran first-order allpass provides continuous delay with unit magnitude:

$$ F(z) = \frac{a_\delta + z^{-1}}{1 + a_\delta z^{-1}}, \quad a_\delta = \frac{1 - \delta}{1 + \delta}, \quad \delta \in [0, 1) $$

The effective loop length becomes $2K + 2\delta$ samples, giving continuous pitch control across integer bins.

### 6. Stiffness Dispersion (Allpass Chain)

For stiff strings (piano, marimba) the wave speed is frequency-dependent: higher partials travel faster, creating inharmonicity:

$$ f_n = n f_0 \sqrt{1 + B n^2} $$

where $B$ is the stiffness coefficient ($\approx 10^{-4}$ piano, $\approx 10^{-1}$ marimba).

Dispersion is modeled by replacing the single fractional-delay allpass with a chain of $R$ first-order allpasses:

$$ F_{\text{stiff}}(z) = \prod_{r=1}^{R} \frac{a_r + z^{-1}}{1 + a_r z^{-1}} $$

The $R$ coefficients $\{a_r\}$ are optimized via least-squares to match the desired group-delay dispersion $\tau_g(\omega) \approx \tau_0 + \alpha \omega^2$. Typical $R = 4$–$12$.

### 7. Scattering Junctions (Wind Instrument Bores)

At a junction between two cylindrical segments with characteristic impedances $Z_1, Z_2$ (where $Z = \rho c / A$, $A$ = cross-sectional area):

Reflection coefficient: $k = \frac{Z_2 - Z_1}{Z_2 + Z_1} = \frac{A_1 - A_2}{A_1 + A_2}$

Scattering equations (pressure waves):

$$ p^+_2 = (1+k) p^+_1 + (-k) p^-_2 $$$$ p^-_1 = k p^+_1 + (1-k) p^-_2 $$

This junction conserves both pressure and volume velocity, modeling the physical discontinuity losslessly. Cascading $N$ segments produces a complete bore model.

### 8. Excitation Models

| Excitation | Implementation |
|---|---|
| **Pluck** (string) | Initial displacement triangle loaded into delay lines: $y^+[0..K] = -(q/K) \cdot \text{tri}(k)$, $y^-[0..K] = (1 - q/K) \cdot \text{tri}(k)$ |
| **Bow** (violin) | Nonlinear friction: $f_{\text{friction}} = F_{\text{bow}} \cdot \tanh(\alpha (v_{\text{bow}} - v_{\text{string}}))$ |
| **Blow** (reed) | Bernoulli flow through reed aperture: $u = \xi \cdot |p_m - p|^+ \cdot \text{sgn}(p_m - p)$ |
| **Air-jet** (flute) | Jet-drive: $Q_{\text{ac}} = b \cdot v_{\text{jet}} \cdot \text{clip}(|\eta_s|/\eta_{\text{max}})$ |
| **Strike** (hammer) | Hertz contact: $F_h(t) = K_c \cdot y(t)^{1.5}$ |
| **Commuted** | Pre-convolved excitation = excitation * body_IR; waveform = waveguide + body in one loop |

## Python/NumPy Implementation Sketch

```python
import numpy as np
from scipy import signal

class DigitalWaveguide:
    """
    Digital Waveguide Synthesis — Monophonic String Model.

    Parameters
    ----------
    sample_rate : int
        Audio sample rate (Hz).
    freq : float
        Fundamental frequency (Hz).
    loop_gain : float
        Overall loop gain (0..1). T60 ≈ -3K / (sr * log10(g)).
    loop_a : float
        Lowpass coefficient (0..1). Higher = more HF damping.
    stiffness_B : float
        Inharmonicity coefficient (0 = ideal string, 1e-4 = piano, 0.1 = marimba).
    pick_pos : float
        Fractional pluck position (0..1). 0.1 = bright, 0.5 = mellow.
    pickup_pos : float
        Fractional readout position (0..1).
    num_allpass : int
        Number of stiffness dispersion allpass sections (0 = none).
    """

    def __init__(self, sample_rate=44100, freq=440.0, loop_gain=0.999,
                 loop_a=0.5, stiffness_B=0.0, pick_pos=0.2,
                 pickup_pos=0.85, num_allpass=4):
        self.sr = sample_rate
        # Delay length: K = floor(sr / (2 * freq))
        K = int(sample_rate / (2.0 * freq))
        frac_delay = sample_rate / (2.0 * freq) - K
        self.K = K
        # Upper and lower delay lines
        self.upper = np.zeros(K)
        self.lower = np.zeros(K)
        self.wr_idx = 0  # write index
        # Loop filter (one-pole lowpass)
        a = loop_a
        self.loop_b = [loop_gain * (1 - a)]
        self.loop_a_coeff = [1, -a]
        self.loop_state = 0.0
        # Fractional-delay allpass
        self.delta = frac_delay
        self.a_delta = (1 - frac_delay) / (1 + frac_delay) if frac_delay < 1 else 0
        self.ap_state = 0.0
        # Stiffness allpass chain
        self.stiff_coeffs = []
        self.stiff_states = np.zeros(num_allpass)
        if stiffness_B > 0 and num_allpass > 0:
            self._design_stiffness_allpasses(stiffness_B, num_allpass, K)
        # Pickup position (spatial sample index)
        self.pickup_idx = int(pickup_pos * K) % K
        self.pickup_frac = (pickup_pos * K) - self.pickup_idx
        # Pluck position
        self.pick_pos = pick_pos
        self.plucked = False

    def _design_stiffness_allpasses(self, B, R, K):
        """Design R allpass sections to approximate stiffness dispersion."""
        # Simplified: distribute allpass coefficients linearly
        # Real impl uses least-squares fit to group delay τ(ω) = τ0 + αω²
        for r in range(R):
            a_r = 0.2 + 0.6 * r / R  # increasing allpass effect
            self.stiff_coeffs.append(a_r)

    def pluck(self):
        """Initialize delay lines with a pluck shape (triangle)."""
        K = self.K
        q = self.pick_pos
        # Create triangle shape: ramps up to peak at position q*K
        peak = int(q * K)
        tri = np.zeros(K)
        tri[:peak] = np.linspace(0, 1, peak, endpoint=False)
        tri[peak:] = np.linspace(1, 0, K - peak, endpoint=False)
        # Split into right-going and left-going components
        self.upper[:] = -q * tri          # right-going
        self.lower[:] = (1 - q) * tri     # left-going
        self.plucked = True

    def _allpass(self, x, a, state):
        """First-order allpass filter: y = a*x + state; state = x - a*y."""
        y = a * x + state
        new_state = x - a * y
        return y, new_state

    def _loop_filter(self, x):
        """One-pole lowpass loop filter."""
        y = self.loop_b[0] * x - self.loop_a_coeff[1] * self.loop_state
        self.loop_state = y
        return y

    def render(self, num_samples):
        """Render num_samples of audio."""
        out = np.zeros(num_samples)
        for n in range(num_samples):
            # Top delay output: upper[wr_idx]
            out_upper = self.upper[self.wr_idx]
            # Bottom delay output: lower[wr_idx]
            out_lower = self.lower[self.wr_idx]

            # Read output at pickup position
            pickup_idx = self.pickup_idx
            p_frac = self.pickup_frac
            y_p = self.upper[(self.wr_idx + pickup_idx) % self.K] * (1 - p_frac) + \
                  self.upper[(self.wr_idx + pickup_idx + 1) % self.K] * p_frac + \
                  self.lower[(self.wr_idx - pickup_idx) % self.K] * (1 - p_frac) + \
                  self.lower[(self.wr_idx - pickup_idx - 1) % self.K] * p_frac

            # Termination at right end (upper → lower after reflection)
            # Loop filter + fractional delay + inversion
            x_left = out_upper
            for a in self.stiff_coeffs:
                x_left, self.stiff_states[0] = self._allpass(x_left, a, self.stiff_states[0])
            x_left, self.ap_state = self._allpass(x_left, self.a_delta, self.ap_state)
            x_left = self._loop_filter(x_left)
            self.lower[self.wr_idx] = -x_left  # write left-going

            # Termination at left end (lower → upper after reflection)
            x_right = out_lower
            for a in self.stiff_coeffs:
                x_right, self.stiff_states[0] = self._allpass(x_right, a, self.stiff_states[0])
            x_right, self.ap_state = self._allpass(x_right, self.a_delta, self.ap_state)
            x_right = self._loop_filter(x_right)
            self.upper[self.wr_idx] = -x_right  # write right-going

            # Advance write index
            self.wr_idx = (self.wr_idx + 1) % self.K

            out[n] = y_p

        return out
```

## Musical Elements Framework

| Element | DWS Mapping |
|---|---|
| **PITCH** | Delay length $K$ + fractional delay $\delta$ set $f_0 = f_s / (2K + 2\delta)$. Stiffness $B$ controls overtone inharmonicity. Pitch bend via continuous $\delta$ (portamento). |
| **RHYTHM** | Excitation events (pluck/strike/blow) triggered by note-ons. Decay time $T_{60} \propto 1 / \log g$. Position $q$ controls harmonic content vs rhythm envelope. |
| **HARMONY** | Monophonic per waveguide. Harmony = multiple waveguide instances per chord. Overtone structure $f_n = n f_0 \sqrt{1+B n^2}$ carries harmonic content. |
| **STRUCTURE** | Section-specific DWS parameters (loop gain, stiffness, pickup position). Waveguide state persists across boundaries for natural legato. |
| **TEXTURE** | Controlled by loop gain $g$, stiffness $B$, bow noise, parallel detuned waveguides (unison chorus). |

## UnitMatrix Integration

**Voices**: Each UnitMatrix voice maps to one waveguide instance (monophonic) or a pool (polyphonic). Voice parameters are per-voice. Percussion voice uses impulse-excited short-delay waveguide (KS drum).

**Sections**: Each section carries its own DWS parameter set. Section transitions crossfade old and new waveguide parameters.

**Workflow**:
1. `UnitMatrixComposer` generates MIDI events.
2. `produce(method="SP-101")` creates DWS instances per note-event, renders directly to audio.
3. DWS output is mixed into the master stereo buffer.

## References

- Smith, J. O. (2010). *Physical Audio Signal Processing*. W3K Publishing. https://ccrma.stanford.edu/~jos/pasp/
- Smith, J. O. (2006). "Digital Waveguide Synthesis." *The Computer Music and Audio DSP Handbook*.
- Jaffe, D. A. & Smith, J. O. (1983). "Extensions of the Karplus-Strong Plucked-String Algorithm." *CMJ* 2, 53–80.
- Karplus, K. & Strong, A. (1983). "Digital Synthesis of Plucked-String and Drum Timbres." *CMJ* 2, 39–52.
- Bilbao, S. (2009). *Numerical Sound Synthesis*. Wiley.
- Välimäki, V. & Takala, T. (1996). "Virtual Electric Guitar." *ICMC 1996*.