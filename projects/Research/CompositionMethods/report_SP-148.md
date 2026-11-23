# REPORT — SP-148 Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR)

**Run date:** 2026-11-23 (cron, autonomous)
**Method ID:** SP-148
**Method name:** Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR)
**Acronym:** FVNR
**Layer:** **absolute** — sound production (LAYER_ARCHITECTURE.md). Category: **Post-Processing / DSP** (spatialization / artificial reverberation).
**One-line description:** Synthesizes the diffuse late-reverb tail as a sparse signed-impulse (velvet-noise) IR on a jittered grid at pulse density ρ, shaped by an analytic per-band exponential envelope — parametric T60, mode-free, `O(ρT)` convolution, and seed-decorrelated per channel.

---

## 1. ID resolution (dynamic)

- Scanned summary table rows `| **SP-NNN** |` → max = **SP-147** (line 367 at read time).
- Cross-checked standalone files `sound_method_SP-*.md` in the directory → highest = `sound_method_SP-147_HPSM.md`. No `SP-148+` files existed.
- `SP-148` confirmed free; **no duplicate method** — novelty greps: `velvet noise` = 0, `sparse impulse` = 0, `stochastic impulse` = 0, `modal reverb` = 0; the single `velvet` hit was the adjective "velvety" in SP-122's dither prose. Free-reed (SP-124 FRAP), sax/clarinet/double-reed (SP-134/023/139), 808/909-style circuits, all reverb families (SP-009, SP-032, SP-071, SP-075, SP-140) checked and excluded.

**Next free SP ID: SP-149** (subject to concurrent sibling agents; at verification time the table max was SP-148).

## 2. Summary-table row (exact, as landed)

```
| **SP-148** | Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR) | **Post-Processing / DSP** | Parametric Smooth Late Reverb / Sparse Stochastic IR & Multichannel Decorrelation | Builds the diffuse late tail as a sparse signed-impulse IR: unit impulses of random sign on a jittered grid at pulse density $\rho$ (grid $T_d=f_s/\rho$), multiplied by a per-band exponential envelope $10^{-3n/(f_s T_{60,b})}$, band-filtered and summed. Smooth broadband at $\rho\approx1500$–$2000$ pulses/s; roughness $\propto 1/\rho$. Analytic per-band $T_{60}$ gives non-exponential/gated/swell decays and HF-faster tails; per-pulse dictionary filters (dark velvet noise, $|H(m,\omega)|=\sum_q|F_q(\omega)|p_q(m)$) decouple colour from density. Direct sparse convolution $O(\rho T)$ — 24× fewer MACs than the 195k-tap dense IR — and independent per-channel seeds give decorrelated stereo with no comb. Verified 10/10 (`_web148_vnr/vnr_prototype.py`; T60 max err 1.4 %, wet-level invariance 0.011 dB across $\rho{=}500\!-\!8000$, 576 kB demo WAV). Candidate: `sound/effects/velvet_reverb.py`. |
```

Patch safety verified after writing: **no `\\` double-escapes** in the row (`T_d=f_s/\rho` matches single-backslash form; literal `\\rho` count = 0), and **single `|` prefix** (no `||`).

## 3. Line counts

| stage | lines |
|---|---|
| `methods_db.md` at initial read | **32,650** |
| after concurrent sibling appended a *non-SP* section (LATC, "Method 149") at 09:21 | 32,734 |
| after appending the SP-148 detailed section (+104) | 32,838 |
| after the summary-table row (+1) | **32,839** |

Net delta attributable to this job: **+105 lines** (104 section + 1 table row).
`wc -l` final = **32,839**.

## 4. Artifacts

| artifact | path | size / status |
|---|---|---|
| Detailed DB section | `methods_db.md` lines **32736–32839** (`# Sound Production Method SP-148 — …`) | 104 lines |
| Summary-table row | `methods_db.md` line **369** | 1 row |
| Standalone write-up | `sound_method_SP-148_FVNR.md` | 11,299 B |
| Report (this file) | `report_SP-148.md` | — |
| Prototype | `_web148_vnr/vnr_prototype.py` | 7.1 KB, 10/10 PASS |
| Results | `_web148_vnr/vnr_results.json` | metrics |
| Demo audio | `_web148_vnr/vnr_out.wav` | 576,044 B, 3.0 s stereo, SHA256 prefix `d0159d59b11af73f` |
| Sources | `_web148_vnr/arxiv_velvet.xml`, `_web148_vnr/dvn_2403.20090.txt` | fetched 2026-11-23 |

## 5. Candidate code path

`sound/effects/velvet_reverb.py` (NumPy/SciPy; dispatched from `workflows/musicom_workflow.py::produce(method="SP-148", ...)`).
Stage position: source → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → **SP-148 space** → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122).

## 6. Technical mechanics — summary

1. **Sequence.** `Td = fs/ρ`; `n_k = floor(k·Td + u_k)`, `u_k ~ U(−Td/2, Td/2)`; signs `s_k ∈ {−1,+1}`; collisions summed.
2. **Spectrum.** Expected PSD flat (`E|V|² = ρT`), random phase → no modes. Measured flatness **0.544 dB** over 7 octave bands.
3. **IR.** `h = Σ_b ( v_b · 10^{−3n/(fs·T60_b)} ) * g_b`, with `T60_b = T60·r^{b−b_ref}` (`r = 0.8` typical, `r = 1` plate-flat). Measured vs target T60 max err **1.4 %**.
4. **Normalisation.** Unit energy: `h /= sqrt(Σh²)`; wet level spread across ρ = 500/2000/8000 is **0.011 dB**.
5. **Cost.** Sparse taps `P = ρT`; 8,125 taps vs 195,000 samples = **24.0×** MAC reduction (length-invariant).
6. **Smoothness.** Roughness ∝ 1/ρ; smooth at **1500–2000 pulses/s**; time-varying 2000→500 acceptable (masking).
7. **Hybrid.** Deterministic early taps (SP-075 or manual) + pre-delay 10–40 ms; velvet only for the diffuse tail.
8. **Colour.** Dark-velvet dictionary filters: `|H(m,ω)| = Σ_q |F_q(ω)| p_q(m)`, PSD independent of ρ; published fit mean T60 err 4 %, max 8 %.
9. **Stereo.** Independent seeds per channel → measured inter-channel r = **0.048** (125–250 Hz), **−0.062** (4–8 kHz); keep LF coherent.
10. **Determinism / zero drift.** Per (row, band, channel) child seeds; same seed ⇒ byte-identical; IR length = `ceil(1.3·max(T60_b)·fs)` = 195,000 samples, exact.

## 7. Musical Elements Framework (condensed)

- **PITCH** — pitch-neutral flat-spectrum tail; register-dependent decay via per-band T60.
- **RHYTHM** — pre-delay flam, T60 overlap/smear, density as grain size; gated/swell envelopes make the tail a rhythmic event; analytic decay can cut exactly on a bar line.
- **HARMONY** — neutral carrier that governs harmonic density; per-band T60 clears 250 Hz–1 kHz for chord legibility while keeping LF weight / HF air.
- **STRUCTURE** — column-level space presets (room/hall/plate/gated/swell) cross-faded; early-vs-late balance is the distance axis of form.
- **TEXTURE** — the home axis; ρ is a grain-size control with no analogue in convolution reverb.

## 8. UnitMatrix integration (condensed)

- **Voices = rows:** `{t60, t60_ratio, rho, bands, predelay_ms, early_taps, late_gain, mix, lf_coherent, seed}`.
- **Sections = columns:** space preset + envelope shape + crossfade; column change = space change (verse dry, chorus long, breakdown gated).
- **Cells = MusicUnit:** dry note plus per-cell send (velocity-derived or explicit); wet buffer rendered at exact section length + deterministic tail, length asserted before mixing.
- **Dispatch:** `produce(midi_path, method="SP-148", params={rows{...}, columns{...}, crossfade_ms})`.

## 9. Quirks / pitfalls hit during this run

1. **Measurement bug (not algorithm):** octave-band *energy* rises +3 dB/octave for white noise because bandwidth grows — flatness must be measured as **PSD per Hz** (divide by bandwidth). First run reported 18.1 dB "flatness"; corrected metric gives 0.544 dB.
2. **T60 anchoring bug:** scaling `T60_b = T60·r^{b/(B−1)}` makes the quoted T60 apply to band 0, not the mid band, so a "2.0 s" preset measured 1.45 s at 750 Hz. Fix: anchor at a reference band (`r^{b−b_ref}`). Second run measured 3.55/4.45 s on LF because the IR was truncated to 2 s while LF target was 2.75 s — fixed by rendering `1.3·max(T60_b)` and measuring each band's own component.
3. **JSON serialisation:** NumPy `bool_`/`float64` from comparisons are not JSON-serialisable — cast before `json.dump`.
4. **Concurrency:** a sibling agent appended a non-SP composition method (LATC, "Method 149") to `methods_db.md` between my first read and the append (line count 32,650 → 32,734). My ID was resolved before that append and LATC consumes no SP number, so **no collision**; the patch tool flagged a stale-read warning, and the table patch applied cleanly on the re-read position.
5. **LaTeX escaping:** verified after patching — row and section contain **single** backslashes (`\rho`, not `\\rho`), and the row has a single `|` prefix.
6. **`python3 -c` / heredoc are approval-blocked in cron** — all computation went through a written `.py` file executed by `$MUSICOM_PYTHON`; large HTML→text extraction via `perl`, not heredoc.
7. **Sparse-IR perf gotcha (design):** direct sparse convolution must accumulate per tap (`wet[lag:] += g*dry[:N-lag]`), not per sample loop over taps — the per-sample loop is 100× slower in Python.

## 10. Complete appended section text

The exact 104 lines appended to `methods_db.md` (lines 32736–32839) follow verbatim below.

---

# Sound Production Method SP-148 — Filtered Velvet-Noise Late-Reverberation Synthesis (FVNR)

### Source

- **Karjalainen & Järveläinen (2001), "Reverberation Modeling Using Velvet Noise," Proc. WASPAA** — the originating method: late reverberation is synthesized as a *sparse* pseudo-random impulse sequence (velvet noise) shaped by an exponential decay, instead of a dense measured impulse response or a recursive network.
- **arXiv:2403.20090, "Non-Exponential Reverberation Modeling Using Dark Velvet Noise"** (2024; abstract + full text fetched live 2026-11-23). Confirms the canonical definitions verbatim: "Original velvet noise [5] is a **sparse pseudo-random noise, which consists of sparsely placed unit impulses with uniformly distributed signs**. The main design parameter … is its **pulse density $\rho$ in pulses/s**", with grid size $T_\mathrm{d}=f_\mathrm{s}/\rho$. States that velvet noise "**becomes smooth broadband noise with a pulse density of 1500 to 2000 pulses/s**", that perceived temporal roughness "is simply **inversely proportional to its pulse density**", and that sparse random FIR alternatives (Rubak–Johansen) "would still need **over 10,000 filter coefficients**". Introduces per-pulse dictionary filters with probabilities $p_q(m)$, PSD $|H(m,\omega)|=\sum_q |F_q(\omega)|p_q(m)$ **independent of $\rho$**, and reports target-IR fits with **mean T60 error 4 %, maximum 8 %** using ten second-order all-pole filters; uses a time-dependent density **2000 → 500 pulses/s**.
- **arXiv:1806.06812, "Frequency domain variants of velvet noise …"** (2018; abstract fetched live). Defines velvet noise as "a **sparse discrete signal consisting of a few non-zero (1 or −1) elements** and sounds **smoother than Gaussian white noise**" and documents its use as an all-pass/excitation signal — evidence that the sequence is a general-purpose sparse stochastic primitive, not only a reverb IR.
- **arXiv:1909.04301, "Frequency domain variant of Velvet noise …"** (2019; abstract fetched live). FVN is "an impulse response of an **all-pass filter** and yields the unit impulse when convolved with the time-reversed version of itself" — corroborates the flat-magnitude / random-phase property.
- **Verified prototype (this run):** `_web148_vnr/vnr_prototype.py` → `vnr_results.json`, `vnr_out.wav` (576,044 B, 3.0 s stereo, SHA256 prefix `d0159d59b11af73f`). **10/10 checks pass** (Technical Mechanics §10).
- **Novelty check (2026-11-23), `grep -ci` on `methods_db.md` before entry:** `velvet noise` = **0**, `sparse impulse` = **0**, `stochastic impulse` = **0**, `modal reverb` = **0**; the single `velvet` hit is the word "velvety" describing ATH-shaped dither (SP-122). Adjacent-but-different: SP-009 (dense measured-IR convolution — millions of taps), SP-032 (FDN — recursive unitary matrix), SP-071 (Dattorro plate — fixed all-pass tank), SP-075 (image-source — geometric early field), SP-140 (Schroeder — comb/all-pass network), SP-146 (texture synthesis by filter statistics — analysis-driven noise, no impulse sparsity). **SP-148 is novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). FVNR is a **Post-Processing / DSP** engine operating on a rendered per-voice (or per-bus) buffer: it takes PCM in, emits PCM of exactly the same length plus a deterministic tail, with no symbolic state and no timing authority. It is an **insert/send effect**, not a source: stage position **source (SP-001/SP-095/SP-147 …) → per-row EQ (SP-007) → spatialize (SP-021/SP-053/SP-119) → FVNR space (SP-148, or SP-009/SP-032/SP-071/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**. Candidate code path: `sound/effects/velvet_reverb.py` (NumPy/SciPy, no training, no external IR corpus); dispatch from `workflows/musicom_workflow.py::produce(method="SP-148", ...)`.

### Description

FVNR builds the **late reverberation tail** as a *sparse stochastic impulse response*: a sequence of unit impulses with random signs placed on a jittered grid at a chosen **pulse density $\rho$** (pulses per second), multiplied by a per-band exponential decay envelope and band-limited by octave filters. At $\rho \approx 1500\text{–}2000$ pulses/s the sequence is perceptually indistinguishable from smooth broadband noise, yet it contains only a few thousand non-zero samples instead of the 100 k+ taps of a dense IR.

Three properties make this a distinct method rather than a cheap convolution:

1. **Parametric decay, not a baked room.** The envelope is applied analytically, so $T_{60}$ per octave band is a *number you set*, and **non-exponential decay** (gated, double-slope, swelling, frequency-dependent spectral evolution) is directly expressible — impossible for a fixed measured IR and awkward for feedback structures, which are locked to exponential decay by construction.
2. **No modes, no metallic ring.** Random phase and aperiodic pulse placement mean there are no resonant eigenfrequencies to ring, so the tail cannot "boing" the way an under-diffused FDN or a short all-pass tank can.
3. **Cost scales with musical need.** Direct sparse convolution is $O(P)$ per sample with $P=\rho T$ (≈8.1 k here), not $O(N)$; the same sequence also serves as a multichannel **decorrelator** (independent seeds per channel give near-zero inter-channel coherence without comb artifacts).

In the mix it behaves like a "synthetic hall/plate" with presets: `hall` (long LF, faster HF, ρ = 2000), `room` (T60 0.6 s, ρ = 3000), `plate` (high ρ, flat-ish decay, bright), `gated` (envelope truncated at a fixed time), `swell` (inverted/ramped envelope for reverse-reverb gestures).

### Technical Mechanics

**1. Velvet-noise sequence.** With sample rate $f_s$ and pulse density $\rho$ the grid period is

$$T_\mathrm{d}=\frac{f_s}{\rho}\quad\text{(samples)},\qquad
n_k=\left\lfloor k\,T_\mathrm{d}+u_k\right\rfloor,\ \ u_k\sim\mathcal{U}\!\left(-\tfrac{T_\mathrm{d}}{2},\tfrac{T_\mathrm{d}}{2}\right),\ \ s_k\in\{-1,+1\}$$

$$v[n]=\sum_{k=0}^{K-1}s_k\,\delta[n-n_k],\qquad K\approx \rho\,T$$

The uniform jitter is what destroys periodicity: an un-jittered grid is a pulse train with a line spectrum at $\rho$ (an audible pitched buzz). Collisions are summed (`np.add.at`), so overlapping pulses become $\pm2$ or cancel to $0$ — a natural amplitude distribution. Verified: 4000 non-zero samples in 2.0 s at $\rho=2000$ (relative error 0.05 %).

**2. Spectrum.** The sequence has (in expectation) a **flat magnitude spectrum and uniformly random phase** — the discrete counterpart of white noise, without the crest-factor of Gaussian noise. Octave-band energies measured over 125 Hz–16 kHz span only **0.54 dB**, so the sequence is spectrally neutral and the *filter*, not the noise, defines colour. Because phase is random, no periodic structure → no metallic modes.

**3. Band-split late IR.** The tail is a sum of independent per-band velvet sequences, each with its own decay:

$$h_\text{late}[n]=\sum_{b=1}^{B}\Big(\big(v_b[n]\cdot 10^{-3n/(f_s T_{60,b})}\big)*g_b[n]\Big),\qquad
T_{60,b}=T_{60}\,r^{\,b-b_\text{ref}}$$

where $g_b$ is an octave band-pass (2nd-order Butterworth SOS here), $r$ the per-band T60 ratio (0.8 ⇒ HF decays faster, LF slower; $r=1$ = flat, "plate-like"), and $b_\text{ref}$ the band where $T_{60}$ is quoted (≈750 Hz). The $10^{-3}$ factor is the −60 dB definition of $T_{60}$. Verified: target vs Schroeder-measured T60 per band = 3.125/3.127, 2.500/2.535, 2.000/1.993, 1.600/1.601, 1.280/1.282, 1.024/1.023 s (**max error 1.4 %**).

**4. Energy normalisation (mandatory).** With $\pm1$ pulses the IR energy grows linearly with $\rho$:

$$\sum_n h^2[n]\ \propto\ \rho\,T \quad\Longrightarrow\quad \tilde h[n]=\frac{h[n]}{\sqrt{\sum_n h^2[n]}}$$

Without step 4, raising $\rho$ (a *quality* knob) also raises the wet level by $10\log_{10}\rho$ — a 12 dB jump from ρ = 500 to 8000. With unit-energy normalisation the wet RMS at ρ = 500 / 2000 / 8000 measured **−0.512 / −0.521 / −0.523 dB → spread 0.011 dB**.

**5. Sparse convolution cost.** Direct-form convolution is $O(P)$ per output sample with $P=\rho T$ taps. For $T_{60}=2$ s, $f_s=48$ kHz, $\rho=2000$: $P=4000$ non-zeros against $N=96{,}000$ samples — a **24× MAC reduction**; at 4 s IR (195 000 samples, 8125 pulses) the ratio is identical because both scale with $T$. FFT convolution of the sparse IR is also valid (the IR is still a finite array), but for short blocks the direct sparse form is cheaper and allocates less.

**6. Roughness / density law.** Perceived tail roughness $\propto 1/\rho$; smooth broadband noise is reached at **ρ ≈ 1500–2000 pulses/s**. Below ~800/s the tail granulates ("crackle"), which can be used deliberately (lo-fi/texture) but must be a decision, not an accident. Time-varying density (2000 → 500 pulses/s, linearly) keeps the late tail cheap without audible roughness because sparse late pulses are masked by earlier dense ones — the scheme used in arXiv:2403.20090.

**7. Early/late hybrid.** Velvet supplies only the **diffuse late field**; the first ~60–80 ms should be deterministic discrete taps (image-source SP-075, or a handful of hand-placed reflections, or the leading fragment of a measured IR):

$$h[n]=h_\text{early}[n]+G_\text{late}\,h_\text{late}[n-d_\text{pre}]$$

Pre-delay $d_\text{pre}$ (10–40 ms) is what separates source from space; without it the reverb collapses onto the note and reads as a "loud room", not a hall.

**8. Coloration control (dark velvet noise).** For target-matching, route each pulse through a dictionary filter $F_q(z)$ drawn with probability $p_q(m)$ that varies over time:

$$h[n]=\sum_k s_k\,F_{q_k}\big[n-n_k\big],\qquad
\big|H(m,\omega)\big|=\sum_q\big|F_q(\omega)\big|\,p_q(m)$$

The PSD is **independent of $\rho$** (it is set by the filter mixture), so density and colour are orthogonal controls — the key structural difference from filtered-noise reverb. With ten second-order all-pole filters extracted from a target IR, the published fit reaches mean T60 error 4 % / max 8 %, with ~50 % fewer coloration filters than frame-wise filtered velvet noise.

**9. Stereo / multichannel decorrelation.** Independent seeds per channel give different pulse positions; coherence is then set by the shared envelope and band gains, not by phase coincidence. Measured inter-channel correlation: **r = 0.048 (125–250 Hz), r = −0.062 (4–8 kHz)** — i.e. effectively decorrelated, with no comb filtering when summed to mono (unlike a fixed-delay Haas widener). Best practice: share the **low-band** sequence (LF must stay coherent for a solid image) and decorrelate only ≥ ~300 Hz.

**10. Verified prototype — 10/10 checks.** `_web148_vnr/vnr_prototype.py`: (1) density 4000 pulses / 2 s, rel. err 5e-4; (2) velvet PSD flatness 0.544 dB over seven octave bands; (3) T60 anchor band 1.993 s vs 2.000 s target (0.375 %); (4) T60 monotone per band, max err 1.4 %; (5) IR unit energy at ρ = 2000 and 4800 (1.000, exact); (6) wet-level invariance 0.011 dB across ρ = 500/2000/8000; (7) determinism: same seed ⇒ `array_equal` True; (8) exact length 195 000 samples; (9) stereo decorrelation |r| < 0.07 both bands; (10) demo WAV 576 044 B > 40 kB.

### Musical Elements Framework

- **PITCH**: FVNR is pitch-neutral by design — a flat-spectrum stochastic tail adds no fundamental and no partials, so it re-spaces a note without re-tuning it. Pitch information survives as *register-dependent decay*: because $T_{60,b}$ falls with frequency, a bass note's tail is long and dark while a cymbal's is short and bright. Deliberately detuning the band gains (a "coloured" tail) is available (DVN §8) but is the exception: the point is that harmony passes through untouched.
- **RHYTHM**: the tail is the *rhythm of space*, not of notes. Controls are pre-delay (flam between attack and room), T60 (how many notes overlap — i.e. how much rhythmic information is smeared), and density (granular vs smooth). Gated envelopes turn the reverb into a rhythmic event (a hard cutoff on the beat); swell/reverse envelopes make the tail anticipate the next downbeat. Because decay is analytic, a tail can be cut exactly on a bar line — impossible with a baked IR.
- **HARMONY**: neutral carrier, but it governs harmonic *density*: long T60 makes successive chords accumulate, so a ii–V–I in a 3 s hall blurs into a cluster while the same progression in a 0.6 s room stays legible. Per-band T60 is the harmony-clearance tool — shorten 250–1000 Hz to keep chord changes articulate while keeping LF weight and HF air.
- **STRUCTURE**: a section-level parameter set. Columns can move the same voices from `room` (ρ 3000, T60 0.6) to `hall` (ρ 2000, T60 2.4) to `gated` (T60 1.2, hard truncation) — a form-defining gesture with one parameter block, cross-faded between IRs so no click. The mix of early taps vs late level is the "distance" axis of form (close verse, distant chorus).
- **TEXTURE**: the method's home axis. Smooth wash (high ρ), grainy crackle (low ρ, deliberate), dark tail (low-pass band ratio), bright plate (high ρ, short LF), shimmer/air (long HF bands, or chained with SP-009/SP-032). Density-as-texture is the one control that has no analogue in convolution reverb: ρ is a *grain size* knob, not a fidelity knob.

### UnitMatrix Integration

**Voices = rows = one send.** Row $v$ carries `{t60 (s), t60_ratio r, rho (pulses/s), bands (octave split), predelay_ms, early_taps (list of (ms, gain, pan) or "none"), late_gain, mix, lf_coherent: bool, seed}`. Each row owns its own velvet banks and seed → rows never phase-lock; two rows with the same preset and different seeds give a naturally wide pair.

**Sections = columns = space state.** Column $j$ holds `{preset: room|hall|plate|gated|swell, t60, rho, predelay_ms, early_gain, late_gain, mix, shape: exp|gated|swell, crossfade_ms}`. A column change is a *space* change: verse tight/dry, chorus wide/long, breakdown gated. Implementation: render two IRs and equal-power crossfade over `crossfade_ms` (never hard-switch an active tail — that clicks).

**Cells = MusicUnit.** A cell $(v,j)$ is a note (or chord) plus its send: `start_tick`/`end_tick` → dry note; **send amount** may be per-cell (velocity-derived or explicit) so individual notes can be pushed back into the space (the classic "only the snare gets the big tail" move). The wet buffer is rendered per row (or per bus) at exactly the section length, plus a deterministic tail that is summed into the *following* column's head or truncated at the section boundary before export — assert buffer length before mixing (zero-drift invariant).

**Produce dispatch:** `produce(midi_path, method="SP-148", params={"rows": {"pad": {"t60": 2.4, "t60_ratio": 0.8, "rho": 2000, "predelay_ms": 25, "early_taps": "none", "mix": 0.35, "seed": 3}, "snare": {"t60": 1.2, "rho": 3000, "predelay_ms": 8, "early_taps": [[11, 0.5, -0.3], [19, 0.35, 0.4]], "mix": 0.5, "seed": 4}}, "columns": {"A": {"preset": "room", "t60": 0.6, "mix": 0.2}, "B": {"preset": "hall", "t60": 2.4, "mix": 0.35}, "C": {"preset": "gated", "shape": "gated", "t60": 1.2, "mix": 0.45}, "crossfade_ms": 400}})` — stage order **dry voices → per-row EQ (SP-007) → FVNR (SP-148) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**.

### Pitfalls

1. **Un-jittered grid = pitched buzz.** Placing pulses exactly on the $T_\mathrm{d}$ grid produces a line spectrum at $\rho$ Hz; the jitter $u_k$ is not optional. Equally, reusing one seed for all channels yields a mono tail that combs when summed with a delayed copy.
2. **Skipping energy normalisation.** IR energy is $\propto\rho$; without dividing by $\sqrt{\sum h^2}$ the ρ knob doubles as a 12 dB wet-level knob (measured spread before normalisation) and every preset change breaks the mix balance.
3. **Density set too low.** Below ~800 pulses/s the tail granulates; roughness $\propto 1/\rho$. If the crackle is wanted, label it a texture decision; otherwise keep ρ ≥ 1500–2000/s, and if you must reduce density in the late tail (cost), ramp it (2000 → 500) so early density masks the sparse region.
4. **Truncating the IR before the decay ends.** A tail cut at $T_{60}$ (rather than ≈1.3·$T_{60,\max}$) chops the LF decay and biases Schroeder T60 *short*; run the render buffer to `tail_frames = ceil(1.3 * max(T60_b) * fs)` and trim only after the last band is 60 dB down.
5. **Forgetting the early field.** Velvet alone has no directional information and no first reflections; used as the whole IR it sounds like "noise glued to the note". Always hybridise with discrete early taps (SP-075 or manual) and a pre-delay.
6. **Feedback-structure temptation.** Wrapping velvet noise in a recursive loop (Karjalainen's cheap variant) re-imposes a single exponential decay and destroys the method's main advantage — arbitrary/non-exponential envelopes. Keep the feed-forward band-bank for parametric decay; use feedback only for pure exponential tails.
7. **Flat spectrum includes DC and infrasonic energy.** A ±1 impulse sequence is white down to 0 Hz; without a high-pass on the wet path (or explicit LF band gain trim) the tail accumulates rumble that eats headroom and modulates the limiter. Allocate per-band gains, don't assume "flat = correct".
8. **Cross-fading mid-tail.** Switching presets by swapping IRs under a ringing tail clicks; equal-power crossfade two rendered IRs over ≥200 ms, or mute the old tail over its own decay.
9. **Determinism / zero drift.** Seed every velvet sequence per (row, band, channel) with the child-seed convention (`seed*101 + row`); same seed + params ⇒ byte-identical WAV. The wet buffer must fill exactly the section's tick-converted sample count (plus tail), asserted before mixing — same discipline as SP-145/SP-146/SP-147.
10. **Not the neighbours.** SP-009 = convolution with a **dense measured** IR (perceptual truth, zero parametric control, $O(N\log N)$); SP-032 = FDN (recursive, modal, exponential only); SP-071 = Dattorro plate (fixed all-pass tank, dense early diffusion); SP-075 = image-source (geometric early field, no diffuse stochastic tail); SP-140 = Schroeder comb/all-pass (periodic echo density, metallic at short T60); SP-146 = texture synthesis by matching filter statistics (analysis-driven, not an impulse-sparse IR). **FVNR = sparse signed impulse IR + analytic per-band decay: parametric, mode-free, $O(\rho T)$ convolution, and a density knob that is a texture control.**
