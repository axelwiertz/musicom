# Frequency Shifting via Hilbert Transform (FSHT) — Method SP-055

> **Layer**: Post-Processing / DSP · **Target**: Metallic / Inharmonic / Barberpole Timbres
> **One-liner**: Adds a constant offset $\Delta f$ (Hz) to *every* spectral component via the analytic-signal (Hilbert) phasing method — the only transform in the Musicom catalog that shifts frequency *additively* rather than multiplicatively, turning harmonic spectra into inharmonic bell/gong/glass timbres.

---

## 1. Core Idea

A **frequency shifter** translates the whole spectrum by a constant amount:

$$f_k \;\to\; f_k + \Delta f$$

- **Not** pitch shifting (which *multiplies*: $f_k \to r f_k$, preserving harmonic ratios).
- **Not** ring modulation (which yields *both* sum and difference sidebands: $X(\omega-\omega_c)+X(\omega+\omega_c)$).
- **Exactly one sideband**: $Y(\omega)=X(\omega - 2\pi\Delta f)$, with no mirror image.

Because the shift is additive, a harmonic series $f_0, 2f_0, 3f_0,\dots$ becomes $f_0+\Delta f,\ 2f_0+\Delta f,\ 3f_0+\Delta f,\dots$, which is **inharmonic** unless $\Delta f$ is an integer multiple of $f_0$. The partials no longer share a fundamental; the timbre acquires a metallic, ringing, "wrong" quality while the temporal envelope stays intact.

---

## 2. Mathematical Mechanics

### 2.1 Analytic signal (Hilbert transform)

The analytic (pre-envelope) signal of a real $x(t)$:

$$x_a(t) = x(t) + i\,\hat{x}(t), \qquad \hat{x}(t) = \mathcal{H}\{x\}(t) = \frac{1}{\pi}\,\mathrm{p.v.}\!\int_{-\infty}^{+\infty}\frac{x(\tau)}{t-\tau}\,d\tau$$

The analytic signal is one-sided in frequency: $X_a(\omega)=0$ for $\omega<0$, and $X_a(\omega)=2X(\omega)$ for $\omega>0$.

### 2.2 One-sided shift (Weaver/phasing modulator)

Multiply by a complex exponential at the shift frequency, keep the real part:

$$y(t) = \mathrm{Re}\big\{x_a(t)\,e^{i2\pi\Delta f\,t}\big\} = x(t)\cos(2\pi\Delta f\,t) \;-\; \hat{x}(t)\sin(2\pi\Delta f\,t)$$

The $\hat{x}$-term cancels the mirror image that the cosine-only (ring-mod) multiply would create, leaving:

$$Y(\omega) = X(\omega - 2\pi\Delta f)$$

$\Delta f>0$ moves the spectrum up; $\Delta f<0$ moves it down.

### 2.3 Discrete time

At sample rate $f_s$, with $\Delta\omega = 2\pi\Delta f/f_s$:

$$y[n] = x[n]\cos(\Delta\omega\, n) \;-\; \hat{x}[n]\sin(\Delta\omega\, n)$$

Two ways to compute $\hat{x}[n]$:

- **FIR Hilbert transformer** — ideal taps $h[n]=\frac{2}{\pi n}\sin^2\!\big(\frac{\pi n}{2}\big)$ for odd $n$, $0$ for even $n$, windowed (Hamming/Blackman) to length $M$ (≥127). Exact in the band $\omega\in(0,\pi)$; poor near DC and Nyquist.
- **FFT analytic signal** — $Z[k]=X[k](1+\operatorname{sgn}(k))$, then $x_a[n]=\mathrm{IFFT}\{Z[k]\}$. Exact circular Hilbert over the block; use windowed overlap-add to avoid edge artifacts.

The complex-exponential multiply is **bin-exact for arbitrary continuous $\Delta\omega$** — the spectrum lands at non-integer bin positions with no quantization, making the frequency shifter a *continuous* (non-chromatic) spectral transform.

### 2.4 Feedback / barberpole extension

$$y[n] = x[n] + g\,y[n-D] \quad\Rightarrow\quad \text{each pass through the loop shifts every partial by another }\Delta f$$

With $\Delta f$ small and $g\to1$, recirculating partials climb (or fall) forever — the Shepard-tone / barberpole illusion; at Nyquist they fold and re-enter as fresh low partials.

**Complexity**: FFT method $O(N\log N)$/block; FIR method $O(NM)$; feedback $O(N)$. Memory $O(N)+O(M)$.

---

## 3. Implementation Sketch (Python / NumPy)

```python
import numpy as np

def hilbert_fir(M=127):
    """Windowed FIR Hilbert transformer (type III, anti-symmetric)."""
    n = np.arange(-(M//2), M//2 + 1)
    h = np.zeros_like(n, dtype=float)
    odd = (n % 2) != 0
    h[odd] = 2.0 / (np.pi * n[odd])          # sin^2(pi n / 2) == 1 for odd n
    w = np.hamming(M)
    return h * w

def analytic_fft(x):
    """One-sided analytic signal via FFT (exact circular Hilbert)."""
    N = len(x)
    X = np.fft.rfft(x)
    Z = np.empty_like(X)
    Z[0]  = X[0]                 # DC
    Z[1:-1] = 2.0 * X[1:-1]      # double positive freqs (drop negative)
    Z[-1] = X[-1]                # Nyquist (real)
    return np.fft.irfft(Z, n=N)

def frequency_shift(x, delta_f, fs, method="fft", M=127):
    """Shift the entire spectrum of x by delta_f Hz (additive, one-sided)."""
    dw = 2.0 * np.pi * delta_f / fs
    n = np.arange(len(x))
    if method == "fft":
        xh = analytic_fft(x).imag
    else:
        xh = np.convolve(x, hilbert_fir(M), mode="same")
    return x * np.cos(dw * n) - xh * np.sin(dw * n)

def barberpole_shift(x, delta_f, fs, delay, g=0.8, method="fft"):
    """Shift + feedback delay -> endlessly rising/falling sheen."""
    y = np.zeros_like(x)
    for i in range(len(x)):
        fb = g * y[i - delay] if i >= delay else 0.0
        y[i] = x[i] + fb
    return frequency_shift(y, delta_f, fs, method=method)
```

Vectorize the feedback loop with `scipy.signal.lfilter([1],[1, 0, ..., -g], x)` for production.

**Dependencies**: NumPy (FFT/convolve), SciPy (windows, lfilter). No external engines needed — consumes a rendered mono buffer per voice.

---

## 4. Musical Elements Framework

- **PITCH** — the defining element. Additive shift detunes every partial by the *same Hz*, breaking partial ratios: a pure sine becomes a sine at exactly $f_0+\Delta f$; a harmonic series becomes inharmonic; chord pitch-classes slide off equal temperament. The only additive-frequency transform in the catalog — a "wrong", bell-like, glassy pitch that no pitch shifter can produce.
- **RHYTHM** — static shift leaves timing intact; time-varying $\Delta f(t)$ couples pitch to rhythm (vibrato/detune LFO, per-onset Hz bends). Feedback delay $D$ imposes a detuned echo grid: repeat $k$ drifts by $k\Delta f$.
- **HARMONY** — destroys tonal gravity by design. Replace HOME/LIFT/TENSE/TURN with *spectral tension*: small $\Delta f$ vs. a reference = beating/roughness; large $\Delta f$ = inharmonic "noise-pitch". Use on one voice for timbral separation, or on all for atonal/metallic color.
- **STRUCTURE** — macro-form = the $\Delta f(t)$ automation curve. Sections prescribe shift regimes (A = small +, B = large −, C = barberpole ascent, recap = reference detune). A monotonic 0→large ramp is a cadence-free structural gesture no pitch shifter can mimic.
- **TEXTURE** — barberpole feedback + cascaded shifts give *spectral sheen*: dense, ever-rising shimmer, partials individually audible but collectively unresolved. Per-voice different $\Delta f$ = stratified spectral bands; tiny global $\Delta f$ = chorus-like detune.

---

## 5. UnitMatrix Integration

- **Rows (Voices)** $v$: each voice rendered mono → its own FSHT with $\Delta f_v$. Lead = small +Δf (bright edge); Bass = −Δf (darken/sub-shift); Pad = LFO-driven Δf (shimmer); Percussion = large Δf (gong/bell hits).
- **Columns (Sections)** $s$: shift recipe per section = timbral macro-form (A reference / B barberpole rise / C deep negative collapse); joins are hard Δf switches or crossfades.
- **Cells** $U_{v,s}$:
  - `{PITCH}`: $\Delta f_{v,s}$ (Hz) — additive displacement.
  - `{HARMONY}`: inharmonicity ratio $|\Delta f|/f_0$ — spectral-tension knob.
  - `{RHYTHM}`: Δf envelope (attack/release bend) + feedback delay $D$.
  - `{TEXTURE}`: feedback gain $g$ + cascade depth — sheen thickness.
- **Flow**: compose+validate UnitMatrix → export MIDI → render mono (SP-001..SP-042) → apply FSHT per cell/section → sum → EQ/DRC (SP-007/008) → spatialize (SP-021/034/043).

---

## 6. Pitfalls

1. **Negative-frequency fold** (down-shift past DC) → partials mirror back up; deliberate barberpole, or a bug. Keep $|\Delta f|<f_{min}$ for clean down-shift.
2. **FIR band-limiting** → short filter inaccurate near DC/Nyquist, leaves mirror sideband. Use $M\ge127$ windowed, or FFT method.
3. **DC offset → audible tone at Δf**. DC-remove the input first.
4. **Ring-mod bleed** (omitting the Hilbert branch) → double sidebands. Always compute the full analytic pair; verify with a single sine → single output peak.
5. **FFT block artifacts** → circular Hilbert leaks at block edges. Window + overlap-add, or use FIR.
6. **Inharmonicity ≠ transposition** → FSHT breaks ratios; use SP-026/037/039 for key changes.
7. **Feedback blow-up** → clamp $g\le0.9$, damping LPF in feedback, limiter (SP-008) downstream.
8. **Stereo cue detune** → shift mono sources *before* spatialization, not after.
9. **Slow Python loop** → vectorize feedback with `lfilter`, JIT with Numba.

---

## 7. Comparison

| Method | Spectrum op | Sidebands | Harmonic ratios | Timbre |
|---|---|---|---|---|
| Pitch shift (SP-026/037/039) | $f_k \to r f_k$ | none | preserved | transposed |
| Ring modulation | sum + diff | both | broken (sum) | metallic |
| FM/PM (SP-010/017) | phase sidebands | many ($J_n(\beta)$) | depends on $c{:}m$ | bell/brass |
| **FSHT (SP-055)** | **$f_k \to f_k+\Delta f$** | **single** | **broken (additive)** | **metallic/barberpole** |

---

## 8. References

- Weaver, D. K. (1956). "A Third Method of Generation and Detection of Single-Sideband Signals." *Proc. IRE* 44(12).
- Dugundji, J. (1958). "Envelopes and Pre-Envelopes of Real Waveforms." *IRE Trans. Info. Theory* 4(1).
- Bode, H. (1961). *Frequency Shifter* (Model 1630), Bode Sound Co. / Moog (735).
- Stockhausen, K. (1965–70). *Mikrophonie II*, *Mixtur*, *Mantra* — Klangumwandler metallic timbres.
- Shepard, R. N. (1964). "Circularity in Judgments of Relative Pitch." *JASA* 36(12).
- Smith, J. O. (2007). "Analytic Signals and Hilbert Transform Filters," *Mathematics of the DFT*, 2nd ed., W3K.
- Zölzer, U. (2011). *DAFX: Digital Audio Effects*, 2nd ed., Wiley.
