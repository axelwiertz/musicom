# Report 127 — Sprague-Grundy Nimber Composition (SGNC)

**Date:** 2026-10-27 · **Method ID:** 127 · **Paradigm:** Rules-Based · **LAYER:** abstract

**One-line description:** Composes from impartial combinatorial games via the Sprague–Grundy theory — Grundy nimbers (mex recursion) are quantized tension levels, P-positions (g=0) are provable cadences, the disjunctive sum of voices makes chord tension the XOR of voice nimbers, and Bouton's winning-move rule is a deterministic voice-leading resolution algorithm; subtraction sets are the melodic interval vocabulary and ultimately periodic Grundy sequences prove their own rondo/intro/cadence schedule.

---

## Summary table row (exact, as inserted in methods_db.md line 137)

```
| **127** | abstract | Sprague-Grundy Nimber Composition (SGNC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (P-position-guided, cadence-exact) | Grid-Locked / Continuous | Meso / Nimber Trajectory | $\mathcal{O}(N \cdot \lvert S \rvert)$ subtraction curves, $\mathcal{O}(N \cdot n^2)$ split games, periodicity-exploitable | Composes from impartial combinatorial games (Sprague 1936; Grundy 1939): every position gets a Grundy nimber g = mex{options}; g=0 = P-position = provable cadence/HOME, g>0 = quantized tension rank. Subtraction set S = melodic interval vocabulary; the nimber sequence over the pitch ladder = the tension curve, ultimately periodic → harmonic-rhythm cycle (verified: S={1,2,3} period 4; S={1,3,4} period 7; Dawson's Kayles preperiod 53, period 34). Polyphony = disjunctive sum of heaps: chord tension = XOR of voice nimbers, XOR=0 = perfect cadence; Bouton's winning move = deterministic voice-leading resolution. P-positions = cadence seams; period = rondo; preperiod = intro; split games (Kayles) fork texture. Abstract layer: nimber curves + cadence schedule + pitch vocabulary → rules/subset_network.py. Rules-Based game-tree foil to 123 GTBRC (economic best-response); combinatorial sibling of 069/076/125; tension-quantized counterpart to 113 PCFSC / 095 CTC. |
```

**Line counts (methods_db.md):** before = 28,603 · after = 28,675 · **delta = +72** (71-line appended section + 1 summary-table row). Section header at line 28,605; summary row at line 137.

## Files

- Standalone write-up: `/opt/data/projects/Research/CompositionMethods/method_127_SGNC.md`
- Report (this file): `/opt/data/projects/Research/CompositionMethods/report_127.md`
- Verification script: `/opt/data/projects/Research/outputs/cgtc_validate/verify_grundy.py` and `/opt/data/projects/Research/outputs/cgtc_validate/measure_period.py`
- Candidate code path: `rules/grundy_composition.py` (class `GrundyComposer`: `mex()`, `subtraction_curve(S, N)`, `find_period(seq)`, `dawsons_kayles(N)`, `nim_sum(heaps)`, `bouton_move(heaps)`, `p_positions(seq)`, `realize_plan()`), consumed by `rules/subset_network.py` and downstream generators via `workflows/unitmatrix_composer.py`. Lives under **rules/** (not generators/) because SGNC is an abstract-layer method: it emits tension curves, cadence schedules, and pitch vocabularies, not events.

## Layer classification

**abstract** — SGNC designs the *plan* before any event exists: per-voice nimber trajectories (tension curves), the XOR chord-tension curve, the cadence schedule (P-positions), and the pitch vocabulary (subtraction set S + position→degree map). All outputs are transposition- and register-invariant (a Grundy value is a function of game structure, not pitch). Emits no notes — register/voicing/durations/velocities are the realize step's job (concrete methods 001/011/050/056-style). Feeds `rules/subset_network.py` like 095 CTC / 099 SSMC / 104 PSSC / 113 PCFSC. It is the 5th abstract method in the DB (after 095, 099, 104, 113) and the only abstract method whose tension curve is *provably* quantized (nimbers) with cadence positions *provably* identified (P-positions).

## Classification details

- **Paradigm:** Rules-Based — mex recursion is deterministic; Grundy function, P/N classification, and periodicity are theorems, not samples. Compositional freedom = choice of move (winning = resolution, losing = prolongation) and choice of game per section — design decisions, not stochastic draws. No training, no corpus, no nature dynamics. Same deterministic-combinatorial family as 069 Christoffel / 076 Thue–Morse / 125 LDSC, but over game trees.
- **Tonal Gravity:** Moderate (P-position-guided, cadence-exact) — cadences are provably placeable (g=0 positions), tonic = the P-position target; exact pitch identity delegated to the realize step.
- **Metric Binding:** Grid-Locked / Continuous — moves are discrete events; placeable on a grid (slot per move) or continuous (move-size spacing).
- **Memory Depth:** Meso / Nimber Trajectory — the nimber sequence spans the section (phrase-length context); g(n) itself is Markovian (depends only on reachable options).
- **Time Complexity:** O(N·|S|) subtraction curves (memoized mex), O(N·n²) split games (Kayles), exploitable via known periodicity; O(V) per chord XOR.
- **Primary Elements:** Pitch, Rhythm, Harmony, Structure, Texture (all five).

## Method section appended (verbatim)

Appended at end of methods_db.md (after SP-125, the file's previous tail), header `# Sprague-Grundy Nimber Composition (SGNC) (Method 127)`, containing `### Source`, `### Layer`, `### Paradigm`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Pitfalls` (10 pitfalls). Full text is in the file at lines 28,605–28,675; a copy of the section content is in `method_127_SGNC.md` (extended form).

## Verified claims

Script `verify_grundy.py` (musicom env, pure stdlib, memoized mex) — all checks passed:
1. Nim: mex recursion == heap size (n=0..23).
2. Sprague–Grundy xor law: direct mex of 2-heap sum == a^b (all a,b ∈ 0..4).
3. Subtraction S={1,2,3}: Grundy sequence period 4 (verified 32 terms).
4. Subtraction S={1,3,4}: period 7 (detected, matches literature).
5. Dawson's Kayles g(0..19) == Guy & Smith published head (exact).
6. Dawson's Kayles: measured (preperiod, period) = (53, 34) on n=0..399 — literature period 34 confirmed; common "preperiod 52" citation is off-by-one (measured 53).
7. Bouton: (grundy==0) ⟺ (xor==0) for all 3-heap positions 0..3 (direct mex vs nim-sum).
8. S={1,3,4} P-position cadence schedule < 60: 0,2,7,9,14,16,21,23,28,30,35,37,42,44,49,51,56,58 (period-7 zero pattern, matches expectation).

## Novelty check

- DB scan: no existing entry uses Sprague/Grundy/nimber/impartial/combinatorial game theory (123 GTBRC is *economic* game theory — non-cooperative, best response, potential games, Nash equilibria — explicitly distinguished in the section, Pitfall 5).
- Literature: arXiv API 0 hits for `"Sprague-Grundy" AND music`, `"Grundy" AND "music generation"`, `"nim" AND "algorithmic composition"`, `"combinatorial game theory" AND music`; DuckDuckGo returns only math-education material (Wikipedia, MathWorld, "The Mathemusicians" video). Closest documented art: Xenakis *Duel*/*Stratégie* (economic zero-sum game theory, already cited by 123 GTBRC) — a different formalism. SGNC is proposed here on documented combinatorial-game foundations.

## Quirks / pitfalls hit during the job

1. **LaTeX escaping:** the patch/write tooling double-escapes backslashes in diffs; verified the raw file has single `\mathcal{O}` (grep found 0 occurrences of `\\` in the inserted row) — no repair needed.
2. **`||` prefix pitfall:** verified 0 lines in the DB start with `||`; the row starts with a single `|`.
3. **First period check failed:** Dawson's Kayles at preperiod 52 (common citation) returned False; re-measured on n=0..399 → (53, 34). The section reports the *measured* values and flags the off-by-one citation.
4. **Naive mex recursion hangs:** the first verification attempt (no memoization) timed out at 180 s on Dawson's Kayles; memoized lru_cache version runs in <1 s — pitfall #1 in the section.
5. **Candidate initially considered:** GAN/MuseGAN (method 057 MT-GAC already exists — avoided), Quantum Walk (052), Neural ODE (058), Normalizing Flow (072), Eulerian trails (claimed by 077 de Bruijn adjacency), Beatty/Sturmian (claimed by 121 IETC degenerate case). SGNC had zero DB overlap.
6. **Table-row count in DB:** summary table ends at line 136 (row 126); inserted 127 at line 137, immediately before the first method section (`# Maximum Entropy Composition (MaxEnt-C) (Method 097)` at former line 138).
7. **DB is not numerically ordered** (097 appears first, then 021, 022…) — the section was *appended* at file end per the mandated workflow (temp file → `cat >>` → `rm`), not inserted in numeric position. This matches the house pattern (126 also sits at the tail).

## Next free ID

**128** (max existing algorithmic-method ID = 127; standalone files and summary rows both confirm).
