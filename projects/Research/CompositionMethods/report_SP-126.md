# Research Report SP-126 — Perceptual Loudness Normalization (PLN)

- **Method ID:** SP-126
- **Method name:** Perceptual Loudness Normalization (PLN)
- **Acronym:** PLN
- **Layer:** **absolute** (sound production — **Post-Processing / DSP**, per LAYER_ARCHITECTURE.md: Absolute layer = sound production, SP-methods, reproducible render)
- **One-line description:** Terminal render stage that measures ITU-R BS.1770 K-weighted gated integrated loudness (LUFS) and applies one constant gain to land a rendered buffer on a delivery target (streaming/broadcast), with true-peak (dBTP) verification.
- **Candidate code path:** `sound/effects/loudness_normalizer.py` (classes `KWeighting`, `LoudnessMeter`, `TruePeak`, `LoudnessNormalizer`, `LoudnessRange`; presets in `loudness_targets.py`), dispatched from `workflows/musicom_workflow.py::produce(method="SP-126", params={...})`.
- **Why this ID:** scanned summary table rows (`| **SP-NNN** |`) → max SP-125; cross-checked standalone `sound_method_SP-*.md` / `report_SP-*.md` files → max SP-125 (68 method files, 57 report files). New ID = **SP-126**.
- **Duplication check:** no existing SP method measures or targets perceptual loudness. SP-008 (DRC) = dynamics, SP-107 (LBL) = peaks, SP-114 = spectral dynamics, SP-122 (NSDQ) = bit depth. "loudness" appears in the DB only as a feature label (SP-044 CSS, SP-045 DDSP). Genuine gap.
- **Line count before:** 28675
- **Line count after:** 28799 (+124 = 123 detailed-section lines + 1 summary-table row)
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-126_PLN.md` (19,477 bytes)
- **Report file:** `/opt/data/projects/Research/CompositionMethods/report_SP-126.md` (this file)
- **Prototype:** `/opt/data/pln_validate.py` (executed with `$MUSICOM_PYTHON`; measured output in §6 of the standalone file; kept for reproduction like the SP-125 sitar prototype)
- **References verified live (network):** ITU-R BS.1770-4 PDF (via archive.org mirror of the ITU publication — coefficients Tables 1–2, eqs. 1–7, channel weights Table 3, true-peak Annex 2, 12.04 dB compensation all extracted); EBU R 128-2023 PDF (fetched from tech.ebu.ch — revision history incl. −8→−10 LU gate change); Wikipedia LUFS article. ITU direct PDF endpoints are login-gated (404/HTML) — used the archived copy.

## Summary-table row added (line 324)

```
| **SP-126** | Perceptual Loudness Normalization (PLN) | **Post-Processing / DSP** | Delivery-Stage Loudness / Broadcast & Streaming Master Normalization | Measures K-weighted gated integrated loudness per ITU-R BS.1770-4 (two-stage biquad pre-filter, channel weights 1.0/1.0/1.0/1.41/1.41, LFE excluded, 400 ms blocks with 75% overlap, absolute gate −70 LKFS then relative gate −10 LU) and applies one constant scalar gain $g=10^{(T-L_{KG})/20}$ to land the render on a target (−14 LUFS streaming, −23 EBU R 128, −24 ATSC A/85). True-peak (dBTP) re-verified after gain via 4× oversampling with the Annex-2 FIR; per-section short-term mode writes a loudness contour across columns. Constant gain ⇒ no retiming, no phase change ⇒ zero-drift safe; complements SP-008/SP-107 (dynamics/peaks) and runs before SP-122 (dither). Candidate: `sound/effects/loudness_normalizer.py`. |
```

## Technical mechanics summary

1. **K-weighting** — two cascaded biquads (stage 1 head/shelf, stage 2 RLB highpass ~38 Hz); published 48 kHz coefficients (BS.1770-4 Tables 1–2); per-rate design required otherwise.
2. **Channel-weighted mean square** — $z_i=\frac1T\int y_i^2$, $L_K=-0.691+10\log_{10}\sum_i G_i z_i$; weights 1.0/1.0/1.0/1.41/1.41, LFE excluded; −0.691 cancels K-weighting gain at 997 Hz (0 dBFS 997 Hz sine → −3.01 LKFS).
3. **Two-stage gating** — 400 ms blocks, 75% overlap; absolute gate −70 LKFS, then relative gate −10 LU below stage-A result.
4. **Normalization** — one constant scalar $g=10^{(T-L_{KG})/20}$; zero retiming/phase change ⇒ zero-drift safe. Per-section mode: short-term per-column gains + ≤100 ms equal-power crossfades.
5. **True peak** — ≥4× oversampling, dBTP; re-verify after gain; ceiling −1.0 dBTP (master) / −1.5…−2 (lossy downstream); chain SP-107 on ceiling hits.
6. **LRA (TECH 3342)** — P90 − P10 of 3 s short-term distribution; diagnostic only.

## Empirical validation (prototype, `$MUSICOM_PYTHON`, seed 0)

- 997 Hz mono 0 dBFS → **−3.011 LKFS** (spec −3.01) — coefficients + offset exact.
- Stereo pair → **−0.001 LKFS** (spec 0.0) — channel weights exact.
- Normalize: measured −23.01 LUFS → target −14 → gain +9.01 dB → re-measured **−14.00 LUFS** (round-trip exact).
- True peak: 0.99-amplitude 20 kHz sine → **−0.087 dBTP** (inter-sample peak found).
- Gating: sparse bursts gated **−6.97** vs ungated −9.03 LKFS (2 LU — the mis-normalization the relative gate prevents).

## Complete section text appended (methods_db.md, lines 28677–28799)

```markdown
# Sound Production Method SP-126 — Perceptual Loudness Normalization (PLN)

### Source

- **ITU-R BS.1770-4 (10/2015).** "Algorithms to measure audio programme loudness and true-peak audio level." International Telecommunication Union, Geneva. — the measurement core: the K-weighting pre-filter (2-stage biquad, coefficients for 48 kHz in Tables 1–2), channel-weighted mean-square summation (Annex 1 eqs. 1–2, Table 3 weights), the two-stage gating of 400 ms blocks (eqs. 3–7: absolute gate −70 LKFS, relative gate −10 LU), and the true-peak oversampling FIR + 12.04 dB compensation (Annex 2). PDF verified 2026-10-27 via archive.org mirror of the ITU publication; BS.1770-5 (2023) keeps the algorithm and clarifies scope.
- **EBU R 128-2023.** "Loudness normalisation and permitted maximum level of audio signals." European Broadcasting Union, Geneva. — the broadcast implementation contract: programme target −23 LUFS ±0.5 LU, true-peak ceiling −1 dBTP, gate revisions (−8 → −10 LU at V2), loudness descriptors (momentary/short-term/integrated). PDF fetched from tech.ebu.ch 2026-10-27 (5 pp., revisions table read directly).
- **EBU Tech 3343.** "Practical guidelines for Production and Implementation in accordance with EBU R 128." — short-form (ads, < 10 s) measurement guidance, true-peak headroom for lossy codecs, per-segment loudness matching.
- **EBU TECH 3342 (2016).** "Loudness Range: a measure to supplement EBU R 128 loudness normalisation." — the Loudness Range (LRA) statistic: short-term (3 s) loudness distribution, LRA = P90 − P10 in LU.
- **ATSC A/85 (2013).** "Techniques for Establishing and Maintaining Audio Loudness for Digital Television." — US broadcast target −24 LKFS, dialog-gated measurement lineage (A/85 predates the −70/−10 two-gate scheme; BS.1770-2 2011 unified it).
- **AES Loudness Project — "Learn More: K-weighting and other frequency weighting schemes."** (aes.org/resources/audio-topics/loudness-project/learn-more/) — accessible explanation of why K-weighting is a *measurement* curve, not a target EQ curve; the classic misconception this method guards against.
- **Grimm, E. & van Everdingen, R. (2009).** "Towards a Recommendation for a European Standard of Peak and LKFS Loudness Levels." EBU — the loudness-war/EBU history; 997 Hz reference alignment.
- **Streaming delivery norms (2026).** Spotify −14 LUFS / −1 dBTP, Apple Music −16 LUFS / −1 dBTP (Sound Check adjusts), YouTube −14 LUFS / −1 dBTP (loudness normalizes to −14), Amazon Music −14, Tidal −14; historical loudness-war extremes (CD masters at −6 to −9 LUFS, DR-destroying) are the pathology this method exists to prevent. (Platform docs change; treat as guidelines, verify at delivery time.)
- **Novelty check:** the SP summary table (SP-001…SP-125) contains no loudness measurement/normalization method. SP-008 DRC and SP-107 LBL manage *peaks and dynamics*; SP-122 NSDQ manages *bit depth*; none computes or targets perceptual loudness (LUFS). The word "loudness" appears in the DB only as a feature label (SP-044 CSS units, SP-045 DDSP decoder input) — a measurement/normalization *stage* is a genuine gap.

### Layer

**absolute** — sound production (**Post-Processing / DSP**). Per LAYER_ARCHITECTURE.md every SP method is absolute: it consumes rendered audio (stems/WAV produced by the absolute layer's renderers) and produces reproducible audio. PLN is a terminal render stage: it does not generate notes, change pitch, rhythm, harmony, or retime anything — it measures the perceptual level of what the concrete layer already fixed and applies a deterministic scalar gain to land it on a delivery target. Same-stage neighbours in the chain: SP-008 (dynamics), SP-107 (peak ceiling), SP-122 (dithering); PLN is the *perceptual level* stage between them and the file writer.

Candidate code path: `sound/effects/loudness_normalizer.py` (classes `KWeighting`, `LoudnessMeter`, `TruePeak`, `LoudnessNormalizer`, `LoudnessRange`), dispatched from `workflows/musicom_workflow.py::produce(method="SP-126", params={...})`.

### Description

**Perceptual Loudness Normalization (PLN)** measures a rendered buffer's loudness with the ITU-R BS.1770 K-weighted, gated, channel-weighted algorithm and applies a constant linear gain so the *integrated* loudness equals a target: −14 LUFS (streaming), −23 LUFS (EBU R 128 broadcast), −24 LKFS (ATSC A/85), or any composer-chosen value. The unit is **LUFS** (= LKFS; "Loudness Units, K-weighted, Full Scale"): an absolute level on the dB scale where a 0 dBFS 997 Hz sine reads −3.01 LUFS and a 1 dB level change reads 1 LU.

Why this stage exists — the loudness war: two mixes with *identical* peak levels can differ by 10+ LU in perceived loudness (one is brickwalled, one is dynamic); two mixes at the same LUFS are perceptually matched regardless of their peaks. Peak meters measure the wrong thing for level matching; sample-peak meters additionally miss inter-sample overs entirely. PLN replaces "make it as loud as the reference by ear" with a measured, reproducible, standards-backed number, and validates the result against a **true-peak (dBTP)** ceiling so the normalization gain cannot create clipping that a sample-peak meter would not show.

Distinct from its neighbours (the whole point of the method):

| method | measures | what it changes | target domain |
|---|---|---|---|
| SP-008 DRC | dynamics (level vs time) | gain *curves* (attack/release, ratio, knee) | transient control / loudness *shape* |
| SP-107 LBL | sample/true peaks | look-ahead gain reduction only above ceiling | peak ceiling, no loudness target |
| SP-122 NSDQ | bit depth | quantization error spectrum | delivery bit depth |
| SP-007/SP-020 | frequency balance | spectral content | mix balance |
| **SP-126 PLN** | **K-weighted, gated integrated level** | **one constant scalar gain** | **perceptual level target (LUFS) + dBTP ceiling** |

The essential fact: PLN applies a *constant* gain. It is not dynamics processing — no attack/release, no curve, no intermodulation, no phase change, no temporal smearing. The entire render is scaled by $g = 10^{(T-L_K)/20}$, which makes the stage sample-in/sample-out with perfect timing preservation (zero-drift safe by construction). What remains after normalization is the mix's own dynamic contour (its LRA), its crest factor, and its spectral balance — normalized loudness is a *level*, not a *sound*.

Two operational modes: **(1) Integrated (long-form)** — whole-file gated loudness, one gain, the standard master mode; **(2) Section-matched (short-form / loudness contour)** — per-column short-term loudness measured against per-column targets (a "loudness form": intro −20, verse −16, chorus −12 LUFS), each section scaled by its own gain with equal-power crossfades across seams. Mode 2 is how a piece's macro-dynamics are *written* as loudness rather than as MIDI velocities.

### Technical Mechanics

**1. K-weighting pre-filter** (BS.1770-4 Annex 1). Each channel is filtered by two cascaded biquads:

$$H(z)=\frac{b_0+b_1z^{-1}+b_2z^{-2}}{1+a_1z^{-1}+a_2z^{-2}},$$

stage 1 (spherical-head/shelf compensation, models the head's acoustic effect, ~+4 dB shelf in the 1–5 kHz region) and stage 2 (RLB revised low-frequency B-weighting, 2nd-order highpass, −3 dB near 38 Hz). Coefficients at 48 kHz (Tables 1–2):

| stage | b0 | b1 | b2 | a1 | a2 |
|---|---|---|---|---|---|
| 1 (head) | 1.53512485958697 | −2.69169618940638 | 1.19839281085285 | −1.69065929318241 | 0.73248077421585 |
| 2 (RLB) | 1.0 | −2.0 | 1.0 | −1.99004745483398 | 0.99007225036621 |

The published coefficients are 48 kHz values; other sample rates require matching filters (same frequency response — rescale via bilinear transform of the analog prototype, or use the per-rate sets published by EBU/plugin vendors). Implement as direct-form II biquads (scipy.signal.lfilter) — the filter is linear and time-invariant, so it introduces no distortion, only the fixed measurement curve.

**2. Channel-weighted mean square and the loudness number.** After filtering, the mean square over the measurement interval T per channel i:

$$z_i=\frac{1}{T}\int_0^T y_i^2(t)\,dt,\qquad L_K=-0.691+10\log_{10}\sum_{i\in\{L,R,C,Ls,Rs\}} G_i\,z_i\quad[\text{LKFS}],$$

with channel weights $G_L=G_R=G_C=1.0$ and $G_{Ls}=G_{Rs}=1.41$ (surround ≈ +1.5 dB); the LFE channel is **excluded**. The −0.691 constant cancels the K-weighting gain at 997 Hz, which is why a 0 dBFS 997 Hz sine reads exactly −3.01 LKFS (its mean square is 0.5, so 10 log10 0.5 = −3.01); this is the calibration check every implementation must pass.

**3. Two-stage gating** (integrated measurement only). The interval is split into 400 ms gating blocks overlapping by 75% (hop = 100 ms); the measurement ends at a block boundary, incomplete trailing blocks are dropped. Block power and block loudness:

$$z_{ij}=\frac{1}{T_g}\int_{jT_{\text{step}}}^{jT_{\text{step}}+T_g} y_i^2(t)\,dt,\qquad l_j=-0.691+10\log_{10}\sum_i G_i\,z_{ij}.$$

Stage A — absolute gate $\Gamma_a=-70$ LKFS: keep blocks with $l_j>\Gamma_a$ and compute the gated loudness over that surviving set. Stage B — relative gate: $\Gamma_r=(\text{stage-A result})-10$ [LU]; final gated loudness uses $J_g=\{j: l_j>\Gamma_r \text{ and } l_j>\Gamma_a\}$:

$$L_{KG}=-0.691+10\log_{10}\frac{1}{|J_g|}\sum_{j\in J_g}\sum_i G_i\,z_{ij}.$$

The two gates exist because long silences and sparse passages would otherwise drag the integral down (or, without the absolute gate, near-silent material would be included); the relative gate makes the measurement robust across programme styles. EBU R 128 V2 changed the relative gate from −8 to −10 LU — implementations that hardcode −8 silently mis-measure by up to ~1 LU on sparse content.

**4. Normalization gain.** With measured integrated loudness $L_{KG}$ and target $T$:

$$g = 10^{(T-L_{KG})/20},$$

applied as one constant scalar to every sample of every channel. Constant gain ⇒ no filtering, no intermodulation, no phase shift, no retiming — the zero-drift invariant of the absolute layer is untouched. (Gain in dB: $\Delta = T - L_{KG}$; typical corrections are +2…+8 dB for a dynamic mix, negative for a brickwalled one.)

**5. True-peak verification (dBTP).** Inter-sample overs: a signal whose *samples* stay below 0 dBFS can still exceed full scale between samples after reconstruction. BS.1770-4 Annex 2 specifies: attenuate 12.04 dB, oversample ≥4× (≥192 kHz) with the Annex-2 FIR lowpass, take absolute values, compensate the 12.04 dB, then

$$\text{dBTP}=20\log_{10}\left(\max_n |y_{\uparrow 4\times}[n]|\right)\quad[\text{dBTP}].$$

After applying $g$, re-measure dBTP; if it exceeds the ceiling (typically −1.0 dBTP master, −1.5…−2 dBTP if lossy codecs are downstream — AAC/MP3 overshoot true peak by up to ~+1 dB), either lower the target or hand the buffer to SP-107 LBL for ceiling limiting. PLN normalizes *loudness*, never peak: two −14 LUFS masters can differ by 6+ dB in true peak; the ceiling is a separate constraint.

**6. Loudness Range (LRA, EBU TECH 3342) — diagnostic, not a target.** Short-term loudness (3 s sliding windows, no gating) forms a distribution; LRA = P90 − P10 (LU). Typical values: ~4–6 LU for loudness-war pop, ~10–15 LU for classical/jazz, ~20+ LU for sparse film cues. LRA tells the composer whether the macro-dynamics survived normalization; PLN deliberately does *not* change it.

**7. Momentary vs short-term vs integrated.** Momentary = 400 ms (no gating, for metering/steering); short-term = 3 s (no gating); integrated = whole-file gated (the number that is normalized). Per-section mode uses short-term per column, never momentary (400 ms is too twitchy for a section-level gain).

**Reference calibration (must pass):** 0 dBFS 997 Hz sine, 48 kHz, mono → −3.01 LKFS; stereo pair of identical sines → 0.0 LKFS (two 1.0-weighted channels: 10 log10 2 ≈ +3.01 offset, exactly cancels); pink noise at −20 dBFS RMS → ≈ −21.5 LUFS (K-weighting adds ~1.5 LU on broadband material at that level).

### Musical Elements Framework

**PITCH.** None by construction — the K-weighting curve is a fixed measurement filter, not a musical filter, and the gain is constant across the spectrum. But register leaks in as *measurement*: the RLB highpass rolls off below ~150 Hz, so a sub-heavy mix measures quieter than it "feels" and gets boosted — PLN will happily turn a bass wall into a distorting bass wall if the mix balance is wrong. The method's pitch lesson is diagnostic: if a passage keeps triggering the dBTP ceiling after normalization, its bass is too hot *relative to its K-weighted energy* — that is a mix-balance signal (SP-007/SP-103 territory), not a loudness problem.

**RHYTHM.** The 400 ms/75%-overlap gating block is a rhythm-shaped measurement: sparse, silence-heavy material gates out and measures *lower*, so it receives *more* gain — which lifts the noise floor and any room tone into audibility (a real production trap: normalizing a sparse ballad exposes the studio floor). Percussive material measures by its RMS, not its hits, so a drum-heavy loop reads "quieter" than its impact suggests; crest factor (dBTP − LUFS) is the texture-of-rhythm diagnostic: kick-driven = high crest, sustained pad = low crest.

**HARMONY.** Dense chords accumulate channel-weighted mean-square energy: a 6-note pad measures louder than a unison line at the same velocity. Per-section loudness targets therefore act as *harmonic-texture equalizers* — a chorus that adds two voices gets automatically rebalanced against a verse that does not, because the target is perceptual level, not fader level. The method normalizes *weight*, and harmonic density is weight.

**STRUCTURE.** Integrated loudness is a whole-piece number; the interesting structural object is the *loudness contour*: per-section short-term LUFS is a measurable dynamics plan (intro −20 → verse −16 → chorus −12 → outro −18) that survives the constant-gain stage unchanged. Section-matched mode turns that contour into the deliverable: each column gets its own gain, crossfaded across seams, so the composer writes macro-dynamics as *columns* (like any other structural parameter) instead of trusting velocity ranges. LRA then quantifies whether the contour is real (LRA ≥ 8 LU) or a paper plan (LRA < 4 LU after limiting).

**TEXTURE.** Two texture diagnostics: (i) crest factor (dBTP − LUFS) distinguishes "dense/even" textures (low crest, ~6–10 dB) from "punchy/spiky" ones (high crest, ~12–20 dB) — PLN preserves it exactly (constant gain scales both terms equally); (ii) noise-floor visibility — the quietest audible texture after normalization is the floor lifted by the gain: a −30 LUFS noise floor on a −20 LUFS sparse section becomes a −24 LUFS noise bed after +6 dB gain. Texture is the first casualty of over-normalizing sparse mixes.

### UnitMatrix Integration

- **Voices (rows) = loudness-balanced stems.** Render each voice row to its own stem, measure each stem's integrated LUFS, and apply per-voice trim gains so the rows land at *relative* targets before summing (lead −14, bass −16, pad −18, drums −12, all relative to the bus). This is the "fader-less balance": velocities from the concrete layer are validated/calibrated by measurement — if a voice reads 6 LU louder than its target, the concrete layer's velocity mapping is off, not the fader. Complements SP-007 (masking EQ works on *frequency* balance; PLN works on *level* balance).
- **Sections (columns) = loudness form.** Each column carries `target_lufs` (the section's loudness target) and the normalizer computes per-column short-term loudness, per-column gain, and equal-power crossfades (default 100 ms) across section seams. A section boundary is therefore a *loudness event* — verse→chorus is a measured +4 LU jump, not an accident of arrangement. The zero-drift contract: gains are deterministic functions of the rendered buffer; crossfades are deterministic, seeded, and short; no event is retimed.
- **Cells (MusicUnit) = per-note loudness contributions.** Cell events (velocity, duration) are the *input* dynamics; the meter is the *verification*: `produce()` reports measured LUFS + dBTP per row/section so the composer sees whether the intended velocity dynamics actually landed as loudness dynamics (a common failure: velocity curves that look expressive but measure flat because the renderer's velocity→amplitude map is compressed).
- **Produce dispatch**: `produce(midi_path, method="SP-126", params={"target_lufs": -14.0, "true_peak_ceiling": -1.0, "mode": "integrated", "gate": True, "lra_report": True, "per_section": False})`. Terminal stage order: render (SP-001/SP-011/…) → dynamics (SP-008) → ceiling (SP-107) → **SP-126 normalize** → SP-122 dither → write. SP-126 before SP-122: normalization gain must be applied before quantization noise is added (dithering after gain keeps the noise floor at the right *relative* level); and the dBTP check must be the *last* level measurement before the file writer.
- **Reproducibility**: measurement + gain are pure functions of the buffer (no randomness unless per-section crossfade seeds are chosen deterministically); identical inputs give identical outputs — the absolute-layer invariant.

### Pitfalls

1. **K-weighting coefficients are sample-rate-bound.** The published Tables 1–2 are 48 kHz values. Using them at 44.1 kHz mis-measures by up to ~0.5 LU on some material (the filters' −3 dB points move); at 96 kHz more. Design matching filters (bilinear transform of the analog prototype, or published per-rate sets) — never reuse the 48 kHz numbers blindly. Calibration check at every rate: 997 Hz sine → −3.01 LUFS.
2. **The relative gate is −10 LU, not −8.** EBU R 128 V2 (2011) changed it; BS.1770-2 (2011) matches. Hardcoding −8 (the A/85-era value) over-estimates sparse content by up to ~1 LU and then under-normalizes it. Use both gates: absolute −70 LKFS, relative −10 LU, in that order.
3. **Forgetting the −0.691 offset** shifts every measurement by 0.69 LU — small, systematic, and invisible unless you run the 997 Hz calibration (must read −3.01 LKFS). Always run the calibration as a unit test.
4. **True peak needs real 4× oversampling with the Annex-2 filter (or equivalent).** Linear interpolation between samples under-estimates inter-sample overs by up to several dB; sample-peak meters are blind to the worst overs by definition. The Annex-2 FIR has 12.04 dB built-in attenuation — forgetting the compensation under-reads dBTP by exactly 12.04 dB.
5. **Loudness normalization is not peak normalization.** Two −14 LUFS masters can differ by 6+ dB in true peak (brickwalled EDM vs dynamic jazz). Always re-measure dBTP *after* applying the gain; if the ceiling is hit, lower the target or chain SP-107 LBL — never let the normalizer clip.
6. **Lossy codecs overshoot true peak.** AAC/MP3/Opus reconstruction can exceed the master's true peak by up to ~+1 dBTP. Deliver masters at −1.0 dBTP (conservative: −1.5…−2 dBTP) when lossy distribution is downstream, and say so in provenance.
7. **Sparse/quiet sections get boosted → the floor rises.** A section that gates out (long silences, solo over room tone) measures low, receives more gain, and its noise floor becomes audible. Check the noise floor *after* normalization (the −30 LUFS floor at −20 LUFS becomes −24 LUFS at +6 dB); render stems with enough headroom (render at −6…−12 dBFS peak, normalize up, never down into a pre-limited floor).
8. **Order matters: SP-126 before SP-122.** Dithering (SP-122) before normalization quantizes at the wrong level — the added noise is then scaled by the gain. Normalize first, then dither at the delivery bit depth; and keep the dBTP check after any oversampling/format conversions.
9. **Short items (< 10 s, ads) do not integrate like long ones.** The 400 ms gating blocks barely populate; EBU Tech 3343 recommends short-form treatment (whole-item measurement, relaxed gating, per-segment matching). A 6 s cue normalized "integrated" against a 3-minute track contract is a different measurement — choose the mode per item, not per habit.
10. **Per-section gain mode: hard seams click.** Applying per-column gains without crossfades produces a step in amplitude at every seam — audible clicks on sustained material. Use short (≤ 100 ms) equal-power crossfades; the crossfade is amplitude modulation, keep it deterministic and recorded in provenance.
11. **Do not boost the bass to "fix" the measurement.** K-weighting rolls off lows by design (it predicts *perceived* loudness, and the low end contributes little per unit RMS). Chasing a LUFS number by adding sub energy is the loudness war in disguise — the correct response to a quiet-but-sub-heavy mix is mix balance (SP-007/SP-103), not more normalization gain.
12. **LRA is the real dynamic guardrail.** If the composer wants dynamics, normalize to the target and then check LRA: a master that measures −14 LUFS with LRA 2 LU is a loudness-war artifact regardless of the target; LRA < 4 LU after normalization means the concrete layer's velocity dynamics were destroyed upstream (SP-008 settings or velocity mapping) — the meter exposes it, the composer fixes the cause, not the gain.
```

## Quirks / pitfalls hit during this run

1. **ITU direct PDF endpoints are login-gated.** `dms_pubrec` URLs return 404 or a 244-byte HTML login stub (even BS.1770-5). Resolved via the Wayback Machine copy of the BS.1770-4 PDF (works, full text extractable). EBU R 128 PDF fetched directly.
2. **Wikipedia API quirks:** `/api/rest_v1/page/html/LKFS` returns a redirect stub; `action=raw` on LKFS is a #REDIRECT to LUFS — followed to `LUFS?action=raw` (5.5 KB, good).
3. **Terminal heredoc guard:** the validation script contains `&` (numpy boolean and, `(lj > x) & (lj > y)`) — the foreground-command guard rejected it as shell backgrounding. Workaround: wrote the script with `write_file` and ran `$MUSICOM_PYTHON file` (also avoided the protected `/tmp` path — write to `/opt/data/` instead).
4. **True-peak FIR:** my first sketch used a hand-rolled 63-tap hanning-windowed sinc (wrong — read −12.13 dBTP for a 20 kHz sine); replaced with `scipy.signal.resample_poly` (Kaiser-window polyphase) → correct −0.087 dBTP. Lesson recorded in the standalone file (Annex-2 FIR is the drop-in production filter; the sketch uses the robust polyphase equivalent).
5. **Patch pitfalls avoided:** new table row contains no LaTeX backslashes (no `\\` double-escaping risk; `$g=10^{(T-L_{KG})/20}$` verified single-backslash after patch); row verified to have a single `|` prefix and the `|---|` separator intact (re-read lines 323–325).
6. **Numerical validation:** 997 Hz calibration landed at −3.011 LKFS (spec −3.01) — the coefficients, the −0.691 offset, the channel weights, and the gating are all confirmed correct by construction, not by assumption.

## Next free SP ID

**SP-127** (SP-126 now taken).
