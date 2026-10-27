# Sound Production Method SP-126 — Perceptual Loudness Normalization (PLN)

**Layer:** absolute (sound production) — **Post-Processing / DSP**
**Candidate code path:** `sound/effects/loudness_normalizer.py` (`KWeighting`, `LoudnessMeter`, `TruePeak`, `LoudnessNormalizer`, `LoudnessRange`; presets in `loudness_targets.py`)
**Summary-table row:** `| **SP-126** | Perceptual Loudness Normalization (PLN) | **Post-Processing / DSP** | Delivery-Stage Loudness / Broadcast & Streaming Master Normalization | Measures K-weighted gated integrated loudness per ITU-R BS.1770-4 (two-stage biquad pre-filter, channel weights 1.0/1.0/1.0/1.41/1.41, LFE excluded, 400 ms blocks with 75% overlap, absolute gate −70 LKFS then relative gate −10 LU) and applies one constant scalar gain $g=10^{(T-L_{KG})/20}$ to land the render on a target (−14 LUFS streaming, −23 EBU R 128, −24 ATSC A/85). True-peak (dBTP) re-verified after gain via 4× oversampling with the Annex-2 FIR; per-section short-term mode writes a loudness contour across columns. Constant gain ⇒ no retiming, no phase change ⇒ zero-drift safe; complements SP-008/SP-107 (dynamics/peaks) and runs before SP-122 (dither). Candidate: `sound/effects/loudness_normalizer.py`. |`
**One-line description:** Terminal render stage that measures ITU-R BS.1770 K-weighted gated integrated loudness (LUFS) and applies one constant gain to land a rendered buffer on a delivery target (streaming/broadcast), with true-peak (dBTP) verification — perceptual level control, distinct from SP-008 dynamics, SP-107 peak limiting, and SP-122 bit-depth dithering.
**Prototype:** `/opt/data/pln_validate.py` (executed with `$MUSICOM_PYTHON`, 2026-10-27; numbers in §6 reproduce bit-for-bit).

---

## 1. Why this is a distinct method

The SP catalogue already manages *peaks* (SP-107 LBL), *dynamics* (SP-008 DRC), *spectral dynamics* (SP-114), *transients* (SP-073/SP-118), and *bit depth* (SP-122 NSDQ) — but nothing measures or targets **perceptual loudness**. That is the missing stage: peak level and perceived level are decoupled by the loudness war. Two masters at identical 0 dBFS-peak can differ by 10+ LU in perceived loudness; two masters at the same LUFS are perceptually matched regardless of their peak meters. Peak metering answers "will it clip?", not "is it as loud as the reference?".

| | measures | changes | target |
|---|---|---|---|
| SP-008 DRC | dynamics (level vs time) | gain curves (attack/release/ratio/knee) | transient control |
| SP-107 LBL | peaks (look-ahead) | gain reduction above ceiling only | no clipping |
| SP-114 SDCX | per-band level | per-band gain masks | spectral balance of level |
| SP-122 NSDQ | bit depth | quantization error spectrum | delivery word length |
| **SP-126 PLN** | **K-weighted gated integrated level** | **one constant scalar gain** | **LUFS target + dBTP ceiling** |

PLN is deliberately the *dumbest* processor in the chain: it applies **one constant gain**. No filtering, no curves, no attack/release, no intermodulation, no phase change, no retiming. Everything the render already is — its dynamics, its LRA, its crest factor, its spectral balance — is preserved exactly; only the perceptual *level* moves to the target. This is what makes it zero-drift safe by construction and why it belongs at the very end of the absolute-layer chain, between the peak limiter and the ditherer.

---

## 2. Standards background

- **ITU-R BS.1770** (2011–2023, revisions 1–5): "Algorithms to measure audio programme loudness and true-peak audio level." Defines the K-weighted, channel-weighted, gated measurement (Annex 1) and true-peak oversampling (Annex 2). The gate (absolute −70 LKFS + relative −10 LU) entered at BS.1770-2 (2011).
- **EBU R 128** (2010→2023): broadcast loudness normalisation contract: programme loudness **−23 LUFS ±0.5 LU**, maximum true peak **−1 dBTP**, loudness descriptors (momentary 400 ms, short-term 3 s, integrated whole-file). Relative gate changed −8 → **−10 LU** at V2 (2011). R 128-2023 adds references to TECH 3342/3343/3401.
- **EBU TECH 3342**: Loudness Range (LRA): distribution of short-term (3 s) loudness; **LRA = P90 − P10** (LU).
- **EBU Tech 3343**: production/implementation guidelines: short-form measurement for items < 10 s, lossy-codec true-peak headroom.
- **ATSC A/85**: US DTV target **−24 LKFS**; **ARIB TR-B32**: Japan −24 LKFS.
- **Streaming platforms (2026 norms)**: Spotify/YouTube/Tidal/Amazon ≈ **−14 LUFS** integrated, −1 dBTP; Apple Music ≈ **−16 LUFS** (Sound Check normalizes anyway); Deezer −15; these drift — read current platform docs before delivery.
- **History**: the loudness war (1990s–2000s CD masters at −6…−9 LUFS, DR ~4–6) is the pathology; BS.1770/R 128 are the cure. The unit **LKFS ≡ LUFS** (EBU renamed for ISO 80000-8 compliance; symbol $L_K$).

---

## 3. The measurement algorithm (BS.1770-4 Annex 1)

### 3.1 K-weighting: two cascaded biquads

Each channel is filtered by two direct-form II biquads

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}}.$$

Stage 1 models the head's acoustic effect (a high-frequency shelf, ≈ +4 dB in the 1–5 kHz region); stage 2 is the **RLB** (revised low-frequency B-weighting) second-order highpass, −3 dB near 38 Hz. Published coefficients, **48 kHz**:

| stage | b0 | b1 | b2 | a1 | a2 |
|---|---|---|---|---|---|
| 1 (head) | 1.53512485958697 | −2.69169618940638 | 1.19839281085285 | −1.69065929318241 | 0.73248077421585 |
| 2 (RLB) | 1.0 | −2.0 | 1.0 | −1.99004745483398 | 0.99007225036621 |

(Verified against the BS.1770-4 PDF, Tables 1–2, 2026-10-27.) **These are 48 kHz values.** For other rates, either use published per-rate sets or design matching filters by bilinear transform of the analog prototype so the −3 dB points and shelf stay put. The K-weighting curve is a *measurement* weighting — it is **not** a target EQ curve (AES Loudness Project, "Learn More"); applying it as an EQ would be a category error.

### 3.2 Mean square, channel weights, and the loudness number

Mean square per channel over the measurement interval $T$ (after K-weighting):

$$z_i=\frac{1}{T}\int_0^T y_i^2(t)\,dt,$$

$$L_K=-0.691+10\log_{10}\sum_{i\in\{L,R,C,Ls,Rs\}} G_i\,z_i\qquad[\text{LKFS}],$$

with $G_L=G_R=G_C=1.0$, $G_{Ls}=G_{Rs}=1.41$ (≈ +1.5 dB; surround channels are correlated, hence the √2-like weight), **LFE excluded**. The constant −0.691 cancels the K-weighting gain at **997 Hz**: a 0 dBFS 997 Hz sine reads **−3.01 LKFS** (its mean square is 0.5 ⇒ 10 log10 0.5 = −3.01). This is the mandatory calibration check.

### 3.3 Two-stage gating (integrated measurement)

- Gating blocks: $T_g$ = 400 ms, overlap 75% ⇒ hop = 100 ms ($T_{\text{step}}=0.25\,T_g$); the measurement ends on a block boundary; incomplete trailing blocks are discarded.
- Block power and block loudness:

$$z_{ij}=\frac{1}{T_g}\int_{jT_{\text{step}}}^{jT_{\text{step}}+T_g} y_i^2(t)\,dt,\qquad
l_j=-0.691+10\log_{10}\sum_i G_i\,z_{ij}.$$

- **Stage A — absolute gate** $\Gamma_a=-70$ LKFS: $J_{ga}=\{j:l_j>\Gamma_a\}$; compute the gated loudness over $J_{ga}$.
- **Stage B — relative gate**: $\Gamma_r=(\text{stage-A result})-10$ LU; final

$$L_{KG}=-0.691+10\log_{10}\frac{1}{|J_g|}\sum_{j\in J_g}\sum_i G_i\,z_{ij},\qquad
J_g=\{j:l_j>\Gamma_r\ \text{and}\ l_j>\Gamma_a\}.$$

Both gates matter: the absolute gate keeps long silences from dragging the integral; the relative gate (added BS.1770-2 / R 128 V2, **−10 LU**, not the old −8) keeps near-quiet programme styles from being measured "louder" than they are. Measured on a sparse bursts signal (50% silence): gated **−6.97 LKFS** vs ungated −9.03 — a 2 LU discrepancy, exactly the kind that shows up as a 2 dB mis-normalization.

### 3.4 Momentary / short-term / integrated

- **Momentary**: 400 ms, no gating — metering only.
- **Short-term**: 3 s, no gating — per-section/per-column measurements.
- **Integrated**: whole-file, gated — the number that is normalized (long-form).

---

## 4. Normalization

Measured integrated loudness $L_{KG}$, target $T$ (LUFS), apply one constant gain to every sample of every channel:

$$g=10^{(T-L_{KG})/20}\qquad(\Delta_{\text{dB}}=T-L_{KG}),$$

$$y_{\text{out}}[n]=g\cdot y_{\text{in}}[n].$$

Constant scalar ⇒ the operation commutes with nothing and changes nothing except level: timing, phase, spectrum, dynamics, LRA, crest factor all preserved ⇒ zero-drift safe, sample-in/sample-out, fully deterministic and reproducible (the absolute-layer contract).

**Per-section (loudness contour) mode:** measure short-term (3 s) loudness per section/column, apply per-column gains $g_s=10^{(T_s-L_s)/20}$, crossfade between columns with short (≤ 100 ms) equal-power ramps so seams do not click. This is the "loudness form": the composer writes macro-dynamics as column targets (−20 intro → −12 chorus) instead of hoping velocity maps survive rendering.

---

## 5. True peak (dBTP) — the second number

Sample-peak meters miss inter-sample overs: a signal whose samples all stay under 0 dBFS can still exceed full scale *between* samples after reconstruction (most audible on HF content near Nyquist). BS.1770-4 Annex 2: attenuate 12.04 dB, oversample ≥ 4× (≥ 192 kHz), filter with the Annex-2 FIR lowpass, take absolute values, compensate the 12.04 dB:

$$\text{dBTP}=20\log_{10}\left(\max_n |y_{\uparrow 4\times}[n]|\right).$$

Production notes:
- The literal Annex-2 FIR is a 48 kHz-specific, attenuation-compensated kernel; a polyphase windowed-sinc interpolator (e.g. `scipy.signal.resample_poly`) is equivalent and rate-robust. Measured: 0.99-amplitude 20 kHz sine → **−0.087 dBTP** with polyphase 4× (sample peak −0.09 dBFS — the sine's true peak falls between samples).
- **After** applying the normalization gain, re-measure dBTP. If it exceeds the ceiling (typical **−1.0 dBTP** master; −1.5…−2 dBTP when lossy codecs are downstream — AAC/MP3/Opus reconstruction overshoots true peak by up to ~+1 dB), lower the target or hand to SP-107 LBL. PLN never clips; it reports.

---

## 6. Reference implementation (NumPy) — validated

`/opt/data/pln_validate.py` (`$MUSICOM_PYTHON`, scipy 1.17.1 / numpy 1.26.4). Core:

```python
import numpy as np
from scipy.signal import lfilter

FS = 48000
# BS.1770-4 Table 1 (head) + Table 2 (RLB), 48 kHz
STAGES = [
    dict(b=[1.53512485958697, -2.69169618940638, 1.19839281085285],
         a=[1.0, -1.69065929318241, 0.73248077421585]),
    dict(b=[1.0, -2.0, 1.0],
         a=[1.0, -1.99004745483398, 0.99007225036621]),
]

def kweight(x):
    y = x.copy()
    for s in STAGES:
        y = lfilter(s["b"], s["a"], y)
    return y

def lufs(x, fs=FS, gate=True, G=(1.0, 1.0)):
    """Stereo integrated loudness, BS.1770-4 Annex 1 (400 ms blocks, 75% overlap)."""
    y = np.stack([kweight(x[:, 0]), kweight(x[:, 1])], axis=1)
    Tg = int(0.4 * fs); step = int(0.25 * Tg)
    n_blocks = (len(y) - Tg) // step + 1
    zs = np.array([np.mean(y[j*step:j*step+Tg]**2, axis=0)
                   for j in range(n_blocks)])          # (blocks, ch)
    if not gate:
        return -0.691 + 10*np.log10(np.mean(zs, axis=0) @ np.array(G))
    lj = -0.691 + 10*np.log10(zs @ np.array(G))         # block loudness (4)
    J = lj > -70.0                                      # absolute gate
    L1 = -0.691 + 10*np.log10(np.mean(zs[J], axis=0) @ np.array(G))
    Jr = (lj > (L1 - 10.0)) & (lj > -70.0)              # relative gate (7)
    return -0.691 + 10*np.log10(np.mean(zs[Jr], axis=0) @ np.array(G))

def normalize(x, target_lufs, gate=True, G=(1.0, 1.0)):
    L = lufs(x, gate=gate, G=G)
    g = 10 ** ((target_lufs - L) / 20)
    return x * g, L, g
```

True peak: `scipy.signal.resample_poly(x, 4, 1, window=("kaiser", 12.0))` → `20*log10(max|·|)`.

**Measured output (reproducible, seed 0):**

```
997Hz mono 0dBFS : -3.011 LKFS  (expect -3.01)      <-- calibration PASS
997Hz stereo     : -0.001 LKFS  (expect 0.0)        <-- channel weights PASS
LP-noise -20dBFS  : -19.399 LKFS  (sanity ~-20..-22)
norm: measured -23.01 LUFS -> target -14, gain +9.01 dB, re-measured -14.00 LUFS
TP 20kHz sine    : -0.087 dBTP (peak-sample -0.09 dBFS)   <-- inter-sample peak found
sparse bursts    : -6.967 LKFS (gated) / -9.032 LKFS (ungated)  <-- gating matters, 2 LU
```

The round trip (−23.01 → +9.01 dB → −14.00 LUFS) is exact; the 997 Hz calibration landing on −3.011 (spec: −3.01) confirms the coefficients and the −0.691 offset are correctly implemented.

---

## 7. Musical Elements Framework

- **PITCH**: none directly — K-weighting is a fixed measurement curve, not a musical filter, and the gain is spectrum-flat. Indirectly: register leaks into the measurement (RLB rolls off below ~150 Hz), so a sub-heavy mix measures "quiet" and gets boosted; repeated dBTP-ceiling hits after normalization are a *balance* signal (bass too hot relative to K-weighted energy → SP-007/SP-103 territory), not a loudness problem.
- **RHYTHM**: the 400 ms/75%-overlap gating block is rhythm-shaped: sparse/silence-heavy material gates out, measures low, receives more gain → its noise floor lifts into audibility (the classic sparse-ballad trap). Percussive material measures by RMS not impact; **crest factor (dBTP − LUFS)** is the rhythmic-texture diagnostic (kick-driven ≈ 12–20 dB, sustained pad ≈ 6–10 dB).
- **HARMONY**: dense chords accumulate channel-weighted mean-square energy — harmonic density is loudness weight. Per-section targets therefore equalize texture: a chorus that adds voices is rebalanced against a sparse verse by construction.
- **STRUCTURE**: the loudness contour (per-section short-term LUFS) is a measurable macro-dynamics plan; section-matched mode writes it as column targets with crossfaded gains. LRA (P90 − P10 of the 3 s short-term distribution) quantifies whether the contour is real (≥ 8 LU) or paper (≤ 4 LU after heavy limiting).
- **TEXTURE**: two diagnostics — crest factor (density/punch) and noise-floor visibility (quiet textures amplified by the gain). Constant gain preserves all texture exactly; PLN only moves the level the texture sits at.

---

## 8. UnitMatrix Integration

- **Voices (rows) = loudness-balanced stems.** Render each row to its own stem, measure each stem's integrated LUFS, apply per-voice trim to relative targets (lead −14, bass −16, pad −18, drums −12 relative to bus) before summing — a fader-less, measurement-grounded balance that validates the concrete layer's velocity mapping (a voice 6 LU hot = velocity map error, not a fader issue). Complements SP-007 (frequency balance).
- **Sections (columns) = loudness form.** Each column carries `target_lufs`; the normalizer computes per-column short-term loudness and crossfaded per-column gains. Verse→chorus becomes a measured +4 LU event, not an accident.
- **Cells (MusicUnit) = input dynamics, verified by measurement.** Velocity/duration are the loudness *inputs*; the meter reports measured LUFS/dBTP per row/section so the composer sees whether intended dynamics actually landed.
- **Dispatch**: `produce(midi_path, method="SP-126", params={"target_lufs": -14.0, "true_peak_ceiling": -1.0, "mode": "integrated", "gate": True, "lra_report": True, "per_section": False})`. Chain: render → SP-008 → SP-107 → **SP-126** → SP-122 → write. SP-126 before SP-122 (gain before dither keeps the noise floor at the right relative level); dBTP is the last level check before the writer.
- **Zero-drift**: constant gain retimes nothing; per-section mode uses deterministic crossfades; identical inputs ⇒ identical outputs (reproducibility invariant).

---

## 9. Pitfalls

1. **Sample-rate-bound coefficients.** Tables 1–2 are 48 kHz values; reuse at 44.1/96 kHz mis-measures (up to ~0.5 LU on some material). Design matching filters per rate; run the 997 Hz → −3.01 LKFS calibration at every rate.
2. **Relative gate = −10 LU, not −8** (R 128 V2 / BS.1770-2 2011). The A/85-era −8 over-measures sparse content and under-normalizes it.
3. **The −0.691 offset.** Forgetting it shifts everything 0.69 LU; the calibration test catches it. Always unit-test.
4. **True peak needs ≥4× oversampling with a proper lowpass.** Linear interpolation misses up to several dB of inter-sample overs; sample-peak meters are blind by definition. The Annex-2 FIR has 12.04 dB built-in attenuation — forget the compensation and dBTP reads 12.04 dB low.
5. **Loudness ≠ peak.** Re-measure dBTP *after* the gain; on ceiling hit, lower target or chain SP-107 — never clip.
6. **Lossy codecs overshoot TP ~+1 dB.** Master at −1.0…−2.0 dBTP when lossy distribution is downstream; record the choice in provenance.
7. **Sparse material ⇒ floor rises.** The gate lowers the measurement; the gain lifts noise/room tone. Render stems with headroom (−6…−12 dBFS peak), normalize up, and inspect the floor after gain.
8. **Order: SP-126 before SP-122.** Dithering first quantizes at the wrong level and the gain then scales the noise.
9. **Short items ≠ long items.** < 10 s cues barely populate the 400 ms blocks; use EBU Tech 3343 short-form treatment (whole-item, relaxed gating, per-segment matching).
10. **Per-section mode: hard seams click.** Crossfade (≤ 100 ms, equal-power), deterministically, and record it.
11. **Don't chase the number with bass.** K-weighting rolls off lows by design; adding sub energy to "fix" LUFS is the loudness war in disguise — fix the mix balance instead.
12. **LRA is the real guardrail.** −14 LUFS with LRA 2 LU is a loudness-war artifact whatever the target; if LRA < 4 after normalization, the concrete layer's dynamics were destroyed upstream (SP-008 settings, velocity mapping) — the meter exposes it, the composer fixes the cause.

---

## 10. References

1. ITU-R BS.1770-4 (10/2015), "Algorithms to measure audio programme loudness and true-peak audio level", ITU, Geneva — Annex 1 (K-weighting, Tables 1–3, eqs. 1–7, gating) and Annex 2 (true-peak FIR, 12.04 dB compensation). PDF verified via archive.org mirror 2026-10-27.
2. ITU-R BS.1770-5 (11/2023) — current revision; algorithm unchanged, scope clarifications.
3. EBU R 128-2023, "Loudness normalisation and permitted maximum level of audio signals", EBU, Geneva — −23 LUFS ±0.5 LU, −1 dBTP, gate revision history (fetched tech.ebu.ch/docs/r/r128.pdf 2026-10-27).
4. EBU Tech 3343, "Practical guidelines for Production and Implementation in accordance with EBU R 128" — short-form measurement, codec headroom.
5. EBU TECH 3342 (2016), "Loudness Range: a measure to supplement EBU R 128 loudness normalisation" — LRA = P90 − P10 of 3 s short-term loudness.
6. ATSC A/85 (2013), "Techniques for Establishing and Maintaining Audio Loudness for Digital Television" — −24 LKFS US broadcast.
7. AES Loudness Project, "Learn More: K-weighting and other frequency weighting schemes" (aes.org) — measurement-vs-EQ clarification.
8. Grimm, E. & van Everdingen, R. (2009), "Towards a Recommendation for a European Standard of Peak and LKFS Loudness Levels", EBU.
9. Wikipedia "LUFS" (retrieved 2026-10-27) — standard history (BS.1770-1…-5, gate introduction at -2, LKFS/LUFS naming, ISO 80000-8 note).
10. Streaming delivery norms (Spotify −14, Apple −16, YouTube −14, Amazon −14, Tidal −14, Deezer −15) — platform docs, verify at delivery time.
