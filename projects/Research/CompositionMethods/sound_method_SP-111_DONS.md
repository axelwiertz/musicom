# Duffing Oscillator Nonlinear Synthesis (DONS) — SP-111

## Layer
**absolute** — Sound Production (Synthesis Engines)
Code path: `sound/synthesis/duffing_synth.py`

## Overview
DONS is a nonlinear oscillator synthesis method that integrates the forced, damped Duffing equation at audio rate and emits the displacement $x(t)$ directly as the output sample. Unlike linear oscillators (SP-029, SP-041, SP-110), the cubic spring term $-\beta x^3$ couples amplitude to frequency, producing:

- Amplitude-dependent detuning (hardening/softening spring)
- Odd-harmonic spectral enrichment ($3\omega, 5\omega, \ldots$)
- Jump resonance / hysteresis (the classic "frequency sweep stays on one branch then snaps")
- Period-doubling route to chaos / strange attractor (Ueda attractor)

The method is the forced-chaotic bridge between SP-057 Chua (autonomous, pitch-free) and the linear oscillator family. It is also the physical counterpoint to SP-043 SATM (which maps chaotic *trajectories* to MIDI) — DONS generates *audio directly* from a chaotic ODE, not composition events.

## The Duffing Equation

$$\ddot{x} + \delta \dot{x} + \alpha x + \beta x^3 = \gamma \cos(\omega t)$$

| Parameter | Symbol | Role | Typical Range | Musical Effect |
|---|---|---|---|---|
| Damping | $\delta$ | Energy dissipation | 0.001–5.0 | Decay time, percussiveness |
| Linear stiffness | $\alpha$ | Natural frequency squared | 0.01–100 | Base resonance $\omega_0 = \sqrt{\alpha}$ |
| Cubic nonlinearity | $\beta$ | Spring hardening/softening | 0.01–100 | Harmonic richness, chaos threshold |
| Drive amplitude | $\gamma$ | Forcing strength | 0.001–5.0 | One-knob chaos control |
| Drive frequency | $\omega$ | Note pitch (2π f_note) | audio range | Pitch |

**Double-well regime** ($\alpha < 0$, $\beta > 0$): potential $V(x) = \frac{\alpha}{2} x^2 + \frac{\beta}{4} x^4$ has two minima at $x = \pm\sqrt{-\alpha/\beta}$. The trajectory can snap between wells, producing chaotic noise bursts with sub-audio thumps.

**Hardening spring regime** ($\alpha > 0$, $\beta > 0$): effective resonance frequency increases with amplitude: $\omega_{\text{eff}}(A) \approx \sqrt{\alpha + \frac{3}{4}\beta A^2}$, from first-order harmonic balance (Nayfeh & Mook 1979).

## Discrete-Time Integration (Semi-Implicit Euler)

State: $[x_n, v_n]$ = [displacement, velocity], step $h = 1/f_s$:

1. Compute drive: $d_n = \gamma \cos(\omega t_n)$
2. Update velocity: $v_{n+1} = v_n + h\left(-\delta v_n - \alpha x_n - \beta x_n^3 + d_n\right)$
3. Update displacement: $x_{n+1} = x_n + h\,v_{n+1}$
4. Output: $y_n = x_n$ (scaled by amplitude envelope, tanh-limited)

Stability: $h\sqrt{\alpha} < 2$ (always true for audio-rate $\alpha$ at 44.1 kHz+). For $\beta > 0$ the effective stiffness grows, tightening stability — safe.

## Musicom Pipeline Implementation

### Per-note rendering

```python
import numpy as np

def render_duffing_note(f0, duration, sr=48000, alpha=1.0, beta=1.0,
                        delta=0.05, gamma=0.6, vel=1.0, seed=0,
                        oversample=2):
    """Render one note-length Duffing oscillator block."""
    sr2 = sr * oversample
    n = int(duration * sr2)
    h = 1.0 / sr2
    omega = 2.0 * np.pi * f0 / sr2  # normalised ang. freq.

    # state (continuous across the note)
    rng = np.random.default_rng(seed)
    x = rng.uniform(-0.01, 0.01)  # tiny random initial displacement
    v = rng.uniform(-0.1, 0.1)

    out = np.zeros(n)
    t = 0.0
    for i in range(n):
        drive = gamma * vel * np.cos(omega * t)
        # semi-implicit Euler
        v += h * (-delta * v - alpha * x - beta * x**3 + drive)
        x += h * v
        out[i] = x
        t += h

    # decimate (simple averaging)
    y = np.mean(out.reshape(-1, oversample), axis=1)

    # soft clip and DC block
    y = np.tanh(y * 1.5)
    y -= np.mean(y[:max(1, int(0.02*sr))])
    return y.astype(np.float32)
```

For multi-voice polyphony, each UnitMatrix voice calls its own render block. The parametric envelope (mid-note velocity change) samples $\gamma$ from the section's $\gamma(t)$ trajectory.

### Parameter atlases (presets)

```python
PRESETS = {
    "sine":    dict(alpha=4.0, beta=0.01, delta=0.5, gamma=0.01),  # near-linear
    "brass":   dict(alpha=1.0, beta=0.5,  delta=0.1, gamma=0.3),   # odd-harmonic rich
    "bass":    dict(alpha=0.5, beta=2.0,  delta=0.2, gamma=0.8),   # subharmonic growl
    "gong":    dict(alpha=2.0, beta=10.0, delta=0.02, gamma=2.0),  # metallic chaos
    "double_well": dict(alpha=-1.0, beta=1.0, delta=0.1, gamma=0.5), # two-well snap
}
```

These atlases map directly to section-level parameter clusters $\theta_s$ in the UnitMatrix.

## Musical Elements Framework

### PITCH
Driving frequency $\omega = 2\pi f_0/f_s$ IS the pitch. Pitch stability in the linear regime is excellent; in the chaotic regime the perceived fundamental blurs into a noisy band. The hardening spring bends pitch upward on loud notes — a natural "overdrive" expression. In the double-well regime, snapping between wells produces sub-audio thumps (tension/release per note).

### RHYTHM
DONS is continuous — rhythm comes from **gating** the drive envelope (seeding and re-seeding). Percussive use: strike the oscillator with a short pulse (non-resonant) and let the natural resonance ring with decay time $2/\delta$. Jump-resonance hysteresis creates natural asymmetry: attack and release shapes depend on sweep direction through the resonance curve.

### HARMONY
Per-voice DONS oscillators at different $f_0$ with independent chaos knobs mix on the bus. The odd-harmonic spectral structure ($3f_0, 5f_0, \ldots$) supports octave/doublestop stacking. In the mode-locked regime, the oscillator shows Arnold-tongue-like synchronization to the drive: frequency ratios $p:q$ produce sub-harmonic organum.

### STRUCTURE
The parameter schedule $\theta_s$ per section is the form map. A section can sweep $\gamma$ from 0.01 → 3.0, transitioning through pure sine → harmonic → chaotic → noise in one arc — a built-in tension trajectory. Double-well on/off acts like an A/B section switch.

### TEXTURE
Texture = distance from the chaos threshold $(\gamma/\gamma_c)$. Low: thin/pure. Mid: warm/vocal/brass-like. High: dense/live/breathed. Per-voice independent $\gamma$ gives stratified density; shared $\gamma$ gives compound texture.

## UnitMatrix Integration

- **Voices**: Independent DONS integrators, each with its own parameter preset and seed.
- **Sections**: Parameter cluster $\theta_s$ defining the chaotic regime + drive envelope trajectory.
- **Cells**: `MusicUnit` decoded via `velocity * gamma = drive amplitude`; `articulation` sets release $\delta$ multiplier.
- **Zero-drift invariant**: state $(x, v)$ of each DONS voice carries across section boundaries — continuous integration handles the seam naturally. No cell padding needed because the integrator runs continuously across the whole voice timeline.

## Pitfalls

1. **Numerical blow-up**: double-well + large $\gamma$ can eject to $\pm\infty$. Clamp $x$ to $\pm 4$. Use symplectic Euler; RK4 is more stable but costs 4× RHS evaluations.
2. **Aliasing**: chaotic spectra reach Nyquist. 2× oversampling + 10 kHz LPF post-filter is enough.
3. **Chaos threshold non-portability**: $\gamma_c$ depends on all parameters. Pre-scan the (α,β,δ,γ,ω) atlas offline; store regime labels per cell.
4. **Pitch ambiguity**: above the chaos threshold the perceived "note" broadens to a noisy band. Use the mode-locked regime ($\gamma < \gamma_c$) for clean pitch.
5. **DC offset in double-well**: mean of $x(t)$ ≠ 0. Apply DC blocker (subtract running mean with τ ≈ 50 ms).
6. **Click on drive envelope steps**: always smooth $\gamma$ with a one-pole (τ = 2 ms).
7. **Linear pitch is cheaper**: DONS is 2–5× more expensive per sample than a PolyBLEP oscillator (SP-110). Use it only for voices that need organic variance.

## References

[1] Duffing, G. (1918). *Erzwungene Schwingungen bei veränderlicher Eigenfrequenz*. Vieweg.
[2] Nayfeh, A. H. & Mook, D. T. (1979). *Nonlinear Oscillations*. Wiley. — Harmonic balance, backbone curve, jump resonance.
[3] Ueda, Y. (1991). *The Road to Chaos*. Aerial Press. — Canonical Duffing strange attractor.
[4] Essl, G. (2019). "Exploring the Sound of Chaotic Oscillators via Parameter Spaces." DAFx 2019.
[5] Spanedda, L. (2025). "Emergent Behaviors in Sound Synthesis." *ECHO* 7.
[6] Holopainen, R. "Nonlinear Oscillators and Frequency Modulation." ristoid.net.
[7] Thompson, J. M. T. & Stewart, H. B. (2002). *Nonlinear Dynamics and Chaos*, 2nd ed. Wiley.