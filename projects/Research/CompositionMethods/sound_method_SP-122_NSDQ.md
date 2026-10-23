# SP-122 — Noise-Shaped Dither Quantization (NSDQ)

**ID:** SP-122
**Layer:** absolute — sound production (Post-Processing / DSP)
**Category:** terminal render stage (bit-depth reduction to the delivery format)
**Candidate code path:** `sound/render/dither.py`
**Pipeline hook:** last transform in `sound/render/pipeline.py`, after `sound/effects/mastering.py` (SP-107), before the WAV/OGG/Opus write
**Produce dispatch:** `workflows.musicom_workflow.produce(method="SP-122")`
**One-line:** Adds TPDF dither ($\pm1$ LSB, $\sigma^2=\Delta^2/6$) before mid-tread requantization and filters the resulting quantization error through an error-feedback noise shaper $\mathrm{NTF}(z)=1-H(z)$ designed by inverse-ATH weighted least squares — the signal passes bit-exact, only the error floor is sculpted out of the 2–4 kHz hearing peak.

---

## 1. Overview

Every other method in this catalogue produces float samples. NSDQ is the stage that makes them *deliverable*: it reduces the mix to $b$ bits (16 for CD/DDP/streaming sources, 24 for masters) without converting the quantization error into distortion.

Two mechanisms, applied in that order:

1. **Dither** — add noise before quantizing, so the error becomes a random variable instead of a deterministic function of the signal. Triangular PDF (the sum of two rectangular PDFs) is the standard because it makes *both* the first and second moments of the total error signal-independent: no harmonic distortion, and no "noise modulation" (the pumping noise floor you get with rectangular dither).
2. **Noise shaping** — put the quantization error in a feedback loop so the *error* is filtered while the *signal* is not:
   $$w[n]=x[n]-\sum_{k=1}^{K}h_k e[n-k],\qquad y[n]=Q(w[n]),\qquad e[n]=y[n]-w[n]$$
   $$\Longrightarrow\quad Y(z)=X(z)+\big(1-H(z)\big)E(z)=X(z)+\mathrm{NTF}(z)E(z)$$

The point is the unity signal path: shaping costs nothing in amplitude or phase, only in *headroom* (the peak of $|\mathrm{NTF}|$). Design the NTF against the absolute threshold of hearing and the noise floor can be pushed below the threshold where the ear is most sensitive — 2–4 kHz — and dumped where it is not: below ~100 Hz and above ~16 kHz.

Why this is a missing method rather than a footnote to an existing one:

| Existing | What it does | Why NSDQ is different |
| --- | --- | --- |
| **SP-104 SRR** (bitcrush) | reduces bits/rate *as an effect* | inverse intent; dither optional, **no shaping filter at all** |
| **SP-107 LBL** | controls peak level | NSDQ controls the *spectrum of the error floor*, not the peak |
| **SP-008 DRC** | controls dynamic range | NSDQ does not change level; it changes where the floor sits |
| **SP-114 SDCX** | per-band dynamics on the *signal* | NSDQ filters only the *error*; signal path is unity |
| **SP-109 SG-ANR** | removes noise | NSDQ deliberately injects a precisely sculpted floor |
| **SP-049/088** (tape) | nonlinear saturation | both add noise, but tape noise is signal-modulated and unshaped |

No SP method owned the noise transfer function of the render, so the catalogue had no defined exit from float to integer delivery.

---

## 2. History & Sources

- **Roberts, L. G. (1962).** "Picture Coding Using Pseudo-Random Noise." *IRE Trans. Information Theory* 8(2), 145–154. (MIT master's thesis, 1961.) First formal dithering of a quantizer.
- **Vanderkooy, J. & Lipshitz, S. P. (1987).** "Dither in Digital Audio." *J. Audio Eng. Soc.* 35(12), 966–975. Dither *linearizes* the quantizer; the required amplitude depends on the PDF, not only the variance.
- **Gerzon, M. A. & Craven, P. G. (1989).** "Optimal Noise Shaping and Dither of Digital Signals." *AES 87th Convention*, Preprint 2822. Masking-weighted NTF optimisation; the "perceptually ~20 bits from 16" claim.
- **Lipshitz, S. P., Wannamaker, R. A. & Vanderkooy, J. (1991).** "Quantization and Dither: A Theoretical Survey." *J. Audio Eng. Soc.* 39(5), 355–375. The canonical taxonomy; proves TPDF is the minimum-power dither removing distortion *and* noise modulation.
- **Wannamaker, R. A. (1992).** "Psychoacoustically Optimal Noise Shaping." *J. Audio Eng. Soc.* 40(7/8), 611–620. The weighted-least-squares design used in §3.5.
- **Wannamaker, R. A., Lipshitz, S. P. & Vanderkooy, J. (1993).** "Dithered Quantizers with and without Feedback." *Proc. IEEE WASPAA*, 140–143. DOI: 10.1109/aspaa.1993.379977. Error-feedback quantizer theory / NTF formulation.
- **Wannamaker, R. A., Lipshitz, S. P., Vanderkooy, J. & Wright, J. N. (2000).** "A Theory of Nonsubtractive Dither." *IEEE Trans. Signal Processing* 48(2), 499–516. DOI: 10.1109/78.823976. Complete moment theory.
- **Terhardt, E. (1979).** "Calculating the Absolute Threshold of Hearing." *Hearing Research* 1(2), 155–156. Analytic ATH curve used as the weighting.
- **SoX `src/dither.c`, `src/dither.h`** (Rob Sykes, 2008–09). Reference open implementation: `lipshitz` (5-tap FIR @44.1 kHz, 2.10 dB headroom), `f-weighted` / `modified-e-weighted` / `improved-e-weighted` (9-tap FIR), `gesemann` (4th-order IIR), `shibata` (20-tap FIR @44.1 kHz, 3.33 dB headroom), `low-shibata`, `high-shibata`. Verified from source 2026-10-23 — the FIR path is exactly $w=x-\sum h_k e[n-k]$; TPDF is the sum of two LCG draws, with a high-pass variant `r[n]-r[n-1]`.
- **Wikipedia: "Dither", "Noise shaping", "Quantization (signal processing)"** (fetched 2026-10-23) — TPDF from two RPDF, in-loop vs out-of-loop dither, WLS design with $W(f)=1/A(f)$, ~4 bits perceived, $\mathrm{SQNR}=1.761+6.02Q$.

---

## 3. Technical Mechanics (full)

### 3.1 The quantizer

Mid-tread (has a true zero — required for silence), $b$ bits, full scale $\pm1$:

$$\Delta = 2^{1-b},\qquad Q(x)=\Delta\cdot\mathrm{round}\!\left(\frac{x}{\Delta}\right),\qquad e[n]=Q(x[n])-x[n]\in\left[-\tfrac{\Delta}{2},\tfrac{\Delta}{2}\right]$$

16-bit $\Rightarrow \Delta = 2^{-15} = 3.052\times10^{-5}$, noise RMS $\Delta/\sqrt{12}=8.81\times10^{-6}=-101.1$ dBFS, $\mathrm{SQNR}=1.761+6.02b=98.1$ dB (full-scale sine).

Undithered, the error is a *deterministic function of the input*: for a periodic signal it is periodic (harmonic distortion), for a swept signal it is a chirping spray, for a slowly decaying signal it is granular grit. That is the whole problem.

### 3.2 Dither PDFs and the total error

Let $u_1,u_2\sim\mathcal{U}[0,\Delta)$ independent.

$$\text{RPDF: } d=u_1-\tfrac{\Delta}{2},\quad \sigma_d^2=\tfrac{\Delta^2}{12}\qquad
\text{TPDF: } d=u_1+u_2-\Delta\sim\triangle(-\Delta,+\Delta),\quad \sigma_d^2=\tfrac{\Delta^2}{6}$$

Dither + quantization error, independent:

$$\sigma_{\text{tot}}^2=\frac{\Delta^2}{6}+\frac{\Delta^2}{12}=\frac{\Delta^2}{4}
\quad\Longrightarrow\quad \sigma_{\text{tot}}=\frac{\Delta}{2},\qquad
\mathrm{SQNR}=6.02b-3.01\ \mathrm{dB}$$

The floor rises $10\log_{10}3 = 4.77$ dB. That is the price of linearization, and it is the cheapest trade in audio.

Why TPDF specifically: the $k$-th moment of the total error is a function of the *characteristic function* of the dither PDF at multiples of $2\pi/\Delta$. RPDF nulls the first moment only (distortion gone, **noise modulation remains** — the floor still breathes with the signal). TPDF nulls the first *and* second moments, so the noise is stationary.

**High-pass TPDF.** $d[n]=r[n]-r[n-1]$ with $r$ iid RPDF is TPDF with PSD scaled by $|1-e^{-j\omega}|^2=4\sin^2(\omega/2)$: a null at DC, +6 dB/oct rise. Kills residual DC/rumble (SoX `-a`), costs ~3 dB more in-band noise.

### 3.3 Noise shaping algebra

$$w[n]=x[n]-\sum_{k=1}^{K}h_k e[n-k],\qquad y[n]=Q(w[n]),\qquad e[n]=y[n]-w[n]$$

$z$-transform, eliminating $w$:

$$Y=X-H E+E \quad\Longrightarrow\quad \boxed{Y(z)=X(z)+\big(1-H(z)\big)E(z)}$$

$$\mathrm{NTF}(z)=1-\sum_{k=1}^{K}h_k z^{-k}\quad(\text{monic, }\mathrm{NTF}(\infty)=1)$$

Consequences:

- **Signal path is unity** — no amplitude, phase or timbre change. Shaping is free in the signal domain.
- **Stability is trivial.** $e[n]$ is the quantization error of $w$, hence $|e[n]|\le\Delta/2$ *by definition*; the FIR feedback state is therefore bounded for any $h$. Contrast a $\Delta\Sigma$ modulator, which feeds $y$ back around the quantizer and can oscillate.
- **Cost is headroom.** Total noise power is amplified by $\max_\omega|\mathrm{NTF}|$; a $K$-th-order differentiator $\mathrm{NTF}=(1-z^{-1})^{K}$ peaks at $2^{K}$ ($6.02K$ dB) at Nyquist.
- **DC.** $\mathrm{NTF}(1)=1-\sum_k h_k$; if that is small, DC/low-frequency noise is boosted. Enforce $\sum_k h_k=0$ (Lagrange multiplier, or an infinite weight at $\omega=0$) to keep $\mathrm{NTF}(\text{DC})=1$.

### 3.4 What the ear wants

Weight by the inverse absolute threshold of hearing (Terhardt 1979, $f$ in kHz):

$$A(f)=3.64f^{-0.8}-6.5e^{-0.6(f-3.3)^2}+10^{-3}f^{4}\ \ \mathrm{dB\,SPL},\qquad W(f)=\frac{1}{10^{A(f)/10}}$$

$W$ is large near 3–4 kHz (quiet threshold) and tiny below 100 Hz and above 16 kHz. Minimising $\int W|\mathrm{NTF}|^{2}$ therefore *pushes* noise to the frequency extremes — exactly the desired direction.

### 3.5 Filter design — weighted least squares

$$\min_{h}\ J(h)=\frac{1}{2\pi}\int_{-\pi}^{\pi}W(\omega)\Big|1-\sum_{k=1}^{K}h_ke^{-j\omega k}\Big|^{2}d\omega$$

Expand: $|1-H|^{2}=1-2\sum_k h_k\cos k\omega+\sum_{k}\sum_{l}h_kh_l\cos((k-l)\omega)$. With the weighted autocorrelation

$$R(m)=\frac{1}{2\pi}\int_{-\pi}^{\pi}W(\omega)\cos(m\omega)\,d\omega$$

$\partial J/\partial h_m=0$ gives the **Toeplitz normal equations**:

$$\sum_{k=1}^{K}h_k\,R(m-k)=R(m),\qquad m=1,\dots,K$$

$O(K^2)$ by Levinson; convex, so the design is deterministic and needs no tuning. $R(m)$ is just the inverse DFT of the sampled weight — the whole design is *one IFFT and one linear solve*.

**Practical regularisation.** Because $A(f)$ extrapolates to >200 dB above 20 kHz, the pure inverse-ATH weight happily buys audible quiet with 35–40 dB of ultrasonic gain. Add a flat term:

$$W_{\text{eff}}(f)=W(f)+\beta\cdot\max_f W(f)$$

$\beta=0$ → deepest null, largest peak; $\beta=1$ → flat weight, i.e. no shaping. Production curves are the regularised end of this family (Lipshitz 2.10 dB, Shibata 3.33 dB of headroom).

### 3.6 Measured (this implementation, 44.1 kHz, 16-bit, $K=9$)

$-60$ dBFS 997 Hz sine, amplitude 32.8 LSB:

| $\beta_{\text{rel}}$ | $\max|\mathrm{NTF}|$ | @1 kHz | @3 kHz | audible noise (20 Hz–12 kHz) vs undithered |
| --- | --- | --- | --- | --- |
| 0 | +38.60 dB | −23.21 dB | −32.71 dB | **−12.85 dB** |
| $10^{-4}$ | +18.35 dB | −13.56 dB | −22.66 dB | −2.32 dB |
| $10^{-3}$ | +12.00 dB | −9.16 dB | −18.86 dB | +0.50 dB |
| $10^{-2}$ | +6.63 dB | −4.95 dB | −13.81 dB | +2.30 dB |
| $10^{-1}$ | +2.39 dB | −1.02 dB | −7.86 dB | +3.70 dB |
| 1 | +0.51 dB | +0.02 dB | −2.10 dB | +4.48 dB (= plain TPDF) |

Error statistics and spurs:

```
LSB = 3.052e-05   signal amplitude = 32.8 LSB (-60 dBFS)

undithered          spur -53.47 dBc @ 18109 Hz   err RMS 0.293 LSB
TPDF                spur -63.19 dBc @ 12482 Hz   err RMS 0.500 LSB
TPDF high-pass      spur -62.37 dBc @ 15478 Hz   err RMS 0.499 LSB
TPDF + shaped K=9   spur -58.08 dBc @ 18671 Hz   err RMS 0.747 LSB

sample count preserved = True | deterministic (same seed) = True | different seeds differ = True
```

Two things to read off this: (i) undithered RMS $0.293$ LSB and TPDF $0.500$ LSB match $\Delta/\sqrt{12}$ and $\Delta/2$ exactly — the theory is numerically correct; (ii) shaping does *not* reduce total error RMS (it rises, 0.5 → 0.75 LSB, because noise moves to the extremes) — it reduces *audible* error. Judging a shaper by RMS is the classic mistake.

### 3.7 Relation to $\Delta\Sigma$ and DSD

The same $\mathrm{NTF}$ lives inside a $\Delta\Sigma$ modulator with oversampling $R$:

$$\mathrm{SQNR}\approx 6.02b+1.76-5.17+30\log_{10}R\quad(\text{2nd order})$$

DSD is the $b=1$, $R=64$ corner. NSDQ is the *non-oversampled* case: no loop instability, no rate conversion, just a $K$-tap FIR on the error — which is why it is the right tool at the render stage while $\Delta\Sigma$ belongs in the converter.

### 3.8 Verification chain

1. $-60$ dBFS 997 Hz sine in, THD+N out: undithered shows a harmonic series; TPDF shows a flat floor; shaped shows a floor whose slope matches $20\log_{10}|\mathrm{NTF}|$.
2. Silence in, FFT the output: the noise must equal $|\mathrm{NTF}|^{2}\cdot\Delta^{2}/12$ bin by bin.
3. Assert $|\bar y|<0.05\Delta$ (no DC) and `out.size == in.size` (zero-drift invariant).

---

## 4. Implementation (Python/NumPy)

The error-feedback loop is inherently sequential (one sample at a time); everything *around* it is vectorised. This is the code that produced the numbers in §3.6 (reduced to essentials).

```python
import numpy as np

FS, BITS = 44100, 16
LSB = 2.0 ** (1 - BITS)                      # full scale +-1  ->  2^-15


def ath_db(f):
    """Terhardt (1979) absolute threshold of hearing, dB SPL. f in Hz."""
    fk = np.maximum(f, 1e-3) / 1000.0
    return (3.64 * fk ** -0.8
            - 6.5 * np.exp(-0.6 * (fk - 3.3) ** 2)
            + 1e-3 * fk ** 4)


def design_ntf(K=9, beta_rel=1e-1, nfft=1 << 15):
    """WLS noise-shaping taps:  min_h int W |1 - sum h_k e^{-jwk}|^2 dw.

    Normal equations:  sum_k h_k R(m-k) = R(m),  R(m) = IFFT(W)[m]
    """
    f = np.fft.rfftfreq(nfft, 1.0 / FS)
    W = 10.0 ** (-ath_db(f) / 10.0)
    W = W + beta_rel * W.max()               # regulariser: caps the HF peak
    w_full = np.concatenate([W, W[-2:0:-1]])  # symmetric spectrum -> real R
    r = np.fft.ifft(w_full).real[: K + 1]     # lags 0..K
    R = np.array([[r[abs(m - k)] for k in range(1, K + 1)]
                  for m in range(1, K + 1)])
    return np.linalg.solve(R, r[1:K + 1])


def nsdq(x, bits=BITS, h=None, seed=0, hp_dither=False):
    """TPDF dither + mid-tread requantization + error-feedback noise shaping."""
    d_lsb = 2.0 ** (1 - bits)
    rng = np.random.default_rng(seed)
    n, K = x.size, (0 if h is None else len(h))
    y = np.empty(n)
    e_hist = np.zeros(K)
    prev_r = 0.0
    for i in range(n):
        w = x[i] - (h @ e_hist if K else 0.0)
        d = ((rng.random() + rng.random() - 1.0) * d_lsb)      # TPDF +-1 LSB
        q = np.round((w + d) / d_lsb) * d_lsb                  # round-half-away
        e = q - w
        y[i] = q
        if K:
            e_hist[1:] = e_hist[:-1]
            e_hist[0] = e
    return y


if __name__ == "__main__":
    t = np.arange(FS) / FS
    x = 10 ** (-60 / 20) * np.sin(2 * np.pi * 997.0 * t)
    y = nsdq(x, h=design_ntf(K=9, beta_rel=1e-2), seed=1)
    assert y.size == x.size and abs(y.mean()) < 0.05 * LSB
    np.testing.assert_allclose(y, nsdq(x, h=design_ntf(K=9, beta_rel=1e-2), seed=1))
```

Production wiring: the loop must be **stateful across the whole render** (see Pitfall 2), so `nsdq()` is called once per output channel over the complete timeline, with `seed = hash(render_seed, channel)` — never per cell or per stem. If `numba` is available, `@njit` the inner loop; at 44.1 kHz the pure-Python version runs ~1.5× real-time per channel, which is acceptable for offline render and unacceptable for preview.

Equivalent one-liners in the existing toolchain:

```bash
sox in.wav -b 16 out.wav dither -s -f shibata     # SoX, shibata 20-tap FIR
ffmpeg -i in.wav -af "aresample=osf=s16:dither_method=triangular_hp" out.wav
```

---

## 5. Musical Elements Framework

- **PITCH.** NSDQ adds no pitch material, but it decides whether pitch *survives at low level*. Undithered quantization of a quiet note produces error harmonics at $k f_0$ — a spurious octave/fifth series that thickens or skews the perceived pitch. TPDF converts that to noise, so a $-70$ dBFS cor anglais keeps its identity. ATH shaping then removes noise in 2–4 kHz, the band carrying the formants that define instrument identity and vowel colour.
- **RHYTHM.** Correlated error is *rhythm-locked*: the grit repeats at the note rate, so undithered 16-bit renders of tight rhythmic material acquire a faint periodic buzz that is in time with the groove. Dithering decorrelates it. RPDF's noise modulation breathes with the beat (audible pumping behind each kick) — which is precisely why TPDF is mandatory, and why high-pass TPDF (noise pushed above the kick fundamental) is preferred for bass-heavy material.
- **HARMONY.** The deterministic error intermodulates: $|m f_1 \pm n f_2|$ products that belong to no chord. In sustained low-level voicings (organ, strings, choir, just-intonation chords with slow beating) this is audible mud. Linearization removes IMD entirely, so close harmony and slow beating stay clean inside a 16-bit container.
- **STRUCTURE.** Shaping is a *form-level automation target*, not a constant: dense loud sections mask heavily (deeper shaping is free), sparse quiet sections (intro, breakdown, coda, solo) need the gentle curve. Section breakpoints on `shape_strength` / `ntf_family` / `bits` make the noise floor part of the arc.
- **TEXTURE.** This is its real surface. Undithered silence is *grainy*, flat TPDF is *hissy*, ATH-shaped is *velvety*, high-shelf-only is *airy*. Fade-outs, reverb tails, and gaps between phrases are where the floor is exposed, so NSDQ is effectively the "air" control of the entire render — the difference between a master that breathes and one that sizzles.

---

## 6. UnitMatrix Integration

- **Voices = rows.** Rows are summed in float64 **first**; the bus is dithered **once**. Row identity matters only for RNG stream assignment — one decorrelated PRNG stream per (row, channel) — otherwise correlated stereo dither collapses into a phantom-centre noise image (Pitfall 9). If per-voice stems are also delivered, each stem is dithered independently and *not* re-summed afterwards.
- **Sections = columns.** Section-scoped master parameters: `bits`, `shape_strength` (a scalar blending between flat TPDF and the designed NTF), `ntf_family` (`lipshitz` / `shibata` / `wls`), `dither_mode` (`tpdf` / `tpdf_hp`). These interpolate across section boundaries like any other automation — but the *filter state* does not reset there.
- **Cells = MusicUnit.** Cells locate the exposure: rests, gates, fade-ins, seams. Two invariants: (a) the error-feedback state and the RNG are indexed on the **absolute sample counter**, never reset per cell — a reset injects a step into the NTF loop and produces a click + noise burst at every seam; (b) the stage is strictly 1:1 in samples, so the tick↔sample mapping, equal-length rows and the zero-drift gate are untouched (`validate()` still passes, `GOLDEN_SHA256` unchanged for a fixed seed).
- **Produce dispatch.** `workflows.musicom_workflow.produce(method="SP-122")` → `sound/render/dither.py`, invoked as the final transform in `sound/render/pipeline.py`. Deterministic in `(seed, channel, sample_index)`.

---

## 7. Pitfalls

1. **Dither once, at the very end.** Dither → sum → dither again adds a second floor (up to $+4.77$ dB each) plus a second shaped component. $N$ dithered stems summed are $\sim10\log_{10}N$ dB noisier than one dithered mix. Stay in float64 until the single integer write.
2. **Never reset the loop at a musical boundary.** Per-cell or per-section resets of `e_hist` / the RNG are the classic "sample-accurate but audibly broken" bug: a noise transient and a click at every seam, and a broken NTF for the first $K$ samples after each reset.
3. **RPDF is not enough.** It removes distortion but leaves second-moment signal dependence → noise modulation. Use TPDF ($\pm1$ LSB) at the final stage; Gaussian dither needs more power for the same linearization.
4. **Shaping without dither = distortion shaping.** With no dither the "noise" is still signal-correlated error, merely relocated — potentially into a *more* sensitive band. Dither is a precondition for shaping to mean anything.
5. **Shaping filters are rate-specific.** The Lipshitz/Shibata curves are defined at 44.1 kHz; using them at 48 kHz shifts the whole NTF. Resample first, then dither/shape.
6. **Headroom and intersample peaks.** A high-order NTF boosts ultrasonic noise; the boosted signal can exceed full scale after sample-rate conversion or in the DAC's reconstruction filter. Apply the design's gain (3.33 dB for `shibata`) and check **true peak**, not sample peak.
7. **Judging a shaper by RMS.** Shaping *raises* total error power and *lowers* audible power (measured: 0.50 → 0.75 LSB RMS while the 20 Hz–12 kHz band drops). Validate with a weighted/perceptual metric.
8. **Truncation instead of rounding.** `floor`/`int` adds a $-0.5$ LSB DC offset and correlated error. Round half-away-from-zero, and still dither.
9. **Correlated stereo dither.** The same RNG sequence in L and R images the noise at phantom centre, where it localizes and becomes audible. Decorrelate channels (independent streams, or offset the second stream by half a period of the LCG).
10. **Wrong container.** Dithering a float WAV that stays float only adds noise. 24-bit dither is acoustically irrelevant but still correct before further *integer* processing; 16-bit delivery is where the choice is audible.
11. **Ignoring the regulariser.** An unconstrained inverse-ATH design (measured: $+38.6$ dB peak) is unusable — it eats the entire headroom for a null nobody asked for. Cap the peak ($\beta\approx10^{-1}$) and buy the rest with bits.

---

## 8. References

1. Roberts, L. G. (1962). *IRE Trans. Information Theory* 8(2), 145–154.
2. Vanderkooy, J. & Lipshitz, S. P. (1987). *JAES* 35(12), 966–975.
3. Gerzon, M. A. & Craven, P. G. (1989). AES 87th Convention, Preprint 2822.
4. Lipshitz, S. P., Wannamaker, R. A. & Vanderkooy, J. (1991). *JAES* 39(5), 355–375.
5. Wannamaker, R. A. (1992). *JAES* 40(7/8), 611–620.
6. Wannamaker, R. A., Lipshitz, S. P. & Vanderkooy, J. (1993). *Proc. IEEE WASPAA*, 140–143. DOI: 10.1109/aspaa.1993.379977.
7. Wannamaker, R. A., Lipshitz, S. P., Vanderkooy, J. & Wright, J. N. (2000). *IEEE TSP* 48(2), 499–516. DOI: 10.1109/78.823976.
8. Terhardt, E. (1979). *Hearing Research* 1(2), 155–156.
9. SoX `src/dither.c`, `src/dither.h` — https://github.com/chirlu/sox (verified 2026-10-23).
10. Wikipedia: Dither; Noise shaping; Quantization (signal processing) (fetched 2026-10-23).
