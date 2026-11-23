# SP-148 — Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR)

**Layer:** absolute — sound production (Post-Processing / DSP)
**Target output:** parametric smooth late reverb; sparse stochastic IR; multichannel decorrelation
**Candidate code path:** `sound/effects/velvet_reverb.py`
**DB section:** `methods_db.md` → "Sound Production Method SP-148"
**Prototype:** `_web148_vnr/vnr_prototype.py` (10/10 checks, `vnr_results.json`, `vnr_out.wav` 576,044 B)

---

## 1. Idea in one paragraph

A late-reverberation impulse response is, perceptually, a smooth noise-like decay. Instead of
storing/convolving a dense measured IR (SP-009) or recirculating a delay network (SP-032,
SP-071, SP-140), FVNR synthesizes the IR as a **sparse signed impulse sequence — velvet noise —**
multiplied by an **analytic per-band exponential envelope** and band-limited by octave filters.
The sequence has (in expectation) a flat magnitude spectrum and random phase, so the *filters*
own the colour and the *envelope* owns the decay. The result is parametric (T60, density,
per-band ratio, pre-delay are numbers), mode-free (no fixed eigenfrequencies to ring), cheap
(`O(ρT)` taps instead of `O(N)`), and trivially decorrelated per channel by changing the seed.

## 2. Velvet noise

Grid period for pulse density ρ (pulses/s) at sample rate fs:

    Td = fs / ρ                          [samples]

Pulse positions and signs:

    n_k = floor(k·Td + u_k),  u_k ~ U(-Td/2, Td/2)
    s_k ∈ {-1, +1}, uniform
    v[n] = Σ_{k=0}^{K-1} s_k · δ[n - n_k],   K ≈ ρ·T

Collisions (two pulses in one bin) accumulate: `np.add.at` yields ±2 or 0, giving a mild
amplitude distribution rather than a strict ±1. Adjacent-pulse correlation is destroyed by the
jitter; an *un-jittered* grid has a line spectrum at ρ (pitched buzz) and must never be used.

### Why the spectrum is flat

For independent random signs, `E[s_k s_l] = δ_kl`, so

    E[ |V(e^{jω})|² ] = Σ_k E[s_k²] = K = ρ·T   (constant in ω)

i.e. flat PSD of height ρ·T over the whole band, with uniformly distributed phase — a
minimum-phase-free, mode-free noise. Measured prototype: seven octave bands (125 Hz–16 kHz)
of the raw sequence span **0.544 dB**.

### Roughness

Perceived temporal roughness is inversely proportional to ρ; smooth broadband noise is reached
at **ρ ≈ 1500–2000 pulses/s** (Karjalainen & Järveläinen 2001; restated in arXiv:2403.20090).
Below ~800/s the tail granulates. A time-varying density (2000 → 500 pulses/s, linear) keeps
the late tail cheap because sparse late pulses are masked by the earlier dense region.

## 3. The IR

    h_late[n] = Σ_b ( (v_b[n] · 10^{-3n/(fs·T60_b)}) * g_b[n] )

with `g_b` an octave band-pass and

    T60_b = T60 · r^{b - b_ref}

`r` = 0.8 gives HF-faster / LF-slower decay (typical rooms); `r = 1` gives a flat, plate-like
tail. `10^-3` encodes the −60 dB definition of T60. The prototype anchors T60 at band index 2
(≈750 Hz) and renders `ceil(1.3 · max(T60_b) · fs)` samples so no band is truncated.

Measured vs target T60 (s), six octave bands (125 Hz … 4–8 kHz):

| band | 125–250 | 250–500 | 500–1k | 1k–2k | 2k–4k | 4k–8k |
|---|---|---|---|---|---|---|
| target | 3.125 | 2.500 | 2.000 | 1.600 | 1.280 | 1.024 |
| measured | 3.127 | 2.535 | 1.993 | 1.601 | 1.282 | 1.023 |

Max error **1.4 %** (Schroeder backward integration, −5…−25 dB fit).

### Energy normalisation (mandatory)

    Σ_n h²[n] ∝ ρ·T   ⇒   h̃[n] = h[n] / sqrt(Σ_n h²[n])

Without it, raising ρ (a *quality* knob) raises the wet level by 10·log10(ρ). With unit-energy
IRs, wet RMS at ρ = 500 / 2000 / 8000 measured −0.512 / −0.521 / −0.523 dB → **0.011 dB spread**.

### Early / late hybrid

    h[n] = h_early[n] + G_late · h_late[n - d_pre]

Velvet owns only the diffuse field. First ~60–80 ms should be discrete taps (image-source
SP-075 or manual), and a 10–40 ms pre-delay separates source from space.

### Coloured tails (dark velvet noise)

Route each pulse through a dictionary filter `F_q(z)` chosen with time-varying probability
`p_q(m)` (arXiv:2403.20090):

    h[n] = Σ_k s_k · F_{q_k}[n - n_k]
    |H(m, ω)| = Σ_q |F_q(ω)| · p_q(m)        (independent of ρ)

Ten second-order all-pole filters fitted by NNLS reach mean T60 error 4 % / max 8 % on a
target hall, with ~50 % fewer coloration filters than frame-wise filtered velvet noise.

## 4. Cost

Direct sparse convolution: `P = ρ·T` multiply-accumulates per output sample. For T = 2 s,
fs = 48 kHz, ρ = 2000: P = 4000 vs N = 96,000 → **24×** fewer MACs. Because both P and N scale
with T, the ratio is length-invariant (prototype IR: 195,000 samples, 8,125 pulses, 24.0×).
FFT convolution also works, but block-wise sparse direct convolution is cheaper for short
blocks and needs no partition bookkeeping.

## 5. Stereo / multichannel

Independent seeds per channel ⇒ different pulse sets, shared envelope and band gains. Measured
inter-channel correlation: **0.048** (125–250 Hz), **−0.062** (4–8 kHz). No fixed delay ⇒ no
comb filtering on mono fold-down. Keep the low band coherent (shared sequence, pan only) for a
solid image; decorrelate ≥ ~300 Hz.

## 6. Presets

| preset | T60 (s) | r | ρ (pulses/s) | pre-delay (ms) | notes |
|---|---|---|---|---|---|
| room | 0.6 | 0.85 | 3000 | 8 | tight, dense, minimal early taps |
| hall | 2.4 | 0.80 | 2000 | 25 | LF weight, HF air |
| plate | 1.8 | 0.95 | 4000 | 5 | flat, bright, dense |
| gated | 1.2 | 1.00 | 2500 | 0 | hard truncation on the beat |
| swell | 2.0 | 0.80 | 2000 | 0 | inverted/ramped envelope (reverse-reverb gesture) |
| lo-fi grain | 1.5 | 0.85 | 600 | 15 | deliberate roughness as texture |

## 7. NumPy implementation sketch

```python
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

FS = 48000
BANDS = [(125, 250), (250, 500), (500, 1000), (1000, 2000),
         (2000, 4000), (4000, 8000)]

def velvet_noise(n, fs, rho, seed):
    rng = np.random.default_rng(seed)
    td = fs / rho
    k = np.arange(int(np.ceil(n / td)))
    pos = np.clip(np.round(k * td + rng.uniform(-.5, .5, k.size) * td).astype(int), 0, n - 1)
    sgn = rng.choice(np.array([-1.0, 1.0]), k.size)
    v = np.zeros(n)
    np.add.at(v, pos, sgn)               # collisions accumulate
    return v

def velvet_ir(t60=2.0, rho=2000, seed=1, fs=FS, r=0.8, n_bands=6, tail=1.3):
    tbs = [t60 * r ** (b - 2) for b in range(n_bands)]     # T60 anchored at band 2
    n = int(round(max(tbs) * tail * fs))
    ir = np.zeros(n)
    for b, (lo, hi) in enumerate(BANDS[:n_bands]):
        hi = min(hi, fs / 2 * 0.98)
        sos = butter(2, [lo, hi], btype="bandpass", fs=fs, output="sos")
        env = 10.0 ** (-3.0 * np.arange(n) / (fs * tbs[b]))  # -60 dB at T60
        ir += sosfilt(sos, velvet_noise(n, fs, rho, seed * 101 + b) * env)
    return ir / np.sqrt(np.sum(ir ** 2) + 1e-30)             # unit-energy IR

def apply(dry, ir):
    wet = fftconvolve(dry, ir)[:dry.size]                    # or sparse direct conv
    assert wet.size == dry.size
    return wet
```

Sparse direct convolution (production form):

```python
taps = np.flatnonzero(ir)                # P indices
gains = ir[taps]
wet = np.zeros_like(dry)
for lag, g in zip(taps, gains):          # vectorise in blocks over output
    wet[lag:] += g * dry[:dry.size - lag]
```

Crossfade preset changes by rendering two IRs and equal-power mixing over ≥200 ms (or by
mutating ρ/T60 in a smoothed parameter block), never by swapping an IR under a ringing tail.

## 8. Verification record (10/10)

| # | check | result |
|---|---|---|
| 1 | pulse density | 4000 pulses / 2.0 s at ρ=2000, rel. err 5e-4 |
| 2 | spectral flatness | 0.544 dB over 7 octave bands |
| 3 | T60 anchor band | 1.993 s vs 2.000 s (0.375 %) |
| 4 | per-band T60 | max err 1.4 %, monotone (HF shorter) |
| 5 | unit-energy IR | 1.000000 at ρ=2000 and ρ=4800 |
| 6 | wet-level invariance | 0.011 dB across ρ = 500/2000/8000 |
| 7 | determinism | same seed ⇒ `array_equal` True |
| 8 | exact length | 195,000 samples |
| 9 | stereo decorrelation | \|r\| = 0.048 (LF), 0.062 (HF) |
| 10 | demo WAV | 576,044 B (3.0 s stereo, SHA256 prefix `d0159d59b11af73f`) |

## 9. UnitMatrix mapping

- **Rows (voices)** → `{t60, r, rho, bands, predelay_ms, early_taps, late_gain, mix, lf_coherent, seed}`.
- **Columns (sections)** → space presets + crossfade; a column change is a *space* change.
- **Cells (MusicUnit)** → dry note + per-cell send (velocity-derived or explicit); the wet buffer
  is rendered at exactly the section length plus a deterministic tail.

Produce call:

```python
produce(midi_path, method="SP-148", params={
    "rows": {
        "pad":   {"t60": 2.4, "t60_ratio": 0.8, "rho": 2000, "predelay_ms": 25,
                  "early_taps": "none", "mix": 0.35, "seed": 3},
        "snare": {"t60": 1.2, "rho": 3000, "predelay_ms": 8,
                  "early_taps": [[11, 0.5, -0.3], [19, 0.35, 0.4]], "mix": 0.5, "seed": 4}},
    "columns": {"A": {"preset": "room",  "t60": 0.6, "mix": 0.20},
                "B": {"preset": "hall",  "t60": 2.4, "mix": 0.35},
                "C": {"preset": "gated", "shape": "gated", "t60": 1.2, "mix": 0.45}},
    "crossfade_ms": 400})
```

## 9b. Pitfalls (condensed)

1. Un-jittered grid ⇒ pitched buzz; identical seeds per channel ⇒ mono/comb.
2. No energy normalisation ⇒ ρ doubles as a 12 dB wet-level knob.
3. ρ < 800/s ⇒ granular tail (use deliberately or not at all).
4. Truncating the IR at T60 instead of ≈1.3·T60_max biases measured T60 short and chops the LF tail.
5. Velvet alone = noise glued to the note: no early reflections, no direction. Hybridise + pre-delay.
6. Feedback-loop velvet re-imposes a single exponential decay — loses the method's parametric-decay advantage.
7. Flat spectrum includes DC/infrasonic energy — band gains or a wet high-pass are required.
8. Cross-fading mid-tail clicks; use two IRs and an equal-power fade.
9. Seed per (row, band, channel); assert buffer length before mixing (zero-drift).
10. Distinguish from SP-009 (dense IR convolution), SP-032 (FDN), SP-071 (Dattorro plate),
    SP-075 (image source), SP-140 (Schroeder), SP-146 (filter-statistics texture).

## 10. References

1. M. Karjalainen & H. Järveläinen, "Reverberation Modeling Using Velvet Noise," *Proc. WASPAA*, 2001.
2. J. Fagerström et al., "Non-Exponential Reverberation Modeling Using Dark Velvet Noise," arXiv:2403.20090 (2024) — pulse density definition, 1500–2000 pulses/s smoothness, DVN dictionary filters, 4 %/8 % T60 fit, 2000→500 density ramp.
3. H. Järveläinen et al., "Frequency domain variants of velvet noise and their application to speech processing and synthesis," arXiv:1806.06812 (2018) — "sparse discrete signal … 1 or −1 … smoother than Gaussian white noise".
4. "Frequency domain variant of Velvet noise and its application to acoustic measurements," arXiv:1909.04301 (2019) — FVN as an all-pass IR.
5. V. Välimäki, J. D. Parker, L. Savioja, J. O. Smith, J. S. Abel, "Fifty Years of Artificial Reverberation," *IEEE TASLP* 20(5), 2012 — survey context (velvet noise vs FDN/convolution).
6. Prototype artifacts: `_web148_vnr/vnr_prototype.py`, `vnr_results.json`, `vnr_out.wav`.
