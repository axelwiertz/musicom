# Method 127 — Sprague-Grundy Nimber Composition (SGNC)

**Paradigm:** Rules-Based (deterministic impartial-combinatorial-game construction) · **Layer:** abstract · **ID:** 127 · **Date:** 2026-10-27

> Every impartial combinatorial game — Nim, subtraction games, Kayles,
> Wythoff — collapses onto a single Nim heap whose size is the *Grundy
> value* of the position (Sprague 1936, Grundy 1939). SGNC makes that
> collapse musical: a position is a tension budget, a move is an event,
> the **nimber sequence is the tension curve**, g=0 positions are
> **provable cadences** (P-positions), the disjunctive sum of voices
> makes **chord tension the XOR of voice nimbers**, and Bouton's
> winning-move rule (1901) is a **deterministic voice-leading algorithm**
> that always knows which voice resolves and to what value. Subtraction
> sets are the melodic interval vocabulary; Grundy sequences are
> ultimately periodic, so the method *proves* its own rondo (period),
> its intro (preperiod) and its cadence schedule (P-positions). No
> training, no corpus, no randomness: verified here — S={1,2,3} period
> 4, S={1,3,4} period 7, Dawson's Kayles preperiod 53 + period 34.

---

## 1. The mathematics

An **impartial combinatorial game** is a finite game where both players
have the same moves from every position, there is no chance and no
hidden information, and the player unable to move loses (normal play).

**P- and N-positions.** A position is a **P-position** (Previous player
wins) if the player to move has no winning move; otherwise it is an
**N-position** (Next player wins). Recursively: a position is P iff all
its options are N; a position is N iff at least one option is P.

**The Grundy value (nimber).** Define

    g(P) = mex{ g(P') : P' is an option of P }

where mex is the *minimal excludant* — the smallest non-negative integer
not in the set. Then g(P) = 0 iff P is a P-position. The classic results:

| result | statement | musical reading |
|---|---|---|
| mex recursion | g = mex{options} | tension = smallest missing tension level among continuations |
| Sprague–Grundy theorem | g(sum of games) = XOR of g's | polyphonic chord tension = XOR of voice tensions |
| Bouton (1901) | Nim P-position iff heap XOR = 0; winning move: heap h with h⊕S < h → h⊕S | cadence iff voice-nimber XOR = 0; the scoreboard names the resolving voice |
| Subtraction-game periodicity | finite S ⇒ Grundy sequence ultimately periodic | the harmonic-rhythm cycle and intro are theorems |
| Wythoff (1907) | P-positions = Beatty pairs (⌊nφ⌋, ⌊nφ²⌋) | aperiodic tension arcs; Sturmian lineage (cf. 121 IETC) |
| Guy & Smith (1956) | Dawson's Kayles: eventual period 34 | a 34-slot hidden cycle from a 2-line rule |

**The disjunctive sum.** The sum of games G₁ + G₂ + … + G_k is played by
moving in exactly one component per turn. This is *polyphony*: each
component is a voice, and the vertical stack at any time is a position
of the sum. The Sprague–Grundy theorem says

    g(G₁ + G₂ + … + G_k) = g(G₁) ⊕ g(G₂) ⊕ … ⊕ g(G_k)

(⊕ = bitwise XOR / nim-sum). So the **chord's tension is the XOR of the
voice nimbers**, and a chord is a perfect cadence iff that XOR is 0.

## 2. Verified invariants

Script: `projects/Research/outputs/cgtc_validate/verify_grundy.py`
(musicom env, pure stdlib, memoized mex recursion).

| property | statement | measured |
|---|---|---|
| Nim mex recursion | g(n) = mex{g(0..n−1)} = n | n = 0..23 all equal heap size |
| Sprague–Grundy xor law | g(G+H) = g(G) ⊕ g(H) | direct mex of the 2-heap sum == a^b for all a,b ∈ 0..4 |
| Subtraction S={1,2,3} | Grundy sequence period 4 | 0,1,2,3,0,1,2,3,… (first 32 terms) |
| Subtraction S={1,3,4} | Grundy sequence period 7 | head 0,1,0,1,2,3,2,…; detected period 7 |
| Dawson's Kayles | Guy & Smith head | g(0..19) == published head exactly |
| Dawson's Kayles period | eventual period 34 | measured (preperiod, period) = (53, 34) on n=0..399 |
| Bouton P-positions | (grundy==0) ⟺ (xor==0) | 3-heap direct mex vs xor for all heaps 0..3 |
| Cadence schedule | P-positions of S={1,3,4} | 0,2,7,9,14,16,21,23,… (period-7 zero pattern) |

Note: the first attempt at the Dawson's Kayles period check used
preperiod 52 (a common citation); the measured value on n=0..399 is
**preperiod 53, period 34** — the literature period 34 is confirmed, the
preperiod citation is off-by-one. Measure, don't trust the citation.

## 3. The musical identities

**Identity 1 — nimbers are quantized tension.** g = 0 is a provable
cadence: no continuation can win, so the phrase must end or be
re-armed. g > 0 is tension with the nimber as its rank; the mex rule
means "the tension of a position is the smallest tension level no move
can reach" — a *functional* labeling of the scale ladder (0 = tonic
bearing, 1,2,3 = progressively tenser degrees).

**Identity 2 — XOR harmony.** With voices as heaps, the vertical
tension is the XOR of voice nimbers. XOR = 0 ⟺ perfect cadence — the
whole ensemble must land on zero *together*. Bouton's rule then tells
you *which* voice must move and *to what nimber*: deterministic
voice-leading toward cadence, no search needed. Chord-tension classes
form the elementary abelian 2-group (ℤ₂)^k.

**Identity 3 — periodicity is form.** Finite subtraction sets give
ultimately periodic Grundy sequences: the period is the rondo/loop, the
preperiod the through-composed intro, the P-position schedule the
cadence plan. Dawson's Kayles — a split game whose move removes two
adjacent pins and forks the row — yields a *2-note gesture that
bifurcates a texture* and hides a 34-slot cycle.

**Identity 4 — cadence ⇒ re-arousal (theorem).** Every move from a
P-position lands on an N-position. A cadence *must* be followed by
tension re-arousal — not a stylistic preference, a theorem. Conversely,
from any N-position a cadence is *guaranteed reachable* (Bouton).

## 4. Python implementation sketch (the verified core)

```python
# rules/grundy_composition.py  (sketch — verified core)
from functools import lru_cache

def mex(values):
    s = set(values); m = 0
    while m in s: m += 1
    return m

def subtraction_curve(S, N):
    """Grundy sequence g(0..N) for the subtraction game with move set S."""
    S = tuple(sorted(S))
    @lru_cache(maxsize=None)
    def g(n):
        return mex(g(n - s) for s in S if n - s >= 0)
    return [g(n) for n in range(N)]

def find_period(seq, tail=200, maxp=200):
    """Ultimate period of an ultimately periodic Grundy sequence."""
    for p in range(1, maxp):
        if all(seq[i] == seq[i + p] for i in range(len(seq) - tail, len(seq) - tail + 60)):
            return p
    return None

def dawsons_kayles(N):
    """Split game: remove 2 adjacent pins, fork row into two sub-rows (disjunctive sum)."""
    @lru_cache(maxsize=None)
    def g(n):
        if n <= 0: return 0
        return mex(g(i) ^ g(n - i - 2) for i in range(n - 1))
    return [g(n) for n in range(N)]

def nim_sum(heaps):
    """Vertical chord tension = XOR of voice (heap) nimbers."""
    x = 0
    for h in heaps: x ^= h
    return x

def bouton_move(heaps):
    """Winning move (Bouton 1901): reduce heap h with h^S < h to h^S. Returns (voice, new_heap)."""
    S = nim_sum(heaps)
    if S == 0: return None                     # P-position: no winning move (cadence)
    for v, h in enumerate(heaps):
        if h ^ S < h:
            return (v, h ^ S)
    return None

def p_positions(seq):
    """Cadence schedule: indices where the Grundy value is 0 (P-positions)."""
    return [n for n, g in enumerate(seq) if g == 0]

def realize_plan(S, heaps, degree_map, moves_per_section):
    """Per-voice abstract plans: (onset, degree, nimber) per move. Realize step fills cells."""
    curve = subtraction_curve(S, max(heaps) + 1)
    plan = {v: [] for v in range(len(heaps))}
    for t in range(moves_per_section):
        for v, h in enumerate(heaps):
            if h <= 0: continue
            plan[v].append((t, degree_map(h), curve[h]))   # (time, degree, tension)
    return plan
```

Consumption: `subtraction_curve`/`dawsons_kayles` per section,
`nim_sum` per column (vertical targets), `bouton_move` for resolution
arcs, `p_positions` for the cadence schedule; hand the abstract plan to
a realize step / concrete generator → `_unit_from_events(events,
section_len)` padding → `validate()` → `to_midi()` via
`workflows/unitmatrix_composer.py`.

## 5. UnitMatrix mapping

- **Voices = rows = heaps of the disjunctive sum.** Each voice's heap
  size trajectory is its event plan; g(heap) is its instantaneous
  tension. Roles: a "composer" heap (winning-strategy line), companion
  heaps (prolonging moves), a "bifurcator" heap (Kayles splits spawn
  counter-voices). Independence by construction; coherence by XOR.
- **Sections = columns = game swaps.** Each column sets its subtraction
  set (pitch vocabulary + density), initial heaps, and a P-position
  seam. The section's nimber curve is its tension arc; rondo = same game
  per column, through-composed = new game per column, reprise = game
  restart with new heaps.
- **Cells = MusicUnit.** Cell (v, s) = voice v's moves in section s:
  onset = move time, pitch = position→degree, duration = move-size
  class, velocity = nimber magnitude. Chord cells: column XOR = vertical
  target; voicing realized by a concrete method (001/011/050/056).

## 6. References

- Bouton, C. L. (1901). "Nim, a game with a complete mathematical
  theory." *Annals of Mathematics* 3(1/2), 35–39. doi:10.2307/1967631.
- Sprague, R. (1936). "Über mathematische Kampfspiele." *Tôhoku
  Mathematical Journal* 41, 438–444.
- Grundy, P. M. (1939). "Mathematics and games." *Eureka* 2, 6–8.
- Smith, C. A. B. (1966). "Graphs and composite games." *Journal of
  Combinatorial Theory* 1(1), 51–81.
- Guy, R. K. & Smith, C. A. B. (1956). "The G-values of various games."
  *Proceedings of the Cambridge Philosophical Society* 52(3), 514–526.
- Dudeney, H. E. (1908). *The Canterbury Puzzles.* (Kayles.)
- Dawson, T. R. (1935). *Fairy Chess Review* problem column.
- Wythoff, W. A. (1907). "A modification of the game of Nim." *Nieuw
  Archief voor Wiskunde* 7, 199–202.
- Berlekamp, E. R., Conway, J. H. & Guy, R. K. (1982). *Winning Ways
  for your Mathematical Plays.* Academic Press.
- Conway, J. H. (1976). *On Numbers and Games.* Academic Press.
- Fraenkel, A. S. (2009). "Combinatorial games: selected bibliography
  with a succinct gourmet guide." arXiv:0908.0068.
- Xenakis, I. (1971). *Duel* / *Stratégie* — economic zero-sum game
  theory (adjacent art; already cited by 123 GTBRC).
- Novelty check 2026-10-27: arXiv API 0 hits (`"Sprague-Grundy" AND
  music`, `"Grundy" AND "music generation"`, `"nim" AND "algorithmic
  composition"`, `"combinatorial game theory" AND music`); DuckDuckGo
  returns only math-education material — no dedicated
  algorithmic-composition method in the literature.
