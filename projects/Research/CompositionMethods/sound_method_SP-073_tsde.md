# SP-073 — Transient Shaping via Differential Envelope Processing (TSDE)

**Layer:** absolute (sound production)
**Category:** Post-Processing / DSP
**Target output:** Transient/Punch & Sustain Shaping (Level-Independent Dynamics)
**Complexity:** $O(1)$ per sample per channel (two one-pole smoothers + one multiply); fully deterministic (no RNG) → zero-drift gate passes trivially.

---

## One-line description

Reshapes the attack/sustain balance of a rendered audio buffer by riding a time-varying gain derived from *two parallel one-pole envelope followers* — a fast peak detector (tracks the transient leading edge) and a slow sustain detector (tracks the steady body). The *difference* between them is the transient content, boosted or attenuated independently by an **Attack** gain and a **Sustain** gain, then recombined into a single gain applied to the original signal. No threshold, no ratio, level-independent — the SPL Transient Designer differential-envelope technique.

## Source

- **SPL Transient Designer** (1998), SPL electronics GmbH — the first dedicated hardware transient shaper and the canonical reference. Its "Differential Envelope Technology (DET)" whitepaper/patent describes the dual-envelope-follower difference scheme.
- **Blesser, B. (1969).** "Audio Dynamic Range Compression for Minimum Perceived Distortion." *IEEE Trans. Audio and Electroacoustics* AU-17(1), 22–32. The envelope-follower/level-detector theory base.
- **Giannoulis, D., Massberg, M., & Reiss, J. D. (2012).** "Digital Dynamic Range Compressor Design — A Tutorial and Analysis." *J. Audio Eng. Soc.* 60(6), 399–408. The one-pole peak/RMS envelope-follower with attack/release coefficients used here.
- **Zölzer, U. (2011).** *DAFX: Digital Audio Effects*, 2nd ed., Wiley. Ch. on dynamics processing (envelope followers, level detection).
- **Rösel, J. / SPL.** "Transient Designer" product literature — the Attack/Sustain two-knob paradigm (level-independent, threshold-free).

## Technical mechanics (extended)

### 1. Input

Rendered mono or stereo buffer $x[n]$, sample rate $f_s$.

### 2. Dual envelope followers

A one-pole envelope follower with separate attack and release coefficients tracks the instantaneous magnitude:

$$E[n]=\alpha\,|x[n]|+(1-\alpha)\,E[n-1],\qquad \alpha=\begin{cases}\alpha_a,& |x[n]|>E[n-1]\\ \alpha_r,& \text{otherwise}\end{cases}$$

The coefficient derives from a time constant $\tau$ (seconds) via

$$\alpha = 1 - e^{-1/(\tau f_s)}.$$

Two followers run in parallel:

| Follower | Attack $\tau_a$ | Release $\tau_r$ | Role |
|---|---|---|---|
| **Fast peak** $E_f$ | 1–5 ms | 30–80 ms | rides the transient leading edge, decays quickly |
| **Slow sustain** $E_s$ | 20–60 ms | 300–800 ms | rides the steady body, ignores the brief attack |

The slow follower may use an RMS smooth instead of $|x[n]|$ (compute a running mean of $x^2[n]$, then $\sqrt{\cdot}$), which tracks perceived loudness better than peak for the body.

### 3. Differential decomposition

The transient content is the fast envelope's excess over the slow envelope, clamped non-negative so the gain never dips below the body:

$$T[n]=\max\!\big(0,\; E_f[n]-E_s[n]\big),\qquad B[n]=E_s[n].$$

The instantaneous level is thus approximated as a *sustain body* $B[n]$ plus a *transient excess* $T[n]$. The normalized transient mix is

$$m[n]=\frac{T[n]}{T[n]+B[n]+\varepsilon},\qquad \varepsilon=10^{-6}.$$

$m[n]\in[0,1]$ is the fraction of the instantaneous level attributable to the transient; it is $\approx 1$ at a sharp onset and $\approx 0$ in the steady body.

### 4. Gain riding

With **Attack** gain $A$ and **Sustain** gain $S$ (both $\ge 0$, unity = neutral):

$$g[n]=A\,m[n]+S\big(1-m[n]\big)=S+(A-S)\,m[n].$$

The output is a pure level rescalement of the input, then optionally soft-limited:

$$y[n]=x[n]\,g[n],\qquad y[n]\leftarrow \tanh\big(\gamma\,y[n]\big)/\tanh(\gamma).$$

Interpretation table:

| $A$ | $S$ | Effect |
|---|---|---|
| $>1$ | $1$ | transient excess boosted → sharper, punchier attacks (kick "smack", pluck "snap") |
| $<1$ | $1$ | transients pulled down → notes round off, drums soften toward a pad-like wash |
| $1$ | $>1$ | sustained body raised → longer, fuller decay/ring; pads and held chords bloom |
| $1$ | $<1$ | body lowered between onsets → signal tightens and "gates" |

### 5. Smoothing & make-up

The per-sample gain $g[n]$ is lowpass-filtered (one-pole, $\tau\approx 5$ ms) to remove zipper noise, then a make-up gain (or post-limiter, SP-008 DRC) compensates the level so the transform reads as a *shape* change, not a loudness change. An optional look-ahead delay (2–5 ms) lets $E_f$ settle on a full attack before the gain is applied — a "true zero-attack" response.

### 6. Complexity

Two one-pole smoothers + one multiply per sample per channel = $O(1)$ per sample, no FFT, no sidechain, no lookahead buffer (unless the optional delay is used), fully deterministic. **Parallel-processing variant:** split the signal into transient and sustain *audio* components, $x_T[n]=x[n]\,m[n]$ and $x_S[n]=x[n](1-m[n])$, process each through its own FX chain (transient → SP-062 ADAA saturation, sustain → SP-008 compression/expansion), then re-sum — "parallel transient design."

## Python/NumPy implementation sketch

```python
import numpy as np

def envelope_follower(x, tau_a, tau_r, fs, rms=False):
    """One-pole peak (or RMS) envelope follower with attack/release."""
    a = 1.0 - np.exp(-1.0 / (tau_a * fs))
    r = 1.0 - np.exp(-1.0 / (tau_r * fs))
    if rms:
        x = np.sqrt(np.convolve(x ** 2, np.ones(32) / 32, mode="same"))  # ~RMS
    E = np.empty_like(x)
    e = 0.0
    for i, v in enumerate(np.abs(x)):
        c = a if v > e else r
        e = c * v + (1.0 - c) * e
        E[i] = e
    return E


def one_pole_lp(x, tau, fs):
    a = 1.0 - np.exp(-1.0 / (tau * fs))
    y = np.empty_like(x)
    s = 0.0
    for i, v in enumerate(x):
        s += a * (v - s)
        y[i] = s
    return y


def transient_shape(x, fs, attack=1.0, sustain=1.0,
                    tau_fa=0.003, tau_fr=0.05,
                    tau_sa=0.04,  tau_sr=0.5,
                    makeup=1.0, lookahead_ms=0.0, eps=1e-6):
    """SP-073: differential-envelope transient shaping."""
    Ef = envelope_follower(x, tau_fa, tau_fr, fs)      # fast peak
    Es = envelope_follower(x, tau_sa, tau_sr, fs, rms=True)  # slow sustain
    T = np.maximum(0.0, Ef - Es)                        # transient excess
    m = T / (T + Es + eps)                              # normalized transient mix
    g = sustain + (attack - sustain) * m                # ride gain
    g = one_pole_lp(g, 0.005, fs)                       # de-zipper
    if lookahead_ms > 0:
        d = int(fs * lookahead_ms / 1000)
        g = np.roll(g, d); g[:d] = g[d]                 # crude lookahead
    y = x * g * makeup
    y = np.tanh(1.5 * y) / np.tanh(1.5)                 # soft-limit
    return y


if __name__ == "__main__":
    fs = 44100
    t = np.arange(fs)
    # synthetic pluck: sharp attack + exponential decay body
    x = np.exp(-t / 3000) * np.sin(2 * np.pi * 440 * t / fs)
    x[:100] *= np.linspace(0, 1, 100) ** 2
    y = transient_shape(x, fs, attack=2.0, sustain=0.8)  # punchier, tighter
    print(f"peak in : {np.abs(x).max():.3f}   peak out: {np.abs(y).max():.3f}")
```

**Note:** the Musicom one-ENV contract requires all composition work to route through the `musicom` engine (`UnitMatrixComposer` / `produce()`), never raw NumPy event loops for MIDI authoring. This TSDE processor belongs in `sound/effects/transient_shaper.py` as a *render-stage* effect applied to buffers produced by `produce()`, mirroring the existing `sound/effects/` modules.

## Candidate code path

`sound/effects/transient_shaper.py` — new module, sibling to the existing dynamics processors (`overlap_comp.py`, `production_chain.py`, `mastering.py`, `multiband.py`) and spectral processors (`phase_vocoder.py`, `spectral_gate.py`). Reuses the one-pole envelope-follower logic already present in the compressor chain. Signature: `transient_shape(x, fs, attack=1.0, sustain=1.0, ...) -> np.ndarray`.

## References

- SPL electronics GmbH (1998). *Transient Designer* — Differential Envelope Technology (DET). https://spl.audio
- Blesser, B. (1969). "Audio Dynamic Range Compression for Minimum Perceived Distortion." *IEEE Trans. AU-17(1)*, 22–32.
- Giannoulis, D., Massberg, M., & Reiss, J. D. (2012). "Digital Dynamic Range Compressor Design — A Tutorial and Analysis." *J. Audio Eng. Soc.* 60(6), 399–408.
- Zölzer, U. (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley.
