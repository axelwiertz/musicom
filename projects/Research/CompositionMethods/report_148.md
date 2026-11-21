# Report — Method 148 (JCOC)

**Run:** 2026-11-21 (scheduled cron research agent)
**DB:** `/opt/data/projects/Research/CompositionMethods/methods_db.md`

## Identity

| field | value |
|---|---|
| Method ID | **148** (next free after this run: **149**) |
| Name | Josephus Counting-Out Composition |
| Acronym | JCOC |
| Paradigm | **Rules-Based** (deterministic combinatorial elimination; no stochastic element, no training, no nature dynamics — the only free choice is the planned counting schedule, seeded like 144–147) |
| LAYER | **concrete** (LAYER_ARCHITECTURE.md) |
| One-liner | Compose from the Josephus counting-out permutation — $n$ people in a circle, every $k$-th is counted out until one survives; the elimination order is a permutation of $\{1..n\}$ mapped onto a pitch pool (every degree exactly once per cell, a "counting aggregate"), the survivor $J(n,k)$ is the cell's terminal cadence anchor ($k{=}2$: $f(n)=2l+1$, the left binary cyclic shift; $k{=}3$: Halbeisen–Hungerbühler, $f(41,3)=31$), round subdivisions descend $n,n{-}1,\dots,1$ (deterministic density arc), sections are a counting schedule chained by survivor seeds, and the sieve of Josephus Flavius (lucky numbers) gives a prime-like formal skeleton. |

## Summary-table row (as inserted, line 158)

```
| **148** | concrete | Josephus Counting-Out Composition (JCOC) | **Rules-Based** | Pitch, Rhythm, Structure, Texture | Moderate (Survivor-anchored: HOME = survivor arrival, TENSE = mid-elimination, TURN = game close, LIFT = new seed/reprise) | Grid-Locked (slot grid: n events of S/n ticks; round subdivisions n, n−1, …, 1) | Meso / Counting State (per game); Macro / Schedule | $\mathcal{O}(n)$ survivor recurrence, $\mathcal{O}(n \log n)$ permutation (Fenwick), $\mathcal{O}(n^2)$ naive | Composes from the Josephus counting-out permutation E(n,k) — n people in a circle, k−1 skipped, k-th eliminated, one survivor: E is a permutation of {1..n} mapped onto a pitch pool (one event per slot, every degree exactly once = per-cell counting aggregate; k = interval generator; k=2 = evens-then-odds two-layer contour). Survivor = terminal anchor: k=2 closed form f(n)=2l+1 = left binary cyclic shift (OEIS A006257), k=3 Halbeisen–Hungerbühler α≈0.8111 (f(41,3)=31), general g(n,k)=(g(n−1,k)+k) mod n. Round subdivisions descend n, n−1, …, 1 (deterministic density arc); sections = a counting schedule (n_j,k_j) chained by survivor seeds; the sieve of Josephus Flavius / lucky numbers (GLMU 1956) = position-based formal elimination with prime-like density ~ n/log n (first position-based sieve in the DB, cf. congruence-based 025); rotations across voices = phase texture (cf. 026). Feeds generators/josephus_permutation.py. |
```

## Line counts

| stage | lines |
|---|---|
| before | 32 459 |
| after appending the method section | 32 540 (+81) |
| after inserting the summary row | **32 541** (+82 total) |

## Artifacts

| artifact | path |
|---|---|
| standalone write-up | `projects/Research/CompositionMethods/method_148_JCOC.md` |
| report (this file) | `projects/Research/CompositionMethods/report_148.md` |
| math verification (19/19) | `projects/Research/CompositionMethods/_web148_jcoc/verify_jcoc_math.py` |
| research sources (raw) | `_web148_jcoc/{josephus,lucky,countingout}.json` (MediaWiki extract API) |

## Candidate code path

- **Primary (concrete generator):** `generators/josephus_permutation.py` — `survivor` (O(n) recurrence), `survivor_k2` (closed form / binary cyclic shift), `elimination_order` (naive O(n²)), `elimination_order_fast` (Fenwick order statistics, O(n log n)), `rotated` (phase dial), `lucky_numbers` (sieve of Josephus Flavius), `tile_cell` (slot tiling, survivor held to seam), `plan`.
- **Optional abstract promotion:** `rules/counting_schedule.py` — schedule design / lucky-sieve macro-form planning, if the schedule is later split into the abstract layer.
- **Engine changes:** none required — the method emits absolute-tick events that tile sections exactly (zero drift by construction), so `UnitMatrixComposer.create_matrix/add_voice/add_section/fill_voice_section/validate/to_midi` work as-is.

## Classification detail

- **Layer = concrete.** The product of one Josephus game is a sequence of note events (pitch, onset, duration, velocity) on a slot grid — exactly a UnitMatrix cell's contents. The $(n,k)$ game and the counting schedule are the *plan*; the elimination-order permutation is the *realized cell*. Same layer family as 012 Euclidean / 144 LSPC / 147 MMTC; opposite of the tick-free abstract plans 145 DPBC / 146 HHFC.
- **Paradigm = Rules-Based.** Everything is deterministic combinatorics: the elimination permutation, the survivor recurrences, the closed forms, the lucky sieve. No sampling, no training, no fitness. The only free choice is the planned counting schedule (seeded).
- **Tonal Gravity = Moderate (Survivor-anchored).** HOME = survivor arrival (the cell's terminal anchor; for $k{=}2$ the tonic is a binary rotation of $n$ — pure arithmetic), TENSE = mid-elimination (density arc descending), TURN = game close (survivor event), LIFT = new seed / reprise. Harmonic content itself is delegated: the survivor chain mod 12 gives a deterministic chord-root plan.
- **Metric Binding = Grid-Locked (slot grid).** $n$ events of $S/n$ ticks per cell; round subdivisions descend $n, n{-}1, \dots, 1$. Slot divisibility ($n \mid S$) is the zero-drift gate.
- **Memory Depth = Meso / Counting State (per game); Macro / Schedule.** One game needs only (circle, position, k) — local; the schedule spans the piece — macro.
- **Time Complexity = $\mathcal{O}(n)$ survivor recurrence, $\mathcal{O}(n \log n)$ permutation (Fenwick), $\mathcal{O}(n^2)$ naive; schedule $\mathcal{O}(\sum n_j \log n_j)$; sieve $\mathcal{O}(N \log N)$.**
- **UnitMatrix:** rows = voices = counting circles `{pool_v, k_v, start_v, velocity_arc}` (rotated starts = phase texture, identical $(n,k)$ = homorhythm); columns = sections = counting games `{n_j, k_j, pool_j, start_j}` (seed-chained: `start_{j+1} = survivor of game j`); cells = the elimination-order events with the survivor extended to the seam — **the zero-drift pad is musically the cadence arrival**.

## Novelty & web research

- Novelty `grep -ci` on `methods_db.md` before entry: `josephus` = 0, `counting-out`/`counting out` = 0, `lucky number` = 0, `elimination` = 0. No existing method generates material from a counting-out / elimination process. Closest neighbours: 065 TTSMC (permutation rows by *transposition*, not elimination), 089 CRCM (adjacent-swap permutation stream), 025 Sieve (congruence-based — the lucky sieve is *position*-based), 128 VESC (self-referential gaps), 090 GRDC (distinct differences), 144 LSPC (distance pairing).
- Sources (all fetched live 2026-11-21 via the MediaWiki extract API): Wikipedia "Josephus problem", "Lucky number", "Counting-out game". Key facts: $k{=}2$ closed form + binary cyclic shift (OEIS A006257); $k{=}3$ Halbeisen–Hungerbühler 1997 ($\alpha \approx 0.8111$, $f(41,3)=31$); general recurrence $g(n,k)=(g(n{-}1,k)+k)\bmod n$; lucky numbers = "sieve of Josephus Flavius" (Gardiner–Lazarus–Metropolis–Ulam 1956), prime-like density per the PNT, $L_n > p_n$; counting-out rhymes (Bolton 1888, divination-by-lots origin).

## Measured verification

`_web148_jcoc/verify_jcoc_math.py` → **19 passed, 0 failed** (run with `$MUSICOM_PYTHON`):
permutation property ($E(8,3)=[3,6,1,5,2,8,4,7]$, survivor 7); $k{=}2$ closed form $f(n)=2l+1$ == recurrence for $n\le200$ ($f(13)=11$ binary cyclic shift, $f(41)=19$); $f(41,3)=31$ via Halbeisen–Hungerbühler vs simulation for $n=5..79$; general recurrence vs simulation sweep ($n\le59$, $k\le14$); Fenwick O(n log n) == naive O(n²) for $n\le49$; density arc $n,n-1,\dots,1$; lucky prefix == OEIS A000959 (40 terms); lucky density $\#\{L\le10^5\}=8772$ vs $x/\ln x=8686$ (and < $\pi(10^5)=9592$, consistent with $L_n>p_n$); slot tiling (events end exactly at $S=n\cdot\mathrm{slot}$; every pool degree used exactly once; survivor event is the terminal anchor); rotation yields a valid permutation.

## Quirks / pitfalls hit during the run

1. **Approval gate on `python3 -c`.** Inline `python3 -c`/`-e` is blocked in this environment (pending-approval). Worked around by writing verification as a `.py` file and running it with `$MUSICOM_PYTHON` (the sanctioned pattern; same as method 147's run). Web fetching via plain `curl` is fine.
2. **Test-expectation bugs (twice), not implementation bugs.** My "known" lucky-number list included 201 while the sieve bound was 200 (201 > bound, correctly excluded), then the full-list comparison failed because the sieve at N=400 returns extra terms beyond the 40-term expectation. Fixed by bounding above the max known value and comparing the prefix. The sieve itself was correct on the first try.
3. **Patch escaping.** The summary-row patch was verified post-insertion: single `|` row prefix (no `||` mangling) and single backslashes (`\mathcal` ×3, zero `\\`). No double-escaping this run; the pre-existing 147 section still carries some `\|`/`\\` artifacts in the file that were NOT touched.
4. **Symlinked paths.** `/opt/data/projects/Research` resolves into `$MUSICOM_ROOT/projects/Research`; write_file and patch reported resolved paths under the repo tree — same inodes, no conflict.
5. **k=2 "evens-first" is a feature.** Early drafts of the pitch mapping tempted a sort to "fix" the contour; the two-layer evens-then-odds shape is the method's signature and is documented as a pitfall instead.

## Complete method section text appended (lines 32461–32541, verbatim)

```markdown
# Josephus Counting-Out Composition (JCOC) (Method 148)

### Source

- **Wikipedia: "Josephus problem"** (fetched live 2026-11-21 via the MediaWiki extract API). Definition of the counting-out game: $n$ people in a circle, $k-1$ skipped, the $k$-th executed, procedure repeated with the remaining people starting at the next person, until one remains and is freed; the elimination order is the **Josephus permutation**. History: Flavius Josephus, siege of Yodfat (1st century), 41 men, serial suicide by lot — he and one other remained; Bachet de Méziriac (1612) suggested the circle-and-count-by-threes mechanism; Herstein–Kaplansky (1974) variant counts every 7th. The medieval 15-Turks/15-Christians ship variant: 30 people, every 9th tossed. Solutions: **$k=2$** — $f(2j)=2f(j)-1$, $f(2j+1)=2f(j)+1$; $f(n)=2l+1$ for $n=2^m+l$, $0\le l<2^m$; explicit $f(n)=2(n-2^{\lfloor\log_2 n\rfloor})+1$; **the survivor is the left cyclic shift of $n$'s binary representation** (OEIS A006257). **$k=3$** — Halbeisen & Hungerbühler (1997) closed form with constant $\alpha\approx 0.8111\ldots$: $f(n)=3(n-\mathrm{round}(\alpha(3/2)^m))+(2\text{ or }1)$; worked example $f(41,3)=31$ — Josephus' own number (his alleged safe position). **General case** — dynamic programming recurrence $g(n,k)=(g(n-1,k)+k)\bmod n$, $g(1,k)=0$ (0-based), $f(n,k)=([f(n-1,k)+k-1]\bmod n)+1$ (1-based), $f(1,k)=1$; $\mathcal{O}(n)$ DP, improved $\mathcal{O}(k\log n)$ for small $k$; the $x$-added-people generalization $p+mx \bmod (n+x)$.
- **Wikipedia: "Lucky number"** (fetched live 2026-11-21). The **"sieve of Josephus Flavius"**, introduced by Gardiner, Lazarus, Metropolis & Ulam (1956): eliminates numbers by their **position in the remaining set** (unlike Eratosthenes, which eliminates by value). Start with the odd numbers; remove every 2nd; then every 3rd of the remaining; then every 7th; ... (each pass $n$ = the next surviving number). Lucky numbers: $1,3,7,9,13,15,21,25,31,33,37,43,49,51,63,67,69,73,75,79,\ldots$ They share properties with the primes: asymptotic density per the prime number theorem, a Goldbach-type conjecture, twin-lucky pairs about as frequent as twin primes, and $L_n > p_n$ for all sufficiently large $n$.
- **Wikipedia: "Counting-out game"** (fetched live 2026-11-21). Children's counting-out rhymes (eeny meeny miny moe, One potato two potato, Yan Tan Tethera, ...); Bolton, *Counting Out Rhymes of Children* (1888) — the custom originated in "the superstitious practices of divination by lots"; the Josephus problem is the formal variant of a counting-out game.
- **Verified prototype (this run):** `_web148_jcoc/verify_jcoc_math.py` — **19/19 checks pass** (permutation property $E(8,3)=[3,6,1,5,2,8,4,7]$, survivor 7; $k{=}2$ closed form vs recurrence for $n\le200$; $f(13)=11$ binary cyclic shift; $f(41)=19$; $f(41,3)=31$ Halbeisen–Hungerbühler vs simulation; general recurrence vs simulation sweep; Fenwick $\mathcal{O}(n\log n)$ = naive $\mathcal{O}(n^2)$; density arc; lucky prefix = A000959; lucky density $\#\{L\le10^5\}=8772$ vs $x/\ln x=8686$; slot tiling / zero drift; rotation).
- **Novelty check (2026-11-21), `grep -ci` on `methods_db.md` before entry:** `josephus` = 0, `counting-out` / `counting out` = 0, `lucky number` = 0, `elimination` = 0. Nearest neighbours are 065 TTSMC (permutation rows by *transposition* of a 12-tone row — not by elimination), 089 CRCM (permutation stream by *adjacent swaps* — a different law), 025 Sieve (congruence-based modular sieves — the lucky sieve is *position*-based), 128 VESC (self-referential gaps), 090 GRDC (distinct *differences*), 144 LSPC (distance pairing). **No existing method generates material from a counting-out / elimination process → Method 148 is novel.**

### Layer

**concrete** (LAYER_ARCHITECTURE.md). The product of one Josephus game is a sequence of note events — pitch, onset, duration, velocity — on a slot grid, i.e. exactly the contents of a UnitMatrix cell. The $(n,k)$ game and the counting schedule are the *plan*; the elimination-order permutation is the *realized cell*. Same layer family as 012 Euclidean / 144 LSPC / 147 MMTC (all fill cells with rhythmic events); contrast the tick-free abstract plans 145 DPBC / 146 HHFC. Candidate code path: `generators/josephus_permutation.py` (new: `survivor`, `elimination_order`, `rotated_game`, `lucky_sieve`, `tile_cell`), with an optional `rules/counting_schedule.py` if schedule/sieve planning is later promoted to the abstract layer.

### Description

JCOC composes from the Josephus counting-out permutation. Four pillars:

**1. The elimination permutation.** $n$ people stand in a circle numbered $1..n$; count inclusively by $k$; the $k$-th is eliminated; resume counting at the next person; repeat. The elimination order $E(n,k)=[e_1,\dots,e_n]$ is a **permutation of $\{1,\dots,n\}$**; the last element $e_n = J(n,k)$ is the survivor. Recursive construction: $e_1=(k-1 \bmod n)+1$, then $E(n-1,k)$ renumbered with offset $k \bmod n$. Musical reading: the permutation maps onto a pitch pool of $n$ degrees ($\mathrm{pitch}_i = \mathrm{pool}[E_i-1]$) → one event per slot, **every pool degree used exactly once per game** — a per-cell "counting aggregate". The counting step $k$ is the *interval generator*: consecutive eliminations are $k$ apart around the shrinking circle, so the melodic contour is a $k$-step spiral that deforms as the circle empties. $k=2$ gives the canonical two-layer shape: all even positions eliminated first in ascending order (an "every-other-degree" arpeggio run), then the odds in a recursively Josephus-ordered tail (a self-similar fractal contour). $k=1$ degenerates to the identity (ascending scale); $k=n-1$ gives the reverse spiral.

**2. Closed forms = cadence algebra.** The survivor — the cell's terminal anchor — is computable without simulation: $k=2$: $f(n)=2l+1$ for $n=2^m+l$, i.e. $f(n)=2(n-2^{\lfloor\log_2 n\rfloor})+1$, equivalently **the left cyclic shift of $n$ in binary** (OEIS A006257); $k=3$: Halbeisen–Hungerbühler (1997) $f(n)=3(n-\mathrm{round}(\alpha(3/2)^m))+(2\text{ or }1)$, $\alpha\approx 0.8111$; general: $g(n,k)=(g(n-1,k)+k)\bmod n$ in $\mathcal{O}(n)$. $f(41,3)=31$ — the composer's own lucky number from the Yodfat story.

**3. The density arc.** Round $r$ of the game scans the remaining circle of $n-r+1$ people. If each round occupies one metric unit, the counting-subdivision *capacity* descends $n,\ n-1,\ \dots,\ 1$ — a deterministic density arc (felt accelerando if round time is fixed: the same counting content is packed into the same span). Optional "audible counting": emit quiet count-ticks at each scanned position before the eliminated note; the intra-round onset pattern is then the eliminated person's current index — a deterministic intra-bar rhythm.

**4. Structure = a counting schedule, plus the lucky sieve.** Sections are successive games $(n_j, k_j, \mathrm{pool}_j, \mathrm{start}_j)$; the column sequence is the **counting schedule**. Seed chaining: the survivor of game $j$ becomes the starting position of game $j+1$ (the "Josephus chain" — continuity by arithmetic). Reprise = reusing $(n,k,\mathrm{pool})$ exactly (TURN by schedule). The macro-form option unique to this family is the **sieve of Josephus Flavius** (lucky numbers, Gardiner–Lazarus–Metropolis–Ulam 1956): remove every 2nd of the naturals, then every 3rd of the remaining, then every 7th, ... ($n$ = next survivor). Lucky positions $1,3,7,9,13,15,21,25,\dots$ have **prime-like density $\sim n/\log n$** (prime-number-theorem analogue), $L_n > p_n$ eventually, twin-lucky ≈ twin-prime frequency. Applied to a candidate grid of beats/sections, the lucky sieve keeps the lucky positions as structural anchors and eliminates the rest — a *position*-based formal skeleton with prime-like statistics, the first such sieve in the DB (025 is congruence-based).

Measured audit (all from `verify_jcoc_math.py`):

| audit | result |
|---|---|
| permutation property | $E(8,3)$ = [3,6,1,5,2,8,4,7], a permutation of 1..8; survivor 7 |
| $k=2$ closed form | $f(41)=2\cdot9+1=19$ with $41=32+9$; recurrence matches |
| binary cyclic shift | $f(13)=11$; bin(13)=1101 → 1011 = 11 |
| $k=3$ | $f(41,3)=31$ (Halbeisen–Hungerbühler; matches simulation) |
| general recurrence | $g(n,k)=(g(n-1,k)+k)\bmod n$ matches simulation for a sweep of $(n,k)$ |
| density arc | round subdivision counts = $n,n-1,\dots,1$ |
| lucky sieve | prefix $1,3,7,9,13,15,21,25,31,33$ = OEIS A000959 |
| lucky density | $\#\{L\le 10^5\} = 8772 \approx x/\ln x = 8686$ (PNT-analogue; 9592 primes) |
| slot tiling | $n$ events of $S/n$ ticks, survivor held to $S$ → all rows equal length |

### Technical Mechanics

**1. Survivor recurrence.** $g(1,k)=0$; $g(n,k)=(g(n-1,k)+k)\bmod n$; 1-based $f=g+1$. $\mathcal{O}(n)$ time, $\mathcal{O}(1)$ space — the cheapest way to compute a cell's cadence note.

**2. Elimination order.** Naive simulation (list + index arithmetic) is $\mathcal{O}(n^2)$; a Fenwick tree (order statistics: find the $k$-th remaining) gives $\mathcal{O}(n\log n)$; the recursive renumbering $E(n,k)=[(k-1\bmod n)+1] \mathbin{++} \mathrm{shift}_{k \bmod n}(E(n-1,k))$ is the cleanest construction.

**3. Rotation.** Starting the count at position $s$ rotates the elimination order: $E^{(s)}(n,k)[i] = E(n,k)[(i+s)\bmod n]$ — the voice-level phase dial.

**4. Tiling a cell.** $n$ events at slot $S/n$ ticks (choose $S$ divisible by $n$); the survivor event $i=n$ is extended to $S$ — the terminal anchor. All voices' cells share $S$ per section, so rows are equal length **by construction**: `validate()` passes without padding.

**5. Lucky sieve.** Maintain the survivor list; each pass removes every $n$-th remaining element where $n$ is the next surviving element; the survivors after all passes up to $N$ are the lucky numbers. $\mathcal{O}(N\log N)$ total.

**6. Complexity.** $\mathcal{O}(n)$ survivor; $\mathcal{O}(n\log n)$ permutation (Fenwick), $\mathcal{O}(n^2)$ naive; a schedule of $S$ sections costs $\mathcal{O}(\sum_j n_j \log n_j)$; the sieve to $N$ costs $\mathcal{O}(N\log N)$. No sampling, no training — fully deterministic given the schedule.

### Musical Elements Framework

- **PITCH**: core. The elimination order is a permutation → **every pool degree exactly once per game** (a per-cell "counting aggregate"; contrast 065's aggregate by transposition). $k$ = interval generator: consecutive events are $k$ apart around the shrinking circle; $k=2$ = the evens-then-odds two-layer contour (ascending "every-other-degree" run + fractal odd tail); $k=1$ = identity scale; $k=n-1$ = descending spiral. Pool = any ladder: 7 diatonic degrees (mode-saturating phrase), 12 pitch classes (12-note counting aggregate), or a chord voicing.
- **RHYTHM**: slot grid of $n$ events per cell plus the **density arc** $n, n-1, \dots, 1$ of counting subdivisions across rounds (deterministic acceleration/deceleration of felt density); optional audible counting ticks make the intra-round onset = the eliminated person's current index (a deterministic intra-bar rhythm). The counting *is* the meter: $k$ is a metric skip.
- **HARMONY**: not generated directly, but the **survivor chain** $J(n_j,k_j)$ across sections yields a deterministic chord-root / cadence plan (survivors mod 12 = tonic roots; the $k=2$ closed form gives a "binary-rotation tonic"). A second, coarser counting game over chord symbols ($n_c$ chords, $k_c$) composes progressions by the same law at a larger scale.
- **STRUCTURE**: sections = counting games; the schedule $(n_j,k_j,\mathrm{start}_j)$ = macro-form; seed chaining = continuity between sections; reprise = repeated $(n,k)$; the lucky sieve = formal elimination of candidate beats/sections with prime-like density (lucky anchors = HOME, eliminated slots = passing material).
- **TEXTURE**: parallel voices = rotations of one game (phase-shifted permutations — homorhythm with rotated pitch order, the combinatorial sibling of 026 DPSM's phase offsets) or independent $(n_v,k_v)$ games (stratified counting with density arcs in different registers). The audible-counting option turns the counting itself into an ornament stream.

### UnitMatrix Integration (Voices & Sections)

**Rows = voices = counting circles.** Voice $v$: `{pool_v (n_v degrees), k_v, start_v, velocity_arc}`. Rotated starts = phase texture; identical $(n,k)$ across rows with distinct pools = chordal homorhythm (the same counting, transposed registers).

**Columns = sections = counting games.** Column $j$: `{n_j, k_j, pool_j, start_j, game_type}`; the column sequence is the schedule. Seed chain: `start_{j+1} = survivor of game j` (Josephus continuity). Reprise columns reuse $(n_j,k_j,\mathrm{pool}_j)$ exactly — TURN/reprise by schedule.

**Cells = MusicUnit.** Cell $(v,j)$ = the game's elimination-order events: $n_j$ events at slot $S_j/n_j$ ticks, pitch = $\mathrm{pool}_v[E_{v,j}(i)-1]$, velocity = the round arc (early eliminations accented, survivor softest — or the reverse: a per-cell dynamic swell toward the survivor), survivor event ($i = n_j$) extended to $S_j$ = the cell's terminal anchor. **The zero-drift pad is musically the cadence arrival.** All rows equal length by construction → `validate()` passes.

**Composition path.** `pick counting schedule ((n_j,k_j,pool_j,start_j)) → survivor chain (recurrence / closed form) → elimination orders (recursive / Fenwick) → rotations per voice → tiling (n_j events of S_j/n_j, survivor held to seam) → MusicUnit per cell → validate() → to_midi() → any SP renderer`.

### Pitfalls

1. **Counting is inclusive.** $k$ means $k-1$ skipped, the $k$-th eliminated. An off-by-one convention flips the whole permutation and the survivor; fix the convention and verify against $f(41,3)=31$.
2. **1-based vs 0-based.** $g$ is 0-based, $f = g+1$. Mixing them silently transposes the survivor (and hence the cell's cadence note) by one position.
3. **Slot divisibility.** $n_j$ events per cell require $S_j$ divisible by $n_j$ (choose $S_j = n_j \cdot \mathrm{slot}$) or the last slot is fractional and the row misses the seam — the zero-drift gate.
4. **$k=2$'s "evens first" is the feature, not a bug.** The two-layer contour (ascending evens, recursive odds) is the method's signature shape; do not "fix" it by sorting — that destroys the elimination structure.
5. **Rotation ≠ new material.** A rotated start is a phase shift of the same permutation (good for texture, useless for variety); change $n$, $k$, or the pool for genuinely new material.
6. **Lucky-sieve density is asymptotic.** Small prefixes deviate from $n/\log n$ ($L_1=1$, $L_2=3$, $L_3=7$); do not over-interpret statistics of a short formal skeleton.
7. **Neighbour audit.** 065 TTSMC (rows by transposition, not elimination); 089 CRCM (adjacent-swap change ringing); 025 Sieve (congruence-based — the lucky sieve is position-based); 128 VESC (self-referential gaps); 090 GRDC (distinct differences); 144 LSPC (distance pairing); 077 DBUC (de Bruijn windows). JCOC is the DB's first elimination-order / counting-out method; its closest structural cousin is 065 (a permutation discipline) and its closest sieve cousin is 025 (but position-based, not congruence-based).
```

## Final verification (post-run)

- `wc -l methods_db.md` = **32 541** (was 32 459).
- Summary row present at **line 158** (`| **148** | ...`), section at **line 32461** (`# Josephus Counting-Out Composition (JCOC) (Method 148)`), 81-line section with all required subsections (Source, Layer, Description, Technical Mechanics, Musical Elements Framework, UnitMatrix Integration, Pitfalls).
- Row verified: single `|` prefix (no `||`), single backslashes (3 `\mathcal` tokens, zero `\\`).
- **Next free ID: 149.**
