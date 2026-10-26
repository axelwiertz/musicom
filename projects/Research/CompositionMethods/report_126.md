# Method 126 — Knight's Tour Composition (KTC) — Registration Report

**Date:** 2026-10-26 · **Agent:** music research cron (autonomous) · **DB:** `methods_db.md`

## Identity

- **Method ID:** 126 (resolved dynamically: max existing algorithmic ID = 125; verified via summary-table scan of `| **NNN** |` rows AND standalone `method_*.md` / `report_*.md` file scan — 78 `method_*.md`, latest `method_125_LDSC.md` / `report_125.md`. No 126+ exists anywhere.)
- **Method name:** Knight's Tour Composition (KTC)
- **Paradigm:** Rules-Based
- **LAYER:** concrete (see classification below)
- **One-line description:** Composes from a Hamiltonian path/cycle on the knight graph — a knight's tour visits every (pitch row, time-slot column) cell of an m×n board exactly once (the 2D aggregate), with the knight signature |Δr|·|Δc| = 2 anti-correlating melodic leaps with durations.
- **Acronym check:** KTC unique in DB (no collision with 095 CTC, 119 TDC, 122 HCSC, etc.).

## Summary-table row (as inserted, line 136)

```
| **126** | concrete | Knight's Tour Composition (KTC) | **Rules-Based** | Pitch, Rhythm, Structure, Texture | Weak (Scale-mapped) | Grid-Locked | Macro / Hamiltonian Path | $\mathcal{O}(N)$ heuristic (Warnsdorff), worst-case $\mathcal{O}(8^N)$ | Composes from a Hamiltonian path/cycle on the knight graph: a knight's tour visits every (pitch row, time-slot column) cell of an m×n board exactly once — the 2D aggregate (each degree exactly n times; no literal pitch-slot repeat; verified 8×8/12×8 row counts all equal n). The knight signature |Δr|·|Δc| = 2 anti-correlates melodic leaps with durations (short notes leap, long notes step); closed tours = seamless re-entrant loops; the board transpose of a tour is a valid tour = the dual voice (invertible counterpoint). Warnsdorff's rule + Pohl tie-break solve in ~O(N) (verified 1–2 ms); DFS fallback; Schwenk's theorem = closed-tour board conditions. Rules-Based grid/aggregate foil to 112 Costas (sparse) / 122 Hilbert (smooth) / 065 twelve-tone (1D aggregate); 2D Hamiltonian counterpart to 089 change-ringing permutations. |
```

## Line counts

- **Before:** 28,383 lines (`wc -l`, pre-append)
- **After:** 28,467 lines (+84 = +83 section lines + 1 summary row)
- Section header at line 28,385; summary row at line 136.

## Files

- **Standalone full write-up:** `/opt/data/projects/Research/CompositionMethods/method_126_KTC.md` (11,601 bytes: extended math, verified-invariant table, Python implementation sketch, references)
- **Report (this file):** `/opt/data/projects/Research/CompositionMethods/report_126.md`
- **Verification script:** `/opt/data/projects/Research/outputs/ktc_validate/verify_ktc.py` (runs under the musicom env python; pure stdlib)
- **Candidate code path:** `generators/knight_tour_composition.py` (class `KnightTourComposer`: `knight_neighbours()`, `warnsdorff_rank()`, `pohl_tiebreak()`, `solve_tour()` [Warnsdorff + DFS fallback], `dual_tour()`, `reflect_tour()`, `decode_band()`, `realize_cell()`), consumed by `workflows/unitmatrix_composer.py`. Optional abstract pre-pass (tour as pitch-slot pairing plan) feeds `rules/subset_network.py`.

## Classification details

| attribute | value | rationale |
|---|---|---|
| Paradigm | **Rules-Based** | deterministic combinatorial construction (Hamiltonian constraint + degree heuristic); no sampling, no nature dynamics, no learned parameters; optional seeded tie-break = piece identity |
| LAYER | **concrete** | tour decodes directly to MusicEvents filling UnitMatrix cells (onset = accumulated slots, pitch = row via scale map, duration = 1-or-2-slot gap); feeds generators/ |
| Primary Elements | Pitch, Rhythm, Structure, Texture | harmony enters via scale map + voice stacks (aggregate reading optional) |
| Tonal Gravity | Weak (Scale-mapped) | exact pc balance is fixed by construction (each row exactly n times) — tonality enters ONLY through row→degree map and register folding |
| Metric Binding | Grid-Locked | slots are grid cells; Δc ∈ {1,2} slots is the rhythm grammar |
| Memory Depth | Macro / Hamiltonian Path | the tour is a global object (whole-board constraint), like WFCGS/SCCC |
| Time Complexity | O(N) heuristic (Warnsdorff), worst-case O(8^N) backtracking | verified: 8×8 in 1.7 ms, 12×8 in 1.0 ms |
| Novelty | high | arXiv: 0 hits for knight's tour + music/composition; Crossref: only Wolfram Demonstrations visualizations; documented pre-digital uses = Sanskrit metrical text-setting (Rudrata 9th c., Desika 14th c.), Perec/Oulipo novel, image encryption — no algorithmic composition method |
| In-catalogue lineage | 112 CADDC (sparse complement), 122 HCSC (smooth complement), 065 TTSMC (1D aggregate → KTC 2D aggregate), 056 SCCC (search machinery), 089 CRCM (1D permutation relative), 071 HAM-C (neural solver) | |

## Verified invariants (measured, 2026-10-26)

| property | measured |
|---|---|
| 8×8 Warnsdorff+Pohl from (0,0) | 64/64 cells, 1.7 ms, signature ✓ |
| 8×8 seeded-random tie-break | 64/64 cells, 0.6 ms, signature ✓ |
| knight signature \|Δr\|·\|Δc\| = 2 | 64/64 moves (both tie-breaks) |
| 2D aggregate | 64 distinct cells; row counts all 8; col counts all 8 |
| row balance 12×8 | 96 cells, every row exactly 8 visits |
| closed tour 8×8 | found from (7,4) in 0.01 s (DFS), closed=True |
| dual tour (board transpose) | valid 8×8 tour, signature ✓ |
| board sweep 5×5/6×6/8×8/10×10/12×8 | all complete, signature ✓, open (corner starts) |

## Complete method section text appended to methods_db.md

```markdown
# Knight's Tour Composition (KTC) (Method 126)

### Source

- **Rudrata (9th c. AD).** *Kavyalankara* 5.15 — the earliest documented knight's-tour artifact: the *turagapadabandha* ("arrangement in the steps of a horse"), a *citra-alaṅkāra* poetic figure on a half-board whose syllables can be read left-to-right *or* by following a knight's tour. (Cited via Wikipedia "Knight's tour", fetched 2026-10-26; Sanskrit edition: Chaudhary Satyadev, *Kavyalankara of Rudrata*, Parimal Sanskrit Series No. 30.)
- **Vedanta Desika (14th c.).** *Paduka Sahasram* ch. 30 (*Chitra Paddhati*) — two consecutive 32-letter verses in Anushtubh meter where the second verse is derived from the first by a knight's tour on a 4×8 board. The earliest documented knight-tour *transformation of a metrical (chantable) text* — the direct human-craft ancestor of this method.
- **Nilakantha (~1600/1700).** *Bhagavantabaskara* — fully symmetric re-entrant tours, predating Euler by at least 60 years.
- **Euler, L. (1759).** "Solution d'une question curieuse qui ne paroît soumise à aucune analyse" — the first Western mathematical treatment of open and closed tours on the 8×8 board.
- **Warnsdorff, H. C. von (1823).** "Des Rösselsprungs einfachste und allgemeinste Lösung" — the first procedure: always move to the square with the fewest onward moves (in graph terms: the adjacent vertex of least degree). Tie-breaks: **Pohl (1967)** and Squirrel & Cull (1996).
- **Pohl, I. (1967).** "A method for finding Hamilton paths and Knight's tours." *Communications of the ACM* 10(7), 446–449. doi:10.1145/363427.363463 — the second-choice tie-break that makes Warnsdorff succeed on the 8×8 board.
- **Schwenk, A. J. (1991).** "Which Rectangular Chessboards Have a Knight's Tour?" *Mathematics Magazine* 64(5), 325–332. doi:10.1080/0025570X.1991.11977627 — closed-tour existence theorem: an m×n board (m ≤ n) has a closed tour unless (both m,n odd), (m ∈ {1,2,4}), or (m = 3 and n ∈ {4,6,8}).
- **Cull, P. & De Curtins, J. (1978).** "Knight's Tour Revisited." *Fibonacci Quarterly* 16(3), 276–285. — divide-and-conquer constructions.
- **Conrad, A., Hindrichs, T., Morsy, H. & Wegener, I. (1994).** "Solution of the Knight's Hamiltonian Path Problem on Chessboards." *Discrete Applied Mathematics* 50(2), 125–134. doi:10.1016/0166-218X(92)00170-Q — the knight's tour on rectangular boards is solvable in **linear time**, unlike the general Hamiltonian-path problem (NP-hard).
- **Parberry, I. (1997).** "An Efficient Algorithm for the Knight's Tour Problem." *Discrete Applied Mathematics* 73(3), 251–260. doi:10.1016/S0166-218X(96)00010-8 — linear-time construction for large boards.
- **Takefuji, Y. & Lee, K. C. (1992).** "Neural network computing for knight's tour problems." *Neurocomputing* 4(5), 249–254 — Hopfield-network tour solving (the 071 HAM-C connection).
- **Perec, G. (1978).** *La Vie mode d'emploi (Life: A User's Manual)* — Oulipo: a 10×10 knight's tour sets the chapter order (literary application of the same combinatorial object).
- **OEIS A165134 / A001230 / A390833** — tour counts: 8×8 has 19,591,828,170,979,904 directed tours (open + closed), 13,267,364,410,532 undirected closed tours; A390833 counts undirected Hamiltonian paths on the k×n knight graph.
- **Novelty check (2026-10-26):** arXiv API returned **0** hits for `"knight's tour" AND music` and `"knight tour" AND composition`; Crossref returned only Wolfram Demonstrations visualizations ("The Knight's Tour", "Beautiful Designs Made from the Knight's Tour", 2007) and chess-psychology items — **no dedicated algorithmic music-composition method** in the literature. Documented uses are poetic text-setting (Rudrata/Desika), novel-chapter ordering (Perec), and image encryption (Philip 2013, *IEEE Potentials* 32(6), 10–16). KTC is proposed here as a composition method on documented Hamiltonian-graph foundations — the same profile as in-catalogue entries 090/091/112.
- In-catalogue lineage: **112 CADDC** (n dots, all displacement vectors distinct — *sparse*) is the sparsity complement of KTC's *full-density* coverage; **122 HCSC** (space-filling path, single-coordinate ±1 moves — smooth glissando) is the smooth complement of KTC's coupled (±1,±2) leaping; **065 TTSMC** (1D aggregate equality per row) is the 1D case of KTC's 2D aggregate (every pitch-slot pair exactly once); **056 SCCC** (backtracking constraint solver) supplies the search machinery; **089 CRCM** (adjacent-swap permutation streams) is the 1D relative; **071 HAM-C**'s Hopfield recall is KTC's neural solver.

### Layer

**concrete** — the tour is a complete assignment of (row = pitch, column = grid slot) to every cell of an m×n board; decoding to `MusicEvent`s is direct (onset = accumulated slot count, pitch = row via the scale map, duration = 1-or-2-slot gap) and fills UnitMatrix cells immediately. Feeds `generators/`.

An **abstract** reading exists and is cheap: the tour is a *pitch-slot pairing plan* — a 2D aggregate design (each pitch exactly n times, each slot exactly m times) that could be exported to `rules/subset_network.py` as a pc-balance-optimal assignment scheme for any concrete method downstream. The layer tag stays concrete because the primary feed is event generation (same reasoning as 125 LDSC).

### Paradigm

**Rules-Based** — deterministic combinatorial construction: board size, start square, and the tie-break policy (Pohl / seeded random) fully determine the tour; generation is heuristic search under a hard Hamiltonian constraint, not sampling. No nature dynamics, no learned parameters; the only "randomness" is an optional seeded tie-break used as the piece's variation identity. Same constraint-satisfaction family as 056 SCCC / 033 WFCGS.

### Description

**Knight's Tour Composition (KTC)** builds the piece from a **Hamiltonian path on the knight graph**: a sequence of knight moves that visits every square of an m×n board exactly once. Board rows = m pitch classes / scale degrees; board columns = n grid slots. Reading the tour in order:

- each step *k* emits one note: pitch = row *rₖ*, onset = accumulated slot count, duration/rest = |cₖ₊₁ − cₖ| slots (always 1 or 2);
- the **knight signature**: every move satisfies |Δr|·|Δc| = 2 — a pitch step of 1 degree pairs with a time jump of 2 slots, a pitch step of 2 degrees pairs with a time jump of 1 slot. **Leaps are anti-correlated with durations by construction**: short notes leap, long notes step;
- the **2D aggregate**: all m·n (pitch, slot) cells are visited exactly once — no literal repetition of any pitch-slot pair in the whole piece, and every pitch row appears exactly n times (verified: 8×8 tour → each row 8 visits, each column 8 visits). Exact pc balance by construction, stronger than LDSC's discrepancy bound (125).

**Closed vs open.** A closed (re-entrant) tour ends one knight move from its start: the piece loops, and the loop seam is itself a knight interval — a seamless homogeneous repeat ideal for riffs and hockets. An open tour is through-composed. Schwenk's theorem (1991) states exactly which boards admit closed tours (not both dimensions odd; smaller side not 1/2/4; not 3×{4,6,8}); open tours exist on every board except m ∈ {1,2}, 3×{3,5,6}, 4×4. Verified here: an 8×8 closed tour exists (found from (7,4)); corner-start Warnsdorff tours on 5×5/6×6/8×8/10×10/12×8 are complete and open.

**Construction.** Warnsdorff's rule (1823): move to the unvisited neighbour with the fewest onward moves — the least-degree heuristic, linear in practice on knight graphs (verified: 8×8 in ~1 ms, 12×8 in ~1 ms). Ties are broken by Pohl's second-choice rule (1967) or a seeded random choice; when the heuristic stalls, fall back to DFS backtracking (the standard CS-exercise solver) or to the linear-time divide-and-conquer constructions (Cull–De Curtins 1978; Conrad et al. 1994; Parberry 1997 for boards ≳ 30×30).

**Companion voices.** Because the knight-move set is symmetric under board transposition, the transpose of a tour is a tour of the transposed board (verified): the **dual tour** swaps the axes' roles — its rhythm sequence is the primal's pitch-step sequence and vice versa, an exact invertible counterpoint. Reflections, rotations, and octave-shifted copies give further related tours. Voices = independent tours (different boards, starts, tie-breaks) = independent-but-similar lines by construction.

**Variation identity.** The piece is fully determined by (m, n, start square, tie-break policy, row→degree map, per-section column bands). Different seeds = different tours — 19.6 quadrillion directed tours on 8×8 alone (OEIS A165134) — so the tour count is the method's "vocabulary size", and there is no training and no corpus.

### Musical Elements Framework

- **PITCH**: rows = scale degrees (m ≤ 12: chromatic m=12, diatonic m=7–8). Each row is visited exactly n times → exact equal-frequency per degree (the 2D aggregate; verified row counts all equal n). The move set forces melodic intervals of 1–2 degrees in a perpetually moving contour with no immediate pitch repeats (Δr ≠ 0 always) and no literal cell repeat — an anti-repetition engine in the family of 065/090/112. Register = octave-block folding of the row index (see Pitfalls 8).
- **RHYTHM**: Δc ∈ {1,2} slots → durations/rests are binary (short/long); the anti-correlation |Δr|·|Δc| = 2 means short notes leap and long notes step — a syncopated, hocket-like rhythmic profile with no literal (pitch, slot) repeat. Density is fixed by m·n (one note per cell; rests = the 2-slot moves). Closed tours give rhythmic periodicity exactly at the loop boundary.
- **HARMONY**: two readings. (i) *Melodic*: harmony = the scale implied by the row→degree map; chords = the vertical stack of voices at a step. (ii) *Aggregate*: grouping notes by column, every column contains all m rows exactly once → the complete m-note aggregate per slot-class — the 2D generalization of 065's row aggregates, spread melodically by the tour (use the column-as-chord reading for mass/aggregate harmony, cf. 020). Companion-voice stacks give controlled verticals: transposed copies = parallel octaves/fifths; the dual tour = complementary invertible motion.
- **STRUCTURE**: macro-form = board geometry (m, n) + column-band sections; closed tour = re-entrant loop (rondo/riff form); start square + tie-break = variation identity; the board's 8 symmetries (transpose, reflect, rotate) = related-form transformations; a section seam is crossed by a knight move (Δc = ±1 or ±2) → the melodic/rhythmic grammar is seamless across seams. Piece length = m·n notes.
- **TEXTURE**: polyphony = stacked tours (dual, transposed, independent); the m visits per column can be realized as a fast rolled arpeggio inside a slot (hocket interlock, cf. 008/111); pointillism = large boards with wide registers; mass = the column-aggregate reading deliberately voiced. Voice independence is by construction (different tours), vertical coherence is by shared board dimensions + shared scale map.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows.** Voice *v* = one tour. Canonical stack: Voice 0 = the primal tour (m×n board, scale-degree rows); Voice 1 = the dual tour (transposed board — invertible counterpoint: rhythm ↔ pitch-step roles swapped, verified valid); Voice 2 = an octave-down copy of the primal (parallel register support); Voices 3+ = independent tours (different boards/starts/tie-break seeds). Vertical intervals at each step are controlled by the chosen tour family (unison/octave for copies, complementary for duals).

**Sections = columns.** Column *s* = the band of board columns [c_s, c_{s+1}) of each voice's tour. A section boundary is a knight move (Δc = ±1 or ±2) → no seam discontinuity in the melodic grammar. Section identity = band width (density), the row→degree/register map per band, and (for closed tours) whether the band aligns with the loop; the final band of a closed tour returns to the first — a built-in recap.

**Cells = MusicUnit.** Cell (v, s) = the segment of voice v's tour inside section s's column band:

1. Solve the tour once per voice (Warnsdorff + Pohl tie-break; DFS fallback; deterministic per seed = start square + tie-break stream).
2. For each step k in the band: onset = accumulated Δc slots; pitch = row rₖ → scale degree via the section's map; velocity = a decoration (row parity, or a per-section curve); duration = Δc slots (the long/short alternation), clipped.
3. Optionally group same-column notes (the m visits per column) as a rolled chord if the aggregate reading is chosen; default = successive melodic events.
4. Pad with `_unit_from_events(events, section_len)` so the terminal landmark lands exactly on the seam — a band may end mid-gap and the zero-drift gate will otherwise fail (same trap as 125 Pitfall 8).
5. Export through the standard composer (`validate()` → `to_midi()`); humanization is safe downstream (slots are already quantized; jitter is applied in ms).

Candidate code path: `generators/knight_tour_composition.py` (class `KnightTourComposer`: `knight_neighbours()`, `warnsdorff_rank()`, `pohl_tiebreak()`, `solve_tour()` [Warnsdorff + DFS fallback], `dual_tour()`, `reflect_tour()`, `decode_band()`, `realize_cell()`), consumed by `workflows/unitmatrix_composer.py`.

### Pitfalls

1. **Warnsdorff can stall.** The naive rule fails on some boards/starts (classic 8×8 examples). Use Pohl's tie-break or a backtracking fallback, and *always verify* the returned path is complete (m·n visits) before decoding — a partial path silently drops the aggregate guarantee.
2. **Board existence (Schwenk).** Closed tours do not exist when both dimensions are odd, when the smaller side is 1/2/4, or on 3×{4,6,8}. Pick Schwenk-legal boards for closed tours, else use open tours (absent only for m∈{1,2}, 3×{3,5,6}, 4×4). Claiming "closed" on an impossible board is a bug.
3. **Grid-locked by design.** Δc ∈ {1,2} slots *is* the rhythm grammar — this is not a continuous-time method (that is 048/053/107's job), and the 2-slot gaps are rests, not quantization error: do not "fix" them away.
4. **Exact pc balance is not adjustable.** Every row is visited exactly n times: the tour cannot weight the tonic or saturate HOME (that dial belongs to 084/121). Tonal gravity enters only through the row→degree map and register folding.
5. **The column-aggregate reading can cluster.** Grouping notes by column sounds all m rows at once (full-scale cluster). Use it deliberately (mass, aggregate harmony) or spread it (melodic reading / rolled chords) — the default should be the melodic reading.
6. **The signature is the identity.** Equalizing all durations or forcing Δc = 1 destroys the anti-correlation |Δr|·|Δc| = 2 and KTC degenerates into a generic grid walk. Keep the 1/2-slot alternation; that alternation IS the method.
7. **No immediate pitch repeats.** Δr ≠ 0 on every move: no repeated notes, no sustained degrees (unless register folding maps different rows to the same octave pitch). For drone/repetition textures use a separate ostinato voice (015) or another method — KTC is an anti-repetition engine (like 065/090/112).
8. **Octave folding.** If rows = scale degrees and the register wraps at the octave, two consecutive tour steps can map to a large MIDI jump despite |Δr| ∈ {1,2} — decide the row→MIDI map (folded vs continuous ladder) before decoding and verify the contour stays in the intended register (cf. 007 register planning).
9. **Closed-tour looping vs matrix seams.** A closed tour's loop length is m·n steps; the matrix end may not align with the loop end. Plan the column bands so the recap lands on the matrix boundary, or the built-in-recap promise is broken.
10. **Zero-drift padding.** Bands end mid-gap (a 2-slot move may straddle the seam); without `_unit_from_events` padding the terminal landmark drifts and `validate()` fails — pad every cell to the section length.
11. **Cost discipline.** Warnsdorff is ~O(m·n·8) per voice (verified: 96 cells in ~1 ms); the DFS fallback is worst-case exponential — cap its node budget and reseed (new tie-break) instead of grinding, and use Parberry's linear construction for boards ≳ 30×30.
```

## Quirks / pitfalls hit during the run

1. **Path protection:** `/tmp` writes are denied by the Hermes environment ("protected system/credential file") — verification script went to the sanctioned `$MUSICOM_ROOT/projects/Research/outputs/ktc_validate/` instead.
2. **Security scanner:** plain-HTTP URLs and `curl | python3` pipes were blocked ("tirith" HIGH). Fixed by using HTTPS and download-then-parse (file, then separate python parse step).
3. **Self-found bug in the verification script:** `closed_check` originally returned `abs(r0-r1), abs(c0-c1) in [(1,2),(2,1)]` — Python parses that as a *tuple* `(dr, in_result)`, always truthy → a false "closed tour found" print. Fixed with parentheses `(abs(r0-r1), abs(c0-c1)) in [...]` and re-ran; final numbers are correct (8×8 closed tour genuinely found from (7,4)).
4. **Table-row pitfalls (as warned):** verified post-patch that the inserted row has a single `|` prefix (grep: 0 rows with `^|| **126**`, 1 with `^| **126**`) and that LaTeX backslashes stayed single (`$\mathcal{O}(N)$` matches the neighbouring rows' format exactly).
5. **DB section placement:** methods_db.md body is chronological (method sections + SP sections interleaved); the new section was appended at EOF (line 28,385), consistent with 125 LDSC (line 28,135) and SP-124 (line 28,225) being near the tail.
6. **Line-count reconciliation:** 28,383 → 28,467 (+84 = 83-line section + 1-line summary row), confirmed by `wc -l` and both greps.

## Next free ID

**127** (max now 126).
