# SP-070 — Feedback Amplitude Modulation Synthesis (FBAM)

**Layer:** absolute (sound production)
**Category:** Synthesis Engines
**Target output:** Harmonic-Rich / Formant / Distortion Timbres
**Complexity:** $\mathcal{O}(1)$ per sample (1 MUL + 1 ADD + 1 table lookup), deterministic per seed

---

## One-line description

Nonlinear synthesis where a sinusoidal carrier is amplitude-modulated by its own fed-back output — $y(n)=\cos(\omega_0 n)[1+\beta\,y(n-1)]$ — a periodically linear time-varying one-pole filter whose coefficient is the input signal itself. A single scalar $\beta$ sweeps spectral brightness from a pure sinusoid to a full harmonic pulse train with no spectral holes (unlike FM); six structural variations extend it to phase distortion, tunable formants, waveshaping, comb-filter timbres, and adaptive audio effects.

## Source

- **Kleimola, J., Lazzarini, V., Välimäki, V., & Timoney, J. (2011).** "Feedback Amplitude Modulation Synthesis." *EURASIP Journal on Advances in Signal Processing*, Article 434378 (18 pp, open access). The canonical modern treatment.
- **Lazzarini, V., Timoney, J., Kleimola, J., & Välimäki, V. (2009).** "Five Variations on a Feedback Theme." *Proc. DAFx-09*, Como, 139–145.
- **Risset, J.-C. (1969).** *An Introductory Catalog of Computer-Synthesized Sounds*, Bell Labs — the MUSIC V feedback-AM unit generator origin.
- **Layzer, A. (1971).** "Some idiosyncratic aspects of computer-synthesized sound."
- **Cherniakov, M. (2003).** *An Introduction to Parametric Digital Filters and Oscillators*, Wiley — the PLTV-filter theory.
- **Arfib, D. (1979)** and **Le Brun, M. (1979)** — nonlinear-distortion / waveshaping lineage.

## Technical mechanics (extended)

### Basic equation

$$y(n)=\cos(\omega_0 n)\left[1+\beta\,y(n-1)\right],\qquad \omega_0=2\pi f_0/f_s,\quad y(n)=0\ \text{for}\ n\le 0.$$

Infinite expansion:

$$y(n)=\sum_{k=0}^{\infty}\prod_{m=0}^{k}\cos[\omega_0(n-m)].$$

### PLTV filter interpretation

$y(n)=x(n)+a(n)\,y(n-1)$ with $x(n)=a(n)=\cos(\omega_0 n)$ — a coefficient-modulated one-pole IIR. Time-varying impulse response:

$$h(m,n)=\prod_{i=m+1}^{n}a(i)=\frac{g(n)}{g(m)},\qquad g(n)=\prod_{i=1}^{n}a(i),\ g(0)=1.$$

With modulator period $N=\lfloor T_0+0.5\rfloor$ ($T_0=2\pi/\omega_0$):

$$H(\omega,n)=\frac{1+\sum_{k=1}^{N-1}b_k(n)e^{-jk\omega}}{1-a_N e^{-jN\omega}},\qquad b_k(n)=\prod_{m=1}^{k}\cos(\omega_0[n-m+1]),\quad a_N=\prod_{m=1}^{N}\cos(\omega_0 m).$$

Equivalent to a time-varying FIR (harmonic generation) cascaded with a fixed comb (peaks at the harmonics). AM-dominant reconstruction: $y(n)=A(n)\cos(\omega_0 n+\phi(n))$, $A(n)=|H(\omega_0,n)|$, $\phi(n)=\arg H(\omega_0,n)$.

### Stability & aliasing

- Stability: $|\beta\,a_N|<1$ (impulse response decays). Ceiling $\beta_{\text{stable}}\approx 1.9986-0.00003532(f_0-27.5)$.
- Aliasing is the real limit: oversampling stretches usable $\beta$; cubed-cosine modulator $\cos^3(\omega_0 n)$ widens it ($|\cos|\le 1$).

### Scaling

Per-$\beta$ polynomial gain (degree 1 for $\beta<0.7$; 2/3/5 for 0.7/0.8/0.9) + linear interpolation at $\Delta\beta=0.05$; or 2-D $(\beta,f_0)$ lookup table (bilinear); or online RMS balancer.

### Variations

1. **Feedforward delay:** $y(n)=\cos[\omega_0(n-1)]-\cos(\omega_0 n)[1+\beta y(n-1)]$.
2. **Coefficient-modulated allpass:** $y(n)=\cos[\omega_0(n-1)]-\beta\cos(\omega_0 n)[\cos(\omega_0 n)-y(n-1)]$ — phase distortion.
3. **Heterodyning.** I (in-loop): $y(n)=\cos(\theta n)\{\cos(\omega_0 n)[1+\beta y(n-1)]\}$. II (out-loop): $s(n)=\cos(\theta n)y(n)$; double-carrier formant: $k=\mathrm{int}(f_c/f_0)$, $g=f_c/f_0-k$, $s(n)=y(n)[(1-g)\cos(k\omega_0 n)+g\cos((k{+}1)\omega_0 n)]$.
4. **Nonlinear waveshaping:** $y(n)=\cos(\omega_0 n)\{1+f[\beta y(n-1)]\}$. Cosine → feedback-FM partial (even harmonics removed); ABS → odd-only square-like; cos+sin stacked → exact feedback FM up to $f_0$.
5. **Non-unitary delay:** $y(n)=\cos(\omega_0 n)[1+\beta y(n-D)]$; at $D=f_s/f_0$ the closed form $y(n)=\cos(\omega_0 n)/(1-\beta\cos(\omega_0 n))$ for $0\le\beta<1$.
6. **Decoupled filter:** $y(n)=x(n)+m(n)\beta y(n-1)$; adaptive effect $y(n)=x(n)[1+\beta y(n-1)]$.

## Python/NumPy implementation sketch

```python
import numpy as np

def fbam(f0, beta, fs=44100.0, dur=1.0, variation="basic",
         waveshaper=None, delay=1, f_ring=None, f_carrier=None):
    """Feedback Amplitude Modulation oscillator (SP-070).
    variation: basic|v1|v2|v3I|v3II|v5|v6
    """
    n = int(fs * dur)
    y = np.zeros(n)
    w0 = 2.0 * np.pi * f0 / fs
    t = np.arange(n)
    c0 = np.cos(w0 * t)                 # carrier
    c0_d = np.cos(w0 * (t - 1))         # delayed carrier (v1/v2)
    yp = 0.0                            # y(n-1) state
    # ring / formant carriers
    wr = 2.0 * np.pi * (f_ring or f0) / fs
    cr = np.cos(wr * t)
    if variation == "v6":
        # decoupled carrier + modulator (here: modulator = carrier)
        for i in range(n):
            y[i] = c0[i] + c0[i] * beta * yp
            yp = y[i]
        return y
    for i in range(n):
        if variation == "basic":
            y[i] = c0[i] * (1.0 + beta * yp)
        elif variation == "v1":
            y[i] = c0_d[i] - c0[i] * (1.0 + beta * yp)
        elif variation == "v2":
            y[i] = c0_d[i] - beta * c0[i] * (c0[i] - yp)
        elif variation == "v3I":
            y[i] = cr[i] * (c0[i] * (1.0 + beta * yp))
        elif variation == "v3II":
            y[i] = c0[i] * (1.0 + beta * yp)          # base FBAM
            y[i] = cr[i] * y[i]                        # ring outside loop
        elif variation == "v5":
            y[i] = c0[i] * (1.0 + beta * yp)          # D handled via state
        if waveshaper is not None:
            y[i] = c0[i] * (1.0 + waveshaper(beta * yp))
        yp = y[i]
    # DC-block (cosine carrier adds DC) + peak normalization
    y = y - np.mean(y)
    y = 0.9 * y / (np.max(np.abs(y)) + 1e-9)
    return y
```

For Variation 5, replace the single state `yp` with a length-`D` delay-line ring buffer. Production code lives in `sound/synthesis/fbam.py`; the adaptive-effect mode (Variation 6) belongs under `sound/effects/`.

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| PITCH | carrier $f_0$ (MIDI→Hz); ratio $q=f_0/f_B$ in the operator's $[\text{osc}]$ vector |
| RHYTHM | per-note ADSR $[\text{env}]=(A,D,S,R)$ gates each operator; first-period attack transient = natural accent |
| HARMONY | $\beta$ = brightness/harmonic count (one-knob); variation = odd/even + missing-harmonic mask; V3-II = formant envelope |
| STRUCTURE | operator topology (parallel/cascade/cross-modulated) = macro-form; per-section $[\text{fbam}]=(v,\beta,ws,D)$ |
| TEXTURE | $\beta$ sweep = dense↔sparse; formant bandwidth $\propto\beta$; delay $D$ = comb density; waveshaper = tonal↔noisy |

## UnitMatrix Integration

- **Rows (Voices)** = one FBAM operator/algorithm per voice (lead = V2/V4 bright, bass = basic low $f_0$, pad = V3-II formant stack, percussion = V5 comb + noise).
- **Columns (Sections)** = `{STRUCTURE}` = `(variation, beta, waveshaper, delay_D, carrier_ratio, env)`; join = $\beta$-crossfade.
- **Cells (MusicUnit)** = PITCH→$f_0$; RHYTHM→onset/ADSR; HARMONY→$\beta$ + variation; TEXTURE→formant/waveshaper settings.
- **Flow:** `compose` → `produce(method="SP-070")` → per-voice FBAM render → sum → post-FX (SP-007/008/009/032).

## Pitfalls

1. Aliasing (not stability) bounds $\beta$ — oversample or use cubed-cosine modulator.
2. Frequency-dependent output gain — per-$\beta$ polynomial / 2-D LUT / RMS balancer.
3. Cosine carrier DC offset + first-period transient — DC-block + init state to steady-state peak.
4. V5 instability at $D=f_s/f_0$, $f_s/2f_0$ — detune $D$ or cap $\beta$.
5. Even waveshapers (cos/ABS) strip even harmonics — pick deliberately; stack cos+sin for full richness.
6. Formant width tied to $\beta$ — use double-carrier + modest $\beta$, scale ~35 dB below fundamental.
7. Sparse-only output — pair with a continuous fill layer (Method Hybridization rule).

## References

- Kleimola, Lazzarini, Välimäki & Timoney (2011), *EURASIP J. Adv. Signal Process.*, 434378.
- Lazzarini, Timoney, Kleimola & Välimäki (2009), *DAFx-09*, 139–145.
- Risset (1969), *An Introductory Catalog of Computer-Synthesized Sounds*, Bell Labs.
- Layzer (1971), *Proc. ASCU*, 27–39.
- Cherniakov (2003), *An Introduction to Parametric Digital Filters and Oscillators*, Wiley.
- Arfib (1979), *JAES* 27(10); Le Brun (1979), *JAES* 27(4).
- Moorer (1976), *JAES* 24(9); Puckette (1995), *JAES* 43(1–2).
