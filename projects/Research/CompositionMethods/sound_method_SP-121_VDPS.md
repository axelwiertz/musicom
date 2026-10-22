# SP-121 — Van der Pol Oscillator Synthesis (VDPS)

**ID:** SP-121
**Layer:** absolute — sound production (Synthesis Engines)
**Candidate code path:** `sound/synthesis/van_der_pol_synthesis.py`
**Produce dispatch:** `workflows.musicom_workflow.produce(method="SP-121")`
**One-line:** Self-oscillating nonlinear oscillator synthesis — integrate $\ddot{x}-\mu(1-x^2)\dot{x}+\omega_0^2 x=0$ at audio rate: nonlinear damping self-sustains a limit cycle (amplitude ≈ 2) that morphs from sinusoid (μ→0) to saw-like relaxation oscillation (large μ) to chaotic hiss when forced; two coupled detuned oscillators reproduce phonation/syrinx glottal-pulse textures.

---

## 1. Overview

Van der Pol Oscillator Synthesis (VDPS) is the canonical **self-sustained (autonomous) nonlinear oscillator** for audio. Unlike forced oscillators (Duffing SP-111) that decay to rest without a drive, the VdP oscillator *pumps its own energy*: the damping coefficient $-\mu(1-x^2)$ is *negative* (anti-damping) while $|x|<1$ and *positive* (saturation) while $|x|>1$. Energy is therefore injected at small amplitude and absorbed at large amplitude, locking the state onto a stable **limit cycle** — a fixed periodic waveform whose amplitude and shape are set by $\mu$ alone, independent of initial conditions. Emitting the displacement $x(t)$ as the audio sample gives:

- $\mu \to 0$: pure sinusoid at $f_0 = \omega_0/2\pi$ (Hopf bifurcation at $\mu=0$);
- moderate $\mu$: rounded saw-like waveform, harmonic rolloff $\sim 1/k$ — analog-lead/bass territory;
- large $\mu$: **relaxation oscillation** — slow build-up, fast discharge (the triode/neon-lamp mechanism), period $T \approx (3-2\ln 2)\mu/\omega_0^2$;
- forced ($+A\sin\omega_d t$): entrainment (injection locking), **subharmonic frequency demultiplication** $f_0/n$ (van der Pol & van der Mark 1927 — the first observed deterministic chaos in a physical system), and fully chaotic hiss/rasp;
- two coupled detuned oscillators: avian-syrinx / vocal-fold phonation model (Mindlin group) — glottal-pulse-like trains with beating and jitter.

The method fills a real gap in the catalogue: no self-oscillating relaxation-oscillator synthesis existed (SP-111 Duffing = forced conservative stiffness; SP-057 Chua = 3D piecewise chaos; SP-070 FBAM = discrete feedback AM; SP-065/066 = waveguide loop models).

---

## 2. History & Sources

- **van der Pol, B. (1920).** "A theory of the amplitude of free and forced triode vibrations." *Radio Review* 1, 701–710.
- **van der Pol, B. (1926).** "On 'relaxation-oscillations'." *Phil. Mag.* 2(11), 978–992. DOI: 10.1080/14786442608564127.
- **van der Pol, B. & van der Mark, J. (1927).** "Frequency Demultiplication." *Nature* 120(3019), 363–364. DOI: 10.1038/120363a0.
- **Cartwright, M. L. & Littlewood, J. E. (1945).** *J. London Math. Soc.* s1-20(3), 180–189. DOI: 10.1112/jlms/s1-20.3.180.
- **Andersen, C. M. & Geer, J. F. (1982).** "Power Series Expansions for the Frequency and Period of the Limit Cycle of the Van Der Pol Equation." *SIAM J. Appl. Math.* 42(3), 678–693. DOI: 10.1137/0142047.
- **Strogatz, S. (2019).** *Nonlinear Dynamics and Chaos*, 2nd ed., CRC Press, Example 8.4.1 (Hopf bifurcation, limit-cycle radius 2, relaxation regime).
- **Laje, R., Gardner, T. J. & Mindlin, G. B. (2002).** "Neuromuscular control of vocalizations in birdsong: A model." *Phys. Rev. E* 65, 051921. DOI: 10.1103/physreve.65.051921. — avian syrinx = two coupled VdP oscillators.
- **Laje, R. & Mindlin, G. B. (2002).** "Diversity within a Birdsong." *Phys. Rev. Lett.* 89, 288102. DOI: 10.1103/physrevlett.89.288102.
- **Mindlin, G. B. (2009).** "Models of birdsong (physics)." *Scholarpedia* 4(1):6923. DOI: 10.4249/scholarpedia.6923.
- **FitzHugh, R. (1961); Nagumo, J., Arimoto, S. & Yoshizawa, S. (1962).** BVP neuron model — VdP family as biological relaxation oscillator (spiking).
- **Wikipedia: "Van der Pol oscillator"** (fetched 2026-10-22) — equation forms, period expansions, chaos parameters (μ=8.53, A=1.2, ω=2π/10) verified.

---

## 3. Technical Mechanics (full)

### 3.1 Equations

**General audio form** ($\omega_0 = 2\pi f_0$):

$$\frac{d^2x}{dt^2} - \mu\,(1 - x^2)\,\frac{dx}{dt} + \omega_0^2\,x = 0$$

**Unit-frequency form** (the literature standard):

$$\frac{d^2x}{dt^2} - \mu(1-x^2)\frac{dx}{dt} + x = 0$$

**First-order state form** ($y = \dot{x}$ — the direct integration target):

$$\dot{x} = y, \qquad \dot{y} = \mu\,(1 - x^2)\,y - \omega_0^2\,x$$

**Liénard / relaxation state-space form** (better conditioned for large $\mu$):

$$y = x - \tfrac{1}{3}x^3 - \tfrac{\dot{x}}{\mu}
\qquad\Longrightarrow\qquad
\dot{x} = \mu\left(x - \tfrac{1}{3}x^3 - y\right), \qquad \dot{y} = \frac{1}{\mu}\,x$$

**Forced form** (entrainment / subharmonics / chaos):

$$\frac{d^2x}{dt^2} - \mu(1-x^2)\frac{dx}{dt} + x = A\sin(\omega_d t)$$

**Coupled pair** (syrinx / vocal folds; output $y = x_1 + x_2$):

$$\ddot{x}_1 - \mu(1-x_1^2)\dot{x}_1 + \omega_1^2 x_1 = k(x_2 - x_1), \qquad
\ddot{x}_2 - \mu(1-x_2^2)\dot{x}_2 + \omega_2^2 x_2 = k(x_1 - x_2), \qquad \omega_2 - \omega_1 = \Delta\omega$$

### 3.2 Dynamics: what the parameters actually do

| Parameter | Role | Regime |
|---|---|---|
| $\mu$ | nonlinear damping strength = **timbre knob** | $<0$: spiral sink (silence); $=0$: linear sinusoid; $0.01$–$0.5$: quasi-sinusoidal; $1$–$5$: rounded saw; $>5$: relaxation spikes |
| $\omega_0$ | linear resonance = **pitch knob** (sine regime) | $f_0 = \omega_0/2\pi$ for small $\mu$; relaxation regime: $f \approx \omega_0^2/(1.614\,\mu)$ |
| $A$ | drive amplitude = **chaos/entrainment knob** (forced mode) | small: locked; large: quasiperiodic → chaotic |
| $\omega_d$ | drive frequency | rational $\omega_d/\omega_0$ → mode locking / subharmonics; irrational → quasiperiodicity |
| $k$, $\Delta\omega$ | coupling strength, detuning (coupled mode) | $k$↑ → mode locking; $\Delta f$ → beating rate |

**Amplitude.** Hopf bifurcation at $\mu=0$: for $0<\mu\ll 1$ the limit cycle is a circle of radius $\approx 2$ (in the unit-frequency form); amplitude grows slowly with $\mu$. The limit cycle is *globally attracting* — initial conditions are forgotten within a few cycles, so output amplitude is fixed by $\mu$ and must be normalized: $y[n] = g \cdot x/2$.

**Period.** No closed-form solution exists (Andersen & Geer give series). Two regimes:

- small $\mu$: $\displaystyle T = \frac{2\pi}{1 - \mu^2/16 + 17\mu^4/3072 + O(\mu^6)}$;
- large $\mu$ (relaxation): $T \approx (3 - 2\ln 2)\,\mu \approx 1.614\,\mu$ (unit-frequency form; real time $T/\omega_0$).

**Pitch calibration (essential).** Because the relaxation-regime fundamental $f \approx \omega_0^2/(1.614\,\mu)$ is *quadratic* in $\omega_0$ and linear in $\mu$, the same $\omega_0$ yields different pitches at different $\mu$. Calibrate numerically: simulate 5–10 cycles, measure the mean zero-crossing period $T_m$, then set $\omega_0 \leftarrow 2\pi f_0 \cdot (T_m f_s \cdot 2\pi f_0/\omega_0)$ — or, cleaner, precompute a per-$\mu$ pitch table (ω₀ → measured $f$) once per voice and invert it for the target MIDI pitch.

### 3.3 Discretization (Python/NumPy)

**RK4** (accurate, $O(1)$/sample/voice, vectorized over voices):

```python
import numpy as np

class VanDerPol:
    """Van der Pol oscillator synthesis. State: (x, v); x is the audio sample.
    Modes: 'free' (self-oscillation), 'forced' (+A sin(wd t)), 'coupled' (two oscs)."""

    def __init__(self, sr=44100.0, mu=3.0, f0=110.0, A=0.0, wd=0.0,
                 k=0.0, detune=0.0, seed=0):
        self.sr, self.mu = sr, mu
        self.w0 = 2.0 * np.pi * f0 / sr          # normalized angular frequency
        self.A, self.wd = A, 2.0 * np.pi * wd / sr
        self.k, self.det = k, 2.0 * np.pi * detune / sr
        rng = np.random.default_rng(seed)
        self.x, self.v = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)
        self.x2, self.v2 = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)
        self.t = 0.0

    def _f(self, x, v, x_other, t):
        # dv/dt = mu(1-x^2)v - w0^2 x + A sin(wd t) + coupling
        return (self.mu * (1.0 - x * x) * v - self.w0 * self.w0 * x
                + self.A * np.sin(self.wd * t) + self.k * (x_other - x))

    def tick(self):
        dt = 1.0 / self.sr
        # --- oscillator 1 (RK4) ---
        k1v = self._f(self.x, self.v, self.x2, self.t)
        k1x = self.v
        k2v = self._f(self.x + 0.5*dt*k1x, self.v + 0.5*dt*k1v, self.x2, self.t + 0.5*dt)
        k2x = self.v + 0.5*dt*k1v
        k3v = self._f(self.x + 0.5*dt*k2x, self.v + 0.5*dt*k2v, self.x2, self.t + 0.5*dt)
        k3x = self.v + 0.5*dt*k2v
        k4v = self._f(self.x + dt*k3x, self.v + dt*k3v, self.x2, self.t + dt)
        k4x = self.v + dt*k3v
        self.x += dt/6.0 * (k1x + 2*k2x + 2*k3x + k4x)
        self.v += dt/6.0 * (k1v + 2*k2v + 2*k3v + k4v)
        # --- oscillator 2 (detuned, coupled) ---
        w2 = self.w0 + self.det
        def f2(x, v, xo):
            return (self.mu * (1.0 - x*x) * v - w2*w2 * x
                    + self.A * np.sin(self.wd * self.t) + self.k * (xo - x))
        k1v = f2(self.x2, self.v2, self.x); k1x = self.v2
        k2v = f2(self.x2 + 0.5*dt*k1x, self.v2 + 0.5*dt*k1v, self.x); k2x = self.v2 + 0.5*dt*k1v
        k3v = f2(self.x2 + 0.5*dt*k2x, self.v2 + 0.5*dt*k2v, self.x); k3x = self.v2 + 0.5*dt*k2v
        k4v = f2(self.x2 + dt*k3x, self.v2 + dt*k3v, self.x); k4x = self.v2 + dt*k3v
        self.x2 += dt/6.0 * (k1x + 2*k2x + 2*k3x + k4x)
        self.v2 += dt/6.0 * (k1v + 2*k2v + 2*k3v + k4v)
        self.t += dt
        return 0.5 * (self.x + self.x2)          # normalized, [-1, 1] approx

    def render(self, n):
        return np.fromiter((self.tick() for _ in range(n)), float, count=n)

    # --- wavetable mode: precompute one limit-cycle period for real-time playback ---
    def limit_cycle(self, cycles=30, warmup=20):
        """Integrate warmup cycles (transient), then return the last full period."""
        dt = 1.0 / self.sr
        n_warm = int(warmup * 2*np.pi / self.w0 / dt)
        for _ in range(n_warm):
            self.tick()
        # capture zero crossing to find one period
        buf = [self.x]
        prev = self.x
        for _ in range(int(3 * 2*np.pi / self.w0 / dt)):
            self.tick(); buf.append(self.x)
            if prev < 0.0 <= self.x:               # rising zero crossing
                break
            prev = self.x
        start = len(buf)
        for _ in range(int(3 * 2*np.pi / self.w0 / dt)):
            self.tick(); buf.append(self.x)
            if prev < 0.0 <= self.x:
                break
            prev = self.x
        return np.array(buf[start:])               # one full period, table-ready
```

**Semi-implicit Euler** (cheap alternative, stable for small $\mu$):

$$v_{n+1} = v_n + dt\,[\mu(1 - x_n^2) v_{n+1} - \omega_0^2 x_n], \qquad x_{n+1} = x_n + dt\, v_{n+1}$$

**Wavetable mode.** The limit cycle is a *fixed periodic waveform* for given $\mu$: integrate ~20 cycles, discard the transient, keep the last cycle, play it back via a standard phase accumulator (optionally with SP-041 mipmap/PolyBLEP anti-aliasing). $\mu$-morph = crossfade between precomputed tables. Real-time cost drops to $O(1)$ table reads with exact, calibration-free pitch — this is the recommended production path.

**Output chain:** $y = g\cdot(x/2)$, DC-block (relaxation spikes are asymmetric → highpass ~20 Hz), optional 2× oversampling for $\mu \gtrsim 5$, optional hard clip.

### 3.4 Canonical parameter presets

| Preset | μ | Mode | Result |
|---|---|---|---|
| Sine lead | 0.1 | free | near-pure tone |
| Analog saw bass | 3–4 | free | rounded saw, ~1/k rolloff |
| Buzzy relaxation | 6–10 | free | spiky, reedy/brassy |
| Subharmonic pulse | 5–8 | forced, $\omega_d = n\,\omega_0$ | entrained f₀/n pulsing |
| Chaos hiss | 8.53 | forced, A=1.2, ω_d=2π/10·(scaled) | deterministic chaos texture |
| Phonation (folds) | 1–2 | coupled, Δf ≈ 0.5–2 Hz | glottal pulses + beating |
| Syllable chirps | 2–4 | coupled, k↑ | mode-locked chirp trains |

---

## 4. Musical Elements Framework

- **PITCH:** $f_0 = \omega_0/2\pi$ (sine regime); relaxation regime calibrated $\omega_0 = \sqrt{1.614\,\mu\,(2\pi f_0)}$; entrained subharmonics $f_0/n$; detuned pairs beat at $\Delta f$; chaos → pitch band/smear.
- **RHYTHM:** relaxation cycle = audio-rate "slow build, fast release"; sub-audio $\mu$ → LFO/pulse (period $T = 1.614\mu/\omega_0^2$); entrainment → period-$n$ grids; coupling → amplitude-modulated chirp rhythms; BVP neuron mode → spiking.
- **HARMONY:** coupled rows at rational frequency ratios mode-lock into harmonic stacks; forced locking at octave/fifth ratios; detuned dyads; chaotic coupling → inharmonic clusters.
- **STRUCTURE:** section automation of $\mu$ (sine→buzz→relaxation arcs), $A$ (drive), $\omega_d/\omega_0$ (sync), $k$ (coupling); chaos↔order trajectories as macro-form; per-voice parameter vectors.
- **TEXTURE:** sinusoid → rounded saw → relaxation spikes → chaotic hiss/rasp; glottal-pulse phonation; jittered coupled textures; polyphonic stacks of independent limit cycles.

---

## 5. UnitMatrix Integration

- **Voices = rows:** per-row parameter vector $(\mu, f_0, A, \omega_d, k, \Delta f, \text{seed})$; e.g. Bass (μ≈3–4), Lead (μ≈0.1), Pulse (sub-audio μ), Folds (coupled pair on a voice).
- **Sections = columns:** section breakpoints automate μ/A/ω_d/k across cells — a section is a parameter-automation span, not a new instrument.
- **Cells = MusicUnit:** note onset retargets parameters (attack), duration = sustain, velocity = output gain $g$ (amplitude is fixed by the limit cycle — never map velocity to initial $x$), note-off glides $\mu \to 0^+$ for a natural release. Per-cell buffers fill the exact section length in ticks → zero-drift invariant preserved; `validate()` must pass before export.
- **Produce:** `produce(method="SP-121")` dispatches `sound/synthesis/van_der_pol_synthesis.py`; per-voice child seed = `seed*101 + row` for deterministic, decorrelated textures.

---

## 6. Pitfalls

1. **No closed-form period** — calibrate pitch numerically per (μ, f₀); μ-sweeps at fixed ω₀ shift pitch (T ∝ μ/ω₀² in relaxation regime).
2. **Amplitude is fixed (≈2)** — the limit cycle forgets initial conditions; map velocity to gain, not to $x_0$.
3. **μ ≤ 0 kills oscillation** — sub-Hopf decay; sustained notes need μ > 0; release = glide to 0⁺.
4. **Stiff at large μ** — fast discharge needs small dt / Liénard form / oversampling; wavetable mode avoids integration at render.
5. **Chaos is parameter-fragile** — float64 + state clamping (x³ overflow → NaN); chaos = texture, not pitch.
6. **Entrainment surprises** — drive near harmonics pulls pitch to f₀/n; FFT-verify pitched parts.
7. **DC + aliasing** — asymmetric relaxation spikes: AC-couple + oversample or mipmapped wavetable.
8. **Correlated jitter** — coupled pairs share dynamics; per-voice seeds; zero-drift requires equal-length cells.
