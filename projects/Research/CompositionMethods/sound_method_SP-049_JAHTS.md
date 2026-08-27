# Jiles-Atherton Hysteresis Tape Saturation (JAHTS) — Method SP-049

**Classification**: Sound Production → Post-Processing / DSP
**Target Output**: Analog Tape Saturation / Warmth & Glue (mix-bus or per-voice)
**Status**: Documented 2026-08-21 (musicom methods database)

---

## 1. One-line summary
Physical model of analog magnetic tape recording: record-head magnetic field → Jiles-Atherton hysteresis magnetization (stateful ODE, RK4-solved) → play-head loss filter. Produces tape saturation, soft-clip warmth, tape hiss, head bump, spacing loss, and wow/flutter. 16× oversampling required.

## 2. Source
Chowdhury, J. (2019). "Real-Time Physical Modelling for Analog Tape Machines." DAFx-19, Birmingham. The paper behind the open-source CHOW Tape Model (jatinchowdhury18/AnalogTapeModel). Hysteresis physics from Jiles & Atherton (1986); recording physics from Bertram (1994); engineering practice from Kadis (2012) and Holters & Zölzer (2016).

## 3. Signal chain
```
x[n] → [16× oversample] → [bias mix: I = x + B·cos(2π·f_bias·nT)] → [record head: H = (NE/g)·I]
    → [Jiles-Atherton hysteresis: dM/dt = f(t,M,H), RK4] → [play head: V = NWEvµ0g·M]
    → [loss FIR: spacing · thickness · gap] → [de-bias LPF] → [downsample] → [wow/flutter modulated delay] → y[n]
```

## 4. Extended mathematics

### 4.1 Record head (Karlqvist field, gap-center collapse)
$$H(t) = \frac{N E}{g}\, I(t), \qquad \hat{H}(n) = \frac{NE}{g}\hat{I}(n)$$
$N$ = turns (~100), $E$ = head efficiency (~0.1), $g$ = head gap (2.5–12 µm).

### 4.2 Jiles-Atherton hysteresis ODE (field form)
$$\frac{dM}{dH} = \frac{(1-c)\,\delta_M\,(M_{an} - M)}{(1-c)\,\delta_S\,k - \alpha\,(M_{an} - M)} + c\,\frac{dM_{an}}{dH}$$

Anhysteretic magnetization (Langevin):
$$M_{an} = M_s \, L\!\left(\frac{H + \alpha M}{a}\right), \qquad L(x) = \coth(x) - \frac{1}{x}$$

Directional flags:
$$\delta_S = \mathrm{sign}(\dot{H}), \qquad \delta_M = \begin{cases}1 & \delta_S\,(M_{an}-M) > 0 \\ 0 & \text{otherwise}\end{cases}$$

### 4.3 Time-domain form (Holters & Zölzer 2016)
$$\frac{dM}{dt} = \frac{(1-c)\,\delta_M\,(M_s L(Q) - M)}{(1-c)\,\delta_S\,k - \alpha\,(M_s L(Q) - M)}\,\dot{H} \;+\; \frac{c\,M_s}{a}\,\dot{H}\,L'(Q)\Big/\!\left(1 - \frac{c\,\alpha\,M_s}{a}L'(Q)\right)$$

with $Q = \frac{H + \alpha M}{a}$, $L'(x) = \frac{1}{x^2} - \coth^2(x) + 1$.

### 4.4 RK4 integration
$$\hat{M}(n) = \hat{M}(n{-}1) + \frac{k_1}{6} + \frac{k_2}{3} + \frac{k_3}{3} + \frac{k_4}{6}, \qquad k_i = T f(\cdot)$$
Half-sample inputs for $k_2, k_3$ by linear interpolation. Trapezoid rule is unstable here — RK4 mandatory.

### 4.5 Play head + loss effects
Ideal voltage: $\hat{V}(n) = N W E v \mu_0 g\, \hat{M}(n)$.

Loss filter (inverse DFT of analytic response):
$$V(t) = V_0(t)\; e^{-kd}\;\left[\frac{1 - e^{-k\delta}}{k\delta}\right]\left[\frac{\sin(kg/2)}{kg/2}\right], \qquad k = \frac{2\pi f}{v}$$

| Term | Name | Effect |
|---|---|---|
| $e^{-kd}$ | spacing loss | HF roll-off from tape-head distance $d$ |
| $\frac{1-e^{-k\delta}}{k\delta}$ | thickness loss | HF roll-off from tape thickness $\delta$ |
| $\frac{\sin(kg/2)}{kg/2}$ | gap loss | sinc null at $f = v/g$; "head bump" just below |

### 4.6 Bias
$$\hat{I}_{head}(n) = \hat{I}_{in}(n) + B \cos(2\pi f_{bias} n T), \qquad f_{bias} \approx 55\ \text{kHz},\ B \approx 5\text{–}10\times$$
Linearizes the loop, removes the zero-crossing deadzone. De-bias LPF (~24 kHz) on playback.

### 4.7 Wow and flutter
Measured periodic timing-imperfection function $\tau(t)$ drives a modulating delay line:
$$y(n) = x(n + \tau(n)) \quad \text{(fractional-delay interpolation)}$$

### 4.8 Ferric-oxide tape constants (Sony TC-260, Chowdhury 2019)
| Constant | Symbol | Value |
|---|---|---|
| Saturation magnetization | $M_s$ | 3.5e5 A/m |
| Hysteresis width ≈ coercivity | $k$ | 27 kA/m |
| Anhysteretic shape | $a$ | 22 kA/m |
| Susceptibility ratio | $c$ | 0.17 |
| Mean-field coupling | $\alpha$ | 1.6e-3 |
| Bias frequency / gain | $f_{bias}, B$ | 55 kHz, 5× |
| Tape speed | $v$ | 3.75 / 7.5 ips |
| Head gap / spacing / thickness | $g, d, \delta$ | 5 / 20 / 35 µm |

## 5. Python / NumPy implementation sketch

```python
import numpy as np
from scipy.signal import lfilter, firwin

Ms, k, a, c, alpha = 3.5e5, 27e3, 22e3, 0.17, 1.6e-3
NE_g = 100 * 0.1 / 6e-6

def langevin(x):
    ax = np.abs(x)
    return np.where(ax < 1e-4, x / 3.0, 1.0 / np.tanh(x) - 1.0 / x)

def langevin_p(x):
    ax = np.abs(x)
    return np.where(ax < 1e-4, 1.0 / 3.0, 1.0 / x**2 - 1.0 / np.tanh(x)**2 + 1.0)

def dMdt(M, H, Hdot):
    Q = (H + alpha * M) / a
    Man = Ms * langevin(Q)
    dMan = Ms / a * langevin_p(Q)
    dS = 1.0 if Hdot >= 0 else -1.0
    dM = 1.0 if dS * (Man - M) > 0 else 0.0
    denom = (1 - c) * dS * k - alpha * (Man - M)
    term1 = (1 - c) * dM * (Man - M) / denom * Hdot if abs(denom) > 1e-12 else 0.0
    term2 = (c * Ms / a * Hdot * dMan) / (1 - c * alpha * Ms / a * dMan)
    return term1 + term2

def rk4_step(M, H_prev, H_cur, Hdot_prev, Hdot_cur, T):
    f = dMdt
    k1 = T * f(M, H_prev, Hdot_prev)
    Hm = 0.5 * (H_prev + H_cur); Hdm = 0.5 * (Hdot_prev + Hdot_cur)
    k2 = T * f(M + 0.5 * k1, Hm, Hdm)
    k3 = T * f(M + 0.5 * k2, Hm, Hdm)
    k4 = T * f(M + k3, H_cur, Hdot_cur)
    return M + (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

def tape_saturate(x, fs=44100, oversample=16, drive=1.0, bias_gain=5.0,
                  bias_freq=55e3, tape_speed_ips=7.5, gap=5e-6,
                  spacing=20e-6, thickness=35e-6, head_width=0.125 * 0.0254):
    fs_os = fs * oversample
    T = 1.0 / fs_os
    n = np.arange(len(x) * oversample) / oversample
    x_os = np.interp(n, np.arange(len(x)), x) * drive
    t = np.arange(len(x_os)) / fs_os
    I = x_os + bias_gain * np.cos(2 * np.pi * bias_freq * t)
    H = NE_g * I
    Hdot = np.gradient(H, T)
    M = np.zeros_like(H)
    for i in range(1, len(H)):
        M[i] = rk4_step(M[i - 1], H[i - 1], H[i], Hdot[i - 1], Hdot[i], T)
    v = tape_speed_ips * 0.0254
    V = 100 * head_width * 0.1 * v * 4 * np.pi * 1e-7 * gap * M
    f = np.fft.rfftfreq(256, 1 / fs_os)
    kk = 2 * np.pi * f / v
    loss = np.exp(-kk * spacing) * (1 - np.exp(-kk * thickness)) / (kk * thickness + 1e-12)
    loss *= np.sinc(kk * gap / (2 * np.pi) + 1e-30)
    loss[0] = 1.0
    h = np.fft.irfft(loss, 256)
    V = lfilter(h, [1.0], V)
    V = lfilter(firwin(65, 0.45 / oversample), [1.0], V)
    return V[::oversample]

def wow_flutter(x, fs=44100, depth=0.001, rate=0.5):
    n = len(x)
    tau = depth * fs * np.sin(2 * np.pi * rate * np.arange(n) / fs)
    out = np.zeros(n)
    for i in range(n):
        d = i + tau[i]
        d0 = int(np.floor(d)); frac = d - d0
        if 0 <= d0 < n - 1:
            out[i] = (1 - frac) * x[d0] + frac * x[d0 + 1]
    return out
```

Production note: the per-sample RK4 loop should be compiled (Numba/Cython) or replaced by the CHOW Tape Model plugin. The musicom engine handles UnitMatrix fill + zero-drift MIDI export upstream; JAHTS consumes rendered audio downstream.

## 6. UnitMatrix integration
- **Rows (Voices)**: bus mode (sum → one JAHTS = mix glue) or per-voice mode (independent drive/bias/speed per row).
- **Columns (Sections)**: per-section drive, bias gain, tape speed, gap/spacing/thickness, flutter depth = timbral macro-form.
- **Cells** $U_{v,s}$: `{TEXTURE}` = drive/bias/hiss; `{RHYTHM}` = flutter depth; `{PITCH}` = tape speed (varispeed); `{HARMONY}` = drive (even/odd harmonic balance).

## 7. Pitfalls (condensed)
1. Trapezoid integrator unstable → use RK4.
2. Aliasing from hysteresis nonlinearity → 16× oversampling.
3. 55 kHz bias unrepresentable at baseband → oversample before bias mix.
4. Langevin cancellation near 0 → $x/3$ guard for $|x|<10^{-4}$.
5. Under-bias → deadzone/crossover distortion (keep $B \approx 5\text{–}10\times$).
6. DC/rumble from hysteresis asymmetry → high-pass 20–40 Hz.
7. Over-depth wow/flutter → seasick warble (use measured sub-ms depth).
8. Pure-Python RK4 slow → Numba/Cython or CHOW Tape plugin.

## 8. References
- Chowdhury, J. (2019). "Real-Time Physical Modelling for Analog Tape Machines." DAFx-19. https://www.dafx.de/paper-archive/2019/DAFx2019_paper_3.pdf
- Jiles, D. C. & Atherton, D. L. (1986). "Theory of ferromagnetic hysteresis." J. Magn. Magn. Mater. 61, 48–60.
- Bertram, H. N. (1994). *Theory of Magnetic Recording*. Cambridge Univ. Press.
- Kadis, J. (2012). *The Science of Sound Recording*. Focal Press.
- Holters, M. & Zölzer, U. (2016). "Circuit simulation with inductors and transformers based on the Jiles-Atherton model of magnetization."
- CHOW Tape Model. https://github.com/jatinchowdhury18/AnalogTapeModel
- Sony Corporation (1965). *Sony TC-260 Service Manual*.
