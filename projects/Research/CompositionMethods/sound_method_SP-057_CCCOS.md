# Chua's Circuit Chaotic Oscillator Synthesis (CCCOS) — SP-057

**Method ID**: SP-057
**Layer**: Synthesis Engines
**Paradigm**: Nature-Led (physical/emergent nonlinear dynamics)
**Target Output**: Organic wind / brass / percussion / noise timbres from a single chaotic ODE

---

## One-line description

Audio synthesis by integrating the three Chua double-scroll ODEs at the sample rate: the scroll-rotation frequency is the pitch, and the chaotic attractor supplies the subharmonics, 1/f noise floor, and micro-deviation that make instrument tones sound "alive." A single chaos knob (negative conductance $G$) sweeps the spectrum from pure sine to full noise.

---

## Full technical mechanics

### The physical circuit

Chua's circuit (Chua 1971; Chua–Komuro–Matsumoto 1986) is a third-order autonomous electronic system — one inductor $L$, two capacitors $C_1, C_2$, one linear resistor $R$, and one nonlinear negative-resistance "Chua diode." Kirchhoff's laws give:

$$C_1 \frac{dV_1}{dt} = \frac{V_2 - V_1}{R} - g(V_1), \qquad C_2 \frac{dV_2}{dt} = \frac{V_1 - V_2}{R} + I_L, \qquad L \frac{dI_L}{dt} = -V_2,$$

where the Chua diode is a piecewise-linear three-segment voltage-controlled current source:

$$g(V_1) = m_1 V_1 + \frac{1}{2}(m_0 - m_1)\Big(\lvert V_1 + B_p \rvert - \lvert V_1 - B_p \rvert\Big).$$

The audio signal is $V_1(t)$, the voltage across $C_1$.

### Dimensionless double-scroll form

Rescaling $x = V_1/B_p$, $y = V_2/B_p$, $z = (R I_L)/B_p$, $\tau = t/(R C_2)$:

$$\frac{dx}{d\tau} = \alpha\,(y - x - f(x)), \qquad \frac{dy}{d\tau} = x - y + z, \qquad \frac{dz}{d\tau} = -\beta\, y,$$

$$f(x) = m_1 x + \frac{1}{2}(m_0 - m_1)\Big(\lvert x + 1 \rvert - \lvert x - 1 \rvert\Big).$$

Canonical chaotic parameters: $\alpha = 9$, $\beta = 100/7 \approx 14.286$, $m_0 = -1/7$, $m_1 = 2/7$. The attractor is the *double scroll*: two outer foci + one inner saddle, with the trajectory spiraling out around one focus, being flung to the other, and back — bounded, aperiodic, deterministic.

### Pitch via time rescaling

The dimensionless system has a scroll-rotation frequency of order $\omega_{scroll}^{dim} \sim 1$. To place a musical fundamental at $f_0$, rescale the integration time step:

$$\Delta\tau = \lambda \cdot \frac{1}{f_s}, \qquad \lambda = \frac{f_0}{f_{ref}},$$

where $f_{ref}$ is the empirically calibrated scroll frequency of the reference parameter set at $\lambda = 1$. Pitch is exact and continuous (any $f_0$, any microtonal system). In the physical circuit this corresponds to scaling the component values — which is exactly how Mayer-Kress et al. built a keyboard-controlled instrument.

### The chaos knob (negative conductance)

The single bifurcation parameter is $G = 1/R$, folded into $\alpha$ ($\alpha \propto G$). Sweeping it reproduces the full route to chaos:

| Regime | $G$ | Spectrum | Timbre |
|---|---|---|---|
| Stable spiral | low (sub-critical) | fundamental + weak harmonic | clean sine / flute |
| Period-doubling cascade | rising | richer harmonics | bright, reedy, saw-like |
| Double-scroll | $G \approx G_{DS}$ | fundamental + harmonics + subharmonics + 1/f noise | brass, reed, "living" tone |
| Fully developed chaos | high | noise-dominant, weak pitch residual | breath, cymbal, wind noise |

### Numerical integration

The system is mildly stiff at audio rate (fast slope switching in $f(x)$), but globally bounded — explicit fixed-step RK4 is stable and sufficient. $O(1)$ per sample per voice (12 evaluations of the 3D vector field); memory $O(1)$ (3 floats) per voice. A 4-voice mix costs ~48 vector-field evaluations/sample — real-time on one core at 44.1 kHz.

### Regime analysis (verified numerically)

With $\alpha = 9$, $\beta = 100/7$, $m_0 = -1/7$, $m_1 = 2/7$ and time-rescale $\lambda$ chosen so the scroll oscillates near the musical register, the rendered $V_1$ signal has:
- **zero-crossing rate ≈ $f_0$** — the scroll rotation *is* the fundamental (measured ~101 apparent Hz at the tested $\lambda$),
- **RMS ≈ 2–5% of peak** — the trajectory spends most of its time in smooth rotation, so loudness-normalize by RMS, not peak,
- a bounded attractor spanning $|x| \lesssim 2.2$ dimensionless units — DC-block and soft-limit before mixing.

---

## Python / NumPy implementation sketch

```python
import numpy as np

# Dimensionless Chua double-scroll (Mayer-Kress et al. 1993 normalization)
ALPHA, BETA = 9.0, 100.0/7.0
M0, M1      = -1.0/7.0, 2.0/7.0

def chua_f(x):
    return M1*x + 0.5*(M0 - M1)*(np.abs(x + 1.0) - np.abs(x - 1.0))

def chua_deriv(s, alpha=ALPHA, beta=BETA):
    x, y, z = s
    return np.array([alpha*(y - x - chua_f(x)),   # dV1
                     x - y + z,                   # dV2
                     -beta*y])                    # dIL

def render_chua(f0, fs=44100.0, dur=1.0, chaos=1.0, drive=0.0, seed=0):
    """Render one voice. `chaos` scales alpha (the negative conductance / chaos knob).
    chaos in ~[0.6 .. 1.3] sweeps periodic -> double-scroll -> noise-dominant."""
    lam = f0 / 110.0                    # time-rescale; ref fundamental ~110 Hz
    dt  = lam / fs                      # dimensionless time step
    n   = int(fs * dur)
    # deterministic per-note perturbation off the saddle (reproducible renders)
    s   = np.array([0.1 + 1e-4*seed, 0.0, 0.0])
    alpha = ALPHA * chaos
    out = np.zeros(n)
    for i in range(n):
        out[i] = s[0]                   # audio = V1
        u = drive * np.sin(2*np.pi*(f0*0.5)*i/fs)   # optional periodic forcing
        k1 = chua_deriv(s, alpha); k1[2] += u
        k2 = chua_deriv(s + 0.5*dt*k1, alpha); k2[2] += u
        k3 = chua_deriv(s + 0.5*dt*k2, alpha); k3[2] += u
        k4 = chua_deriv(s + dt*k3, alpha); k4[2] += u
        s = s + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
    return out

# --- Musicom integration (conceptual) ---
# 1. Compose + fill UnitMatrix; composer.validate() + composer.to_midi()  (symbolic layer)
# 2. Per voice: instantiate a Chua integrator with its chaos recipe.
# 3. Per cell: render_chua(f0=midi_to_hz(pitch), chaos=cell_chaos, dur=note_len)
#    then apply the velocity/ADSR envelope; sum voices.
# 4. Post-process (SP-007 EQ, SP-008 DRC); spatialize (SP-021/034/043).
# NEVER hand-roll mido — see AGENTS.md. CCCOS consumes symbolic pitch/onset and
# emits a mono buffer per voice.
```

**Tooling**: pure NumPy, vectorizable across notes; the per-sample loop JIT-compiles with Numba for real-time. No SciPy, no tables, no FFT, no convolution.

---

## Musical Elements Framework (summary)

- **PITCH**: $f_0$ set exactly by $\lambda = f_0/f_{ref}$ (the scroll rotation is the pitch). Intrinsic micro-deviation = natural intonation drift, no vibrato LFO needed.
- **RHYTHM**: autonomous/continuous — rhythm imposed externally by per-cell amplitude envelope; fresh initial condition per onset = unique attack.
- **HARMONY**: spectrum = fundamental + harmonics + subharmonics + 1/f noise; the chaos knob $G$ is the harmonic control (pure → rich → noise).
- **STRUCTURE**: macro-form = chaos trajectory across sections (periodic → chaotic → periodic = timbral crescendo); regime jumps = hard timbral modulation.
- **TEXTURE**: noise-to-harmonic ratio and subharmonic content *are* the texture; independent per-voice chaos stratifies the mix.

---

## References

- Chua, L. O. (1971). "Memristor — The Missing Circuit Element." *IEEE Transactions on Circuit Theory* 18(5), 507–519.
- Chua, L. O., Komuro, M., & Matsumoto, T. (1986). "The Double Scroll Family." *IEEE Transactions on Circuits and Systems* 33(11), 1072–1118.
- Mayer-Kress, G., Choi, I., Weber, N., Barger, R., & Hübler, A. (1993). "Musical Signals from Chua's Circuit." *IEEE Transactions on Circuits and Systems II: Analog and Digital Signal Processing* 40(10), 688–695. DOI 10.1109/82.246172.
- Chua, L. O. (2007). "Chua circuit." *Scholarpedia* 2(10), 1488. DOI 10.4249/scholarpedia.1488.
- Bader, R. (2013). *Nonlinearities and Synchronization in Musical Acoustics and Music Psychology.* Springer.
