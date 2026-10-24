# Report SP-123 — Dynamic Convolution Synthesis (DCL)

**Date:** 2026-10-24 (cron research job)
**Agent:** Hermes sound-production research agent (musicom methods DB)

---

## 1. Identity

| field | value |
|---|---|
| **Method ID** | **SP-123** |
| **Method name** | Dynamic Convolution Synthesis (DCL) |
| **Layer** | **absolute** — sound production (**Post-Processing / DSP**) |
| **One-line description** | Renders audio through a time-varying impulse response $h[n,k]$ — the convolution kernel itself is animated by a control $\theta(t)$, implemented as partitioned block convolution (Gardner zero-latency scheme; uniform/non-uniform partitions, Wefers/Farina) with per-partition anti-zipper spectrum crossfades: morph a booth→cathedral→plate→guitar-body along one automation curve. |
| **Candidate code path** | `sound/effects/dynamic_convolution.py` (new module, class `DynamicConvolution`), IR frames sourced from `sound/effects/ir_designer.py`, invoked from `workflows.musicom_workflow.produce(method="SP-123")` as a post stage in `sound/render/pipeline.py`. |

**ID resolution:** scanned the summary table (`| **SP-NNN** |` rows) AND the standalone `sound_method_SP-*.md` / `report_SP-*.md` files. Highest existing = **SP-122** (summary row line 317, detailed section line 27814; standalone `sound_method_SP-122_NSDQ.md`, `report_SP-122.md`). No SP-123 anywhere (only `method_123_GTBRC.md` / `report_123.md`, which are composition-method 123, a separate numbering). Previous report (`report_SP-122.md`) itself stated "Next free = SP-123". → **new ID = SP-123.** No duplicate: DB has SP-009 (static convolutive reverb), SP-048 (commuted/KS pre-convolution), SP-031 (STFT spectral morph), SP-050 (spectral delay) — none is time-varying kernel convolution.

## 2. Full summary-table row (as inserted)

```
| **SP-123** | Dynamic Convolution Synthesis (DCL) | **Post-Processing / DSP** | Time-Varying IR Morphing / Convolution-Based Space & Timbre Morph | Generalizes SP-009's static convolution to a time-varying impulse response $h[n,k]$: the kernel itself is animated by a control $\theta(t)$ — $y[n]=\sum_k h[n,k]\,x[n-k]$, implemented as partitioned block convolution (Gardner zero-latency scheme; uniform/non-uniform partitions, Wefers/Farina) with per-partition spectrum crossfades (equal-power $\sin^2$, anti-zipper). Morph a booth→cathedral→plate→guitar-body along one automation curve; linear kernel, no IMD; sample-in/sample-out, zero-drift safe. Candidate: `sound/effects/dynamic_convolution.py`. |
```

Inserted at **line 318**, immediately after the SP-122 row, before the table terminator `|---|`. Pipe-prefix check: single `|` (verified). LaTeX check: single backslashes (verified by byte-level `ord()` scan — 4 backslash chars in the row at `\theta`, `\sum_k`, `\,`, `\sin^2`; the `\\` seen in tool display is terminal JSON escaping, not file content).

## 3. Line counts

- `methods_db.md` before: **28 038** lines (measured 2026-10-24, before append)
- `methods_db.md` after: **28 132** lines (28038 + 93 lines detailed section + 1 line summary row)
- Delta: **+94 lines**

## 4. Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-123_DCL.md` (14 697 bytes)
- This report: `/opt/data/projects/Research/CompositionMethods/report_SP-123.md`
- DB detailed section: `methods_db.md` lines 28041–28132

## 5. Research & verification status of sources

Web research via direct fetches + Crossref API (network OK on 2026-10-24):

| source | status |
|---|---|
| Wikipedia "Reverb effect"/"Convolution reverb" | **fetched** 2026-10-24 |
| Stefani/Binelli/Farina 2025, JAES (nonuniform partitioned conv., 6DoF dynamic auralization) | **DOI verified** via Crossref API 2026-10-24 (10.17743/jaes.2022.0224) |
| Gaydecki & Atbas 2023, Acoustics 2023 (IR synth + real-time convolution) | **DOI verified** via Crossref API 2026-10-24 (10.25144/16611) |
| Misic/Nikolov/Tomasevic 2016, Telfor J. (CPU/GPU convolution reverb) | **DOI verified** via Crossref API 2026-10-24 (10.5937/telfor1602121m) |
| Gardner 1995 (zero-latency partitioned convolution) | standard citation, JAES 43(3) 127–136 — not re-fetched |
| Wefers 2015 PhD thesis (RWTH Aachen) | standard citation — RWTH publications page behind JS challenge, not fetched |
| Hehmsoth 2003 "Dynamic Convolution", *Keys* (German) 5/2003 | term coined; issue ref from secondary/community documentation, **not** re-fetched |
| Native Instruments Kontakt 5 "Dynamic Convolution" (2011) | feature per release documentation; NI live page redirected to Kontakt 8 at fetch time |

## 6. Technical mechanics summary

1. **Static core** (SP-009's domain): $y[n]=\sum_k h[k]x[n-k]$.
2. **Time-varying IR:** $y[n]=\sum_k h[n,k]\,x[n-k]$ — the IR becomes a function of output time.
3. **Morph interpolation:** $h[n,k]=\sum_i w_i(\theta(n))\,h_i[k]$; linear ($w_0{=}1{-}\theta$) vs equal-power ($w_0{=}\cos(\pi\theta/2)$, $w_1{=}\sin(\pi\theta/2)$); three implementations — IR-domain (1×, interference), output-domain (2×, clean), **partition-spectrum interpolation (1×, default)**.
4. **Partitioned block convolution (Gardner 1995):** $y[n]=\sum_p (x*h_p)[n-\Delta_p]$, $\Delta_p=\sum_{q<p}L_q$; uniform $L_p=L$ or non-uniform $L_p=L_0 2^p$ (latency $\approx 2L_0$, CPU ≈1.5× optimal — Wefers/Farina); FFT block convolution, $N=B+L_p-1$; zero-latency first partition keeps dry/wet sample-aligned.
5. **Dynamic update:** $H_p^{(b)}(\omega)\leftarrow\sum_i w_i(\theta_b)H_{i,p}(\omega)$ per block, smoothed by $\sin^2(\pi t/2R)$ crossfade (anti-zipper); tail partitions at 1/4–1/8 update rate (perceptual scheduling).
6. **Normalization:** equal-energy IR frames; power interpolation $|H|=\sqrt{w_0|H_0|^2+w_1|H_1|^2}$ for brightness-tracking morphs.
7. **Cost:** per-sample $O(\frac{L_{IR}}{L_p}(B+L_p)\log(B+L_p))/B$; verification chain: frozen-$\theta$ must reproduce SP-009 bit-for-bit; impulse identity test; zipper test; zero-drift sample-count check.

## 7. UnitMatrix integration (summary)

Voices = rows → per-voice IR family + per-voice $\theta$ (or one bus morph after float summing, SP-122 rule); Sections = columns → breakpoints `morph_target`, `morph_position θ`, `crossfade_samples R`, `tail_update_rate`, interpolated across seams; Cells = MusicUnit → morph events with the crossfade straddling seams (convolution state on the **absolute sample counter**, never reset — same invariant class as SP-122's RNG rule); sample-in/sample-out, `validate()` passes, zero-drift safe.

## 8. Quirks / pitfalls hit during the run

1. **Concurrent cron job**: a sibling job appended composition "Method 124 (DPPC)" (+~110 lines) mid-run — methods_db.md grew 27 928 → 28 038 between two reads. Handled by re-reading before every write and using a unique anchored patch (SP-122 row tail) for the table row; `cat >>` append is atomic-safe against concurrent appends.
2. **Patch tool LaTeX escaping (known pitfall a):** the summary-row patch displayed `\\theta` in the diff; byte-level `ord()` diagnostics proved the FILE content was correct single-backslash all along — the apparent double-escape was terminal/JSON display escaping. No fix needed; verified with `ord()` counts (4 backslashes in row, 9 in the detailed-section equation line = authored counts).
3. **Patch `||` prefix (known pitfall b):** none — row starts with single `|` (read_file's `NNN|` line-number prefix masquerades as `||`; confirmed by grep `^| \*\*SP-123\*\*`).
4. **No piped interpreters / `python3 -c` / heredoc-to-DB:** cron blocks them; used `write_file` scripts + `$MUSICOM_PYTHON` (established pattern) for all Python work; DB append done strictly via `write_file` → `cat >>` → `rm`.
5. **`/tmp` is protected** for write_file — temp scripts lived in the CompositionMethods dir and were removed after use (0 `_tmp*` files remain).
6. **Search engines useless:** Bing HTML search returned AI-garbage (French locale, off-topic), DuckDuckGo Instant Answer API is a stub; Crossref API (polite pool, mailto) and direct fetches worked.
7. **Archive.org + RWTH rate-limited/JS-challenged** (429s, fast-challenge) — source verification statuses recorded honestly in §5; the two canonical citations (Gardner 1995, Wefers 2015) are flagged as standard-citation-not-refetched.

## 9. Complete section text appended (methods_db.md lines 28041–28132)

```markdown
# Sound Production Method SP-123 — Dynamic Convolution Synthesis (DCL)

### Source

- **Gardner, W. G. (1995).** "Efficient Convolution without Input-Output Delay." *J. Audio Eng. Soc.* 43(3), 127–136 (also AES 97th Convention preprint 3897, 1994). — the canonical partitioned-convolution scheme: split the impulse response into blocks ("partitions"), run the early partitions as direct time-domain taps for zero input-output latency, and compute the tail partitions with FFT block convolution. This is the structural backbone every real-time convolution engine (and every dynamic variant) builds on.
- **Wefers, S. (2015).** *Partitioned Convolution Algorithms for Real-Time Auralization.* PhD thesis, RWTH Aachen University. — the modern taxonomy: uniform vs. non-uniform partitioning, block-size/latency/CPU trade-offs, and the perceptual scheduling rules (later partitions updated less often) that dynamic convolution inherits.
- **Stefani, D., Binelli, M. & Farina, A. (2025).** "Improved Real-Time Six-Degrees-of-Freedom Dynamic Auralization Through Nonuniformly Partitioned Convolution." *J. Audio Eng. Soc.* DOI: 10.17743/jaes.2022.0224 (verified via Crossref API 2026-10-24). — time-varying (dynamic) convolution with non-uniformly partitioned IRs for head-tracked auralization: exactly the "the IR is allowed to move while the signal flows through it" regime formalized below.
- **Gaydecki, P. & Atbas, E. (2023).** "Impulse Response Synthesis and Real-Time Convolution for Acoustic Instrument Emulation." *Acoustics 2023.* DOI: 10.25144/16611 (verified via Crossref API 2026-10-24). — synthesis of IRs and their real-time convolution as instrument-body emulators; the "body morph" application family.
- **Misic, M., Nikolov, D. & Tomasevic, M. (2016).** "Analysis of CPU and GPU implementations of convolution reverb effect." *Telfor Journal* 8(2). DOI: 10.5937/telfor1602121m (verified via Crossref API 2026-10-24). — complexity analysis of partitioned/FFT convolution implementations.
- **Hehmsoth, C. (2003).** "Dynamic Convolution." *Keys* (German edition), 5/2003. — the article that coined the term in music production: convolution whose impulse response is driven by an external control (velocity/level) rather than fixed; documented in community literature (KVR/GearSpace threads and later NI materials); specific issue reference from secondary documentation, not re-fetched 2026-10-24.
- **Native Instruments (2011).** *Kontakt 5* — shipped a "Dynamic Convolution" convolution engine (convolution effects whose IRs switch/crossfade with input level/velocity, with a library of >100 IRs). Feature documented in the v5.0 release notes; the NI product page redirected to Kontakt 8 at fetch time 2026-10-24, so the feature description is taken from documented release material, not the live page.
- **Wikipedia: "Reverb effect" / "Convolution reverb"** (fetched 2026-10-24) — background anchor: convolution reverb records the impulse response of a physical space and reproduces it by convolution; SP-009's domain. DCL is the time-varying generalization.

### Layer

**absolute** — sound production (**Post-Processing / DSP**). See LAYER_ARCHITECTURE.md: every SP method is absolute (sound production, reproducible render). DCL is the time-varying generalization of **SP-009 (Convolutive Reverberation)** — same linear-convolution core, one extra degree of freedom: the impulse response itself becomes a function of time (or of a control $\theta(t)$), so the convolution kernel *animates*. It is the convolution-domain counterpart of **SP-031 (Spectral Cross-Synthesis)** (which morphs spectral envelopes in the STFT domain) and of **SP-050 (Spectral Delay Filters)** (which animates per-bin delays); DCL animates the *entire* kernel, space and timbre together, in the sample domain via partitioned block convolution. The candidate code path is `sound/effects/dynamic_convolution.py` (new module: class `DynamicConvolution`), with IR frames sourced from `sound/effects/ir_designer.py` (SP-123's sibling: algorithmic IR synthesis), invoked from `workflows.musicom_workflow.produce(method="SP-123")` as a post stage in `sound/render/pipeline.py` after SP-107/SP-122 and before the WAV/OGG write.

### Description

Static convolution multiplies the signal's spectrum by one fixed impulse response for the whole render: $y = x * h$, one $h$, forever. Dynamic Convolution replaces $h$ with a *time-varying impulse response* $h[n,k]$ — the IR "as it stands at output time $n$". Two regimes, one engine:

1. **Parameter-indexed IR morphing** — a family of $M$ IR frames $h_0, \dots, h_{M-1}$ (rooms, bodies, filters, vocal tracts, synthetic `ir_designer` recipes) is interpolated by a control $\theta(t)$: $h[n,k] = \sum_i w_i(\theta(n))\, h_i[k]$. A single automation curve — section of the form, envelope follower, MIDI CC, LFO, or a UnitMatrix column — glides the kernel from one space/timbre to another. This is the "morphing reverb" / "body morph" / "vocal-tract morph" family (Kontakt 5's Dynamic Convolution; LiquidSonics-style fusion IRs).
2. **Blockwise time-varying convolution** — the IR is *replaced* (not interpolated) on a block schedule: each output block $b$ is filtered by the IR frame active for that block. This is the partitioned-convolution regime (Gardner 1995; Wefers 2015; Farina 2025): the IR is partitioned into $P$ blocks; each partition's spectrum can be updated independently and at its own rate; abrupt swaps are smoothed by per-partition crossfades. This is what makes real-time dynamic auralization and level/velocity-driven convolution effects possible.

Mathematically the two regimes unify: blockwise replacement is the limit of a very fast morph ($\theta$ stepping at block rate with a short crossfade). The musical content of DCL is therefore *kernel motion*: the filter through which every voice passes becomes an animated object. A render can start in a tight vocal booth, bloom into a cathedral, pass through a metallic plate, and land in a guitar-body resonance — with every intermediate IR a genuine convolution (no spectral-patch seams of the STFT-morph kind), and with the dry signal untouched (the wet/dry law is the same as SP-009).

Differentiators: **SP-009** owns the *static* kernel (its IR never moves); DCL's degenerate $\theta=\text{const}$ case must reproduce SP-009 bit-for-bit — a built-in sanity check. **SP-048 (Commuted Synthesis)** pre-convolves an excitation with a body IR *once* to drive a Karplus-Strong loop; DCL convolves the *rendered programme* with a moving kernel. **SP-031** morphs magnitude envelopes per STFT bin (phase re-synthesized); DCL morphs the kernel itself, so phase relationships of the IR (early-reflection delays, comb structure) morph too — audible as the space's geometry changing, not just its EQ.

### Technical Mechanics

**Static convolution (the core SP-009 already uses).** For IR length $L$:

$$y[n] = \sum_{k=0}^{L-1} h[k]\, x[n-k] \qquad\Longleftrightarrow\qquad Y(\omega) = H(\omega)\, X(\omega)$$

**Time-varying IR (the DCL generalization).** The IR becomes a function of output time $n$:

$$y[n] = \sum_{k=0}^{L-1} h[n,k]\, x[n-k], \qquad h[n,k] \equiv \text{IR tap } k \text{ applied at time } n$$

Causality is preserved as long as $h[n,k]$ is defined for all $n$ (an IR that changes *after* the input passed through it cannot retroactively affect that input — the blockwise convention below respects this by construction).

**Morph interpolation (regime 1).** With $M$ IR frames and normalized weights $\sum_i w_i(\theta) = 1$:

$$h[n,k] = \sum_{i=0}^{M-1} w_i\big(\theta(n)\big)\, h_i[k] \qquad\Longrightarrow\qquad y[n] = \sum_{i=0}^{M-1} w_i\big(\theta(n)\big)\, \big(x * h_i\big)[n]$$

Linear crossfade $w_0 = 1-\theta,\ w_1 = \theta$; equal-power crossfade $w_0 = \cos(\tfrac{\pi}{2}\theta),\ w_1 = \sin(\tfrac{\pi}{2}\theta)$ (constant perceived loudness between energy-normalized IRs). Two distinct implementations:

- **IR-domain interpolation** (1× convolution cost): form $\bar h[n] = \sum_i w_i h_i$ per sample/block, convolve once. Risk: the two IRs *interfere* inside the single filter during the fade (their partials/comb structures beat), producing phaser-like colorations — usually fine for room tails, wrong for filter/body morphs.
- **Output-domain crossfade** (2× cost): compute $x * h_i$ for the two active frames, crossfade the *outputs*. Both filters stay pure; the fade is artifact-free but costs two convolutions. The practical compromise (used below) is **partition-spectrum interpolation**: crossfade the *partition spectra* $H_{i,p}$ in the frequency domain at block rate — 1× FFT cost with artifact behavior close to output-domain quality, because each partition's contribution is coherent.

**Partitioned block convolution (regime 2; Gardner 1995).** Split the IR into $P$ partitions of length $L_p$ (uniform: $L_p = L$; non-uniform: $L_p = L_0 2^{p}$):

$$h[k] \to \{h_p[m]\}_{p=0}^{P-1}, \qquad y[n] = \sum_{p=0}^{P-1} \big(x * h_p\big)[n - \Delta_p], \qquad \Delta_p = \sum_{q<p} L_q$$

Each partial convolution is FFT block convolution with overlap-add/save: block size $B$, transform size $N = B + L_p - 1$ (next power of two). Per block of $B$ samples the cost is $O\big(P\, N \log N\big)$ FFT work, i.e. $O\big(\tfrac{L_{IR}}{L_p}\, (B{+}L_p)\log(B{+}L_p)\big)/B$ per sample. Gardner's zero-latency trick: the first partition ($p=0$) runs as direct time-domain taps (no block delay), so the dry path is sample-aligned while the tail rides the FFT pipeline — this is what keeps DCL compatible with the zero-drift invariant (see UnitMatrix Integration). Non-uniform partitioning (Wefers 2015; Farina 2025) puts only the first two small partitions in the latency path: latency $\approx 2L_0$ with CPU within ~1.5× of the optimal uniform configuration.

**Dynamic update & anti-zipper crossfade.** At a morph event (block boundary $b$), the partition spectra change:

$$H_p^{(b)}(\omega) \;\leftarrow\; \sum_i w_i(\theta_b)\, H_{i,p}(\omega), \qquad p = 0,\dots,P-1$$

The swap is smoothed over $R$ samples with a first-derivative-continuous window $c(t) = \sin^2\big(\tfrac{\pi t}{2R}\big)$ (equal-power, zero derivative at both ends — no click). Tail partitions ($p$ large) are updated on a sparser schedule than onset partitions — perceptual scheduling: the tail's fine structure is masked, only its energy envelope is audible, so it may morph at 1/4–1/8 the rate (Wefers). The partition-wise update rate is itself a musical parameter (see RHYTHM).

**Normalization.** Before morphing, IR frames are equal-energy normalized: $h_i \leftarrow h_i / \|h_i\|_2$ (optionally per-octave band). Otherwise the morph pumps loudness. For brightness-tracking morphs use **power interpolation** of magnitudes $\big|H(\omega)\big| = \sqrt{w_0 |H_0|^2 + w_1 |H_1|^2}$ rather than linear $|H|$ interpolation (linear dips mid-fade).

**Verification chain.** (i) impulse in, $\theta$ frozen → output must equal the interpolated IR exactly (identity test); (ii) $\theta=\text{const}$ render must match SP-009 static convolution of the same IR bit-for-bit in float; (iii) zipper test: step $\theta$ abruptly with crossfade off → measure broadband click energy; with crossfade on → smooth, no click at the seam; (iv) zero-drift: sample count identical to input, `validate()` passes, cell length in ticks preserved.

### Musical Elements Framework

- **PITCH:** convolution is linear — a static IR adds no new pitch material, only spectral weighting; the *motion* of the IR, however, colors pitch expressively: a pitched IR (an `ir_designer` `chord_body` or `vowel` frame) turns the voice into a resonator whose formants glide as $\theta$ moves; oscillating $\theta$ at sub-audio rate = "formant vibrato" (a vowel morph wobble that thickens sustained pitches without touching the source oscillator); stepping $\theta$ rhythmically = pitch-color arpeggiation of a single note. Unpitched (room/plate) frames leave pitch untouched but change which partials survive.
- **RHYTHM:** two independent rhythmic layers. (a) *Morph rhythm* — the $\theta$ curve can be tempo-synced (LFO, step sequencer, or a per-section automation grid), turning the kernel into a rhythmic filter: a drum bus morphing booth→hall→plate on the beat grid re-times and re-spaces every hit. (b) *Partition rhythm* — the tail-partition update schedule (1/4, 1/8 rate) sets how fast the space "breathes"; slow updates = stable space, fast = shimmering instability. IR families with sparse early reflections (`drawn_echoes`) morph into delay patterns — the rhythm of the space itself.
- **HARMONY:** the IR spectrum multiplies the chord spectrum; morphing between IRs *moves* the harmonic emphasis (formant bands, comb notches) over a static chord — the harmonic equivalent of a filter sweep but with the full modal structure of a space/body moving, not a single cutoff. Morphing between two *pitched* IR families (two `chord_body` frames tuned to different roots) glides a resonant chord under the harmony; the beating during the fade is musically usable (a deliberate "detuned resonator" moment). No new intermodulation products arise (linearity) — unlike waveshaping methods, DCL can morph harmonically *without* adding IMD.
- **STRUCTURE:** the morph curve is a macro-form. Section-scoped targets: intro = close booth (dry, small IR), verse = small room, chorus = cathedral with the crossfade spanning the seam; a timbral arc (body → vocal tract → plate) can define an entire song form. The same automation infrastructure as SP-050/SP-122 (breakpoint sets per section) drives $\theta$, so the form *is* the kernel trajectory; contrast = IR-family distance across seams, repetition = returning to a previous $\theta$ (and thus a previous space).
- **TEXTURE:** DCL's home turf. Morphing room tails = texture "bloom" (the reverb swells from tight to vast while the dry stays put); metallic ↔ warm = grit control; `reverse_bloom` frames = percussive swells; the crossfade duration itself is a texture parameter (5 ms = snap morph, 1 bar = slow bloom). Because the kernel is a genuine convolution at every instant, the texture never develops the "spectral smear" of STFT morphs — it stays a *place*, just a moving one.

### UnitMatrix Integration

- **Voices = rows:** per-voice IR family + per-voice $\theta$ trajectory. A lead voice can ride a vocal-tract morph while pads sit in a static hall and drums live in a tight booth — each row is an independently animated convolution, giving every voice its own spatial/timbral motion. Bus variant: sum rows in float, run ONE morphing convolution on the bus (cheaper, and — like SP-122 — dither/processing happens once on the mix, not per stem).
- **Sections = columns:** each column carries a breakpoint set for `morph_target` (which IR frame or family), `morph_position θ`, `crossfade_samples R`, and `tail_update_rate`. These interpolate across section boundaries; the *crossfade* — not a reset — carries the kernel across the seam, so the form animates the filter without clicks.
- **Cells = MusicUnit:** cells trigger morph events (a cell with `morph+0.25, crossfade=1 bar`). Two invariants: (a) the convolution state — delay-line history and FFT overlap buffers — is indexed on the **absolute sample counter** and never reset at a cell/section seam (a reset injects a step into the filter → click + transient at every seam, the same bug class as SP-122's RNG reset); (b) the stage is strictly sample-in/sample-out, tick↔sample mapping untouched — `validate()` still passes, cell length in ticks preserved bit-exactly, zero-drift guaranteed (the Gardner zero-latency first partition keeps the wet path sample-aligned with the dry).
- **Produce dispatch:** `workflows.musicom_workflow.produce(method="SP-123")` → `sound/effects/dynamic_convolution.py` (class `DynamicConvolution`: `set_ir_family()`, `set_morph_position()`, `process()`), IR frames from `sound/effects/ir_designer.py`, invoked as a post stage in `sound/render/pipeline.py`; deterministic per seed (seeded morph curve + fixed partition schedule) so re-renders are byte-identical (`GOLDEN_SHA256`-safe).

### Pitfalls

1. **Zipper noise on abrupt IR swap.** Stepping $\theta$ with no smoothing replaces the kernel discontinuously → broadband click/zipper on the *whole* wet signal. Always crossfade over $\ge$ a few ms with a first-derivative-continuous window ($\sin^2$ or raised cosine); per-partition smoothing prevents the tail from "snapping".
2. **IR-domain vs output-domain crossfade is a real fork.** Interpolating two IRs in the time domain makes their partials/comb structures interfere inside one filter (phaser-like beating mid-fade). Output-domain crossfade is clean but 2× CPU. Use partition-spectrum interpolation (1× cost, coherent per partition) for long IRs; reserve output-domain for short, filter-like IRs where interference is objectionable.
3. **Loudness pumping.** Morphing between IRs of different energies (or with linear magnitude interpolation) changes the wet level — the fade sounds like a volume swell, not a space change. Equal-energy-normalize frames and use equal-power weight laws; for brightness-tracking morphs, power-interpolate magnitudes $\sqrt{w_0|H_0|^2+w_1|H_1|^2}$.
4. **Latency misaligns dry and wet.** Naive block convolution delays the wet path by the block size; mixing a delayed wet with the live dry combs transients and, worse, breaks sample-level alignment of the render. Use the Gardner zero-latency scheme (first partition in the time domain) so the dry/wet mix is sample-aligned — this is also what keeps the zero-drift invariant intact.
5. **FFT block-boundary clicks.** If a partition spectrum changes mid-overlap-add, the overlap region sums two different filters → click. Change spectra only at block boundaries and crossfade over the overlap window $R$; never change $H_p$ mid-block.
6. **Pre-echo and phase artifacts.** Morphing between linear-phase-ish IRs (filter sweeps, body IRs) produces pre-echo/smear because the phase of the interpolated kernel is a mixture. Use minimum-phase-matched frames, or interpolate magnitudes with phase continuation, for filter-like morphs; room IRs are usually forgiving.
7. **CPU blow-up from naive multi-target morphing.** $M$ targets × full convolution = $M$× cost. Interpolate the partition *spectra* once per block (1× FFT cost) instead of running $M$ convolutions; schedule tail partitions at reduced update rates (1/4–1/8) — perceptually free, big CPU win.
8. **Linear magnitude interpolation dips.** $\big|H\big| = w_0|H_0| + w_1|H_1|$ sags mid-fade where the two spectra are disjoint (audible "hole" in the morph). Power interpolation $\sqrt{w_0|H_0|^2 + w_1|H_1|^2}$ tracks perceived brightness.
9. **Stereo IR desync.** Morphing L and R IR pairs with independent $\theta$ (or independent crossfade indices) makes the image wander and the space "rotate" unintentionally. Drive both channels from one shared $\theta$ and one shared crossfade counter.
10. **Confusing DCL with SP-009.** Static convolution is the degenerate $\theta=\text{const}$ case — DCL only earns its place when the kernel moves. Keep the frozen-$\theta$ render as a regression test: it must match SP-009's static convolution bit-for-bit in float, which also double-checks that the partition machinery is transparent.
```

## 10. Next free SP ID

**SP-124** (SP-123 is now the highest registered sound-production method).
