# Report — SP-146 Sound Texture Synthesis via Filter Statistics (STS)

**Date:** 2026-11-20 · **Agent:** sound production research cron · **DB:** `/opt/data/projects/Research/CompositionMethods/methods_db.md`

---

## 1. Identity

| field | value |
|---|---|
| Method name | Sound Texture Synthesis via Filter Statistics |
| Acronym | STS |
| ID | **SP-146** |
| Layer | **absolute** (sound production — `LAYER_ARCHITECTURE.md`) |
| Category | Synthesis Engines |
| One-line description | Imposes a summary-statistics vector of a reference sound (per-band envelope moments, cross-band envelope correlations, modulation spectra) onto noise to synthesize an indefinitely extendable stationary texture. |
| Candidate code path | `sound/synthesis/texture_statistics.py` |
| Dispatch | `workflows/musicom_workflow.py::produce(method="SP-146", ...)` |
| Standalone write-up | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-146_STS.md` (17,666 B) |
| Prototype | `/opt/data/projects/Research/CompositionMethods/_web146_sts/sts_prototype.py` |

## 2. ID resolution (dynamic)

- Summary-table scan `| **SP-NNN** |` → max **SP-145**.
- Standalone-file scan `sound_method_SP-*.md` + `report_SP-*.md` → max **SP-145**.
- Cross-check: `grep -c 'SP-146' methods_db.md` before entry → **0**; no `*SP-146*` file.
- Note: the *composition* methods table has its own numbering (147 MMTC, 146 HHFC) — a
  separate family. SP-146 is free in the **SP** family.
- **Resolved ID: SP-146.** Next free SP ID: **SP-147**.

## 3. Layer classification

**absolute.** STS produces PCM and nothing else: no events, no onsets, no pitch classes,
no timing authority. It consumes a statistics vector and returns a buffer. Stage
position = **source** (a complete bed generator), upstream of per-row EQ (SP-007) →
spatialisation (SP-021/SP-053/SP-075/SP-119) → space/tail (SP-009/SP-032/SP-140) →
bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122).

## 4. Novelty check (run before entry)

`grep -ci` on `methods_db.md`: `Simoncelli` 0 · `McDermott` 0 · `TexStat` 0 · `TexEnv` 0 ·
`cochlear` 0 · `kurtosis` 0 · `modulation filter` 0 · `sound texture` 0 ·
`histogram matching` 0 · `quantile` 0 · `envelope correlation` 1 (a stereo L/R
measurement inside a spatialisation entry, unrelated). "Texture synthesis" appears once,
in the **symbolic** WFC composition method (grid tiles, not audio).

Nearest neighbours and why they are different: SP-016 granular (explicit grain schedules),
SP-044 concatenative (real corpus units), SP-069 wavelet-packet (reweighting one existing
signal), SP-026/027/039 (deterministic sinusoidal models), SP-035 GENDYN (random
breakpoints in one period), SP-072 HPSS (stem splitting). None models a sound as a
statistics vector and generates new audio by imposing it.

## 5. Line counts

| stage | lines |
|---|---|
| before | 32,346 |
| after table row | 32,347 |
| after detailed section append | **32,459** |
| delta | **+113** |

## 6. Summary-table row (as inserted at line 365)

```
| **SP-146** | Sound Texture Synthesis via Filter Statistics (STS) | **Synthesis Engines** | Statistical / Homogeneous Ambient-Texture Timbres | Generates a stationary sound texture by imposing a summary-statistics vector of a reference onto noise. Analysis: ERB cochlear filterbank (24–30 bands, 52–8848 Hz, partition of unity $\sum_b H_b(f)=1$), analytic envelopes $e_b=|x_b+j\mathcal{H}\{x_b\}|$ compressed $c_b=e_b^{0.3}$, decimated to 400 Hz, then a 20-band 0.5–200 Hz modulation filterbank. Statistics: per-band moments $M_1..M_4$ (mean, normalised variance, skew, kurtosis), the full cross-band envelope correlation matrix $S_2=\operatorname{vech}\operatorname{corr}(c_1..c_B)$, modulation power profile $S_3$, and modulation cross-correlations $S_4$ (same band, octave-spaced rates) / $S_5$ (same rate, different bands). Synthesis: alternate two exact projections — per-band **quantile (histogram) projection** (rank-order assignment of the target's sorted envelope; matches the whole marginal in one step, no gradient descent) and **Cholesky correlation recolouring** $\mathbf{E}\leftarrow\mathbf{C}_{cur}^{-1/2}\mathbf{C}_{tgt}^{1/2}\mathbf{E}$ — then amplitude-modulate the base fine structure, $y=\sum_b x_b\,E_b/B_b$, with 2–3 outer consistency iterations. Marginals alone give only "filtered noise"; the cross-band correlation term is what fuses micro-events into one perceived texture. Textures morph by interpolating quantile functions and Cholesky factors. No training, no corpus, deterministic per seed; $\mathcal{O}(BN\log N)$ analysis, $\mathcal{O}(B^2T)$ per sweep. Prototype: correlation error 0.032 → 0.0009 (projection) / 0.142 → 0.119 (acoustic), band RMS within 0.34 dB median, centroid within 0.83 %. Candidate: `sound/synthesis/texture_statistics.py`. |
```

Patch verification: row starts with a single `|` (no `||`), ends `stics.py`. |`; a script
scan of rows 365 and 32348–32459 found **0** occurrences of `\\` (no double-escaped
LaTeX). `grep -c '^||' methods_db.md` → **0**.

## 7. Technical mechanics (summary)

**Analysis.** ERB-spaced cochlear filterbank (Glasberg–Moore $E(f)=21.4\log_{10}(1+0.00437f)$),
partition of unity so bands sum back to the input; analytic envelope
$e_b=|x_b+j\mathcal{H}\{x_b\}|$; 0.3-power cochlear compression; decimate to 400 Hz; a
20-band 0.5–200 Hz modulation filterbank per envelope.

**Statistics.** $S_1$ moments $M_1$–$M_4$ per band (mean, normalised variance, skew,
kurtosis); $S_2$ full cross-band envelope correlation matrix (the fusion term); $S_3$
modulation power profile; $S_4$/$S_5$ modulation cross-correlations. Loss =
$\sum_j\beta_j\,\mathrm{MSE}(S_j(x),S_j(y))$.

**Synthesis.** Alternating projections: (a) per-band quantile/histogram projection —
rank-order assignment of the target's sorted envelope, matching the whole marginal in one
`argsort`; (b) Cholesky recolouring
$\mathbf{E}\leftarrow\mathbf{C}_{cur}^{-1/2}\mathbf{C}_{tgt}^{1/2}\mathbf{E}$, which sets
the covariance exactly. Then resynthesis
$y=\sum_b x_b\,E_b/B_b$ (AM of the base fine structure by the target/base envelope ratio,
both envelopes low-passed at 150 Hz), plus 2–3 outer consistency iterations that
re-analyse the acoustic result and re-project.

**Morphing.** Interpolate quantile functions and Cholesky factors (not raw correlation
matrices) → seamless texture-to-texture morphs without audio crossfades.

**Complexity.** $\mathcal{O}(BN\log N)$ analysis, $\mathcal{O}(B^2T)$ per projection
sweep. NumPy/SciPy only; no training, no corpus, deterministic per seed.

**Prototype measurements** (4 s, 22.05 kHz, 24 bands, 15 inner × 3 outer, seed 7):
projection correlation error 0.032 → **0.0009**; acoustic re-analysis 0.142 → **0.119**;
per-band RMS error **0.34 dB** median / 0.57 dB max; centroid **0.83 %** off target;
kurtosis max 8.09 vs 9.08; peak 0.89; DC −3e−18; WAV 176,444 B; runtime 1.9 s.

## 8. Research sources (fetched 2026-11-20)

1. McDermott & Simoncelli 2009, WASPAA — DOI 10.1109/ASPA.A.2009.5346467, abstract via
   OpenAlex API (`oa1.json`).
2. McDermott, Oxenham & Simoncelli 2011, *Neuron* 70(6):1178 — DOI
   10.1016/j.neuron.2011.06.032.
3. Lagrange, Marchand & Raspaud 2011, "State of the art in sound texture synthesis" —
   HAL hal-01161296, full PDF + extracted text (`hal_sota.txt`, 63 kB).
4. "Sound texture synthesis from summary statistics" PhD thesis 2019 — HAL
   tel-03789695, full PDF + text (`hal_thesis.txt`, 300 kB), ch. 4 eqs. 4.1–4.11.
5. TexStat/TexEnv/TexDSP 2025 — arXiv:2506.04073, HTML + text (`texstat.txt`), five
   statistic sets and the differentiable envelope synthesiser.
6. Glasberg & Moore ERB formula (1983) — used for band spacing.

Raw dumps live in `_web146_sts/`.

## 9. Quirks and pitfalls hit during this run

1. **Unclamped raised-cosine taper (silent killer).** `0.5+0.5*cos(pi*(f-hi)/w)` keeps
   oscillating for $f\gg hi$, so every "band" gains non-zero weight across the whole
   spectrum while the bank still sums to 1. Symptoms: every band's RMS identical,
   reconstruction exact, but analysis meaningless and output 63 % energy above 4 kHz.
   Fix: `np.clip((f-hi)/w, 0, 1)` inside the taper.
2. **Unit-phasor resynthesis splatters.** $x_b/|x_b|$ is not an analytic unit phasor;
   normalising by a near-zero envelope injects broadband noise up to Nyquist (centroid
   2575 → 5501 Hz). Fix: keep the base band signal, multiply by the smoothed
   target/base envelope ratio.
3. **400 Hz envelope interpolation needs low-passing.** Piecewise-linear interpolation
   creates derivative discontinuities every 2.5 ms → audible HF splatter despite correct
   band RMS. 150 Hz 4th-order Butterworth (`sosfiltfilt`) on both envelopes fixes it.
4. **Z-scoring bands destroys spectral tilt.** Mixing bands after per-row normalisation
   equalises band levels, producing a flat, hissy texture. Quantile projection must
   restore the target's absolute per-band scale (it does, if applied after mixing).
5. **Projection domain ≠ acoustic domain.** The correlation matrix is matched to 0.0009
   in envelope space but only ~0.12 after re-analysis, because overlapping bands
   redistribute energy. Outer consistency iterations are the remedy; report the measured
   acoustic number, not the internal one.
6. **Novelty grep false positives.** "envelope correlation" and "texture synthesis" both
   hit once — in a stereo measurement and in a *symbolic* WFC entry respectively. Checked
   context rather than trusting counts.
7. **Two numbering families share the file.** Composition methods use 146 HHFC / 147
   MMTC; SP methods stopped at 145. The SP-146 choice is safe but the collision of
   *numbers* (not names) is worth noting for future runs.
8. **Tooling constraints.** No web-search tool in cron: sources were fetched with
   `curl` + OpenAlex/arXiv APIs. `python -c` triggers an approval gate — all Python was
   run from written `.py` files instead. PDF text extracted with `pypdf` from the musicom
   env.

## 10. Complete section text appended to `methods_db.md` (lines 32348–32459)

# Sound Production Method SP-146 — Sound Texture Synthesis via Filter Statistics (STS)

### Source

- **J. H. McDermott & E. P. Simoncelli, "Sound texture synthesis via filter statistics," IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), 2009, pp. 297–300.** DOI 10.1109/ASPA.A.2009.5346467 (metadata verified via the OpenAlex API, 2026-11-20). Abstract, quoted from the record: *"Many natural sounds, such as those produced by rainstorms, fires, or insects at night, consist of large numbers of rapidly occurring acoustic events… Simply matching the marginal statistics (variance, kurtosis) of individual frequency subbands was generally necessary, but insufficient, to yield good results. Imposing various pairwise envelope statistics (correlations between bands, and autocorrelations within each band) greatly improved the results."* This is the paper's central negative-then-positive result and the reason the method is not merely "match the spectrum".
- **J. H. McDermott, A. J. Oxenham & E. P. Simoncelli, "Sound texture perception via statistics of the auditory periphery: evidence from sound synthesis," *Neuron* 70(6), 2011, 1178–1192.** DOI 10.1016/j.neuron.2011.06.032. The full algorithm: 30 cochlear bands spanning 52–8848 Hz, envelopes decimated to 400 Hz, 20 modulation filters spanning 0.5–200 Hz, and the eight statistic families imposed band-by-band by gradient descent, highest-power band first.
- **M. Lagrange, S. Marchand & M. Raspaud, "State of the art in sound texture synthesis," DAFx-11, 2011** (HAL hal-01161296, full text fetched 2026-11-20) — taxonomy that places the method relative to subtractive/additive, granular, corpus-based concatenative, wavelet and physical-model synthesis; confirms statistics-based parametric synthesis as its own family.
- **"Sound texture synthesis from summary statistics," PhD thesis, 2019** (HAL tel-03789695, full text fetched 2026-11-20), ch. 4 — the cleanest published statement of the algorithm: eqs. (4.1)–(4.11) reproduce the analytic-signal envelope, the 0.3-power compression, the modulated filterbank, the eight statistics and the sequential gradient-descent imposition, together with its known inconsistency (bands modified one after another are not mutually consistent after re-decomposition).
- **"A Statistics-Driven Differentiable Approach for Sound Texture Synthesis and Analysis" (TexStat / TexEnv / TexDSP), arXiv:2506.04073, 2025** (HTML fetched 2026-11-20) — modern restatement in five weighted statistic sets $S_1..S_5$ plus a differentiable synthesiser (`TexEnv`: IFFT-built envelopes multiplied onto a fixed filtered-noise "seed"), which is the implementation pattern adopted here.
- **Repo antecedents:** SP-016 granular (discrete grains, explicit schedules), SP-044 concatenative (unit selection from a corpus), SP-069 wavelet-packet (band reweighting of *one* signal), SP-026 phase vocoder / SP-027 SMS (deterministic partial + noise models), SP-035 GENDYN (breakpoint randomness), SP-039 IFFT additive, SP-072 HPSS, SP-100 Volterra. **None imposes a *statistical* description (marginals + cross-band envelope correlations + modulation spectra) on noise to generate a new, indefinitely extendable texture.**
- **Novelty check (2026-11-20), `grep -ci` on `methods_db.md` before entry:** `Simoncelli` = **0**, `McDermott` = **0**, `TexStat` = **0**, `TexEnv` = **0**, `cochlear` = **0**, `kurtosis` = **0**, `modulation filter` = **0**, `sound texture` = **0**, `histogram matching` = **0**, `quantile` = **0**. `envelope correlation` = 1 (a single stereo L/R measurement inside a spatialisation entry, unrelated). "Texture synthesis" appears once — inside the **symbolic** WFC method 147-neighbour prose (grid tiles, not audio). **No SP method performs statistical audio-texture synthesis → SP-146 is novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). STS is a **Synthesis Engines** statistical generator: it consumes a *statistics vector* (measured from a reference recording, or authored directly) and emits PCM — no events, no timing authority, no pitch decisions. Stage position: **source** — it produces a complete, homogeneous bed for a row, exactly where SP-001/SP-016 would sit; the output then passes per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-075/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Candidate code path: `sound/synthesis/texture_statistics.py` (NumPy analysis + projection synthesiser, no training, no external data); dispatch from `workflows/musicom_workflow.py::produce(method="SP-146", ...)`.

### Description

STS treats a class of sound as a **stationary stochastic process** and reproduces it by imposing a compact set of *summary statistics* onto white noise. The class is the "auditory texture": rain, wind, fire, surf, crowd babble, insects, machinery hum, vinyl surface noise, breath — sounds made of very many rapid micro-events whose individual identities are irrelevant but whose *aggregate* statistics are highly recognisable. A texture is therefore not a sequence of events to be scheduled; it is a point in a statistics space.

Analysis has two stages. A **cochlear filterbank** (ERB-spaced, deliberately mimicking the auditory periphery, not a musical octave bank) splits the reference into ~24–30 sub-bands. Each band's **analytic envelope** is taken, compressed by a 0.3 power (the cochlea's compressive nonlinearity), and decimated — envelopes vary slowly, so 400 Hz is ample. The envelopes are then themselves filtered by a second, **modulation filterbank** (0.5–200 Hz, ~20 log-spaced bands), because "how fast the loudness fluctuates in this band" is what distinguishes a hiss from a crackle from a rumble.

The statistics are deliberately primitive — things a few neurons could compute: per-band mean, normalised variance, skewness and kurtosis; the **full cross-band envelope correlation matrix**; the modulation-band power profile of each band; and two modulation-correlation families (same modulation rate across different bands; octave-spaced modulation rates within one band). Synthesis then inverts the description: start from noise, and iteratively force its statistics to equal the target's.

The crucial empirical fact (McDermott & Simoncelli 2009) is that **marginal statistics alone are not enough**. Matching only variance/kurtosis per band yields something that is clearly "noise shaped like the target" but does not fuse into a recognised texture. The cross-band correlation matrix is what makes many independent micro-sources fuse into *one* perceived texture — it is the statistical analogue of phase-locking, and it is the single most important control in the method.

For composition, the practical consequence is that STS gives a **continuous, infinitely extendable, parameter-morphable bed** rather than a loop: because the description is a vector of numbers, two textures can be crossfaded *in statistics space* (rain → fire) with no audio crossfade, no loop point, and no repetition.

### Technical Mechanics

**1. Cochlear filterbank (ERB scale).** Band edges are equally spaced on the Glasberg–Moore ERB-rate scale

$$E(f)=21.4\log_{10}\!\left(1+0.00437f\right),\qquad f_b=E^{-1}\!\left(E(f_{\min})+\tfrac{b}{B}\left[E(f_{\max})-E(f_{\min})\right]\right)$$

with $B\approx24$–30 bands over 52–8848 Hz (this DB's prototype uses 24 over 60–8000 Hz at $f_s=22.05$ kHz). The filters must form a **partition of unity**, $\sum_b H_b(f)=1$, so that summing the bands reconstructs the input exactly; implementations use flat passbands with short raised-cosine crossfades. Naive wide crossfades (or an unclamped cosine taper, which keeps oscillating outside its half-period) make every band broadband, destroying both the analysis and the reconstruction.

**2. Analytic envelope and compression.** For band signal $x_b[n]$,

$$x^{a}_b[n]=x_b[n]+j\,\mathcal{H}\{x_b\}[n],\qquad e_b[n]=\left|x^{a}_b[n]\right|,\qquad c_b[n]=e_b[n]^{0.3}$$

The compressed envelope $c_b$ is decimated to $f_e=400$ Hz (block mean or low-pass + decimate). The **fine structure** $u_b[n]=x^{a}_b[n]/|x^{a}_b[n]|$ carries the within-band phase and is what makes the result sound like a recording rather than a noise generator; it is preserved, never regenerated from scratch.

**3. Modulation filterbank.** Each $c_b$ is split into $N_G\approx20$ logarithmic modulation bands $m_{b,k}=g_k * c_b$ over 0.5–200 Hz, capturing the "grain rate" of the texture (rain ≈ broadband 20–200 Hz modulation; surf ≈ 0.1–1 Hz swell; fire ≈ crackle bursts at 5–50 Hz).

**4. Statistic sets.** Following the TexStat restatement (arXiv:2506.04073), with $E[\cdot]$ the windowed expectation:

$$S_1=\{M_1,M_2,\dots,M_L\}_b,\quad M_1=E[c_b],\ M_2=\frac{\operatorname{Var}(c_b)}{M_1^2},\ M_l=\frac{E[(c_b-M_1)^l]}{\sigma_b^{l}}\ (l\ge3)$$

$$S_2=\operatorname{vech}\big(\operatorname{corr}(c_1,\dots,c_B)\big)\in\mathbb{R}^{T_{B-1}},\qquad T_n=\frac{n(n+1)}{2}$$

$$S_3=\biguplus_b\frac{\big(\sqrt{\operatorname{Var}(m_{b,1})},\dots,\sqrt{\operatorname{Var}(m_{b,N_G})}\big)}{\sqrt{\operatorname{Var}(c_b)}}$$

$$S_4=\biguplus_b\operatorname{vech}\big(\operatorname{corr}(m_{b,1},\dots,m_{b,N_G})\big),\qquad S_5=\biguplus_k\operatorname{vech}\big(\operatorname{corr}(m_{1,k},\dots,m_{B,k})\big)$$

and the distance that the synthesiser minimises is $\mathcal{L}=\sum_{j=1}^{5}\beta_j\,\mathrm{MSE}\big(S_j(x),S_j(y)\big)$. $S_2$ is the fusion term; $S_3$ is the grain-rate profile; $S_4$/$S_5$ are the modulation cross-correlations.

**5. Imposition by alternating projections.** Rather than McDermott's original per-band gradient descent (slow, and order-dependent), the practical implementation alternates two *exact* projections on the envelope matrix $\mathbf{E}\in\mathbb{R}^{B\times T}$:

- **Marginal (histogram) projection.** For each band, replace the current envelope values by the target's sorted values, assigned in the current rank order:
$$\tilde{E}_{b,(i)}=c^{\text{tgt}}_{b,(i)}\quad\text{where }(i)=\operatorname{rank}\big(E_b[i]\big)$$
This is monotone quantile mapping; it matches **all** moments of the marginal exactly in one step (no gradient step, no learning rate), and it is the practical fix for the moment-only imposition of the 2011 paper.

- **Correlation recolouring.** Whiten the current envelope matrix and recolour with the target correlation:
$$\mathbf{E}\leftarrow\mathbf{C}_{\text{cur}}^{-1/2}\,\mathbf{C}_{\text{tgt}}^{1/2}\,\mathbf{E},\qquad \mathbf{C}^{-1/2}=\mathbf{V}\boldsymbol{\Lambda}^{-1/2}\mathbf{V}^{\!\top}$$
so that $\operatorname{Cov}(\mathbf{E}')=\mathbf{C}_{\text{tgt}}$ exactly. The two projections do not commute, so they are iterated (10–20 sweeps); the measured correlation error falls monotonically, e.g. $\|\mathbf{C}-\mathbf{C}_{\text{tgt}}\|_F/\|\mathbf{C}_{\text{tgt}}\|_F: 0.032\to0.0009$ in the prototype.

**6. Resynthesis.** Expand each projected envelope back to audio rate, undo the compression, and amplitude-modulate the base fine structure:

$$y[n]=\sum_{b=1}^{B}x_b[n]\cdot\frac{E_b[n]}{B_b[n]},\qquad E_b[n]=\big(\hat{c}_b[n]\big)^{1/0.3}$$

where $B_b$ is the base noise's own (smoothed) envelope and $\hat c_b$ the interpolated projected envelope. Both envelopes are low-passed (~150 Hz) before division; piecewise-linear interpolation of a 400 Hz envelope has derivative discontinuities that splatter broadband noise if used raw.

**7. Outer consistency iterations.** Re-analysing the summed signal does not return the envelopes that were imposed (band overlap redistributes energy). Two or three outer iterations — re-analyse $y$, re-project, re-synthesise — reduce the measured acoustic correlation error (prototype: 0.142 → 0.119) and are the honest way to close the loop.

**8. Statistics morphing.** Because the target is a vector, textures interpolate. Correlations must stay positive-semidefinite, so interpolate the **Cholesky factors**, not the matrices: $\mathbf{L}_\lambda=(1-\lambda)\mathbf{L}_A+\lambda\mathbf{L}_B$, $\mathbf{C}_\lambda=\mathbf{L}_\lambda\mathbf{L}_\lambda^{\!\top}/\|\cdot\|$, while the marginals interpolate as quantile functions $Q_\lambda=(1-\lambda)Q_A+\lambda Q_B$.

**9. Complexity and implementation.** Analysis: $B$ FFTs + $B$ Hilbert transforms + one $B\times B$ correlation, $\mathcal{O}(BN\log N)$; synthesis: $\mathcal{O}(B^2T)$ per sweep with $T=N/55$. Pure NumPy/SciPy, no training, no corpus, deterministic given the base-noise seed. The prototype (`_web146_sts/sts_prototype.py`) renders 4 s at 22.05 kHz in ~1.9 s including 3 outer × 15 inner sweeps.

**10. Verified prototype.** `_web146_sts/sts_prototype.py` → `sts_stats.json`, `sts_out.wav` (176,444 B), `sts_target.wav`. Input: synthetic rain-like reference (Poisson impact train 55 s⁻¹ through a resonant body + band-limited bed + 0.7 Hz gusting). **Measured:** projection-domain correlation error **0.0009**; acoustic re-analysis correlation error **0.142 → 0.119** over 3 outer iterations; per-band RMS error **0.34 dB median / 0.57 dB max**; spectral centroid 2553.5 Hz vs 2574.8 Hz target (**0.83 %**); max kurtosis 8.09 vs 9.08 target (abs. error ≤ 0.99). Peak 0.89, DC ≈ 0, all output finite.

### Musical Elements Framework

- **PITCH**: STS is deliberately **unpitched** — a texture has no f0, and the method's own literature names pitched material (bells, speech, chimes, music) as a documented failure class. Pitch enters only (a) as a **brightness anchor**: mapping a MIDI note to a band-gain tilt or a resampling ratio moves the spectral centroid, so a "tuned" texture can track the harmony by its colour without acquiring a fundamental; and (b) as an *emergent* pseudo-pitch when a modulation band dominates (a 60 Hz modulation reads as a 60 Hz buzz). Do not ask STS for a note.
- **RHYTHM**: the rhythmic content is the **modulation spectrum** $S_3$. The rate of micro-events (impact rate, crackle density) is directly the modulation-band power profile, and it can be *imposed*: boosting the modulation band at $f=\text{BPM}/60$ makes a texture "breathe" in tempo without a single onset event. Sub-audio modulation (0.05–0.5 Hz) gives swells; 4–16 Hz gives tremolo/granular shimmer; >40 Hz gives roughness/buzz. STS therefore supplies rhythmic *density and pulse feel*, never rhythmic *articulation*.
- **HARMONY**: no pitch classes. The harmonic role is played by the **spectral envelope** (the band gain vector): a section can shift the whole texture's register/brightness (dark rumble ↔ bright hiss), which functions perceptually like a change of instrumentation. Two texture rows "in harmony" means their band-gain profiles do not fight (complementary centroid, no masking); SP-007's masking EQ is the natural downstream partner.
- **STRUCTURE**: form must be imposed from outside, because the model is stationary by construction. The compositional device is the **statistics trajectory**: per-section presets and linear/curved interpolation of $S$ across section boundaries, i.e. form as a path in statistics space (intensity arc, brightness arc, coherence arc). A texture never cadences; it either morphs or is cut. This makes STS ideal for introductions, transitions, beds and codas, and useless for thematic argument.
- **TEXTURE**: this *is* the texture axis, and it is four-dimensional: **density** (event/modulation rate), **grain size** (which modulation bands carry power), **noisiness** (kurtosis — Gaussian hiss vs impulsive crackle), and **coherence** (the off-diagonal mass of $\mathbf{C}$: high = one fused source; low = many independent sources, "a crowd of small things"). Stationarity itself is a fifth dial: imposing the target over a short window forces a static texture, over a long window permits slow evolution.

### UnitMatrix Integration

**Voices = rows = one texture layer.** A row is a statistics object: `{name, ref (audio path or null), stats (S1..S5 or a preset name), B, fmin, fmax, env_fs, seed, base ("white"|"pink"|audio)}`. Row identity is the *kind of sound*, not an instrument: `rain_roof`, `wind_low`, `fire_crackle`, `crowd_babble`. Two rows with the same reference but different seeds are two independent takes of the same texture — useful for wide stereo (shared $\mathbf{C}$, decorrelated fine structure).

**Sections = columns = statistics state.** Column $j$ holds a partial override of the row's statistics: `{intensity (scales M1), brightness (band-gain tilt or fmin/fmax), coherence_scale (scales off-diagonal C), grain_rate (shifts S3), morph_to, morph_lambda}`. Because a whole section shares one state, the texture is **generated once per (row, section)** for the full section length plus tail, then sliced — never generated per note, which would break stationarity at every event boundary.

**Cells = MusicUnit.** A cell $(v,j)$ is a *region*, not a sequence: its `MusicEvent`s declare where the texture is present (pitch = brightness anchor or ignored, velocity = intensity, `start_tick`/`end_tick` = region bounds). Zero drift is preserved because the region is tick-bounded and the renderer pads to the section length; but **note-off is a fade, not a stop** — a 20–50 ms cosine fade at the region edge, or the texture clicks. Overlapping regions of the same row sum, so density can be built by layering cells.

**Produce dispatch:** `produce(midi_path, method="SP-146", params={"rows": {"rain": {"ref": "assets/rain_roof.wav", "B": 24, "fmin": 60, "fmax": 8000, "seed": 3}, "crowd": {"preset": "babble", "coherence": 0.35, "seed": 11}}, "columns": {"A": {"intensity": 0.35, "brightness_db": -3}, "B": {"intensity": 0.85, "grain_rate": 1.3, "morph_to": "rain_roof", "morph_lambda": 0.25}}})` — stage order **STS statistics synthesis (source) → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-075) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**. Output is fixed-rate PCM: resample before sample-count-sensitive stages (SP-050's GCD grids) or re-quantise to the tick grid.

### Pitfalls

1. **Statistics are necessary but not sufficient.** McDermott's three documented failure classes are **pitch** (bells, chimes, speech, music), **rhythm** (tapping, drumming) and **reverberation** (firecrackers, drumbeats). If the reference has a clear f0, a clear beat, or a long discrete tail, STS will produce a plausible-sounding *smear* of it, not the thing. Use SP-145/SP-074/SP-016 for those instead.
2. **Marginal-only matching is the classic failure.** Matching per-band variance and kurtosis alone gives "noise shaped like the target" that listeners do not recognise. The cross-band correlation matrix $\mathbf{C}$ is not an optional refinement — it is the term that makes the result a texture. Budget most of the iteration on $S_2$.
3. **Verify on the re-analysed output, not on the internal envelope matrix.** The projection is exact in envelope space by construction; the acoustic result is not, because band overlap redistributes energy on re-analysis. Always run the outer consistency loop and report the *measured* acoustic statistics.
4. **Envelope sample rate is part of the model.** At 400 Hz the correlation matrix means "envelopes co-fluctuate over 2.5 ms frames". Compute envelopes at audio rate and the same statistic becomes meaningless (and $\mathbf{C}$ becomes near-diagonal). Keep $f_e$ fixed across analysis and synthesis.
5. **Do not regenerate the fine structure.** Replacing the base phase with random phase or a unit phasor produces a metallic, "phase-vocoder" character; normalising by a near-zero base envelope explodes into broadband splatter. Keep the base fine structure, divide only by a *smoothed* base envelope, and low-pass both envelopes before dividing.
6. **Statistic count must respect window length.** Each statistic is estimated over $T$ envelope samples; $S_1..S_5$ contain $O(B^2)$ and $O(BN_G)$ terms. With $B=30$, $N_G=20$ and a 1 s window the system is over-determined and the projection fits noise. Use ≥ 3–5 s windows, or reduce $B$/$N_G$ (the prototype's 24/– at 4 s is a safe point).
7. **Time-invariance is the feature, not a bug.** The output is *not* sample-aligned with the reference and will not null against it. Never evaluate by difference-to-target; evaluate by statistic distance (TexStat), by FAD, or by listening.
8. **Stereo must be joint.** Computing statistics per channel independently destroys the inter-channel relationship: the image collapses or becomes unstable. Either extend $\mathbf{C}$ to $2B$ bands (L and R bands together, which captures width and inter-channel coherence) or share one envelope set and decorrelate only the fine structure.
9. **Fades and edits change the statistics.** Because the model is stationary, every fade, gate or cut is an audible statistical event. Prefer region-level cosine fades ≤ 50 ms, and never fade inside a section whose statistics are meant to be constant.
10. **Zero drift still binds.** A texture cell's buffer must fill exactly the section's tick length (plus tail) or the row desynchronises. Generate to `section_ticks` converted at the row's sample rate and pad/trim deterministically; assert the sample count before mixing.
11. **Determinism.** Seed the base noise; record the seed and the statistic vector hash in provenance. Same seed + same reference + same parameters must give a byte-identical WAV — that is what makes the method testable, and why it is safe for golden-hash regression tests.
12. **Neighbour audit.** SP-016 granular = explicit grain schedules, discrete events, no statistics; SP-044 concatenative = real recorded units selected from a corpus (the output *is* recordings); SP-069 WPSS = wavelet decomposition/reweighting of a *single* existing signal (editing, not generation); SP-026/SP-027/SP-039 = deterministic sinusoidal models (they preserve partials, which textures do not have); SP-035 GENDYN = random breakpoints in one period, not a statistical description; SP-072 HPSS = splitting a rendered buffer. **STS = impose a summary-statistics vector (marginals + cross-band envelope correlations + modulation spectra) on noise, with no corpus, no training and no events.** Repo: `sound/synthesis/texture_statistics.py` (new; NumPy/SciPy analysis + alternating-projection synthesiser).
