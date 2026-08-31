# Fractional Delay-Line Modulation Synthesis (FDLMS) — SP-059

**Method ID**: SP-059
**Layer**: Post-Processing / DSP
**Paradigm**: Rules-Based (deterministic time-varying delay-line DSP)
**Target Output**: Modulated-delay effects — chorus, flanger, vibrato, Doppler/Leslie, doubling, pitch shift

---

## One-line description

Audio effect synthesis by continuously modulating the read pointer of a delay line with **sub-sample interpolation** (linear FIR or unity-gain first-order allpass), producing chorus, flanger, vibrato, Doppler, and pitch-shift effects from a single time-varying-delay engine. The modulated-delay counterpart to the static SP-013 feedback delay, static SP-032 FDN reverb, and dispersive SP-058 spring reverb.

---

## Full technical mechanics

### 1. The fractional delay filter

Given a desired time-varying delay $d(n) = M + \eta(n)$ where $M = \lfloor d(n) \rfloor$ is the integer part and $\eta(n) \in [0,1)$ is the fractional part, the output is interpolated from the two nearest buffer samples $x(n-M)$ and $x(n-M-1)$.

**Linear interpolation (FIR, one zero)**:

$$y(n) = (1 - \eta)\,x(n-M) + \eta\,x(n-M-1)$$

Transfer function for fixed $\eta$: $H(z) = (1-\eta) + \eta z^{-1}$. Squared magnitude:

$$|H(e^{j\omega})|^2 = 1 - 2\eta(1-\eta)(1-\cos\omega)$$

Worst-case rolloff at $\eta = 0.5$: $|H(e^{j\pi/2})|^2 = 0.5$ (i.e. −3 dB at $f_s/4$). Linear interpolation is a $\text{sinc}^2$ frequency response — acceptable for oversampled/narrowband signals, but audible as HF loss on broadband material, and it *accumulates* on each pass through a feedback loop.

**First-order allpass interpolation (IIR, unity gain)**:

$$y(n) = \eta_{\text{ap}}\,[x(n-M) - y(n-1)] + x(n-M-1)$$

Transfer function:

$$H(z) = \frac{\eta_{\text{ap}} + z^{-1}}{1 + \eta_{\text{ap}}\,z^{-1}}$$

Magnitude $|H(e^{j\omega})| = 1$ for all $\omega$ — no amplitude distortion, only phase distortion. The allpass coefficient is set so the DC phase delay equals the desired fractional delay $\eta$:

$$\eta_{\text{ap}} = \frac{1 - \eta}{1 + \eta}, \qquad \tau_p(0) = \frac{1-\eta_{\text{ap}}}{1+\eta_{\text{ap}}} = \eta$$

Cost: 1 multiply + 2 adds per sample (identical to linear), but the unity gain is critical inside feedback loops (flanger, feedback chorus) where the linear interpolator's HF rolloff would compound into a dull, muffled sound.

### 2. Modulation signals

The modulation $m(n)$ added to the base delay $d_0$:

- **Sinusoidal LFO**: $m(n) = A \sin(2\pi f_{\text{LFO}} n / f_s)$ — smooth, organic sweep (spends more time at extremes).
- **Triangle / trapezoid**: linear sweep, uniform sweep rate.
- **Envelope follower**: $m(n)$ tracks the input amplitude envelope (amplitude-dependent pitch wobble).
- **Algorithmic trajectory**: $m(n)$ from 040 Perlin noise, 043 SATM attractor, or 026 DPSM phase offset — Musicom composition methods drive the modulation.

### 3. Chorus / flanger topology

$$w(n) = y(n) + g_f\,w(n-1)$$

$$\text{out}(n) = \text{dry}(n) + \alpha\,w(n)$$

where $g_f$ is feedback gain and $\alpha$ the wet/dry mix. Effect parameters:

| Effect | Base delay $d_0$ | Depth | Rate | Mix $\alpha$ | Feedback $g_f$ |
|---|---|---|---|---|---|
| Vibrato | 1–5 ms | 1–3 ms | 1–10 Hz | wet only | 0 |
| Chorus | 10–30 ms | 1–5 ms | 0.1–5 Hz | ~0.5 | 0 |
| Flanger | 0–1 ms | <1 ms | 0.1–5 Hz | 0.7–1.0 | 0.5–0.8 |
| Doubling | 10–100 ms | 0 (fixed) | 0 | 0.5 | 0 |
| Echo | 50–80 ms | 0 (fixed) | 0 | 0.5 | 0.5–0.8 |

### 4. Multi-voice ensemble chorus

For $K$ delay lines with independent LFOs (phase-spread + rate-detuned):

$$w_k(n) = y_k(n) + g_f\,w_k(n-1), \quad \text{out}(n) = \text{dry}(n) + \frac{\alpha}{K}\sum_{k=1}^{K} w_k(n)$$

Phase spread $\phi_k = 2\pi k / K$ and rate detune $f_k = f_0 + \delta f_k$ ($\delta f_k \sim \mathcal{N}(0, 0.05)$ Hz) prevent the "metallic" sound of perfectly synchronized modulation.

### 5. Pitch shift via dual read heads

Two read pointers separated by $L/2$ samples, sweeping from 0 to $L-1$:

$$d_1(n) = (d_1(n-1) + r) \bmod L, \quad d_2(n) = (d_1(n) + L/2) \bmod L$$

Crossfaded with complementary windows $h_1, h_2$ ($h_1 + h_2 = 1$), so the wrap discontinuity of one head coincides with the midpoint of the other:

$$\text{out}(n) = h_1(d_1)\,y_1(n) + h_2(d_2)\,y_2(n)$$

Pitch ratio = read speed $r$ (e.g. $r = 1.5$ = up a fifth).

### 6. Doppler / Leslie

For a source moving at velocity $v(n)$: $d(n) = d_0 + \frac{v(n)}{c} d_0$. A Leslie rotor (circular motion radius $R$, angular velocity $\Omega$) gives $v(n) = R\Omega\sin(\Omega n/f_s)$ — a sinusoidal pitch wobble at the rotation rate. The Doppler pitch shift is $\Delta f/f \approx -\frac{1}{c}\frac{dd}{dn}$.

### Complexity

$\mathcal{O}(1)$ per sample per delay line (one buffer read + one interpolate). $\mathcal{O}(V \cdot K)$ per sample for $V$ voices × $K$ delay lines. Trivially real-time.

---

## Python / NumPy implementation sketch

```python
import numpy as np

def fractional_delay_chorus(x, fs=44100, base_delay_ms=15.0, depth_ms=3.0,
                            rate_hz=0.8, feedback=0.0, wet=0.5, n_voices=3,
                            interpolation='allpass'):
    """Fractional delay-line modulation: chorus / flanger / vibrato (SP-059)."""
    base_delay = int(base_delay_ms * fs / 1000)
    depth = depth_ms * fs / 1000
    max_delay = base_delay + int(depth) + 2
    buf = np.zeros(max_delay)
    buf_ptr = 0
    phases = np.linspace(0, 2*np.pi, n_voices, endpoint=False)   # phase spread
    rates = rate_hz + 0.05 * np.random.randn(n_voices)           # rate detune
    ap_state = np.zeros(n_voices)                                # allpass state
    out = np.zeros_like(x)
    for n in range(len(x)):
        t = n / fs
        mod = depth * np.sin(2 * np.pi * rates * t + phases)
        delays = base_delay + mod
        wet_sum = 0.0
        for v in range(n_voices):
            d = delays[v]
            M = int(np.floor(d)); eta = d - M
            idx0 = (buf_ptr - M) % max_delay
            idx1 = (buf_ptr - M - 1) % max_delay
            x0, x1 = buf[idx0], buf[idx1]
            if interpolation == 'linear':
                y_v = (1 - eta) * x0 + eta * x1
            else:  # allpass: coefficient set so DC delay = eta
                eta_ap = (1 - eta) / (1 + eta) if (1 + eta) > 1e-9 else 0.0
                y_v = eta_ap * (x0 - ap_state[v]) + x1   # unity gain, phase-only
                ap_state[v] = y_v
            wet_sum += y_v
        wet_sum /= n_voices
        wet_sum += feedback * (out[n-1] if n > 0 else 0.0)
        buf[buf_ptr] = x[n] + feedback * wet_sum
        buf_ptr = (buf_ptr + 1) % max_delay
        out[n] = (1 - wet) * x[n] + wet * wet_sum
    return out
```

**Tooling**: pure NumPy, vectorizable across voices (Numba JIT for real-time); no FFT, no convolution. The musicom engine handles UnitMatrix fill and zero-drift MIDI export upstream (per AGENTS.md — never hand-roll mido); FDLMS consumes *rendered audio buffers* from any SP-xxx voice engine.

---

## Musical Elements Framework

- **PITCH**: Directly modulates pitch via the Doppler effect ($\Delta f/f \approx -\tfrac{1}{c}\tfrac{dd}{dn}$). Vibrato = pure pitch modulation. Chorus = pitch thickening via detuned copies. Flanger = sweeping comb-filter notches (perceived "whoosh", not pitch shift). Pitch-shift mode = harmonic transposition of the full spectrum by a ratio.
- **RHYTHM**: LFO rate $f_{\text{LFO}}$ is a rhythmic parameter — slow (0.1–1 Hz) = long gestures; fast (5–20 Hz) = tremolo-like. LFO shape (sine/triangle/algorithmic) sets feel: sine = organic, triangle = mechanical, Perlin/SATM = irregular-evolving.
- **HARMONY**: Chorus adds detuned copies → richer ensemble spectrum. Flanger creates moving notches → sweeping harmonic color. Pitch shift creates harmonic intervals (fifth, fourth) → harmonization layers.
- **STRUCTURE**: Modulation recipe per section = timbre arc (A dry → B light chorus → C heavy flanger → D pitch-shifted). Stateful buffer carries the modulated tail across section joins = continuous form-glue.
- **TEXTURE**: Voice count $K$ + depth $A$ are texture knobs. Chorus thickens, flanger sculpts, pitch shift layers.

## UnitMatrix Integration (Voices / Sections / Cells)

- **Rows (Voices)**: Each voice $v$ = independent FDLMS instance. Lead = light chorus; bass = dry/subtle vibrato; pad = heavy chorus; percussion = flanger. Summed, then spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)**: Each section $s$ prescribes the modulation recipe → timbre arc; stateful delay line makes joins continuous.
- **Cells** $U_{v,s}$: `{PITCH}` preserved (or ratio-shifted in pitch-shift mode); `{RHYTHM}` = modulation rate; `{HARMONY}` = modulation type's transform; `{TEXTURE}` = wet/dry + depth.
- **Mapping Flow**: compose + fill UnitMatrix → validate → export MIDI (musicom engine) → render dry per voice → apply FDLMS per voice → sum → post-process (SP-007/SP-008) → export/spatialize.

## Pitfalls

1. **Zipper noise** from abrupt delay changes → smooth $m(n)$ with a one-pole LP (~10–20 Hz), never reset LFO phase abruptly.
2. **Linear-interp HF rolloff** (sinc², −3 dB @ $f_s/4$) → muffled, compounds in feedback loops → use allpass (unity gain) or oversample.
3. **Flanger runaway feedback** → enforce $|g_f|<1$, hard-clamp buffer while tuning, verify impulse decays < −60 dB.
4. **Chorus "metallic" from synchronized LFOs** → phase-spread $\phi_k = 2\pi k/K$ + rate detune.
5. **Pitch-shift wrap clicks** → dual heads + complementary raised-cosine crossfade.
6. **Bass mud/phase cancellation** → high-pass the send below ~150 Hz or keep bass dry.
7. **Per-sample Python loop too slow** → Numba JIT / vectorize / precompute modulation.
8. **Stateful buffer → unpredictable joins** → per-section buffer fade ("dump") for clean breaks.

---

## References

- Dattorro, J. (1997). "Effect Design, Part 2: Delay-Line Modulation and Chorus." *Journal of the Audio Engineering Society* 45(10), 768–788.
- Laakso, T. I., Välimäki, V., Karjalainen, M., & Laine, U. K. (1996). "Splitting the unit delay — Tools for fractional delay filter design." *IEEE Signal Processing Magazine* 13(1), 30–60.
- Smith, J. O. (2010). *Physical Audio Signal Processing.* W3K Publishing. (Delay-line interpolation chapter.)
- Välimäki, V., & Väänänen, A. (2012). "Fifty years of artificial reverberation." *IEEE Transactions on Audio, Speech, and Language Processing* 20(5), 1421–1444.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects.* 2nd ed., Wiley.
