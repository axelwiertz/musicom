# REPORT — SP-128 Empirical Mode Decomposition / Hilbert–Huang Adaptive Resynthesis (EMD-HAR)

**Primary record.** Chat delivery was a 6-line caveman summary only; everything is here.

| Field | Value |
|---|---|
| **Method ID** | **SP-128** |
| **Method name** | Empirical Mode Decomposition / Hilbert–Huang Adaptive Resynthesis (EMD-HAR) |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md); no note events emitted, buffer → buffer |
| **Category** | Post-Processing / DSP (data-driven modal decomposition) |
| **One-line description** | Decomposes a rendered buffer, with no fixed basis, into narrowband AM–FM intrinsic mode functions by iterative cubic-spline envelope sifting, then resynthesizes each mode from its own Hilbert instantaneous amplitude/frequency — exactly invertible, so modes can be gained, transposed, gated or deleted individually. |
| **Candidate code path** | `sound/effects/emd_resynthesis.py` (`emd()` → IMFs+residue; `HilbertModes`; `EMDResynthesizer.process()`), dispatched from `workflows/musicom_workflow.py::produce(method="SP-128", params={...})` |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-128_EMDHAR.md` |
| **Verification script** | `/opt/data/projects/Research/outputs/sp128_research/verify_sp128_emd.py` (+ `verify_refs.py`, `verify_refs2.py` for DOI checks) |
| **methods_db.md line count** | **29046 before** → **29146 after** section append (+100) → **29147 after** summary-row insert (+1) |
| **Next free SP ID** | **SP-129** |

---

## 1. ID resolution (dynamic, not assumed)

| Probe | Result |
|---|---|
| `grep -o '\| \*\*SP-[0-9]*\*\*'` on methods_db.md | max = **127**, 124 distinct rows (sparse: gaps exist, e.g. SP-076…086 missing) |
| `ls sound_method_SP-*.md report_SP-*.md` → extract ids | max = **127** (files SP-120…127 present only) |
| `grep '^# Sound Production Method SP-'` (detailed sections) | last = **SP-127** at line 28880 |
| Anomaly checked | The file *ends* with `# Artin Braid Group Composition (ABGC) (Method 129)` — a **composition-method** number, not an SP-ID; SP-127's Pitfall 9 also says "cf. 128 Pitfall 9", which refers to that composition series. Confirmed **not** an SP entry. |
| **Conclusion** | Next free SP-ID = **SP-128** |

Duplicate check before writing: `grep -ci` on methods_db.md → `"empirical mode"` 0, `"Hilbert-Huang"` 0, `"intrinsic mode"` 0, `"sifting"` 0, `IMF` 0, `EEMD` 0, `CEEMDAN` 0. Zero prior coverage of EMD/HHT at any layer. (NMF was rejected as a candidate because method 085 NMF-C already exists — symbolic/composition layer — even though a spectral-domain NMF would be technically distinct.)

---

## 2. Summary-table row as inserted (line 328)

Verbatim:

```
| **SP-128** | Empirical Mode Decomposition / Hilbert–Huang Adaptive Resynthesis (EMD-HAR) | **Post-Processing / DSP** | Data-Driven Modal Re-Orchestration / Per-Mode Band Editing & Transposition | Splits a rendered buffer into finite intrinsic mode functions by iterative cubic-spline envelope sifting $h_{k+1}=h_k-\tfrac12(e_{\max}+e_{\min})$ until $\mathrm{SD}_k<0.2$, then resynthesizes each mode from its Hilbert analytic pair $a_j(t)=\lvert z_j\rvert$, $f_j=\dot\varphi_j/2\pi$. Exact reconstruction $\sum_j c_j+r_n=x$ (verified $1.4\times10^{-14}$); modes behave as a quasi-dyadic filter bank (Flandrin 2004 — real-render centroids 4657/1986/810/330/184/57 Hz); transposition by IF scaling $a_j\cos(2\pi r\!\int\! f_j)$ is exact on narrowband modes (verified ratio 1.500). Mode mixing is the default failure (EEMD/CEEMDAN cures, but they break completeness). 20–45× realtime in NumPy/SciPy. Candidate: `sound/effects/emd_resynthesis.py`. |
```

Post-patch verification (both known pitfalls checked):
- `grep -c '\\\\[a-zA-Z]'` inside the new section = **0**; row-level double-backslash scan = **0** → LaTeX backslashes are single (`\tfrac`, `\varphi`, `\sum` intact).
- Row starts with a single `|` and contains exactly **6** pipe characters (5 columns) → no `||` prefix, column count matches the header.
- Table header format re-read: `| Method ID | Method Name | Layer | Target Output | Description / Integration |`.

---

## 3. Research summary (technical mechanics)

**Sifting.** Envelopes $e_{\max},e_{\min}$ through local extrema by natural cubic spline; iterate
$h_{k+1}=h_k-\tfrac12(e_{\max}+e_{\min})$ until $\mathrm{SD}_k=\sum(h_{k-1}-h_k)^2/\sum h_{k-1}^2<\theta\approx0.2$.
Result is an IMF (extrema/zero-crossing count balanced, zero-mean envelopes). Outer loop subtracts
each IMF and re-sifts the residual → $x=\sum_j c_j+r_n$ exactly.

**Hilbert spectral analysis.** $z_j=c_j+j\mathcal H[c_j]$ gives $a_j=|z_j|$ and
$f_j=\dot\varphi_j/2\pi$; Hilbert spectrum $H(\omega,t)=\sum_j a_j\delta(\omega-\omega_j)$,
marginal spectrum $h(\omega)=\int H\,dt$.

**Resynthesis / editing.** $y=\sum_j \gamma_j g_j a_j\cos(2\pi r_j\!\int f_j+\varphi_j(0))$.
Narrowband modes transpose exactly under phase-rate scaling; wideband modes do not (Bedrosian).

**EEMD / CEEMDAN.** Ensemble average over noise-perturbed decompositions cures mode mixing but
destroys completeness (measured 0.45 relative error at M=6, ε=0.3σ); CEEMDAN adds noise to the
residual per stage and restores it.

**Filter-bank property.** Flandrin/Rilling/Gonçalves 2004: IMF index ≈ octave band, so mode
selection is a zero-phase adaptive crossover with no filter design.

**Implementation.** NumPy + SciPy only (`CubicSpline`, `hilbert`, `unwrap`, `gradient`); no
FluidSynth/VST. Measured 21–45× realtime at 44.1 kHz mono.

**Numerical evidence (all run, not assumed):**
reconstruction error **1.394e-14** (6 IMFs, 1 s test signal); monotone-decreasing IMF centroids;
transposition ratio **1.500** exact for 660 Hz and 220 Hz modes (and a nonsense 2.000 for the
wideband trend mode); mode mixing demonstrated (220 Hz moved between IMF2 and IMF3 under 0.05σ
perturbation, index set `[1,3,3,3,3]`); EEMD completeness loss 0.451; burst-concentration test
proving EMD is **not** a transient separator (3.6 % vs 4.5 % uniform); real `compose()`+`produce()`
render decomposed into 6 IMFs in 0.04 s (45× realtime, err 1.7e-16, centroids
4657/1986/810/330/184/57 Hz).

---

## 4. Complete section text appended to methods_db.md (lines 29048–29147, 100 lines)

# Sound Production Method SP-128 — Empirical Mode Decomposition / Hilbert–Huang Adaptive Resynthesis (EMD-HAR)

### Source

- **Huang, N. E., Shen, Z., Long, S. R., Wu, M. C., Shih, H. H., Zheng, Q., Yen, N.-C., Tung, C. C., Liu, H. H. (1998).** "The empirical mode decomposition and the Hilbert spectrum for nonlinear and non-stationary time series analysis." *Proceedings of the Royal Society of London A* **454**(1971), 903–995. DOI 10.1098/rspa.1998.0193 — the founding paper: the sifting algorithm, the intrinsic mode function (IMF) definition, and the Hilbert spectrum. (Verified via Crossref, 2026-10-30.)
- **Wu, Z., Huang, N. E. (2009).** "Ensemble empirical mode decomposition: a noise-assisted data analysis method." *Advances in Adaptive Data Analysis* **1**(1), 1–41. DOI 10.1142/S1793536909000047 — EEMD: add white noise, decompose, average by IMF index; the standard cure for mode mixing. (Verified via Crossref.)
- **Flandrin, P., Rilling, G., Gonçalves, P. (2004).** "Empirical mode decomposition as a filter bank." *IEEE Signal Processing Letters* **11**(2), 112–114. DOI 10.1109/LSP.2003.821662 — proves EMD is effectively a dyadic (quasi-octave) filter bank on wide-sense-stationary noise: IMF index ↔ octave band, $P_j \approx 2^{j}$. The theoretical basis for using EMD as a *band selector*. (Verified via Crossref.)
- **Torres, M. E., Colominas, M. A., Schlotthauer, G., Flandrin, P. (2011).** "A complete ensemble empirical mode decomposition with adaptive noise." *Proc. IEEE ICASSP 2011*, 4144–4147. DOI 10.1109/ICASSP.2011.5947265 — CEEMDAN: noise is added to the *residual* at each stage, which recovers the completeness (exact reconstruction) that EEMD loses and fixes the spurious-IMF problem. (Verified via Crossref.)
- **Boudraa, A.-O., Cexus, J.-C. (2007).** "EMD-based signal filtering." *IEEE Transactions on Instrumentation and Measurement* **56**(6), 2196–2202. DOI 10.1109/TIM.2007.907967 — partial reconstruction from a subset of IMFs as a data-driven filter; the reference for "drop IMF1 as noise" and its failure modes. (Verified via Crossref.)
- **Audio-domain precedents (analysis, not synthesis):** Molla, Hirose, Minematsu (2004), "Audio source separation from the mixture using empirical mode decomposition with independent subspace analysis," *Interspeech 2004*, 2449–2452, DOI 10.21437/interspeech.2004-395 — EMD as a front end for audio source separation; Lai, Chou, Chou, Schuller (2023), "Robust audio watermarking based on empirical mode decomposition and group differential relations," *J. Audio Eng. Soc.* **71**(3), 100–117, DOI 10.17743/jaes.2022.0067 — EMD as an audio-domain embedding/transform tool. Both treat EMD as *analysis*; **neither resynthesizes audio from the modes as a production method.**
- **Adjacent-but-distinct DB neighbours:** SP-026 (STFT phase vocoder — *fixed* linear basis, complex spectrum reused), SP-027 SMS (sinusoidal peak tracks + stochastic residual), SP-069 (wavelet packets — *fixed* QMF basis, octave bands by construction), SP-072 HPSS (median-filter masks, no per-component resynthesis, separates by *temporal character* not by band), SP-108 McAulay-Quatieri (harmonic partial tracks, requires an F0 grid), SP-127 STRAIGHT (F0-adaptive envelope, monophonic, excitation re-synthesis), SP-055 (Hilbert used only for a quadrature frequency shifter). EMD is the only entry whose basis is **data-driven, nonlinear, basis-free and exactly invertible**, and whose components carry their own instantaneous amplitude *and* frequency rather than a fixed bin.
- **Novelty check (2026-10-30):** `grep -ci` on methods_db.md before this entry — `"empirical mode"` = 0, `"Hilbert-Huang"` = 0, `"intrinsic mode"` = 0, `"sifting"` = 0, `IMF` = 0, `EEMD` = 0. No EMD/HHT method exists in the DB at any layer.

### Layer

**absolute** — SP-128 is a sound production method (LAYER_ARCHITECTURE.md): it consumes a *rendered audio buffer* and emits acoustic air pressure. It writes no note events and holds no symbolic state; it sits downstream of any synthesis engine (SP-001/SP-011/SP-029/…) and upstream of the dynamics/loudness chain. Candidate code path: `sound/effects/emd_resynthesis.py` (fit `emd()` → `imfs, residue`; `HilbertModes` for $a_j,f_j$; `resynthesize()` for per-mode gain/transpose), dispatched from `workflows/musicom_workflow.py::produce(method="SP-128", params={...})`. Same family as SP-026/SP-037/SP-072: a buffer processor, not an instrument.

### Description

**Empirical Mode Decomposition (EMD)** answers a question the STFT, the wavelet transform and every sinusoidal model dodge: *what are the natural components of this particular signal?* All fixed-basis transforms impose their basis (sines, or scaled wavelets) and pay for it — an STFT smears a transient across the whole window, a wavelet octave band merges two partials that sit in the same octave. EMD instead **builds the basis from the signal's own extrema**, one oscillatory mode at a time, with no kernel, no window length, no hop size and no F0 assumption.

The algorithm is a nested loop. The inner loop (*sifting*) subtracts the local mean defined by the upper and lower cubic-spline envelopes through the extrema, repeatedly, until what remains is a symmetric, zero-mean oscillation — an **Intrinsic Mode Function (IMF)**: a narrowband AM-FM component with the property that its Hilbert transform is physically meaningful. The outer loop subtracts that IMF from the residual and sifts again, producing modes from highest to lowest frequency and ending with a monotone residue (trend/DC). Because nothing is ever discarded, the decomposition is **exactly invertible**: $x(t)=\sum_j c_j(t)+r_n(t)$ (verified to $1.4\times10^{-14}$ relative error, 1 s @ 44.1 kHz, 6 IMFs).

Two properties make this a *production* method rather than an analysis curiosity:

1. **The modes are a dyadic filter bank** (Flandrin, Rilling & Gonçalves 2004). On broadband material the $j$-th IMF occupies roughly the octave below the $(j-1)$-th, so "keep IMFs 1–3" is a data-driven, zero-phase, signal-adaptive band split that tracks the material instead of a designer's crossover frequency. Measured on a real `compose()`+`produce("SP-001")` render, the IMF spectral centroids came out 4657 / 1986 / 810 / 330 / 184 / 57 Hz — a clean octave ladder with no filter design at all.
2. **Each mode carries its own instantaneous amplitude and frequency** via the Hilbert transform: $z_j(t)=c_j(t)+j\mathcal{H}[c_j](t)=a_j(t)e^{j\varphi_j(t)}$, with $f_j(t)=\dot\varphi_j(t)/2\pi$. Resynthesizing a mode from $(a_j, f_j)$ is lossless, so *editing* one is a surgical operation on one band: transpose it ($f_j \to r f_j$), swell it ($a_j \to g(t)a_j$), gate it, or delete it.

The Hilbert–Huang pipeline is therefore: **sift → analytic pairs → edit per mode → sum**. In the DB's terms it is a *modal re-orchestrator*: you can move a rendered voice's octave strata independently, thin a mix by deleting a mode, or build a "register-split" arrangement from material that was recorded as one sound. It is **not** a source separator (see Pitfall 4) and **not** a replacement for HPSS: EMD stratifies by *frequency*, never by *temporal character*.

### Technical Mechanics

**Sifting (inner loop).** For a real signal $x(t)$, let $e_{\max}(t)$ and $e_{\min}(t)$ be natural cubic splines through the local maxima and minima respectively (Rilling's boundary conditions extended at the ends). The local mean is $m(t)=\tfrac12[e_{\max}(t)+e_{\min}(t)]$ and one sifting step is

$$h_{k+1}(t) = h_k(t) - \tfrac12\big[e_{\max}^{(k)}(t) + e_{\min}^{(k)}(t)\big], \qquad h_0 = x .$$

Iterate until the normalized squared difference falls below a threshold (Huang's SD criterion, typical $\theta = 0.2$):

$$\mathrm{SD}_k = \frac{\sum_t \lvert h_{k-1}(t)-h_k(t)\rvert^2}{\sum_t h_{k-1}^2(t)} < \theta .$$

The result $c_1 = h_K$ is an IMF: (i) the number of extrema and zero crossings differ by at most one; (ii) the mean of its upper and lower envelopes is zero. The outer loop is

$$r_1 = x - c_1,\quad r_2 = r_1 - c_2,\ \dots,\quad r_n = r_{n-1}-c_n, \qquad x = \sum_{j=1}^{n} c_j + r_n .$$

Terminate when the residual has fewer than ~3–4 extrema (it is a trend). Note the count is **not** fixed in advance: $\mathbb{E}[n]\approx\log_2 N$ for broadband noise, so IMF count is itself a signal statistic that must go into provenance.

**Hilbert spectral analysis.** For each IMF, form the analytic signal

$$z_j(t)=c_j(t)+j\,\mathcal{H}[c_j](t),\qquad a_j(t)=\lvert z_j(t)\rvert=\sqrt{c_j^2+\mathcal{H}[c_j]^2},\qquad \varphi_j(t)=\arctan\frac{\mathcal{H}[c_j]}{c_j},$$

$$f_j(t)=\frac{1}{2\pi}\frac{d\varphi_j}{dt}\quad(\text{discrete: } f_j[m]=\frac{f_s}{2\pi}\,\Delta_{\text{unwrap}}\arg z_j[m]).$$

The **Hilbert spectrum** places the amplitude on the instantaneous-frequency curve, $H(\omega,t)=\sum_j a_j(t)\,\delta(\omega-\omega_j(t))$, and its time integral $h(\omega)=\int H(\omega,t)\,dt$ is the *marginal spectrum* — the EMD analogue of a power spectrum that does not assume stationarity and does not leak. This is the feature the DB cares about: the marginal spectrum and the IF tracks are the *score-readable* output of the transform.

**Resynthesis.** Exact: $\hat{x}(t)=\sum_j a_j(t)\cos\varphi_j(t)+r_n(t)$. With per-mode edits (gain $\gamma_j$, transposition $r_j$, envelope $g_j(t)$):

$$\hat{x}(t)=\sum_j \gamma_j\,g_j(t)\,a_j(t)\,\cos\!\Big(2\pi r_j\!\int_0^t f_j(\tau)\,d\tau+\varphi_j(0)\Big)+r_n(t).$$

Verified: a narrowband mode at 660 Hz and one at 220 Hz both transposed to **exactly 1.500×** their original frequency by phase-rate scaling $r_j=1.5$ — no filter, no resampling, no formant drag, because $a_j$ (the envelope) is untouched and only the phase rate changes.

**EEMD / CEEMDAN (mode-mixing cures).** EEMD decomposes $M$ noise-perturbed copies and averages by index:

$$x_i(t)=x(t)+\epsilon\,w_i(t),\ w_i\sim\mathcal{N}(0,1);\qquad \bar{c}_j=\frac1M\sum_{i=1}^{M} c_j^{(i)} .$$

The average is *not* a decomposition of $x$ any more — measured reconstruction error with $M=6$, $\epsilon=0.3\sigma$ was **45 %** versus $1.4\times10^{-14}$ for plain EMD. CEEMDAN (Torres et al. 2011) fixes this by adding noise to the running residual per stage, $\tilde r_j = r_j + \beta_j E_1[w]$, keeping completeness; cost is $M\times$ the sifting.

**Implementation requirements.** Pure Python + NumPy/SciPy: `scipy.interpolate.CubicSpline` for the envelopes, `scipy.signal.hilbert` for the analytic signal, `np.unwrap`/`np.gradient` for IF. No FluidSynth, no VST, no GPU. Measured cost on this machine (single core, 44.1 kHz mono): 0.5 s → 0.02 s (25× realtime), 1.0 s → 0.03 s (32×), 2.0 s → 0.09 s (21×), and 45× realtime on a real 2 s engine render; each additional sift pass is linear in $N$ plus a tridiagonal spline solve $O(M)$ in the number of extrema.

### Musical Elements Framework

**PITCH.** PITCH is *measured*, not assumed: $f_j(t)$ is the instantaneous frequency of each mode, so EMD gives a partial-tracking read of a buffer with no F0 estimate and no harmonic assumption (it works on inharmonic bells as well as on a flute). Editing: phase-rate scaling $r_j$ transposes a mode exactly ($f \to r f$) while leaving its envelope — the transposition is *formant-free but also register-free*, since a mode has no formants, only a band. Vibrato/portamento can be injected by adding a modulation to $f_j$ before integration, and pitch is stable under amplitude edits (gain does not move $f_j$ at all, unlike a nonlinear chain). The characteristic failure is PITCH *instability*: when a partial is split across two IMFs (mode mixing) its energy flickers between them and the IF of each mode wobbles — audible as roughness on sustained tones.

**RHYTHM.** Rhythm lives in the envelope tracks $a_j(t)$, which are true amplitude envelopes at sample resolution (not frame resolution): onsets are sharp in $a_j$ even when they are smeared in an STFT. Beat-synchronous gating ($a_j \to \text{gate}(t)\,a_j$) is a per-band rhythmic filter; the residue $r_n$ carries the slow "breath" of the section. Time-stretching is *not* free here — unlike SP-026/SP-037 there is no explicit time map, so stretching means resampling the parameter tracks and re-integrating phase, which preserves $a_j$ but not $\varphi_j$ (transients smear). Use EMD for timbral/spectral rhythm (band gating, swells, gesture envelopes), not for time manipulation.

**HARMONY.** Harmony is only *partially* available, and this is the honest limitation: EMD separates by frequency band, and its bands are quasi-octave (Flandrin), so widely spaced chord tones usually land in different IMFs while close intervals (a third, a cluster, a doubled unison) merge into one mode. Consequence: you cannot extract chord tones from an EMD, but you *can* re-orchestrate register strata — move the top octave of a pad up a fifth, darken the low stratum, thin the middle. Cross-row harmony is done by mixing decomposed stems, never by decomposing the sum (EMD is nonlinear: $\mathrm{EMD}(a+b)\neq \mathrm{EMD}(a)+\mathrm{EMD}(b)$).

**STRUCTURE.** Each section (column) can carry an EMD *policy* rather than a filter setting: {IMF subset retained, per-IMF gain, per-IMF transposition, $M$/$\epsilon$ for EEMD}. Because a subset sum is still a legal audio signal, section contrast can be made by mode selection alone: intro = residue + IMF3–4 (dark, body-less), chorus = all modes (full), bridge = IMF1–2 only (bright, brittle). That is a structural gesture with no MIDI change at all — the same property SP-127 exploits in the envelope domain, here in the mode domain. Partial reconstruction also gives a data-driven "arrangement declutter" (drop modes, not instruments).

**TEXTURE.** The mode set *is* the texture: mode count ≈ brightness/complexity, per-mode gain ≈ band balance, residue ≈ weight and drift. Because the split is data-driven, EMD is the natural tool for material whose band structure is not known in advance (field recordings, prepared piano, feedback drones, granular clouds). Sifting the noise floor yields near-geometric band spacing, so recombining a subset of noise modes synthesizes a *colored noise bed with the colour of the source* — texture matching without filter design. The catch (Pitfall 4) is that EMD does not separate "noise" from "tone" the way a listener does.

### UnitMatrix Integration

- **Voices = rows = independent buffers.** EMD is nonlinear, so the decomposition must be applied **per voice stem**, not to the mix: render row $v$, sift it, edit modes, sum. A row's mode set is its *timbral fingerprint* for that section; per-row parameters are $\{n_{\text{imfs}}, \theta, \gamma_j, r_j\}$. Applying EMD to the summed mix is legal only when the goal is a global band-and-texture treatment (and then the modes are mix strata, not voices).
- **Sections = columns = mode policies.** Column $s$ stores: which IMFs survive, per-mode gain and transposition, and whether EEMD is used. Seam handling is the one hard constraint: spline envelopes diverge at buffer edges, so each column is decomposed on its *own* full-section buffer with mirrored padding, and the seams are crossfaded (5–20 ms) after resynthesis — never sift a buffer that starts or ends mid-note, or the edge artifact lands exactly on the section boundary.
- **Cells = MusicUnit.** Cells define the time grid the buffer is cut on. Practical rule: decompose per **section-length stem**, then slice the resynthesized output at cell boundaries — slicing *IMFs* per cell and sifting each cell separately multiplies cost by the cell count and produces inconsistent mode numbering across cells (IMF1 of cell 3 is not the same band as IMF1 of cell 4). Cell velocity can drive per-mode gain curves; cell pitch content determines which modes matter (a bass-only cell lives in IMF4–6, a cymbal cell in IMF1–2).
- **Produce dispatch:** `produce(midi_path, method="SP-128", params={"max_imfs": 6, "sd_thresh": 0.2, "scope": "row", "keep_imfs": [1,2,3,4,5,6], "imf_gain": [1,1,1,1,1,1], "imf_transpose": [1,1,1,1,1,1], "eemd_ensembles": 0, "edge_mode": "mirror", "seam_xfade_ms": 12})`. Stage order: render (SP-001/SP-011/…) → **SP-128 per row** → mix → SP-008 dynamics → SP-126 loudness → SP-122 dither. Upstream of SP-126 deliberately: mode editing changes the spectral balance and therefore the K-weighted level, so loudness must be measured *after* it.
- **Reproducibility:** plain EMD is fully deterministic given $\{\theta, \text{max sift}, \text{interpolation, boundary rule}\}$ — record all four in provenance. EEMD/CEEMDAN are stochastic (noise realisations): seed the ensemble per row and record the seed, exactly as SP-127 records its excitation seed. Zero-drift is untouched — no events are moved; the row lengths in ticks are unchanged.

### Pitfalls

1. **Mode mixing is the default failure, not an edge case.** Measured on 220 Hz + 660 Hz + a noise burst + a 1.2 Hz trend: the 220 Hz partial landed in IMF2 in one realisation and IMF3 in four others after a *0.05σ* noise perturbation (index set `[1,3,3,3,3]`, stable = False). Consequences: per-mode transposition hits the wrong band, and a "keep IMF1–2" policy is not reproducible across renders. Cures: decompose per stem (not per mix), use EEMD/CEEMDAN, or add a masking signal at the frequency you want separated. Never assume IMF $j$ = "band $j$" without checking the centroid.
2. **EEMD/CEEMDAN destroy exact reconstruction.** $\sum_j \bar c_j \neq x$: measured 45 % relative error with $M=6$, $\epsilon=0.3\sigma$, versus $1.4\times10^{-14}$ for plain EMD. If the chain needs a null test (bypass = bit-comparable, parallel-processing sanity check), use plain EMD or CEEMDAN with its residual term added back — and verify $\lVert \hat x - x\rVert$ explicitly rather than assuming.
3. **End effects are structural and land on section seams.** Cubic-spline envelopes are extrapolations at the buffer edges and can overshoot by more than the signal amplitude; the error propagates inward by roughly one period of the lowest IMF (tens of ms for bass modes). Fix: mirrored/AR-predicted padding ≥ 2 periods of the lowest band, discard 20–50 ms at each edge, and crossfade seams after resynthesis. Do not "fix" it by sifting the whole song as one buffer and then cutting it — that just moves the artifact to the top and tail.
4. **EMD is not a transient/tonal separator.** Measured burst concentration: the 45 ms noise burst occupied 3.6 % of IMF1's energy and 3.2 % of IMF2's — *below* the 4.5 % uniform expectation. EMD stratifies by frequency, so a broadband transient is spread across every mode (and partially cancelled between them, which is why per-mode burst "shares" can exceed 100 %). For harmonic/percussive splitting use SP-072 HPSS; for transient reshaping use SP-073/SP-118. Choosing EMD for a transient job is the most common misuse of this method.
5. **The Bedrosian condition is what makes $f_j$ meaningful — and it fails on wideband modes.** $a_j(t)$ may be treated as lowpass relative to $\cos\varphi_j$ only for narrowband modes; otherwise $\varphi_j$ is not a physical phase, IF can go negative, and transposition produces sideband garbage. Verified: narrowband modes (660 Hz, 220 Hz) transposed at exactly 1.500×, while the broadband 1 Hz trend mode transposed at 2.000× and was meaningless. Gate every per-mode operation on a bandwidth test (e.g. $\sigma_{f_j}/\bar f_j < 0.3$) and leave failing modes untouched.
6. **The decomposition is not unique, so pin the parameters.** Sifting threshold, max sift count, spline type, boundary rule and the extremum-detection convention each change the IMF set; two implementations of "EMD" routinely disagree. Store $\{\theta, K_{\max}, \text{spline}, \text{edge rule}\}$ in provenance — otherwise "the same MIDI" is not the same audio, which breaks the absolute-layer reproducibility contract.
7. **Nonlinearity forbids superposition.** $\mathrm{EMD}(a+b)\neq\mathrm{EMD}(a)+\mathrm{EMD}(b)$ and $\mathrm{EMD}(\alpha x)\neq\alpha\,\mathrm{EMD}(x)$ in general (amplitude scaling changes which extrema exist). This is the opposite of every linear transform in the DB, and it means: per-voice processing must be per-voice, A/B comparisons must be re-run on the edited signal, and "decompose once, reuse the modes for a different mix" is invalid.
8. **Non-causal and offline.** Sifting needs both future and past extrema; there is no streaming form without windowed latency and boundary stitching. Budget it as a render-stage processor (20–45× realtime measured for one 44.1 kHz mono buffer), never as a real-time insert.
9. **Do not decompose per cell.** Cost scales with the number of sift operations, and per-cell sifting both multiplies cost and makes mode numbering inconsistent across cells (cell-level IMF1 ≠ section-level IMF1). Decompose per section-length stem, slice afterwards.
10. **"Drop IMF1 = denoise" is a musical decision, not a default.** Boudraa & Cexus filtering assumes the first modes are noise; in music IMF1 is often the attack of a cymbal, the bow rosin, or the breath — exactly the content a producer paid for. Audition the marginal spectrum and the IF tracks before deleting a mode; and always high-pass or discard the residue $r_n$ if it contains drift, or the DC will intermodulate in SP-008/SP-107.

---

## 5. Quirks / pitfalls hit during this run (and how they were handled)

1. **ID resolution ambiguity.** The DB's last H1 section is `# Artin Braid Group Composition (ABGC) (Method 129)`, and SP-127's Pitfall 9 says "cf. 128 Pitfall 9". Both "128"/"129" belong to the *composition-method* series, not the SP series. Verified by grepping `^# Sound Production Method SP-` (max 127) and by the absence of any `SP-128` string. Do **not** take the trailing method number as the next SP-ID.
2. **Sibling-writer race.** The patch tool warned that `methods_db.md` had been modified by another agent's run since my last read. The summary-row patch was therefore anchored on a *unique string at the end of the SP-127 row* rather than by line number, so it landed after SP-127 without clobbering anything. Line numbers shifted by +1 afterwards — that is why the section moved from 29047 to 29048 and why the first report draft's extract was off by one line (caught and rebuilt).
3. **Line-number drift in the report extract.** Extracting by hard-coded `sed -n 'A,Bp'` after a table insert silently dropped the final pitfall line. Fixed by locating the section programmatically (`startswith("# Sound Production Method SP-128")` → next top-level `# `) instead of trusting stored line numbers.
4. **Patch pitfalls (both checked, both clean).** No `||` prefix (row has exactly 6 pipes = 5 columns); no doubled backslashes (`grep '\\\\[a-zA-Z]'` = 0 in both row and section).
5. **Sandbox/security blocks.** Plain-HTTP requests and `curl | python3` pipes were refused by the security scanner in this cron context; all literature verification was therefore done with `urllib` inside a `.py` file over **https** (Crossref REST API), run with `$MUSICOM_PYTHON`. `/tmp` is write-protected here → scratch scripts live in `projects/Research/outputs/sp128_research/`.
6. **First EMD implementation returned 0 IMFs.** The initial stopping rule (mean-|envelope| tolerance) rejected every candidate mode. Replaced with the standard extremum-count rule (residual needs ≥4 extrema to continue; each IMF needs ≥2). Also learned that `SD<0.2` with `max_sift=10` **over-sifts** drifty material: a 1.2 Hz trend fragmented into four ~1.5 Hz IMFs; adding `max_imfs=6` + the extremum gate fixed it. This became Pitfall 1/6 in the entry.
7. **Hilbert IF on a mixed mode is misleading.** IMF2's median IF read 123 Hz while its spectral argmax was 220 Hz — a live demonstration of mode mixing, kept in the entry as evidence rather than "fixed" for cosmetics.
8. **Crossref rate limiting (HTTP 429)** on repeated DOI lookups; retried with sleep. 7 of 7 cited papers ultimately verified (title/authors/venue/pages/date), including the 2009 EEMD paper on retry.
9. **Real-render test wrote inside the project tree.** `compose()`/`produce()` created `outputs/Pop/workflow-demo/…` under the cron cwd (`projects/Research/outputs/sp128_research/`), which is the sanctioned output location — no files were written into the repo root.

## 6. Verification commands run (final state)

```
$ wc -l /opt/data/projects/Research/CompositionMethods/methods_db.md      # 29147
$ grep -n '^| \*\*SP-128\*\*' .../methods_db.md                            # 328  (summary row)
$ grep -n '^# Sound Production Method SP-128' .../methods_db.md            # 29048 (detailed section)
$ awk '/^### /' over 29048..29147   # Source, Layer, Description, Technical Mechanics,
                                    # Musical Elements Framework, UnitMatrix Integration, Pitfalls  (all 7)
$ grep -c 'SP-128' .../methods_db.md                                       # 4
```

Files produced:
- `methods_db.md` — +100 lines (section) +1 line (summary row)
- `sound_method_SP-128_EMDHAR.md` — standalone write-up (extended math, NumPy sketch, measured results table, 9 references)
- `report_SP-128.md` — this file
- `outputs/sp128_research/verify_sp128_emd.py` — runnable verification harness (9 tests, all executed)
- `outputs/sp128_research/verify_refs.py`, `verify_refs2.py` — Crossref DOI verification
