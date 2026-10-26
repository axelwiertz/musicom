# Method 126 — Knight's Tour Composition (KTC)

**Paradigm:** Rules-Based (deterministic Hamiltonian-path construction) · **Layer:** concrete · **ID:** 126 · **Date:** 2026-10-26

> Take the oldest documented combinatorial art object in the database — a
> 9th-century Sanskrit *knight's tour* that orders syllables so a verse
> reads along the horse's path — and make it a composition engine. A
> knight's tour visits every (pitch, time-slot) cell of an m×n board
> exactly once: the **2D aggregate** (each degree exactly n times, no
> literal pitch-slot repeat) with a built-in musical fingerprint, the
> **knight signature** |Δr|·|Δc| = 2 — melodic leaps are anti-correlated
> with durations, so short notes leap and long notes step. Closed tours
> loop seamlessly; the board transpose of a tour is another tour, giving
> an exact invertible-counterpoint companion voice. Rules-Based, no
> training, no corpus, ~1 ms for a full 8×8 piece skeleton.

---

## 1. The object

A **knight's tour** on an m×n board is a sequence of knight moves that
visits every one of the m·n squares exactly once. It is a *Hamiltonian
path* of the **knight graph** K(m,n) — vertices = squares, edges =
legal knight moves ((±1,±2) and (±2,±1) in (row, column)). A tour whose
last square is one knight move from its first is **closed (re-entrant)**;
otherwise **open**. Unlike the general Hamiltonian-path problem (NP-hard),
the knight's tour on rectangular boards is solvable in **linear time**
(Conrad–Hindrichs–Morsy–Wegener 1994; divide-and-conquer constructions of
Cull–De Curtins 1978 and Parberry 1997).

**Existence (Schwenk 1991).** An m×n board (m ≤ n) has a *closed* tour
unless (both m,n odd), (m ∈ {1,2,4}), or (m = 3, n ∈ {4,6,8}). An *open*
tour exists unless (m ∈ {1,2}), (m = 3, n ∈ {3,5,6}), or (m,n) = (4,4).

**Counts (OEIS A165134).** Directed tours on n×n: n=5 → 1,728; n=6 →
6,637,920; n=7 → 165,575,218,320; n=8 → 19,591,828,170,979,904 (≈2×10^16).
Undirected closed tours on 8×8: 13,267,364,410,532. The tour count is the
method's *vocabulary size* — variation identity without a corpus.

**History (the oldest method in this database).** The earliest known tour
artifact is 9th-century: Rudrata's *Kavyalankara* 5.15 presents a
*knight's-tour* poetic figure (*turagapadabandha*) whose 4×8 half-board
syllables read left-to-right *or* along the tour. In the 14th century,
Vedanta Desika's *Paduka Sahasram* ch. 30 derives a second metrical verse
from a first by a knight's tour on a 4×8 board — a knight-tour
*transformation of a chantable text*, the direct ancestor of KTC's
tour-as-voice construction. Nilakantha (~1600/1700) built fully symmetric
closed tours; Euler treated them mathematically in 1759; Warnsdorff gave
the first procedure in 1823; the Oulipo group used a 10×10 tour to order
the chapters of Perec's *Life: A User's Manual* (1978). No algorithmic
music-composition method exists in the literature (arXiv: 0 hits; Crossref:
only Wolfram Demonstrations visualizations) — KTC is proposed here on
these documented foundations.

## 2. The three musical identities

**Identity 1 — the knight signature (rhythm × contour).** Every move
satisfies |Δr|·|Δc| = 2 (one coordinate changes by 1, the other by 2).
With rows = pitch degrees and columns = grid slots, a note's *pitch step*
and its *temporal step* are anti-correlated by construction:

| move | pitch step | duration / rest | musical effect |
|---|---|---|---|
| (±2, ±1) | 2 degrees (leap) | 1 slot (short) | short notes leap |
| (±1, ±2) | 1 degree (step) | 2 slots (long) | long notes step |

This binary long/short alternation with coupled leaps is a syncopated,
hocket-like profile no Markov (002), Brownian (048) or noise (040) method
produces — it is a *combinatorial* groove, exact and repeatable.

**Identity 2 — the 2D aggregate (pitch balance, exact).** Because every
cell is visited exactly once, each of the m pitch rows is sounded exactly
n times and each of the n time slots exactly m times (verified on 8×8 and
12×8: row counts all equal n). This is twelve-tone aggregate equality
(065) generalised to two dimensions, and it is **exact by construction** —
stronger than LDSC's (125) discrepancy bound, which only *approximates*
balance. Consequence: the piece never literally repeats a (pitch, slot)
pair; it is an anti-repetition engine.

**Identity 3 — the dual tour (invertible counterpoint).** The knight-move
set is symmetric under board transposition, so transposing a tour's
coordinates yields a valid tour of the transposed board (verified). The
**dual voice**'s rhythm sequence is the primal voice's pitch-step sequence
and vice versa: an exact role-swap counterpoint — the "inversion" of 013
made combinatorial and two-dimensional.

**Closed tours (form).** A closed tour ends a knight move from its start:
looping the piece repeats through a seam that is itself a knight interval
— a homogeneous, seamless riff/loop, and the final band returns to the
first (built-in recap). Schwenk's theorem is the form-existence law.

## 3. Construction (verified)

**Warnsdorff's rule (1823):** from the current square, move to the
unvisited neighbour with the fewest onward moves (least degree of the
remaining graph). On knight graphs this is linear in practice (verified:
8×8 in 1.7 ms, 12×8 in 1.0 ms). Ties broken by **Pohl's rule (1967)** —
among tied candidates choose the one with the fewest onward moves *after*
it — or by a seeded random choice. **DFS fallback** (Warnsdorff-ordered
backtracking) rescues the boards/starts where the heuristic stalls; cap
its node budget and reseed. For boards ≳ 30×30 use Parberry's linear
construction.

**Piece identity** = (m, n, start square, tie-break policy, row→degree
scale map, per-section column bands). With 2×10^16 tours on 8×8 alone,
seeding is cheap and never repeats.

## 4. Verified invariants

Script: `projects/Research/outputs/ktc_validate/verify_ktc.py` (musicom
env, pure stdlib, deterministic except the labelled seeded tie-breaks).

| property | statement | measured |
|---|---|---|
| 8×8 completeness | Warnsdorff + Pohl from (0,0) | 64/64 cells, 1.7 ms |
| random tie-break | seeded RNG tie-break | 64/64 cells, 0.6 ms |
| knight signature | every move has \|Δr\|·\|Δc\| = 2 | 64/64 moves, both tie-breaks |
| 2D aggregate | every (row, col) cell once | 64 distinct cells; row counts all 8; col counts all 8 |
| row balance | each pitch row exactly n times | 8×8: all rows 8; 12×8: all rows 8 |
| closed tour | Schwenk-legal 8×8 | found from (7,4) in 0.01 s (DFS), closed=True |
| dual tour | transpose is a valid tour | 64 cells, signature True |
| cost | Warnsdorff on bigger boards | 12×8: 96 cells in 1.0 ms; 10×10: 100 cells, complete |
| board sweep | 5×5, 6×6, 8×8, 10×10, 12×8 | all complete, signature True, open (corner starts) |

## 5. Python implementation sketch (the verified core)

```python
# generators/knight_tour_composition.py  (sketch — verified core)
MOVES = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]

def knight_neighbours(pos, m, n, visited):
    r, c = pos
    return [(r+dr, c+dc) for dr, dc in MOVES
            if 0 <= r+dr < m and 0 <= c+dc < n and (r+dr, c+dc) not in visited]

def warnsdorff_rank(pos, m, n, visited):
    """Fewest onward moves first (least degree)."""
    cands = knight_neighbours(pos, m, n, visited)
    return sorted((len(knight_neighbours(c, m, n, visited | {c})), c) for c in cands)

def solve_tour(m, n, start, tiebreak="pohl", rng=None, max_nodes=2_000_000):
    """Warnsdorff + Pohl/seeded-random tie-break, DFS fallback. Returns tour."""
    tour, visited = [start], {start}
    pos = start
    while len(tour) < m*n:
        ranked = warnsdorff_rank(pos, m, n, visited)
        if not ranked:
            return _dfs_fallback(m, n, start, max_nodes)   # stall -> backtrack
        best = ranked[0][0]
        ties = [c for k, c in ranked if k == best]
        if len(ties) == 1:
            nxt = ties[0]
        elif tiebreak == "pohl":
            nxt = min(ties, key=lambda c: len(knight_neighbours(c, m, n, visited | {c})))
        else:
            nxt = rng.choice(ties)
        tour.append(nxt); visited.add(nxt); pos = nxt
    return tour

def dual_tour(tour):            # board transpose -> invertible-counterpart voice
    return [(c, r) for (r, c) in tour]

def decode_band(tour, c_start, c_end, row_to_degree, slots_per_col=1):
    """Cell (voice, section) decoder: tour steps whose column is in [c_start, c_end)."""
    events = []
    tick = 0
    for (r0, c0), (r1, c1) in zip(tour, tour[1:]):
        if not (c_start <= c0 < c_end):
            tick += abs(c1 - c0) * slots_per_col; continue
        dur = abs(c1 - c0) * slots_per_col          # 1- or 2-slot duration/rest
        events.append((tick, row_to_degree(r0), dur))
        tick += dur
    return events                                    # pad with _unit_from_events
```

Consumption: one `solve_tour` per voice; `dual_tour`/`reflect_tour`/octave
copies for the companion voices; per-section column bands → `MusicEvent`s
→ `_unit_from_events(events, section_len)` padding → `validate()` →
`to_midi()` via `workflows/unitmatrix_composer.py`.

## 6. UnitMatrix mapping

- **Voices = rows of the matrix.** Voice 0 = primal tour; Voice 1 = dual
  tour (invertible counterpoint); Voice 2 = octave-down copy (parallel
  support); Voices 3+ = independent tours (different boards/starts/seeds).
- **Sections = columns of the matrix.** A section = a band of board
  columns; seams are crossed by knight moves (Δc = ±1, ±2) so the grammar
  is seamless; the closed tour's final band returns to the first = recap.
- **Cells = MusicUnit.** The band's tour steps decode to
  `(onset_tick, pitch, duration)`; aggregate reading groups the m notes
  per column as a rolled chord; zero-drift padding via `_unit_from_events`.

## 7. References

- Rudrata, *Kavyalankara* 5.15 (9th c.); Vedanta Desika, *Paduka
  Sahasram* ch. 30 (14th c.); Nilakantha, *Bhagavantabaskara* (c. 1600/1700) —
  documented via Wikipedia "Knight's tour" (fetched 2026-10-26).
- Euler, L. (1759). "Solution d'une question curieuse…", *Mém. Acad. Sci.
  Berlin* 15.
- Warnsdorff, H. C. von (1823). "Des Rösselsprungs einfachste und
  allgemeinste Lösung", *Schmalkaldische Unterhaltungen*.
- Pohl, I. (1967). "A method for finding Hamilton paths and Knight's
  tours." *Comm. ACM* 10(7), 446–449. doi:10.1145/363427.363463.
- Schwenk, A. J. (1991). "Which Rectangular Chessboards Have a Knight's
  Tour?" *Math. Mag.* 64(5), 325–332. doi:10.1080/0025570X.1991.11977627.
- Cull, P. & De Curtins, J. (1978). "Knight's Tour Revisited." *Fibonacci
  Quarterly* 16(3), 276–285.
- Conrad, A., Hindrichs, T., Morsy, H. & Wegener, I. (1994). "Solution of
  the Knight's Hamiltonian Path Problem on Chessboards." *Discrete Appl.
  Math.* 50(2), 125–134. doi:10.1016/0166-218X(92)00170-Q.
- Parberry, I. (1997). "An Efficient Algorithm for the Knight's Tour
  Problem." *Discrete Appl. Math.* 73(3), 251–260.
  doi:10.1016/S0166-218X(96)00010-8.
- Takefuji, Y. & Lee, K. C. (1992). "Neural network computing for knight's
  tour problems." *Neurocomputing* 4(5), 249–254.
- Perec, G. (1978). *La Vie mode d'emploi.* Gallimard (Oulipo 10×10 tour).
- OEIS A165134, A001230, A390833 (tour counts / Hamiltonian paths on
  knight graphs).
- Novelty check 2026-10-26: arXiv API (0 hits), Crossref (Wolfram
  Demonstrations only), DuckDuckGo — no algorithmic-composition method in
  the literature.
