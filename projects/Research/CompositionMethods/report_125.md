# Report 125 — Low-Discrepancy Sequence Composition (LDSC)

**Method ID:** 125 · **Date:** 2026-10-25 · **Job:** scheduled cron (music research agent)

## Identity

| field | value |
|---|---|
| Method name | Low-Discrepancy Sequence Composition (LDSC) |
| Paradigm | **Rules-Based** (deterministic equidistributed digital sequences; "quasi-random" in the QMC sense — neither random nor pseudorandom, with provably better balance) |
| LAYER | **concrete** (generates events that fill UnitMatrix cells; feeds `generators/`) |
| One-line description | Composes from deterministic equidistributed digital sequences — van der Corput radical inverse $g_b(n)$, Halton/Hammersley/Sobol nets — whose star discrepancy $D_N^* \le C(\log N)^s/N$ guarantees every time window and pitch band its fair share of events: maximal evenness WITHOUT periodicity and WITHOUT randomness. |
| Primary elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Moderate (Region-width-guided; HOME/LIFT/TENSE/TURN = region widths, visit frequency = width exactly) |
| Metric Binding | Grid-Locked / Continuous (quantized slots or raw ticks) |
| Memory Depth | None (State = index n) |
| Time Complexity | $\mathcal{O}(N)$ ($O(\log_b n)$ digit ops per radical inverse, amortized $O(1)$ per event) |
| Next free ID | **126** |

## Full summary-table row (appended at methods_db.md line 135)

```
| **125** | concrete | Low-Discrepancy Sequence Composition (LDSC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Region-width-guided, HOME/LIFT/TENSE/TURN = region widths) | Grid-Locked / Continuous (quantized slots or raw ticks) | None (State = index n) | $\mathcal{O}(N)$ | Composes from deterministic equidistributed digital sequences — van der Corput radical inverse $g_b(n)$, Halton/Hammersley/Sobol nets: star discrepancy $D_N^* \le C(\log N)^s/N$ guarantees every prefix window and pitch band its fair share of events (verified: $D^*_{1024}=0.00098$ vs random 0.029; pc max|dev| 2.0 vs 5.0). $\varphi_2(n)$ = onset ticks (each new onset bisects the largest empty gap, verified n=1..255), $\varphi_3(n)$ = pitch class / harmonic region (visit frequency = region width exactly, verified max dev 0.0010), per-section scrambling = macro-form, coprime base pairs per voice = independent balanced streams (joint balance verified). Rules-Based aperiodic foil to 012 Euclidean (periodic evenness) / 076 Thue-Morse (binary parity); proof-backed "quasi-random" replacement for RNG-driven placement (040/048/053). |
```

## Line counts

| metric | value |
|---|---|
| methods_db.md before | 28132 lines |
| methods_db.md after | 28222 lines |
| delta | **+90** (+89 method section at lines 28134–28222, +1 summary row at line 135) |

## Files

| file | path | status |
|---|---|---|
| Standalone file path | `/opt/data/projects/Research/CompositionMethods/method_125_LDSC.md` | written (11 369 B) |
| Report (this file) | `/opt/data/projects/Research/CompositionMethods/report_125.md` | written |
| Verification script | `/opt/data/projects/Research/outputs/ldsc_validate/verify_ldsc.py` | written, run, **12/12 checks pass** (musicom env, numpy 1.26.4) |
| DB method section | `methods_db.md` lines 28134–28222 | appended, verified by grep |
| DB summary row | `methods_db.md` line 135 | patched, verified (single `|` prefix — 0 double-pipe; single-backslash `\mathcal` — 0 `\\mathcal` on the row) |

## Candidate code path

`generators/lds_composition.py` — class `LDSComposer` with
`radical_inverse()`, `halton()`, `hammersley()`, `sobol()`,
`scramble()` (Owen digital shift), `region_partition()`, `realize_cell()`;
consumed by `workflows/unitmatrix_composer.py` (cells = decoded index windows
padded via `_unit_from_events` for the zero-drift gate). The abstract
pre-pass (per-section region partitions exported as weighted tension curves)
feeds `rules/subset_network.py`.

## Classification details

- **Paradigm — Rules-Based.** The sequences are deterministic functions of
  the integer index $n$ (digit reversal), not random draws. The QMC
  literature calls them "quasi-random": neither random nor pseudorandom, but
  sharing useful properties of random variables with *provably better*
  balance (Niederreiter 1992). Generation is arithmetic, not sampling; seed
  = index schedule + scrambling keys. The stochastic-flavored uses
  (replacing an RNG) are explicitly a different job (DB Pitfall 7).
  Nearest catalogue neighbours: 012 Euclidean / 069 Christoffel (periodic
  evenness), 076 Thue-Morse (base-2 parity digital sequence), 121 IETC
  (ergodic exact visit frequencies by rotation), 084 ZMRC (statistical
  rank-frequency). LDSC is the deterministic *aperiodic evenness* family:
  the largest-gap bisection rhythm, exact region-visit frequencies, and
  coprime-base independent streams — none of which any existing method owns.
- **Layer — concrete.** The draws decode directly to `MusicEvent`s (onset
  ticks from $\varphi_2$, pcs from $\varphi_3$, velocity from $\varphi_5$,
  harmonic function = region index) filling UnitMatrix cells. An abstract
  pre-pass is natural (region partition = tension-curve designer →
  `rules/subset_network.py`), but the primary feed is event generation.
- **Novelty.** No dedicated music-composition literature exists for the
  van der Corput / Halton / low-discrepancy family — confirmed by arXiv API,
  Crossref API and DuckDuckGo searches (2026-10-25). Same profile as
  in-catalogue entries 076/077/083/090/091/112: documented mathematics,
  novel musical application.
- **Musical argument.** "Evenness with a proof, without periodicity": the
  N=16 min-gap measurement (0.0312 vs random 0.0032, 9.7×) is the groove
  statement — random placement clumps, LDSC spreads, both without a bar
  periodicity. Fux-style balance rules (no clumping, no starvation) become
  discrepancy bounds the composer can compute *before* writing a note.

## Verified measurements (script: outputs/ldsc_validate/verify_ldsc.py, musicom env, numpy)

| property | measured |
|---|---|
| $g_2$ first 8 values | 1/2, 1/4, 3/4, 1/8, 5/8, 3/8, 7/8, 1/16 (dev 0) |
| $g_3$ first 8 values | 1/3, 2/3, 1/9, 4/9, 7/9, 2/9, 5/9, 8/9 (dev < 1e-12) |
| star discrepancy $D^*_{1024}(g_2)$ | 0.00098 ≤ (log2 1024 + 2)/1024 = 0.01172 |
| random baseline | mean 0.02922 (20 trials) → **30×** better |
| largest-gap bisection | 255/255 points land in the largest empty gap |
| rhythm evenness (N=16 min-gap) | 0.0312 vs random 0.0032 → **9.7×** |
| pc balance (Halton 2,3, N=120) | max|dev| 2.0 vs random 5.0 |
| region visits = widths | [0.350, 0.200, 0.200, 0.249] vs [.35,.20,.20,.25], dev 0.0010 (N=2000) |
| scrambling variation | two XOR masks reorder; $D^*$ 0.0142 / 0.0147 ≤ 0.125 bound |
| determinism | pure function of $n$ (asserted identical) |
| joint balance (Halton 3,5, 4×4 cells, N=400) | max|dev| 2.0 (expected 25/cell) |

## Quirks & pitfalls hit during the job

1. **Method-number resolution.** Max algorithmic ID scanned from the summary
   table rows (001–124, sparse historical gaps e.g. 058 referenced but never
   registered) AND cross-checked against `method_*.md` / `report_*.md` files
   (method_124_DPPC.md exists; no 125 anywhere; grep for `| **1[2-9][5-9]** |`
   and `method_12[5-9]*` returned zero) → new ID = 125. Next free ID = **126**.
2. **`curl | python3` is blocked** by the security scan (tirith
   `curl_pipe_shell`) — Crossref JSON had to be saved to files and parsed
   separately. Also learned: inline `python -c` is blocked; verification
   lives in a script file (`verify_ldsc.py`).
3. **arXiv has no direct music papers** on van der Corput/low-discrepancy
   (queries returned the Plackett-Luce QMC paper and an IET-discrepancy
   paper, no composition work). This is a *novelty confirmation*, not a gap:
   the method is built on the canonical QMC mathematics (van der Corput
   1935; Halton 1960; Hammersley 1960; Sobol 1967; Niederreiter 1992) and
   matches the profile of DB entries 076/077/083/090/091/112. The report
   states this honestly in the Source section.
4. **Two initial verification failures were test bugs, not method bugs.**
   (a) `7/9` as a Python literal vs `7 * (1/9)` accumulated by the radical
   inverse differ by 1 ulp — the exact-value assertion needed a 1e-12
   tolerance. (b) The largest-gap test compared the new point against gaps
   computed *after* insertion (so the bisected largest gap always "lost" to
   the second-largest) — fixed by testing against the *pre-insertion* gaps.
   After both fixes: 12/12 PASS, exit 0.
5. **Patch-tool pitfalls (both avoided).** Summary-table row inserted via a
   unique tail anchor (`greedy MAP = deterministic $(1-1/e)$ mode. |` from
   the 124 row); verified post-patch with `grep -cF '| **125** |'` = 1,
   `sed -n '135p' | grep -c '^||'` = 0 (no double-pipe prefix) and
   `grep -c '\\\\mathcal'` on the row = 0 (no double-escaped LaTeX; the 41
   `\\mathcal` lines elsewhere in the file are all pre-existing historical
   sections, untouched). Also hit GNU grep BRE `\|` = alternation when
   counting the row (`grep -c '^\| \*\*125...'` matched every line) — fixed
   with `grep -F`.
6. **DB section appended via the sanctioned workflow** (write_file temp →
   `cat >>` → `rm`); no heredoc/execute_code used; temp file confirmed gone.
   The append raised a "file modified since last read" warning on the
   subsequent patch (expected — the `cat >>` was the external write);
   re-read before patching.
7. **Env.** Used `$MUSICOM_PYTHON` (ONE-ENV contract) for the verification
   script; numpy 1.26.4 present. Verification script lives under
   `/opt/data/projects/Research/outputs/ldsc_validate/` (output rule
   compliance).

## Appended method section text (byte-identical to methods_db.md lines 28134–28222)

<!-- APPENDED_SECTION_BEGIN -->
# Low-Discrepancy Sequence Composition (LDSC) (Method 125)

### Source

- **van der Corput, J. G. (1935).** "Verteilungsfunktionen (Erste Mitteilung)." *Proceedings of the Koninklijke Akademie van Wetenschappen te Amsterdam* 38, 813–821. — the origin: the radical-inverse sequence $g_b(n) = \sum_{k=0}^{L-1} d_k(n)\, b^{-k-1}$ (digits of $n$ in base $b$, read in reverse after the radix point), the simplest one-dimensional low-discrepancy sequence over $[0,1)$.
- **Halton, J. H. (1960).** "On the efficiency of certain quasi-random sequences of points in evaluating multi-dimensional integrals." *Numerische Mathematik* 2, 84–90. — the $s$-dimensional generalization $x(n) = (g_{b_1}(n), \dots, g_{b_s}(n))$ with pairwise-coprime bases, star discrepancy $D_N^* \le C' (\log N)^s / N$.
- **Hammersley, J. M. (1960).** "Monte Carlo methods for solving multivariable problems." *Annals of the New York Academy of Sciences* 86, 844–874. — the Hammersley set $x(n) = (g_{b_1}(n), \dots, g_{b_{s-1}}(n), n/N)$: one exact endpoint dimension, discrepancy $C (\log N)^{s-1} / N$ — the "closed form" (last event lands exactly on the cadence point).
- **Sobol', I. M. (1967).** "On the distribution of points in a cube and the approximate evaluation of integrals." *USSR Computational Mathematics and Mathematical Physics* 7(4), 86–112. — direction numbers / digital nets: the high-dimensional workhorse (Antonov–Saleev Gray-code variant; Bratley & Fox 1988, *ACM TOMS* 14(1), 88–100, Algorithm 659).
- **Niederreiter, H. (1992).** *Random Number Generation and Quasi-Monte Carlo Methods.* SIAM CBMS-NSF 63. — discrepancy theory: the star-discrepancy bounds and the "quasi-random ≠ random" epistemology (deterministic sequences that share the useful properties of random variables with provably better balance).
- **Kuipers, L. & Niederreiter, H. (1974/2005).** *Uniform Distribution of Sequences.* Dover (pp. 129, 158). — equidistribution theory: Weyl's criterion, the Kronecker/rotation family (golden-ratio case), and the digital-sequence family.
- **Owen, A. B. (1997).** "Monte Carlo variance of scrambled net quadrature." *SIAM Journal on Numerical Analysis* 34(5), 1884–1910. — scrambling (digit permutations + digital shifts): the standard way to get *variation without losing balance* — the section-variation mechanism used below.
- **Wikipedia: "Van der Corput sequence", "Low-discrepancy sequence", "Halton sequence"** (fetched 2026-10-25). — cross-check of the radical-inverse definition (including the Python implementation), the star-discrepancy bounds $D_N^*(g_b) \le C \log N/N$ and the Hammersley/Halton constants, and the golden-ratio Kronecker case $c = (\sqrt5-1)/2 \approx 0.618034$.
- **Novelty check (2026-10-25):** arXiv API, Crossref API and DuckDuckGo searches for "van der Corput / Halton / low-discrepancy + music / rhythm / composition" returned **no** dedicated music-composition literature — the family is proposed here as a novel composition technique on documented QMC mathematics, the same profile as in-catalogue entries 076/077/083/090/091/112.
- In-catalogue lineage: **012 Euclidean** (periodic maximal evenness) and **069 Christoffel** (balanced words) own the *periodic* evenness; **076 Thue-Morse** is a base-2 *parity* digital sequence (balance of digit sums); **121 IETC** guarantees visit frequencies by unique ergodicity (rotation); **084 ZMRC** shapes *statistical* rank-frequency. LDSC is the deterministic *aperiodic* evenness family: balance with a proof, without periodicity and without randomness.

### Layer

**concrete** — the low-discrepancy draws decode directly to `MusicEvent`s (onset ticks from $\varphi_2$, pitch classes from $\varphi_3$, velocity from $\varphi_5$, region index = harmonic function) that fill UnitMatrix cells. Nothing is left abstract; the index window per (voice, section) is resolved immediately into events. Feeds `generators/`.

An **abstract** pre-pass is natural and cheap: the region partition $[0,1) \to$ {HOME, LIFT, TENSE, TURN} *is* a tension-curve designer (region widths are the tension weights, and the visit frequency equals the width exactly), so the per-section partition can be exported to `rules/subset_network.py` as a weighted progression plan for any concrete method downstream. The layer tag stays concrete because the primary feed is event generation.

### Paradigm

**Rules-Based** — the sequences are deterministic functions of the integer index $n$ (digit reversal), not random draws. The "quasi-random" label in the QMC literature is deliberate: the values are "neither random nor pseudorandom, but share some properties of random variables" (Niederreiter 1992) — with *provably better* balance. Generation = arithmetic, not sampling; the same seed (here: the index schedule + scrambling keys) always produces the same piece. The stochastic-flavored uses (replacing an RNG in a stochastic method) are explicitly a *different* job (see Pitfalls).

### Description

**Low-Discrepancy Sequence Composition (LDSC)** replaces both the random number generator and the periodic grid with a deterministic *equidistributed* sequence. The core object is the **radical inverse** (van der Corput, 1935): for $n \ge 1$ with base-$b$ digits $n = \sum_k d_k(n) b^k$,

$$g_b(n) \;=\; \sum_{k=0}^{L-1} d_k(n)\, b^{-k-1} \;=\; 0.\, d_{L-1} \cdots d_0 \text{ in base } b,$$

i.e. the digits of $n$, reversed and pushed after the radix point. $g_2$ gives $1/2, 1/4, 3/4, 1/8, 5/8, 3/8, 7/8, 1/16, \dots$ (verified) — the sequence *recursively bisects the timeline*, and every new point lands in the **largest currently-empty gap** (verified for $n = 1..255$). This one property is the whole musical idea: **the van der Corput rhythm is the sound of recursive bisection** — each onset fills the biggest silence so far.

**The balance guarantee.** The star discrepancy of the first $N$ points,

$$D_N^*(g_b) \;=\; \sup_{0 \le x \le 1} \left| \frac{\#\{n \le N : g_b(n) < x\}}{N} - x \right| \;\le\; C\,\frac{\log N}{N},$$

bounds *every* prefix window: every segment of the piece gets its fair share of events. Random i.i.d. points only achieve $\Theta(N^{-1/2})$ in expectation — measured here $D^*_{1024} = 0.00098$ for $g_2$ vs a random mean of $0.02922$ (30× better), inside the bound $(\log_2 N + 2)/N = 0.01172$. **Evenness with a proof, without periodicity** — the aperiodic complement to 012 Euclidean (which is maximally even only because it repeats every bar) and 069 Christoffel words (balanced only as infinite periodic/Sturmian words).

**The dimensions (Halton).** With pairwise-coprime bases the $s$-dimensional Halton sequence $x(n) = (g_{b_1}(n), \dots, g_{b_s}(n))$ inherits the bound with $(\log N)^s$: the 2D (2,3) Halton spreads (time, pitch-class) uniformly over the unit square — every pitch-time cell gets its fair share of notes (verified: pc histogram at $N{=}120$ has max deviation 2.0 vs 5.0 for random). The Hammersley variant swaps the last radical inverse for the *exact* endpoint $n/N$ — a built-in cadence: the $N$-th event lands precisely at the section end (discrepancy $C(\log N)^{s-1}/N$, one power better).

**Harmony as a partition of $[0,1)$.** The unit interval is cut into function regions (HOME/LIFT/TENSE/TURN) of widths $w_j$; $g_3(n)$ selects the region for event $n$. Equidistribution makes the *visit frequency of region $j$ equal $w_j$ exactly* (verified: widths $[0.35, 0.20, 0.20, 0.25]$ at $N{=}2000$ gave counts $[0.350, 0.200, 0.200, 0.249]$, max deviation 0.0010). Tonal gravity is a dial: widen HOME, and the tonic *provably* recurs more often — no weights, no sampling variance, the same guarantee family as 121 IETC's unique ergodicity but obtained by digit reversal instead of rotation.

**Variation (scrambling, Owen 1997).** A section is an index window $[N_s, N_{s+1})$ plus a scrambling key (digit permutation and/or a digital XOR shift). Scrambling reorders the values while provably preserving the discrepancy bound (verified: two XOR masks change the order, both keep $D^* \le$ bound). Repetition = reusing the key; contrast = different keys; macro-form = the schedule of keys, widths, and densities.

**Multi-voice independence.** Voice $v$ draws from its own base pair — (2,3), (2,5), (2,7), … — pairwise coprime, so the per-voice streams are *jointly* equidistributed (verified: 2D Halton (3,5) fills a 4×4 cell grid with max deviation 2.0 vs expected 25/cell at $N{=}400$): independent balanced streams with a provable joint-balance guarantee, no correlation tuning.

**Cost.** $O(\log_b n)$ digit operations per radical inverse — effectively $O(1)$ amortized per event (the incremental "bit-reversal carry" formulation), $O(N)$ for a whole piece, no state beyond the index. The entire method is a few lines of arithmetic; the UnitMatrix fill is trivially real-time.

### Musical Elements Framework

**PITCH**: the 2D Halton pair $(\varphi_2(n), \varphi_3(n))$ gives (time, pitch-class); $\varphi_3$ is the pitch axis because base 3 decorrelates from base 2's dyadic rhythm. Pitch classes are visited with *guaranteed* frequency $1/12 \cdot N \pm O(\log N)$ (verified: max deviation 2.0 over 120 notes) — the "modal balance" of 076 Thue-Morse but for 12 (or any $k$) classes and *aperiodically*. Consecutive $\varphi_3$ values alternate wide and narrow jumps in a self-similar pattern (the digit-reversal refinement hierarchy), giving a fractal leaping-fill contour — the aperiodic arpeggiation counterpart of 049 IFS attractors, but with the balance bound instead of a contraction guarantee. Register = a digit-shifted copy of the same axis (shift by $b^k$) — transposition that preserves balance exactly.

**RHYTHM**: $\varphi_2(n) \times T$ places onset $n$; the largest-gap property (verified) means each new onset fills the biggest current silence — a self-organizing, non-periodic groove whose *order of filling* is the dyadic hierarchy (half, quarters, eighths, …). Density = number of indices in the window; swing/rubato = post-hoc humanization (zero-drift safe), because the sequence itself is the even skeleton. Euclidean (012) is the periodic maximal-evenness rhythm of one bar; LDSC is the aperiodic maximal-evenness rhythm of the *whole piece*.

**HARMONY**: the region partition of $[0,1)$ is the harmonic grammar: widths $w_j$ = tonal gravity (HOME width = tonic saturation), region order along $\varphi_3$ = the non-periodic progression (no isorhythmic cycle — the aperiodic foil to 032 ITCM), and the *exact* visit-frequency identity replaces statistical weights (084 ZMRC) with a guarantee. Chords = the pc-set of the events in a window: because $\varphi_3$ equidistributes, every window of length $M$ has near-exact pc balance — "the chord IS the window". Voice-leading = the nearest-scale-degree map inside each region.

**STRUCTURE**: macro-form = the schedule of (scrambling key, region partition, index-window density) per section. Section = a permuted copy of the same balanced sequence → variation with guaranteed evenness, no seams (each window is as balanced as the whole). Hammersley's exact endpoint $n/N$ = a guaranteed arrival on the section seam — cadence as a mathematical identity. Repetition (rondo/recap) = reuse key + window; climax = widening TENSE + increasing density (more indices per unit time — the onset crowding that the discrepancy bound still spreads evenly).

**TEXTURE**: 3D Halton (2,3,5) adds velocity/articulation as a third balanced axis — dynamics that never clump. Polyphony = per-voice base pairs (coprime → independent balanced streams, joint-balance verified) with shared $\varphi_2$ time axis → rhythmic coherence with harmonic/registral independence. Pointillism = sparse windows (few indices, wide spread); mass = dense windows; the *transition* between them is a density schedule, not a rewrite.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows.** Voice $v$ owns a base pair: time base $b_t(v)$ (shared $\varphi_{b_t}$ axis keeps rhythmic coherence; staggered by a digital shift so onsets interlock — the hocket), pitch base $b_p(v)$ from the coprime set {3, 5, 7, 11, …} — pairwise-coprime bases give provably independent equidistributed streams (joint-balance verified). Vertical harmony per column: the column's pc-set is the set of $\varphi_{b_p(v)}(n)$ draws over the column's index window; because every base equidistributes, every column of length $M$ is near-exactly pc-balanced — the chord is the window, automatically.

**Sections = columns.** Column $s$ = index window $[N_s, N_{s+1})$ + scrambling key (Owen digit permutation / XOR shift — variation with preserved discrepancy, verified) + region partition (harmonic grammar) + density ($N_{s+1}-N_s$ = event count target). Columns are *intervals of one infinite balanced sequence*: no seam discontinuity in balance, no transition rule to write — the balance guarantee holds per window by construction. Hammersley endpoint for the final column = exact cadence arrival.

**Cells = MusicUnit.** A cell = the events of its index window, decoded and quantized:

1. Window indices $n = N_{cell}, \dots, N_{cell+1}-1$; onset ticks $t_n = \lfloor \varphi_{b_t}(n) \cdot \text{len}_\text{cell} \rfloor$ (or raw continuous ticks); pitch class $p_n = \lfloor \varphi_{b_p}(n) \cdot k \rfloor$ mapped through the section's scale; velocity $\propto \varphi_5(n)$; harmonic function = region of $\varphi_3(n)$ (or $\varphi_{b_p}$ if one axis only).
2. Scramble the window per the section key before decoding (order variation, balance preserved).
3. Emit `MusicEvent(pitch, volume, start_tick, end_tick)` per onset; durations = distance to next onset in the window (clipped).
4. Pad with `_unit_from_events(events, section_len)` so the terminal landmark lands exactly on the section seam — required, because a sparse cell may have no onset in the last slot and the zero-drift gate will otherwise fail.
5. Record the cell's empirical discrepancy $D^*$ (computed on its decoded onsets) as a per-cell "balance score" — the quality meter of the method, with units.

Candidate code path: `generators/lds_composition.py` (class `LDSComposer`: `radical_inverse()`, `halton()`, `hammersley()`, `sobol()`, `scramble()`, `region_partition()`, `realize_cell()`), consumed by `workflows/unitmatrix_composer.py`; the abstract pre-pass (per-section region partitions exported as weighted tension curves) feeds `rules/subset_network.py`.

### Pitfalls

1. **Determinism is not variety.** The raw sequence is the same every piece — without scrambling, every composition has an identical rhythm skeleton. The Owen/digit-permutation/XOR-shift scrambling is *mandatory* for section variation, and the seed (index schedule + keys) is the only source of piece identity. Contrast with 002 Markov, where variety is structural.
2. **Base choice is a musical decision, not a detail.** $b=2$ = dyadic bisection fill (the "largest-gap" rhythm — verified), but *only* for $b=2$; larger bases fill in $b$-ary blocks with visibly ordered runs (the order of region visits under $g_3$ has base-3 structure — powers of 3 cluster). Choose the base for the *order* you want, then accept its discrepancy; or scramble to hide the order.
3. **Grid quantization can destroy the guarantee.** Rounding $\varphi \cdot T$ to a slot grid collapses distinct points into one slot (two onsets sharing a tick = a micro-clump the discrepancy bound never promised to prevent *after* rounding). Quantize only when the grid is fine enough to be injective ($T \ge N$ slots), or keep onsets continuous and let the humanizer grid them.
4. **The discrepancy bound is about prefix windows, not every sub-window.** $D_N^*$ bounds intervals $[0,x)$ anchored at 0; an arbitrary window $[a,b)$ can deviate more (its bound follows from the prefix bound with a factor, but it is not the same constant). When a section's window must be *individually* balanced, verify its empirical discrepancy (the script does exactly this) or use the Hammersley endpoint construction.
5. **Halton's high-dimension degradation.** The Halton bound is $C'(\log N)^s/N$: for $s \ge 5$ the "low discrepancy" advantage shrinks and known linear-correlation artifacts appear between high bases. Music's $s \le 3$ (time, pitch, velocity) is safe; for more axes use Sobol' nets (direction numbers) or drop the extra axes.
6. **Multi-voice bases must stay coprime.** Reusing a base for two voices makes their streams *identical* under the same index — a perfect unison by construction. Pairwise-coprime bases give the verified joint-balance; a shared time base (same $b_t$) is fine and even desirable for rhythmic coherence, but then stagger voices by a digital shift, never by re-indexing (re-indexing changes the *phase* of the whole sequence and breaks per-voice window balance).
7. **"Quasi-random" is not "random".** Values are correlated by design (each is a function of $n$); there is no independence. Do NOT drop LDSC values into a method that assumes i.i.d. draws (Markov counting 002/087, DPP kernels 124, MRF Gibbs 064) — the downstream statistics will be subtly biased. LDSC is for *event placement* (onsets, pcs, regions), not for *sampling distributions*.
8. **Sparse cells and the zero-drift gate.** A window may contain no onset in its final slots; without `_unit_from_events` padding the terminal landmark drifts and `validate()` fails. Pad every cell to the section length before `to_midi()`.
9. **The largest-gap property is dyadic.** Verified for $g_2$ (each point bisects the largest empty gap); the unrestricted greedy largest-gap sequence (van der Corput's original splitting) agrees with $g_2$ at dyadic scales but differs in fine structure — don't claim the property for non-dyadic bases.
10. **Don't confuse the axes.** $\varphi_2$ for rhythm, $\varphi_3$ for pitch, $\varphi_5$ for velocity is a *convention*; the coprimality is what matters. If two axes must correlate (e.g. pitch and harmony), derive both from the *same* base by different region partitions rather than from two bases — two bases are independent by construction.
<!-- APPENDED_SECTION_END -->
