# REPORT — SP-129 Transaural Crosstalk-Cancelled Binaural Rendering (TCCR)

**Primary record.** Chat delivery was a 6-line caveman summary only; everything is here.

| Field | Value |
|---|---|
| **Method ID** | **SP-129** |
| **Method name** | Transaural Crosstalk-Cancelled Binaural Rendering (TCCR) |
| **Layer** | **absolute** (sound production — LAYER_ARCHITECTURE.md): no note events emitted, buffer → buffer |
| **Category (table)** | **Post-Processing / DSP** (spatialization) |
| **One-line description** | Pre-distorts a binaural ear-signal bus by the regularized inverse of the 2×2 speaker→ear acoustic plant so the far-ear paths cancel at a listening position — headphone-grade imaging over two loudspeakers, inside a positional sweet spot. |
| **Candidate code path** | `sound/effects/transaural.py` — `plant()` (2×2 model) → `invert()` / `shuffler()` (regularized inverse, gain-capped difference) → `design()` (causal L-tap IRs) → `process()` (4-path convolution on the summed binaural bus) |
| **Dispatch** | `workflows/musicom_workflow.py::produce(method="SP-129", params={...})` |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-129_TCCR.md` (16 930 B) |
| **Verification scripts** | `/opt/data/projects/Research/outputs/sp129_research/` → `tccr_ref.py`, `verify_sp129_tcc.py`, `verify_sp129_tables.py`, `exec_docblock.py` (executes the *published* code block), `check_sketch.py` |
| **methods_db.md line count** | **29 221 before** → **29 349 after** section append (+128) → **29 350 after** summary-row insert (+1) → **29 358 after** latency-table correction (+8) |
| **Detailed section location** | `methods_db.md` line **29 224** (`# Sound Production Method SP-129 …`) to EOF |
| **Status** | documented + numerically verified 2026-10-31 (NumPy 1.26.4 / SciPy 1.17.1) |
| **Next free SP ID** | **SP-130** |

---

## 1. ID resolution (dynamic, not assumed)

| Probe | Result |
|---|---|
| `grep -oE '\| \*\*SP-[0-9]{3}\*\* \|'` on `methods_db.md` | max = **128** (rows SP-001…SP-128; sparse — e.g. SP-076…086, SP-090, SP-091 absent) |
| `ls sound_method_SP-*.md \| sed … \| sort -n \| tail` | max = **128** (`sound_method_SP-128_EMDHAR.md`) |
| `ls report_SP-*.md` | max = **128** |
| `grep -c "SP-129"` before writing | **0** |
| **Assigned** | **SP-129 = max + 1** |

Note on a numbering trap: the DB's tail (after the SP-128 section) contains a
*composition* method document headed "Subshift of Finite Type Composition (SFT-C)
(Method 130)" whose pitfall text references "125–129". That is the **composition
methods** numbering space (`C-…`), not the SP space. The SP summary table and the
`sound_method_SP-*.md` files both stop at 128, so SP-129 is the correct next SP ID.
Do not read the composition counter as an SP counter.

---

## 2. Novelty check (no duplicate)

`grep -ci` on `methods_db.md` before this entry:

| Probe | Hits | Verdict |
|---|---|---|
| `transaural` | **0** | — |
| `Kirkeby` | **0** | — |
| `regularized inverse` | **0** | — |
| `crosstalk` | 4 | none is a method: 1 parenthetical inside SP-021's pitfall 1, 2 about neural-network pattern capacity, 1 about voice-vector bundles |
| `sweet spot` | 8 | all comparative remarks about *other* spatializers (SP-021/034/043/053) |
| `Atal` | 67 | substring noise (`fatal`, `total`, …); the only real hit is Atal **and Hanauer 1971** inside the SP-028 LPC entry |

The DB itself names the gap: SP-021's Pitfall 1 reads *"Binaural (SP-021) works
only with headphones (or requires crosstalk cancellation that is
listener-position-dependent)."* SP-129 is that cancellation, specified.

---

## 3. Layer

**absolute** — per `LAYER_ARCHITECTURE.md`, SP-129 consumes an already-rendered
binaural buffer and emits acoustic air pressure from two loudspeakers. It writes no
symbolic state, holds no note events, and cannot be `.relative` (it does not
reshape a UnitMatrix; it is downstream of note realization). Code path family:
`sound/effects/` — same layer as SP-119 (`haas_zone.py`), upstream of SP-008 /
SP-126 / SP-122, downstream of SP-021.

---

## 4. Full summary-table row (as inserted, line 330)

```
| **SP-129** | Transaural Crosstalk-Cancelled Binaural Rendering (TCCR) | **Post-Processing / DSP** | 2-Channel Loudspeaker Binaural Render / Sweet-Spot Spatialization | Two-speaker binaural reproduction: the symmetric 2×2 plant $h_{es}(f)=(A_{es}/r_{es})e^{-j2\pi f r_{es}/c}$ (ipsilateral $h_s$, contralateral $h_o$ with head shadow $f_c\approx c/2\pi a\approx 624$ Hz) is inverted so the far-ear paths cancel acoustically: $\mathbf{C}=\mathbf{H}^{H}(\mathbf{H}\mathbf{H}^{H}+\beta\mathbf{I})^{-1}$, or in Cooper–Bauck shuffler form two scalar filters $1/(h_s+h_o)$ (sum) and $1/(h_s-h_o)$ (difference, the ill-conditioned one). Measured (48 kHz, ±30° at 1 m, head radius 8.75 cm): shuffler ≡ matrix inverse to −292 dB; $\beta=10^{-4}$ gives −37 dB worst-case crosstalk for +18.4 dB corrective gain; 1–8 kHz suppression −59…−69 dB. Low frequency is the limit ($|h_s|/|h_o|$ within 0.4 dB at 80–200 Hz → $|h_s-h_o|$ 24 dB down → clamp $|C_{diff}|\le +18$ dB, giving −11.9 dB there). Sweet spot fails asymmetrically: 5 cm lateral −22 dB, yaw 10° −24 dB, but 5 cm sagittal → +0.1 dB (cancellation inverts into reinforcement); a ±15° array under ±30° filters → −1 dB. Source-independent, so one 2×2 inverse serves the whole UnitMatrix (rows = seats, columns = scenes, cells need no filters); apply after per-row HRTF placement (SP-021) and before any room simulation (SP-009/SP-032). |
```

Escaping audit after insert (mandatory, per the two known patch pitfalls):

| Check | Result |
|---|---|
| `||` prefix | none — row begins with exactly `| **SP-129** |` |
| double backslashes `\\` | **0** occurrences; every LaTeX macro is a single `\` (5 × `\mathbf`, 1 × `\approx`, 1 × `\le`, 1 × `\beta`, 1 × `\times`) |
| column count | 5 cells (`4 × " \| "` separators) matching the header `| Method ID | Method Name | Layer | Target Output | Description / Integration |` |
| row length | 1 383 chars |

---

## 5. Technical mechanics (summary)

**Plant.** $h_{es}(f)=\dfrac{A_{es}(f)}{r_{es}}e^{-j2\pi f r_{es}/c}$; $r_{es}$ from
speaker/ear geometry ($\pm30°$ @ 1 m → ipsi 1.0465 m, contra 0.9592 m, ITD
**0.254 ms** = 12.2 samples @ 48 kHz); $A_{es}$ = 1 ipsilateral, first-order
lowpass contralateral with $f_c\approx c/2\pi a\approx 624$ Hz.

**Inverse.** Exact: $\mathbf{C}=\mathbf{H}^{-1}=\frac{1}{h_s^2-h_o^2}\begin{bmatrix}h_s&-h_o\\-h_o&h_s\end{bmatrix}$.
Regularized: $\mathbf{C}=\mathbf{H}^{H}(\mathbf{H}\mathbf{H}^{H}+\beta\mathbf{I})^{-1}$.
Shuffler (Cooper–Bauck): in $u=s_L+s_R$, $v=s_L-s_R$ the plant is diagonal, so the
inverse is two scalar filters $1/(h_s+h_o)$ and $1/(h_s-h_o)$.

**Why it is hard.** $h_s-h_o$ is the cancellation channel. At 80–200 Hz
$|h_s|/|h_o|$ is within 0.4 dB, so $|h_s-h_o|$ is 24 dB down and
$1/(h_s-h_o)$ demands +24 dB — regularize or clamp. At 4 kHz a 2 cm head move is a
quarter wavelength, which is the sweet-spot problem.

---

## 6. Verified numbers (all produced by running code on this machine)

Rig: $f_s=48$ kHz, speakers $\pm30°$ @ 1.0 m, head radius 8.75 cm, one-pole 700 Hz
shadow, 8-note harmonic test signal, virtual source at $+30°$ (model results; a real
room is worse).

**Regularization sweep** (100 Hz–16 kHz worst-case $|\mathbf{H}\mathbf{C}-\mathbf{I}|$):
$\beta=0$ → −260.0 dB at $+18.58$ dB max gain; $10^{-6}$ → −77.1; $10^{-4}$ →
**−37.4** at $+18.35$ dB; $10^{-3}$ → −19.3; $10^{-2}$ → −8.7; $10^{-1}$ → −6.6 dB.

**Per-band suppression** ($\beta=10^{-3}$): −23.7 (20–80 Hz), −19.7 (80–200),
−19.3 (200–500), −37.8 (0.5–1 k), −58.5 (1–2 k), −63.3 (2–4 k), −68.8 (4–8 k),
−74.3 dB (8–16 k).

**Conditioning** ($\beta=0$): $|h_s|/|h_o|$ = −0.7 dB at 20–80 Hz (i.e. near-equal
magnitudes) → $|h_s-h_o|$ 21.8 dB down → $C_{\text{diff}}$ wants +21.8 dB; at
2–8 kHz the ratio is 20.4 dB so it needs only +1.9 dB.

**Gain cap** (bass management): +18 dB → −11.9 dB residual in 20–200 Hz with
0.5–8 kHz untouched; +12 dB → −8.5 / −18.8; +6 dB → −7.2 / −10.3 dB.

**Head pose** ($\beta=10^{-3}$, 0.5–8 kHz): centred −37.8 dB; lateral 2 cm −31.8;
lateral 5 cm −22.1; yaw 2° −35.1; yaw 5° −30.6; yaw 10° −24.4; **forward 2 cm −7.9;
forward 5 cm +0.1; back 5 cm +0.4** (cancellation becomes reinforcement).

**Array mismatch:** $\pm30°$ filters over $\pm15°$ → −1.1 dB; over $\pm45°$ → −2.5 dB.

**Shuffler vs matrix inverse:** identical to **−292 dB** crosstalk residual (differ
only in the DC bin) — confirms the two forms are the same filter.

**Causal L-tap design (the latency discovery):** suppression depends on pre-delay,
not on filter length — 3.0 ms → −10.2 dB; 5.5 ms → −27.9; 8.0 ms → −47.5;
11.0 ms → −47.5; 13.7 ms → **−55.8**; 21.0 ms → −61.3 dB. $L=2048/4096/8192$
measure identically at a fixed pre-delay. End-to-end (delay-aligned): −41.6 dB
error on a centre image, −35.5 dB on a hard-left target, recovered inter-ear level
within 0.1 dB of target.

**Mono fold-down:** hard-left source −2.3 dB; centre source 0.0 dB (difference
channel idle, measured side energy −283 dB relative).

---

## 7. Complete section text appended to `methods_db.md`

(Verbatim, `methods_db.md` lines 29 224–29 358, including the two later corrections
to the latency claim and to Pitfall 4.)

# Sound Production Method SP-129 — Transaural Crosstalk-Cancelled Binaural Rendering (TCCR)

### Source

- **Atal, B. S., Schroeder, M. R. (1966).** "Apparent sound source translator." *Journal of the Acoustical Society of America* **40**(4), 770–779. The origin: two loudspeakers plus electrical cancellation of the far-ear path so that a *binaural* signal can be reproduced over *loudspeakers*; the paper that defines the "transaural" problem as a 2×2 acoustic inversion.
- **Cooper, D. H., Bauck, J. L. (1989).** "Prospects for transaural recording." *Journal of the Audio Engineering Society* **37**(1/2), 3–19. Introduces the **shuffler** formulation — sum/difference (M/S) domain in which the 2×2 inverse decouples into two scalar filters $1/(h_s+h_o)$ and $1/(h_s-h_o)$ — and the binaural-to-transaural "compatibility" argument.
- **Bauck, J. L., Cooper, D. H. (1993).** "Developments in transaural stereo." *Proc. IEEE ASSP Workshop on Applications of Signal Processing to Audio and Acoustics*, 114–117. DOI 10.1109/aspaa.1993.379983 — later refinements: frequency-dependent crosstalk, headphone/loudspeaker interoperability, and the practical filter-design chain.
- **Kirkeby, O., Orduna, F., Nelson, P. A. (1993).** "Inverse filtering in sound reproduction." *Applied Signal Processing* **26**, 261–266; and **Kirkeby, O., Nelson, P. A. (1999).** "Digital filter design for inversion problems in sound reproduction." *Journal of Sound and Vibration* **223**(4), 583–605. The **regularized least-squares / fast-deconvolution** formulation $c=(\mathbf{H}^{\mathsf{T}}\mathbf{H}+\beta\mathbf{I})^{-1}\mathbf{H}^{\mathsf{T}}\delta$ that makes the inverse robust and implementable in the frequency domain — the design method every modern TCC uses.
- **Bai, M. R., Lee, C.-C. (2006).** "Development and implementation of cross-talk cancellation system in spatial audio reproduction based on subband filtering." *Journal of Sound and Vibration* **290**, 1269–1289. DOI 10.1016/j.jsv.2005.05.016 — subband (band-split) TCC: apply the inverse only where it is well conditioned, which is the disciplined form of "bass management".
- **Bai, M. R., Lee, C.-C. (2006/2007).** "Subband approach to bandlimited cross-talk cancellation system in spatial sound reproduction." *EURASIP Journal on Audio, Speech, and Music Processing* **2007**, 071948. DOI 10.1155/2007/71948 — band-limited variant; cancellation band chosen by design rather than by accident.
- **Ward, D. B., Elko, G. W. (1998).** "Optimum loudspeaker spacing for robust crosstalk cancellation." *Proc. IEEE ICASSP*, 3541–3544. DOI 10.1109/icassp.1998.679636; and **Ward, D. B., Elko, G. W. (1999).** "Effect of loudspeaker position on the robustness of acoustic crosstalk cancellation." *IEEE Signal Processing Letters* **6**, 106–108. DOI 10.1109/97.755428 — quantifies how the loudspeaker span trades cancellation depth against positional robustness (the sweet-spot width law).
- **Hollebon, J., Fazi, F. M., Simón Gálvez, M. (2021).** "A multiple listener crosstalk cancellation system using loudspeaker-dependent regularization." *Journal of the Audio Engineering Society* **69**, 191–203. DOI 10.17743/jaes.2020.0067 — per-loudspeaker regularization so that more than one seat gets useful cancellation.
- **Marchand, S., Meaux, T. (2021).** "Synthetic transaural audio rendering (STAR): a perceptive 3D audio spatialization method." *Journal of the Audio Engineering Society* **69**(7/8), 497–505. DOI 10.17743/jaes.2021.0015; and **(2023)** "STAR: extension to full 3D spatialization." *JAES*, 596–606. DOI 10.17743/jaes.2022.0098 — perceptual-cost-driven TCC (the inverse is allowed to be *perceptually* right rather than numerically exact).
- **Vidal, A., Herzog, P., Lambourg, C. (2023).** "Comparison of transaural configurations inside usual rooms." *Journal of the Audio Engineering Society*, 202–215. DOI 10.17743/jaes.2022.0055 — what survives when the loudspeakers are in a real living room.
- **Huang, X., Zhao, S., Li, J. (2026).** "An optimal control point distribution method for two-channel crosstalk cancellation." *JASA*, 2539–2551. DOI 10.1121/10.0043134 — current work: choosing *where* in the listening area the cancellation error should be minimized.
- **Adjacent-but-distinct DB neighbours:** SP-021 (binaural Woodworth–Schlosberg HRTF — *headphone* reproduction; the very method whose pitfall #1 in this DB reads "requires crosstalk cancellation that is listener-position-dependent" — SP-129 is the missing half of that sentence), SP-053 VBAP and SP-043 WFS / SP-034 HOA (arrays and wavefields — amplitude or field synthesis, no ear-level inversion), SP-075 (image-source *room* modelling — a different physics problem), SP-119 (auto-pan — one-dimensional amplitude motion), and SP-009/SP-032 (reverb *after* spatialization; TCC must precede them, see Pitfall 3).
- **Novelty check (2026-10-31):** `grep -ci "transaural"` on methods_db.md = **0**; `grep -ci "Kirkeby"` = **0**; `grep -ci "regularized inverse"` = **0**. `crosstalk` = 4 hits, none a method (one parenthetical in SP-021's pitfall list, two about neural-network pattern capacity, one about voice-vector bundles). `sweet spot` = 8 hits, all comparative remarks about other spatializers. No transaural / crosstalk-cancellation method exists in the DB at any layer.

### Layer

**absolute** — SP-129 is a sound production method (LAYER_ARCHITECTURE.md): it consumes a rendered, already-spatialized *binaural bus* and emits acoustic air pressure from two loudspeakers. It writes no note events and holds no symbolic state; it sits downstream of any synthesis engine (SP-001/SP-011/SP-021/…) and upstream of the dynamics/loudness chain. Candidate code path: `sound/effects/transaural.py` (`design_filters()` → frequency-domain 2×2 regularized inverse or shuffler pair; `TransauralFilter.process()` → block FFT/windowed convolution; `bass_manage()` → difference-filter gain clamp), dispatched from `workflows/musicom_workflow.py::produce(method="SP-129", params={...})`. Same family as SP-119 (`haas_zone.py`) and SP-021 (`sound/synthesis/binaural.py`): a buffer processor, not an instrument.

### Description

Binaural audio assumes headphones: the left ear hears only the left signal. Loudspeakers break that assumption — each ear hears **both** speakers, so a binaural render played over a stereo pair arrives as a blurred, inside-the-head image with the left cue leaking into the right ear. **Transaural reproduction** restores the assumption electrically: it pre-processes the binaural pair with a 2×2 inverse of the acoustic plant so that, *at a specific ear position*, the far-ear contributions cancel acoustically.

The plant is a 2-in / 2-out matrix. With speakers $s\in\{L,R\}$ and ears $e\in\{L,R\}$, each entry is a delay, a $1/r$ spread and a head-shadow filter:

$$\mathbf{E}(f)=\mathbf{H}(f)\,\mathbf{S}(f),\qquad \mathbf{H}=\begin{bmatrix} h_{LL} & h_{LR}\\ h_{RL} & h_{RR}\end{bmatrix},\qquad h_{es}(f)=\frac{A_{es}(f)}{r_{es}}e^{-j2\pi f r_{es}/c}.$$

Wanted: $\mathbf{E}=\mathbf{B}$ (the binaural target). Therefore $\mathbf{S}=\mathbf{C}\mathbf{B}$ with $\mathbf{C}=\mathbf{H}^{-1}$. For a listener on the midline and a symmetric pair, $h_{LL}=h_{RR}\equiv h_s$ (ipsilateral, unshadowed) and $h_{LR}=h_{RL}\equiv h_o$ (contralateral, shadowed), and the inverse is closed-form:

$$\mathbf{C}=\frac{1}{h_s^2-h_o^2}\begin{bmatrix} h_s & -h_o\\ -h_o & h_s\end{bmatrix}.$$

The whole method lives in the denominator: **$h_s-h_o$ is the cancellation channel**, and it is small exactly where human hearing is least able to localize anyway (low frequency), and it is *phase-critical* everywhere (a 2 cm head movement is a quarter-wavelength at 4 kHz). Transaural rendering is therefore not a filter but a **geometry contract**: cancellation is exact at one point in space, degrades smoothly away from it, and collapses to nothing when a reflection arrives first.

Two implementation forms, mathematically identical, numerically very different:

1. **Matrix form** — invert the 2×2 at every FFT bin (regularized).
2. **Shuffler form** (Cooper–Bauck) — rotate to sum/difference coordinates $u=s_L+s_R$, $v=s_L-s_R$, where $\mathbf{H}$ is *diagonal*, so the inverse is two scalar filters: $1/(h_s+h_o)$ (sum, always benign) and $1/(h_s-h_o)$ (difference, the ill-conditioned one). All robustness work happens on that single difference filter — which is why every practical TCC is really "a gain-limited difference filter".

Measured on this machine (NumPy, $f_s=48$ kHz, symmetric pair at $\pm30°$, 1.0 m, head radius 8.75 cm, one-pole 700 Hz head shadow, 8-note harmonic test signal): the shuffler form reproduces the 2×2 inverse to a **−292 dB** crosstalk residual (they differ only in the DC bin), i.e. it *is* the same filter — implement the shuffler, debug the shuffler.

### Technical Mechanics

**Geometry and the plant.** Speaker positions $\mathbf{p}_s$, ear positions $\mathbf{p}_e$ (interaural axis $\perp$ facing direction, $\pm a$ with $a=0.0875$ m):

$$r_{es}=\lVert \mathbf{p}_s-\mathbf{p}_e\rVert,\qquad \tau_{es}=r_{es}/c,\qquad A_{es}(f)=\begin{cases}1,& e=s\\ \bigl(1+j f/f_c\bigr)^{-1},& e\ne s\end{cases},\qquad f_c\approx \frac{c}{2\pi a}\approx 624\ \text{Hz}.$$

For $\pm30°$ at 1 m the four paths measure 1.0465 m (ipsi) and 0.9592 m (contra) — **ITD 0.254 ms**, i.e. 12.2 samples at 48 kHz: the cancellation is a fractional-delay problem, not an integer-shift one, and needs fractional-delay (Lagrange/allpass) or FFT-domain phase.

**Inversion.** Exact: $\mathbf{C}=\mathbf{H}^{-1}$. Regularized (Kirkeby):

$$\mathbf{C}(f)=\mathbf{H}^{H}\bigl(\mathbf{H}\mathbf{H}^{H}+\beta\mathbf{I}\bigr)^{-1}=\bigl(\mathbf{H}^{H}\mathbf{H}+\beta\mathbf{I}\bigr)^{-1}\mathbf{H}^{H},$$

equivalently, in the time domain, minimize $\lVert \mathbf{H}\mathbf{c}-\boldsymbol{\delta}\rVert^2+\beta\lVert\mathbf{c}\rVert^2$ and solve the Toeplitz normal equations by FFT — the *fast deconvolution* route, cost ≈ 2–4 FFTs per block, which is what makes TCC cheap enough to run on a whole mix bus.

**Measured regularization trade-off** (band 100 Hz–16 kHz, worst-case $\lvert\mathbf{H}\mathbf{C}-\mathbf{I}\rvert$ off-diagonal):

| $\beta$ | max $\lvert C\rvert$ (dB) | crosstalk residual (dB) | total error vs binaural target (dB) |
| :--- | :--- | :--- | :--- |
| $0$ | 18.58 | **−260.0** | −126.0 |
| $10^{-8}$ | 18.58 | −117.1 | −125.9 |
| $10^{-6}$ | 18.58 | −77.1 | −103.1 |
| $10^{-4}$ | 18.35 | **−37.4** | −63.3 |
| $10^{-3}$ | 16.50 | −19.3 | −44.7 |
| $10^{-2}$ | 8.71 | −8.7 | −32.4 |
| $10^{-1}$ | −0.06 | −6.6 | −27.4 |

Two things to read off this table: (i) exact inversion is achievable in floating point, so any audible failure is a *model* failure, not a solver failure; (ii) $\beta$ buys stability with crosstalk decibels, and $\beta=10^{-4}$ is where the curve is still steep — +18.4 dB of corrective gain for −37 dB of crosstalk.

**Per-band suppression** ($\beta=10^{-3}$, centred listener): −24 dB (20–80 Hz), −20 dB (80–200 Hz), −19 dB (200–500 Hz), −38 dB (0.5–1 kHz), −59 dB (1–2 kHz), −63 dB (2–4 kHz), −69 dB (4–8 kHz), −74 dB (8–16 kHz). The low bands are *not* limited by physics here but by $\beta$; the raw inverse wants 22–24 dB of difference-filter gain down there (see Pitfall 2), so the regularization is deliberately spending low-frequency cancellation to keep the gain sane.

**Bass management (the disciplined alternative to $\beta$).** Clamp only the difference filter, $\lvert C_{\text{diff}}\rvert\le G_{\max}$, leaving the sum filter alone (Bai & Lee's band-limited/subband construction). Measured: cap $+18$ dB → −11.9 dB residual in 20–200 Hz with the 500 Hz–8 kHz band untouched; cap $+12$ dB → −8.5 dB (20–200 Hz) and −18.8 dB (0.5–8 kHz); cap $+6$ dB → −7.2 / −10.3 dB. Below the cap the output is effectively mono in that band, which is the honest trade: **you cannot cancel what both ears already hear identically.**

**Sweet spot (measured, $\beta=10^{-3}$, 500 Hz–8 kHz).** Moving the head *laterally* is the benign direction; moving *forward/back* is fatal, because it changes both path lengths in phase:

| pose change | crosstalk suppression | total error |
| :--- | :--- | :--- |
| centred | −37.8 dB | −44.7 dB |
| lateral 2 cm | −31.8 dB | −26.6 dB |
| lateral 5 cm | −22.1 dB | −18.6 dB |
| yaw 2° | −35.1 dB | −38.5 dB |
| yaw 5° | −30.6 dB | −33.0 dB |
| yaw 10° | −24.4 dB | −27.8 dB |
| forward 2 cm | −7.9 dB | −32.7 dB |
| forward 5 cm | **+0.1 dB** | −25.3 dB |
| back 5 cm | **+0.4 dB** | −24.9 dB |

At 5 cm forward the "cancellation" has become a 0 dB *recombination* — the difference channel now arrives in phase and the cross-talk is reinforced instead of cancelled. That is the single most important number in this entry: the method does not degrade gracefully in the sagittal direction, it **inverts**.

**Loudspeaker-span sensitivity.** Filters designed for $\pm30°$ played over a $\pm15°$ array give −1.1 dB residual; over $\pm45°$, −2.5 dB. The geometry must be *measured*, not assumed; the span is the design parameter that Ward & Elko show trades depth for robustness.

**Implementation requirements.** Pure Python/NumPy: `np.fft.rfft` on 4096–16384-sample blocks with overlap-save, 2×2 complex matmuls per bin (`np.linalg.inv` on a batched 2×2, or the closed-form shuffler), `scipy.signal.fftconvolve` for the 4-path offline render. Cost: two FFTs per channel per block — negligible next to any synthesis method in this DB. No FluidSynth, no VST, no GPU.

The one real cost is **latency**, and it is larger than the textbooks suggest. The inverse of a delayed, low-passed response is non-minimum-phase, so a *causal, L-tap* implementation can only cancel to the extent the inverse's tail fits inside the pre-delay budget. Measured with $L=8192$ taps at 48 kHz, suppression in 0.5–8 kHz:

| pre-delay | 3.0 ms | 5.5 ms | 8.0 ms | 11.0 ms | 13.7 ms | 21.0 ms |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| suppression | −10.2 dB | −27.9 dB | −47.5 dB | −47.5 dB | **−55.8 dB** | −61.3 dB |

So the honest number is **8–14 ms of pre-delay** for a usable filter (3 ms gives −10 dB, i.e. almost nothing), and 21 ms if the last 5 dB matter. Filter length is *not* the lever — pre-delay is; $L=2048$ and $L=8192$ measure identically at a given pre-delay until the pre-delay exceeds the window. End-to-end closed loop with the 13.7 ms design: −41.6 dB error on a centre image and −35.5 dB on a hard-left target, with the recovered inter-ear level ratio within 0.1 dB of the binaural target. That latency budget is why SP-129 is a render stage and not a monitor-path insert.

### Musical Elements Framework

**PITCH.** Pitch content is untouched — TCC is a linear, source-independent spatial operator — but *pitch determines how well the spatial cue survives*. Above ~1.5 kHz the head shadow is 8–25 dB deep, so the contralateral cancellation has real signal to work with and the image is stable; below ~200 Hz both ears receive nearly the same pressure ($\lvert h_s\rvert/\lvert h_o\rvert$ within 0.4 dB at 80–200 Hz), so the bass is spatially ambiguous *by physics*, not by implementation. Practical consequence for arranging: melodic and harmonic interest that must be *localized* belongs above ~250 Hz; the bass line will sit at the centre whatever the pan says. A corollary that is easy to miss: because the cancellation is phase-exact, a small pitch-independent delay error turns into a frequency-dependent comb at the ear — mistuned TCC audibly *colours* timbre (a broad 2–4 dB ripple above 2 kHz) before it audibly mis-localizes.

**RHYTHM.** The filters are LTI, so the groove is bit-transparent in the steady state; the rhythmic risk is entirely at the **block boundary and at the pre-delay**. Transient attacks are where a non-causal inverse shows itself: the anti-causal tail pre-rings into the silence before the hit, which reads as a soft "shhh" before every drum. Two standard fixes — keep percussive stems on a parallel dry path (SP-118 transient control on the wet/dry balance) or shorten the inverse and accept a shallower cancellation band. If the renderer is *dynamic* (head-tracked, per-block re-design), the filter change must be crossfaded over ≥ 20 ms or the update itself becomes a rhythmic artefact (zipper noise at the block rate).

**HARMONY.** Azimuth becomes a compositional axis that is *orthogonal to pitch*, which is the whole point of using SP-129 in this DB: two voices can share a register and a timbre and still be perceptually separated by seat. Because $\mathbf{C}$ is applied to the **summed** binaural bus (it is source-independent), adding voices costs nothing in filter terms — 40 rows still need exactly one 2×2 inverse. Conversely the low register cannot be spread: everything under ~250 Hz collapses toward the centre, so close-position bass harmony will always arrive as one mass, and any harmonic writing that relies on hearing the inner voice of a low chord must move that voice up an octave or accept the blur.

**STRUCTURE.** A section (column) is a **scene**: a set of azimuth/elevation/distance assignments plus the room assumption. Because the inverse is global, a scene change is a change in the *input* binaural bus, not in the filter — so section contrast can be huge (a hard-left cluster in the verse, a wide arc in the chorus) at zero filter cost, provided the scene transition is crossfaded across the seam. Structural dynamics of the "space opens up" kind are cheap here in a way they are not in WFS, which needs a speaker array per scene.

**TEXTURE.** Texture is directly addressable as *apparent source width and distance*: dry/direct sources stay point-like and cancel cleanly; diffuse sources (reverb-heavy, decorrelated) are exactly what TCC cannot place, because a diffuse field is by definition arriving from everywhere with no cancelling direct path. The design rule follows: **TCC before reverb** — spatialize the dry material, cancel, then add the room (SP-009/SP-032), or the room's reflections will re-introduce the crosstalk the filter just removed.

### UnitMatrix Integration

- **Voices = rows = seats.** Each row owns a static $(azimuth, elevation, distance)$ triple plus a width parameter. Row-level spatial identity is stable across the whole piece, exactly like SP-053's per-row pan, but in a 3-D frame and with the ear-level correction applied once at the bus.
- **Sections = columns = scenes.** Column $s$ stores the row→seat map, the room assumption (anechoic / measured IR), and the bass-management band. Changing a scene means re-rendering the binaural bus for that column, then crossfading the *speaker feed* across the seam by ≥ 20 ms (a filter-domain crossfade is unnecessary — the filter does not change).
- **Cells = MusicUnit.** Cells carry the note events that produce the binaural bus; they do **not** carry filters. Because TCC is source-independent, the matrix's cell granularity is irrelevant to the spatial stage — which is the key architectural difference from SP-043 WFS (per-speaker, per-source) and the reason SP-129 can be a single insert on the master path.
- **Produce dispatch:** `produce(midi_path, method="SP-129", params={"speaker_span_deg": 60.0, "speaker_dist_m": 1.0, "head_radius_m": 0.0875, "beta": 1e-4, "form": "shuffler", "diff_gain_cap_db": 18.0, "hrtf": "model|measured", "block": 8192, "pre_delay_ms": 3.0, "scene_xfade_ms": 25})`. Stage order: render (SP-001/SP-011/…) → per-row binaural placement (SP-021 HRTF) → sum to binaural bus → **SP-129 inverse / shuffler** → SP-009/SP-032 room (after, never before) → SP-008 dynamics → SP-126 loudness → SP-122 dither. Audition on loudspeakers only; headphone monitoring of a transaural render is meaningless (it is pre-distorted for the loudspeaker path).
- **Reproducibility:** the render is fully deterministic given $\{$speaker geometry, head radius, $c$, $f_c$, $\beta$ or gain cap, block size, pre-delay$\}$ — record all eight in provenance, because the audible result is a *function of the assumed geometry*, not of the audio alone. Two renders that differ only in `speaker_span_deg` are different pieces of spatial music. Zero-drift is untouched: no events move, row lengths in ticks are unchanged.

### Pitfalls

1. **The sweet spot is a chair, not a room — and it fails asymmetrically.** Measured: ±5 cm forward collapses suppression from −37.8 dB to +0.1 dB (cancellation becomes *reinforcement*), while 5 cm lateral only costs 16 dB. Design for the sagittal axis: mark the listening position, and if the piece is to be heard anywhere else, reduce the ambition (lower $\beta$ target, wider span) or add head tracking.
2. **Low-frequency gain blow-up is structural.** At 80–200 Hz, $\lvert h_s\rvert$ and $\lvert h_o\rvert$ are within 0.4 dB, so $\lvert h_s-h_o\rvert$ sits 24 dB below $\lvert h_s\rvert$ and $1/(h_s-h_o)$ demands **+24 dB** of corrective gain on the difference channel. Unregularized, that is a 20 dB bass boost plus a near-DC pole — the classic way to destroy a tweeter (or an ear). Always regularize ($\beta$) *or* clamp the difference filter; never ship the raw inverse.
3. **Reflections veto the method.** $\mathbf{C}=\mathbf{H}^{-1}$ cancels the *direct* path only. A reflection arriving within the first few ms carries a different $h_o$ and re-injects crosstalk that the filter has already "used up" its gain to remove. Apply TCC before room simulation (SP-009/SP-032) and keep the loudspeakers away from side walls; in an ordinary living room the achievable suppression is far below the anechoic numbers above (see Vidal et al. 2023 for measured in-room configurations).
4. **The inverse is non-minimum-phase, so the transients move — and so does your latency budget.** Pre-ringing ahead of attacks, plus a pre-delay that is much longer than the propagation delay: 3 ms of "obvious" headroom yields only −10 dB of cancellation, while 13.7 ms yields −56 dB (measured, see Technical Mechanics). Percussion and plucked material need either a parallel dry path (SP-118) or a shortened inverse with a narrower cancellation band; a live instrument monitored through SP-129 is not viable at these latencies.
5. **Geometry assumptions are audible, not cosmetic.** $\pm30°$ filters over a $\pm15°$ array: −1.1 dB residual — i.e. no cancellation at all. Measure the span and distance, or design the piece for the deployment you control.
6. **Mono fold-down changes the piece.** Measured on a hard-left virtual source: −2.3 dB level loss when the transaural pair is summed to mono (centre sources: 0.0 dB, because the difference channel is idle for a centre image). Streaming platforms, phone speakers and club mono sums will therefore alter the spatial arrangement's *balance*, and for off-centre material the anti-phase content can partially null. Check the mono fold-down as a deliverable, exactly as SP-007 checks mid/side.
7. **Not SP-021 and not SP-053.** SP-021 renders binaural audio *for headphones* (no crosstalk to cancel — that is the point of headphones); SP-053 places sources in an *array* by amplitude panning with no ear model. SP-129 is the only entry that assumes a two-speaker plant and an ear position. Confusing them produces the classic failure of "HRTF applied to a stereo mix", which sounds phasey and hollow.
8. **Applying TCC to an already-panned stereo mix is wrong.** A stereo mix's channels are *loudspeaker* signals, not ear signals; inverting the plant on them cancels the phantom centre and hollows the image. TCC's input must be a genuine binaural bus (per-row HRTF placement, summed) — build it in the pipeline, do not retrofit it.
9. **Perceptual ≠ exact, and that is allowed.** Marchand & Meaux's STAR results show that a perceptually-weighted inverse can beat a numerically exact one, because exact inversion can over-correct where hearing is insensitive and under-correct where it is not. If the render is judged by ear, optimize the perceptual error; if it is judged by a null test, use exact inversion. Record which was used.
10. **Do not attempt this on headphones, and do not compare it there.** A transaural render monitored on headphones sounds comb-filtered and wrong — it is *pre-distorted* for the two-speaker path. Audition on loudspeakers, and keep the headphone master (SP-021) as a separate deliverable from the same binaural bus: one bus, two delivery masters, two provenance records.

---

## 8. Integration / workflow notes

- **Stage order:** render (SP-001/SP-011/…) → per-row binaural placement (SP-021)
  → sum to binaural bus → **SP-129** → room (SP-009/SP-032) → SP-008 → SP-126 →
  SP-122. TCC must precede reverb: reflections re-inject the crosstalk the filter
  removed.
- **UnitMatrix:** rows → static seats $(az, el, dist, width)$; columns → scenes
  (seat map + room assumption + bass band), crossfaded ≥ 20–25 ms across seams;
  cells → no filters at all. The inverse is source-independent, so 40 voices still
  cost one 2×2 filter — the key architectural difference from SP-043 WFS.
- **Provenance must record:** speaker geometry, head radius, $c$, $f_c$, $\beta$ or
  gain cap, filter length, total pre-delay, block size. The audible result is a
  function of the *assumed geometry*, not of the audio alone.
- **Deliverables:** keep the headphone master (SP-021) and the transaural master
  from the same binaural bus; check the mono fold-down separately, exactly as SP-007
  checks mid/side.

---

## 9. Quirks, bugs and pitfalls hit during the work

1. **Geometry bug (caught by a symmetry assertion).** The first model put the ears
   at $(\pm a, 0)$ and the speakers at $(d\cos\theta, \pm d\sin\theta)$ — i.e. the
   interaural axis was parallel to the facing direction. The resulting $\mathbf{H}$
   was not symmetric ($h_{LL}\ne h_{RR}$ by 6 dB), the closed-form inverse was wrong,
   and the shuffler form disagreed with the matrix inverse by 1.3 dB. Fix: ears at
   $(0,\pm a)$. Lesson: **assert $\mathbf{H}$ is complex symmetric before trusting any
   inverse** — it is the precondition for the closed form and for the shuffler.
2. **Conjugate-transpose Tikhonov is not symmetric.** $\mathbf{C}=\mathbf{H}^{H}(\mathbf{H}\mathbf{H}^{H}+\beta\mathbf{I})^{-1}$
   is only symmetric at $\beta=0$. Comparing the shuffler form against a $\beta>0$
   inverse therefore always shows a small difference; the equivalence test must be
   run at $\beta=0$ (and even then only up to the DC bin, where $1/(h_s-h_o)$ is a
   real scale factor).
3. **Overlap-save is invalid for a frequency-sampled filter.** The first sketch
   used 50 %-overlap blocks and *added* the outputs; with a filter whose IR fills the
   whole block, that both aliases and double-counts (measured 45.5 dB error against
   direct convolution). The published block therefore uses the offline
   4-path `fftconvolve`, which is exact.
4. **Causality sign.** The exact inverse sits at $t=-146$ samples. Multiplying by
   $e^{+j\omega\tau}$ moves it *further* negative (wraps to the end of the block,
   filter becomes ~silent: peak 0.0069 instead of 1.0). The correct sign is
   $e^{-j\omega\tau}$.
5. **The real finding: pre-delay, not tap count.** After fixing the sign, the
   truncated design still gave only −9.6 dB. Sweeping the pre-delay showed the
   inverse's tail must be given room: 3 ms → −10 dB, 13.7 ms → −56 dB, while
   $L$ from 2048 to 8192 changes nothing at fixed pre-delay. This contradicted the
   first draft's "2–4 ms" claim, so both the section (§Technical Mechanics) and
   Pitfall 4 were corrected after measurement. **Document the measured trade, not
   the textbook rule of thumb.**
6. **Latency-alignment error in the closed-loop metric.** Comparing a 13.7 ms-latent
   render against an undelayed target gives a meaningless −15 dB "error" for a
   centre image (that is just the delay). Align before measuring: −41.6 dB.
7. **Pre-existing table artefact.** Line 331 of `methods_db.md` holds a stray
   `|---|` immediately after the SP-128 row (not introduced here). The new row was
   inserted *before* it, so the table still renders; left untouched as out of scope.
8. **Composition-vs-SP numbering.** See §1 — "Method 130" in the DB tail is the
   composition counter, not an SP ID.
9. **Write-path restriction.** `write_file` refused `/tmp/tcc_test.py` (protected
   path); scratch work was moved to `/opt/data/tmp_tcc/` and results to
   `$MUSICOM_ROOT/projects/Research/outputs/sp129_research/`.
10. **Memory limit.** A 96 k-sample × 16 k-tap `fftconvolve` sweep was OOM-killed
    (exit 137); all final numbers use ≤ 32 k grids.

---

## 10. Deliverables checklist

| Item | Status |
|---|---|
| Next SP ID resolved dynamically (table + file scan) | ✅ SP-129 |
| Layer stated (`absolute`) in report + section header | ✅ |
| Web research with real DOIs (2021–2026 papers incl. JASA 2026) | ✅ 14 references |
| Section appended with all 7 required headings | ✅ Source / Layer / Description / Technical Mechanics / Musical Elements Framework / UnitMatrix Integration / Pitfalls |
| Summary table row inserted, escaping + `\|\|` audited | ✅ line 330 |
| Standalone file `sound_method_SP-129_TCCR.md` | ✅ 16 930 B, code block executed end-to-end |
| `wc -l` + `grep SP-129` verification | ✅ 29 358 lines, 10 hits |
| This report | ✅ |
