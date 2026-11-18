# Report SP-144 — PADsynth Spectrum-to-Wavetable Synthesis (PADS)

**Date:** 2026-11-18 (cron). **Agent:** sound production research agent.

## Identity

- **Method ID:** SP-144 (dynamically resolved — see Resolve below)
- **Method name:** PADsynth Spectrum-to-Wavetable Synthesis (PADS) — Nasca's spectrum→wavetable construction algorithm (ZynAddSubFX PADsynth module)
- **Layer:** **absolute** (sound production — LAYER_ARCHITECTURE.md). Classification: **Synthesis Engines** (per the methods_db summary-table taxonomy; wavetable-construction algorithm, sibling of SP-041/SP-039/SP-116).
- **One-line description:** Builds a perfectly looped wavetable directly from a user harmonic spectrum with a single inverse FFT — each harmonic is spread into a Gaussian detune band (bandwidth in cents of the first harmonic, growing linearly with harmonic number) with uniform-random per-bin phases, so internal ensemble beating is baked into the table with zero LFOs and zero overlap-add; extended form adds inharmonic relF ratios (bells) and bwscale growth; base_frequency resampling keeps the spectral envelope fixed in Hz across the keyboard.
- **Candidate code path:** `sound/synthesis/padsynth.py` (new module; NumPy-only table builder + minimal phase-accumulator loop player; dispatch from `workflows/musicom_workflow.py::produce(method="SP-144", ...)`).

## Resolve of the next SP number

- Highest existing SP-ID: **SP-143** (Neural GAN Vocoder Synthesis GANV) — confirmed by scanning the summary table rows `| **SP-NNN** |` (max SP-143 at line 360) AND the standalone files `sound_method_SP-*.md` (max = SP-143_GANV) AND `report_SP-*.md` (max = report_SP-143.md). The "Method 144 / Method 145" headers in the DB are **composition-method** numbers (LSPC, DPBC), not SP numbers — no collision.
- Cross-check: `grep -n "SP-144"` on methods_db.md before entry = **0** hits.
- **New ID = SP-144.**

## Novelty audit (grep on methods_db.md before entry)

| pattern | hits | meaning |
|---|---|---|
| `padsynth` / `PADsynth` | **0** | family absent |
| `Nasca` | **0** | author absent |
| `base_frequency` | **0** | key trick absent |
| `harmonic profile` | 2 | both TWEMS organ drawbar prose (fixed 9 ratios, no detune bands) |
| `bandwidth.*cents` | 3 | all SP-050 spectral-delay window prose |
| `detuned.*band` | 4 | SP-141 supersaw *playback* prose (audio-rate oscillator stack) |
| `spectrum.*IFFT` | 2 | SP-055 FSHT Hilbert analytic signal / SP-056 Walsh sequency — unrelated |

Wavetable family already in DB: SP-041 BLW-MI (playback-side mipmaps/morph of pre-computed tables), SP-039 IFFT additive (per-frame IFFT + overlap-add resynthesis), SP-116 DSFS (closed-form time-domain additive), SP-022 wave terrain (2-D surface scanning), SP-018 scanned synthesis (physical-model-driven scanning). **No SP method constructs the table from per-harmonic detune bands → SP-144 is novel** (the missing table-building member of the wavetable family).

## Summary-table row appended (exact text, line 361)

```
| **SP-144** | PADsynth Spectrum-to-Wavetable Synthesis (PADS) | **Synthesis Engines** | Pad / Ensemble / Choir / Bell Wavetable Timbres | Builds a perfectly looped wavetable from a user harmonic spectrum with a single IFFT: each harmonic nh gets a Gaussian detune band bw_hz = (2^(bw/1200)-1)*f*nh wide (bandwidth in cents of the first harmonic, growing linearly with nh) with uniform-random per-bin phases — internal ensemble beating is baked into the table, zero LFOs, zero overlap-add. Energy per harmonic is bandwidth-invariant (1/bwi Gaussian profile normalization). Extended form adds relF(nh) inharmonic ratios (bells) + bwscale growth law; base_frequency resampling keeps the spectral envelope fixed in Hz across the keyboard. Public-domain algorithm (Nasca 2007, ZynAddSubFX PADsynth module). Candidate: `sound/synthesis/padsynth.py`. |
```

Row written with **zero LaTeX backslashes** (caret notation `2^(bw/1200)` instead of `$2^{bw/1200}$`) — the known `\\` double-escape pitfall cannot trigger; re-read confirmed 0 backslashes and single leading `|`.

## Line counts

- methods_db.md **before** append: **31 931** lines (measured `wc -l` immediately before `cat >>`).
- methods_db.md **after** append + table-row patch: **32 008** lines → delta **+77** (detailed section +76: 31931 → 32007; table row +1: 32007 → 32008).
- No concurrent-cron shift observed this run (verified post-append: row at 361, section at 31933, no interleaved foreign content).

## Files written

| file | role |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | summary-table row (line 361) + detailed section (lines 31933–32007, 75 lines) |
| `/opt/data/projects/Research/CompositionMethods/sound_method_SP-144_PADS.md` | standalone full write-up (144 lines: extended math, NumPy implementation sketch, references) |
| `/opt/data/projects/Research/CompositionMethods/report_SP-144.md` | this report (primary record) |
| `/opt/data/_web144_pads/*` | web research cache: padsynth_doc.htm/.txt (archived canonical page), zyn_wiki.html, padnote244.cpp, padnote.cpp/h, surge_padsynth.cpp (404), sc_padsynth.md (404), ryukau_readme.md, nyan_padsynth.md, verify_padsynth.py (+ output) |

## Research sources (fetched live 2026-11-18)

1. **Nasca, O. P. (2007). "PADsynth algorithm."** https://zynaddsubfx.sourceforge.io/doc/PADsynth/PADsynth.htm — live path now 404s; fetched via web.archive.org (`/web/2024id_/…`). Full pseudocode (basic + extended), Gaussian profile `profile(x)=exp(-x²)/bwi`, tips (random start, stereo N/2 offset, per-pitch tables, base_frequency resampling), public-domain C/C++ code. **Primary source.**
2. **ZynAddSubFX (GPL)** — tag 2.4.4 `src/Synth/PADnote.cpp` (PADnote table player) + current master `src/Synth/OscilGen.cpp` (spectrum-mode construction, `Prand` phase randomness, `ADvsPAD` flag); default table size 262144 @ 44100 Hz. (Modern repo refactored the old standalone PADsynth class into OscilGen.)
3. **Wikipedia "ZynAddSubFX"** — "an original algorithm used to generate wavetables in the PADSynth engine" (attribution corroborated).
4. **Independent implementations:** `ryukau/padsynth_kde` (Python/NumPy, KDE-profiled variant, cites canonical page); `nyanpasu64/padsynth` (Rust: `Harmonic(stdev)` mode, seedable, `random_amplitudes`, chord mode); `mmontag/padsynth-js`. (Surge XT PADSynth path and the shimpe SC-quark path 404'd — not cited.)
5. **Verified prototype (this run):** `/opt/data/_web144_pads/verify_padsynth.py` run with `$MUSICOM_PYTHON` — **6/6 checks pass** (see Verification).

## Technical mechanics summary

- **Inputs:** $N$ = table length (power of two, "like 262144"), $f_s$, $f$ = table fundamental, $bw$ = first-harmonic bandwidth in cents (>0), `number_harmonics < fs/f`, $A[1..H]$ = amplitudes.
- **Spectrum assembly:** per harmonic $nh$: $bw_{Hz} = (2^{bw/1200}-1)\, f\, nh$; $bwi = bw_{Hz}/(2 f_s)$; $fi = f\,nh/f_s$; accumulate Gaussian $e^{-x^2}/bwi$ ($x = (k/N - fi)/bwi$) × $A[nh]$ into bins $k=0..N/2{-}1$. The $1/bwi$ factor makes each harmonic's integrated energy bandwidth-invariant ($\int = \sqrt{\pi}$).
- **Phases + IFFT:** uniform random phase per bin ($\varphi_k \sim \mathcal{U}(0,2\pi)$), DC=0, conjugate-symmetric extension (incl. zero Nyquist bin), ONE IFFT, peak-normalize. Perfect loop by construction; no windowing, no overlap-add.
- **Extended:** $bw_{Hz} = (2^{bw/1200}-1)\, f\, relF(nh)^{bwscale}$, $fi = f\, relF(nh)/f_s$ — inharmonic ratios (bells) + bandwidth growth law; basic algorithm is the $relF{=}nh$, $bwscale{=}1$ special case.
- **Playback:** phase accumulator at $f_0/f_s$ rate, linear/cubic interp; random start per note-on; stereo via $N/2$ offset; per-octave table bank or base_frequency resampling of $A[]$ for keyboard anti-aliasing.
- **Complexity:** build $O(NH)$ + one $O(N\log N)$ IFFT (offline); playback $O(1)$/sample; 1 MB float32 per 262144-sample table; pure NumPy, deterministic per seed, no training, no external data.

## Verification (post-append)

- `wc -l methods_db.md` = **32 008** (before 31 931 → delta +77).
- `grep -n "| **SP-144** |"` → summary-table row at line **361** (single leading `|`, 0 backslashes — both patch pitfalls dodged).
- `grep -n "^# Sound Production Method SP-144"` → section header at line **31933**, 75-line section with all 7 required subsections (`### Source`, `### Layer`, `### Description`, `### Technical Mechanics`, `### Musical Elements Framework`, `### UnitMatrix Integration`, `### Pitfalls`).
- **Algorithm prototype 6/6 checks pass** (`/opt/data/micromamba/envs/musicom/bin/python verify_padsynth.py`): (1) N=65536 build, peak 1.0000, mean +1.38e-10 (no DC); (2) energy invariance across bandwidth — rms(bw=20)=0.2698 vs rms(bw=80)=0.2519, ratio 0.934 ≈ 1; (3) internal beating — envelope std/mean = 0.219 over the loop (evolving timbre, no LFO); (4) determinism — same seed byte-identical, different seed differs; (5) bell relF — all 10 inharmonic partials land exactly at 220·{1,2,2.4,3.2,4.2,5,6.4,7.6,8.8,9.9} Hz; (6) loop seam — max sample jump 0.3614 (click-free, perfect loop).

## Quirks / pitfalls hit

1. **Patch-tool double-escape avoidance:** the SP-144 table row was written with **zero LaTeX backslashes** (caret notation) so the known `\\` double-escape pitfall cannot trigger; re-read confirmed 0 backslashes.
2. **`||` prefix check:** re-read of line 361 shows content `| **SP-144** | …` — single pipe; the `||` seen in reader output is the line-number separator, not file content.
3. **Nyquist-bin bug in the first implementation sketch:** naive conjugate-symmetric extension `concat(X, conj(X[1:][::-1]))` yields N−1 bins (drops the Nyquist bin) → IFFT length mismatch. Fixed to `concat(X, [0j], conj(X[1:][::-1]))` (N bins) in both the sketch and the verification script; caught by check 1's shape assertion.
4. **Test-threshold false negatives (2×):** (a) top-6-bin peak picking clustered inside the strongest 220 Hz band — replaced with per-partial window probing; (b) a 0.2×max threshold missed high partials because per-bin peak amplitude falls ∝ 1/relF (wider bands spread constant energy — the algorithm's intended behavior) — replaced with a 3×spectrum-median threshold. Both were test flaws, not algorithm flaws.
5. **Live-source 404s:** the canonical sourceforge.io PADsynth page now returns 404 (nginx) — fetched via web.archive.org; Surge XT PADSynthOscillator.cpp and the shimpe SuperCollider quark also 404'd (different paths/branches) — dropped from citations rather than guessed.
6. **Symlink resolution:** `/opt/data/projects/Research` resolves into `$MUSICOM_ROOT/projects/Research` (ONE-ENV contract) — writes land in the real repo tree; verified path after write.

## Complete section text appended (lines 31933–32007)

```
# Sound Production Method SP-144 — PADsynth Spectrum-to-Wavetable Synthesis (PADS)

### Source

- **Nasca Octavian Paul, "PADsynth algorithm" (2007).** Canonical algorithm description — https://zynaddsubfx.sourceforge.io/doc/PADsynth/PADsynth.htm (fetched live 2026-11-18 via web.archive.org/web/2024/…; the live sourceforge.io path now returns 404). Contains the complete pseudocode (basic + extended algorithm), the Gaussian harmonic-profile function, input/output spec (N, samplerate, f, bw, number_harmonics, A[]), the random-phase step, tips (random start position, stereo N/2 offset, per-pitch wavetables, base_frequency resampling), and public-domain C/C++ implementations. Released **public domain** by the author.
- **ZynAddSubFX (GPL)** — the original implementation, "PADsynth module" (Wikipedia: "an original algorithm used to generate wavetables in the PADSynth engine", fetched 2026-11-18). Modern repo `zynaddsubfx/zynaddsubfx`: tag 2.4.4 `src/Synth/PADnote.cpp` (PADnote table player) and current master `src/Synth/OscilGen.cpp` (spectrum-mode wavetable construction with per-harmonic bandwidth + phase randomness `Prand`, `ADvsPAD` flag). ZynAddSubFX default table size 262144, samplerate 44100.
- **Independent implementations (fetched live 2026-11-18):** `ryukau/padsynth_kde` (Python/NumPy, KDE-profiled variant — cites the canonical page); `nyanpasu64/padsynth` (Rust resynthesis variant: `Harmonic(stdev)` mode, seedable, `random_amplitudes` flag, chord mode); `mmontag/padsynth-js` (JavaScript). All follow the same spectrum→IFFT construction.
- **Repo antecedents:** wavetable-family SP-041 BLW-MI (playback-side mipmaps/morph of pre-computed tables), SP-039 IFFT additive (per-frame IFFT + overlap-add resynthesis), SP-116 DSFS (closed-form time-domain additive), SP-022 wave terrain (2-D surface scanning), SP-018 scanned synthesis (physical-model-driven table scanning). **None constructs the table from a per-harmonic detune-band spectrum.**
- **Novelty check (2026-11-18):** `grep -ci` on `methods_db.md` **before** entry: `padsynth` = **0**, `PADsynth` = **0**, `Nasca` = **0**, `base_frequency` = **0**. `harmonic profile` = 2 (both TWEMS organ drawbar prose — fixed 9 ratios, no detune bands); `bandwidth.*cents` = 3 (all SP-050 spectral-delay window prose); `detuned.*band` = 4 (SP-141 supersaw *playback* prose); `spectrum.*IFFT` = 2 (SP-055 FSHT Hilbert analytic signal, SP-056 Walsh sequency — unrelated). **No SP method builds wavetables from per-harmonic detune bands → SP-144 is novel.**

### Layer

**absolute** (sound production — LAYER_ARCHITECTURE.md). PADS is a **Synthesis Engines** wavetable-construction algorithm: it consumes a symbolic harmonic spec (amplitudes $A[h]$, bandwidth $bw$, optional overtone ratios $relF$) and emits a static, perfectly looped wavetable that any table-scanning player (SP-041-style or a bare phase-accumulator reader) renders at pitch. It decides nothing about composition, emits no events, holds no timing authority — the player does. Stage position: **source** — PADS builds the *oscillator tables* that SP-029-style subtractive chains or SP-041-style players scan; per-row filter (SP-029/SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122). Candidate code path: `sound/synthesis/padsynth.py` (NumPy table builder + minimal loop player); dispatch from `workflows/musicom_workflow.py::produce(method="SP-144", ...)`.

### Description

PADSynth builds one large, perfectly looped wavetable directly from a user-defined harmonic spectrum — no oscillators, no filters, no overlap-add: a **single inverse FFT** turns the whole spectrum into the sample. The core idea (Nasca 2007): a real-world "harmonic" (a choir, an ensemble, a bell) is not one sine but a *band* of closely spaced frequencies. PADSynth lets the composer specify, per harmonic, an amplitude $A[h]$ and a bandwidth in cents; bandwidth grows with harmonic number (natural ensembles detune proportionally to frequency), and every bin inside each band receives a **uniform random phase**. The random phases are the trick: they are never heard as noise (all bins sit inside the harmonic's band) but they make the looped table carry continuous internal beating — each period differs microscopically from the next, exactly like $N$ detuned voices — so the sound evolves on its own, with **zero LFOs and zero playback modulation**. Because the phase pattern repeats with the loop, the evolution is perfectly periodic too (loop period = $N/f_s$). The result is the classic ZynAddSubFX pad/choir/ensemble voice: huge, organic, slow-moving, perfectly loopable. The extended algorithm adds $relF(h)$ (arbitrary overtone ratios → detuned harmonics, metallic bells, inharmonic spectra) and $bwscale$ (bandwidth growth law); the *base_frequency* trick resamples the harmonic-amplitude array per pitch so the spectral envelope stays tied to **absolute frequency** across the keyboard.

### Technical Mechanics

**1. Inputs.** $N$ = wavetable length (power of two; the doc recommends large — "like 262144"; ZynAddSubFX default 262144); $f_s$ = sample rate (44100); $f$ = fundamental frequency of the table (e.g. 440 Hz); $bw$ = bandwidth of the first harmonic in cents (must be > 0); `number_harmonics` < $f_s/f$; $A[1..\text{number\_harmonics}]$ = per-harmonic amplitudes.

**2. Spectrum assembly (basic algorithm).** Initialize `freq_amp[k] = 0` for $k = 0..N/2{-}1$ (bin $k$ ↔ frequency $k f_s / N$). For each harmonic $nh$:

$$bw_{Hz}(nh) = (2^{bw/1200} - 1)\, f\, nh, \qquad bwi = \frac{bw_{Hz}}{2 f_s}, \qquad fi = \frac{f\, nh}{f_s}$$

then accumulate the Gaussian profile into every bin:

$$x = \frac{k/N - fi}{bwi}, \qquad \mathrm{profile}(x) = \frac{e^{-x^2}}{bwi}, \qquad \mathrm{freq\_amp}[k] \mathrel{+}= \mathrm{profile}(x)\cdot A[nh]$$

The $1/bwi$ factor keeps each harmonic's integrated energy independent of bandwidth: $\int \mathrm{profile} = \sqrt{\pi}$ for any $bwi$ — the doc's rule "the harmonic must have the same amplitude, regardless of the profile functions/parameters and the bandwidth". Bandwidth in Hz grows linearly with harmonic number (constant relative detune), so wide bands merge into a noise band near Nyquist — "a normal thing", not to be avoided.

**3. Phases + single IFFT.** Every bin gets a uniform random phase; DC excluded; conjugate-symmetric extension for $k > N/2$; one IFFT for the whole sample:

$$\varphi_k \sim \mathcal{U}(0, 2\pi), \qquad X[k] = \mathrm{freq\_amp}[k]\, e^{j\varphi_k}, \qquad \mathrm{smp} = \mathrm{IFFT}(X), \qquad \mathrm{normalize}(\mathrm{smp})$$

No windowing, no overlap-add — "there is only one IFFT for the whole sample". A periodic spectrum yields a perfectly periodic (looped) time signal by construction.

**4. Extended algorithm.** $relF(nh)$ = relative frequency of the $nh$-th overtone ($relF(nh){=}nh$ → harmonic series; inharmonic ratios → bells/metallic); $bwscale$ = how fast bandwidth grows with harmonic index:

$$bw_{Hz} = (2^{bw/1200}-1)\, f\, relF(nh)^{bwscale}, \qquad fi = f\, relF(nh) / f_s$$

With $relF(nh){=}nh$ and $bwscale{=}1$ this is exactly the basic algorithm.

**5. Playback (table player).** Phase-accumulator read at pitch $f_0$: $\varphi \mathrel{+}= f_0/f_s$ per sample, linear or cubic interpolation into the table. Doc tips: (a) start each note-on at a **random table position** (avoids the identical attack on every keystroke); (b) stereo = play the same table at positions offset by $N/2$ left/right (decorrelated beating); (c) generate **different wavetables for different pitches** and use the closest (per-octave table bank — the anti-aliasing strategy, since the table is only band-limited to its own Nyquist); (d) *base_frequency* resampling: for pitch $f_0 \neq f_{base}$, resample the $A[]$ array by factor $f_{base}/f_0$ (e.g. $A_{orig} = \{1,2,1,3,0,0,1,0\}$ at 440 Hz → 16 entries at 220 Hz, 4 entries at 880 Hz) so the spectrum is constant in **Hz**, not in harmonic number.

**6. Complexity.** Table build: $O(N \cdot H)$ (H harmonics × $N/2$ bins) + one $O(N \log N)$ IFFT — offline, once per voice. Playback: $O(1)$ per sample. Memory: one float32 table of $N$ samples (262144 → 1 MB); a few tables per voice for octave coverage. Pure NumPy (`numpy.fft.ifft`/`irfft`); no training, no external data, deterministic per seed.

### Musical Elements Framework

- **PITCH**: the table's fundamental $f$ IS the pitch anchor; transposition = reading the table at another rate (phase accumulator), which shifts the whole spectrum *including the detune bands* — relative detune is preserved, so the ensemble character survives transposition. The *base_frequency* trick keeps the **absolute** spectral envelope fixed across the keyboard (harmonics tracked by frequency, not by number — Nasca's principle).
- **RHYTHM**: none intrinsic — the table is a static periodic loop; the internal beating period is $N/f_s$ seconds (262144/44100 ≈ 5.94 s), the longest "rhythmic" event in the timbre. Onset/decay shaping is delegated to the player's envelope or downstream per-row dynamics (SP-008/SP-107). Loop-seam safety is automatic: the table loops exactly, so a held note never clicks (the zero-drift invariant's audio analogue — the loop period is sample-exact).
- **HARMONY**: the amplitude array $A[]$ is a one-note spectral chord; choir = broad bands over odd+even partials, bell = inharmonic $relF$ ratios. Because the spectrum is user-specified, multiple fundamentals' partials can be summed into ONE table (the nyanpasu64 variant's chord mode) — a single-note chord timbre, the spectral analogue of SP-097 SHOS's subharmonic stacks.
- **STRUCTURE**: the table is a timbre object, not a form object; structure enters via table selection per section/row (a column change = timbre change) and via the internal evolution timescale ($N/f_s$). Multi-table banks (per octave) act as a registral macro-form.
- **TEXTURE**: the defining output. The detune bandwidth $bw$ (cents) is the single texture knob: $bw \to 0$ = pure sine-like "single voice"; $bw \approx 10$–$50$ cents = classic detuned-ensemble pad; large $bw$ = choir/noise-band shimmer (bands merge near Nyquist). Random phases produce the "many-voices" motion (chorus/ensemble) with no chorus effect; the loop makes the evolution repeat exactly.

### UnitMatrix Integration

**Voices = rows = one table per row (or per row-register).** Row $v$ params: `{N, fs, f_base, bw_cents, A[] (per-voice harmonic spec), relF[], bwscale, seed, table_bank (per-octave tables), player {interp, random_start}}`. A row's timbre identity IS its harmonic spec + bandwidth; the seed fixes the phase pattern — same spec + same seed = byte-identical table and audio (deterministic render, provenance-friendly).

**Sections = columns = table/parameter switches.** Column $j$ holds `{bw_cents_override, A[]_override, seed_j, table_bank_j}` — a column change is a timbre change (section A = narrow-band "solo" pad, section B = wide-band "choir"). Seam safety: a note held across a seam renders click-free (phase accumulator continues through the perfect loop); per-section table *swaps* land on the section grid — pick $N$ so the loop period $N/f_s$ divides the section's sample count (or resample the table to fit).

**Cells = MusicUnit.** Cell $(v, j)$: the cell's `MusicEvent` (pitch, start/end ticks) drives the player — pitch → table rate $f_0/f_{base}$, duration → sample count; `random_start` per note-on (the doc's tip) seeds the read position so repeated cells do not sound identical. Cell-level edits = local spectral surgery (per-cell $bw$ or $A[]$ overrides) without rebuilding the whole row.

**Produce dispatch:** `produce(midi_path, method="SP-144", params={"rows": {"pad": {"N": 262144, "bw_cents": 40, "amps": "1/sqrt(h)", "seed": 7}, "choir": {"N": 262144, "bw_cents": 80, "amps": "1/h^1.2", "seed": 11}}, "player": {"interp": "linear", "random_start": true}, "columns": {"A": {"bw_cents": 25}, "B": {"bw_cents": 70}}})` — the row's table is built once (offline), then the row's MIDI events render through the table player. Stage order: **PADS table build → table player (source) → per-row filter (SP-029/SP-007) → spatialize (SP-021/SP-053/SP-119) → space/tail (SP-009/SP-032/SP-140) → bus dynamics (SP-008/SP-107) → loudness (SP-126) → dither (SP-122)**. PADS emits fixed-rate PCM — resample before sample-count-sensitive stages (SP-050 spectral-delay GCD grids) or re-quantize to the tick grid.

### Pitfalls

1. **Loop-period math.** The loop period is $N/f_s$. Notes shorter than the loop truncate mid-evolution (fine — fade out); if a section needs exact loop alignment (click-free layered loops), choose $N$ so $N/f_s$ divides the section's sample count. 262144/44100 ≈ 5.94 s is long — most notes never complete a loop (that is the point: the timbre evolves).
2. **bw in cents is relative; Hz is absolute.** Basic-algorithm bandwidth is cents-of-the-first-harmonic scaled linearly with harmonic number → constant relative detune. Fixed-Hz-width bands need $relF$/`bwscale` bending; and at very low fundamentals a 40-cent band is tiny (40 cents of 55 Hz ≈ 1.3 Hz ≈ a single bin at small $N$) — raise $N$ or the band vanishes.
3. **Keep the 1/bwi normalization.** Dropping it makes wide-band harmonics louder than narrow ones — exactly what the doc forbids ("the harmonic must have the same amplitude, regardless of the profile functions/parameters and the bandwidth").
4. **DC and Nyquist bins.** Set `freq_amp[0] = 0` (no DC thump) and keep harmonic energy off the $k = N/2$ Nyquist bin (it breaks conjugate symmetry for a real IFFT) — the doc's array runs $0..N/2{-}1$ for this reason.
5. **Random start position is load-bearing.** Always playing from index 0 makes every note-on attack identical and can expose a strong transient at the table head; the doc's tip is a random start per note-on.
6. **Aliasing at high octaves.** The table is band-limited only to its own Nyquist; transposing up octaves pushes harmonics past it → foldback. Fixes: per-octave table bank (nearest table by pitch), or *base_frequency* resampling of $A[]$ so higher tables naturally carry fewer harmonics.
7. **Seed determinism.** The phase pattern (hence the beating structure) is fixed by the seed — record it in provenance; a different seed = a different "take" of the same voice (same stance as SP-141's phase-randomization seeds).
8. **Neighbour audit.** SP-041 BLW-MI = *playback* of pre-computed tables (mipmaps, morphing, PolyBLEP) — PADS is the *table-construction* algorithm those players consume; SP-039 IFFT additive = per-frame IFFT + overlap-add for *resynthesis* of existing audio — PADS is one IFFT, no overlap-add, and the spectrum is *designed*, not analyzed; SP-116 DSFS = closed-form time-domain partial summation (no IFFT, no detune bands); SP-022 wave terrain = 2-D surface scanning; SP-018 scanned = physical-model-driven scanning; SP-141 SOSS = detuned saw *stack playback* (audio-rate phase randomization) — PADS bakes the detune into one static table. **SP-144 PADS = spectrum→wavetable construction with per-harmonic Gaussian detune bands + random phases — the missing table-building member of the wavetable family.** Repo: `sound/synthesis/padsynth.py` (new; NumPy-only builder + minimal loop player; no training, no external data).
```
