# Method 148 — Josephus Counting-Out Composition (JCOC)

- **ID:** 148
- **Paradigm:** Rules-Based (deterministic combinatorial elimination; the only "choice" is the planned counting schedule, seeded like 144–147)
- **Layer:** concrete (LAYER_ARCHITECTURE.md) — emits note events (pitch, onset, duration, velocity) on a slot grid, i.e. fills UnitMatrix cells; the $(n,k)$ game is the plan, the elimination-order permutation is the realized cell
- **Family:** permutation/combinatorial. Siblings: 065 TTSMC (permutation rows by transposition), 089 CRCM (permutation stream by adjacent swaps), 025 Sieve (congruence-based sieves), 090 GRDC (distinct differences), 144 LSPC (distance pairing), 012 Euclidean (hit distribution). JCOC is the only method whose material is an **elimination order**.
- **One-liner:** compose from the Josephus counting-out permutation — $n$ people in a circle, every $k$-th is counted out until one survives; the elimination order is a permutation of $\{1..n\}$ that maps onto a pitch pool (every degree exactly once per cell, a "counting aggregate"), the survivor $J(n,k)$ is the cell's terminal cadence anchor ($k{=}2$: $f(n)=2l+1$, the left binary cyclic shift; $k{=}3$: Halbeisen–Hungerbühler, $f(41,3)=31$), round subdivisions descend $n,n{-}1,\dots,1$ (deterministic density arc), sections are a counting schedule chained by survivor seeds, and the sieve of Josephus Flavius (lucky numbers) gives a prime-like formal skeleton.

---

## 1. The counting-out game

A counting-out game selects one person from a group by cyclic counting (eeny meeny miny moe and friends; Bolton 1888 traced the custom to divination by lots). The Josephus problem is its formal variant: $n$ people in a circle numbered $1..n$, count inclusively by $k$ ($k-1$ skipped, the $k$-th eliminated), resume at the next person, repeat until one remains and is freed.

**Elimination order.** $E(n,k) = [e_1,\dots,e_n]$ with $e_i$ = the $i$-th eliminated index, $e_n = J(n,k)$ the survivor. Recursive construction: $e_1 = (k-1 \bmod n)+1$; the remaining circle of $n-1$ is renumbered starting at the person after $e_1$, so

$$E(n,k) = \big[\,(k-1 \bmod n)+1\ \big]\ \mathbin{++}\ \mathrm{shift}_{k \bmod n}\big(E(n-1,k)\big).$$

$E(n,k)$ is a **permutation of $\{1,\dots,n\}$** — no index repeats, every index appears exactly once. That one fact is the musical engine: map the order onto a pitch pool of $n$ degrees and every degree sounds exactly once per game.

**Worked permutation.** $E(8,3) = [3,6,1,5,2,8,4,7]$ — verify: count 1,2,3 → 3 out; continue 4,5,6 → 6 out; 7,8,1 → 1 out; 2,4,5 → 5 out; 6? (renumbered 6,7,2 → 2 out); then 4,7,8 → 8 out; 4? (4,7 → 4 out); survivor 7. All of $1..8$ exactly once, survivor $J(8,3)=7$.

**Musical reading.** $\mathrm{pitch}_i = \mathrm{pool}[E_i - 1]$: one event per slot, every pool degree exactly once — a per-cell **counting aggregate**. The counting step $k$ is the interval generator: consecutive eliminations are $k$ apart around the shrinking circle, so the contour is a $k$-step spiral that deforms as the circle empties. $k=1$ degenerates to the identity (ascending scale); $k=2$ gives the canonical two-layer shape — all evens eliminated first in ascending order (an "every-other-degree" arpeggio run: $2,4,6,\dots$), then the odds in recursively Josephus-ordered tail (self-similar fractal contour); $k=n-1$ gives the reverse spiral.

## 2. Closed forms = cadence algebra

The survivor — the cell's terminal anchor — is computable without simulation:

**$k=2$** (OEIS A006257):
$$f(2j)=2f(j)-1,\qquad f(2j+1)=2f(j)+1,\qquad f(n)=2l+1 \text{ for } n=2^m+l,\ 0\le l<2^m,$$
$$f(n)=2\big(n-2^{\lfloor\log_2 n\rfloor}\big)+1.$$
Equivalently: **$f(n)$ is the left cyclic shift of $n$'s binary representation** — $n=1101_2=13 \Rightarrow f(13)=1011_2=11$. The tonic of a $k{=}2$ cell is a binary rotation of the circle size: pure arithmetic, no circle needed.

**$k=3$** (Halbeisen & Hungerbühler 1997): with $\alpha \approx 0.8111\ldots$, let $m$ be the greatest integer with $\mathrm{round}(\alpha(3/2)^m)\le n$; then
$$f(n) = 3\big(n - \mathrm{round}(\alpha(3/2)^m)\big) + (2 \text{ if rounded up, else } 1), \qquad n\ge 5.$$
Worked: $n=41$, $m'=\mathrm{round}(\log_{3/2}(41/\alpha))\approx 10$, $\mathrm{round}(\alpha(3/2)^{10})\approx 47 > 41$ so $m=9$, $\mathrm{round}(\alpha(3/2)^9)\approx 31$, hence $f(41,3)=3(41-31)+1=31$ — Josephus' own alleged safe position at Yodfat.

**General $k$:** 0-based recurrence
$$g(1,k)=0,\qquad g(n,k)=\big(g(n-1,k)+k\big)\bmod n \quad(\mathcal{O}(n));$$
1-based $f=g+1$; improved $\mathcal{O}(k\log n)$ variant eliminates $\lfloor n/k\rfloor$ people per step (see the Wikipedia solution section). The $x$-added-people generalization: survivor stays at $p+mx$ modulo $n+x$.

## 3. The density arc

Round $r$ of the game scans the remaining circle of $n-r+1$ people. If each round occupies one metric unit, the counting-subdivision *capacity* descends

$$n,\ n-1,\ n-2,\ \dots,\ 1$$

— a deterministic linear density arc (felt accelerando when round time is fixed: the same counting content is packed into the same span; felt ritardando if the count-rate is fixed). This is the method's rhythmic signature: the piece "sorts itself" to the survivor under a monotone thinning of subdivision.

**Audible counting (optional).** Emit a quiet count-tick at each scanned position before the eliminated note. The intra-round onset pattern is then the eliminated person's current index — a deterministic intra-bar rhythm that depends on the whole history of the round.

## 4. Structure: counting schedule + the lucky sieve

**Counting schedule.** Sections are successive games $(n_j, k_j, \mathrm{pool}_j, \mathrm{start}_j)$; the column sequence is the schedule. **Seed chaining**: $\mathrm{start}_{j+1} = J(n_j,k_j)$ — the survivor of game $j$ opens game $j+1$ (continuity by arithmetic). **Reprise** = reusing $(n,k,\mathrm{pool})$ exactly (TURN by schedule; the $k{=}2$ case even predicts the reprise's tonic as a binary rotation of $n$).

**The sieve of Josephus Flavius (lucky numbers).** Gardiner, Lazarus, Metropolis & Ulam (1956): remove every 2nd of the natural numbers, then every 3rd of the remaining, then every 7th of the remaining, ... (each pass removes the $n$-th remaining element where $n$ is the next surviving element). Survivors: $1,3,7,9,13,15,21,25,31,33,37,43,49,51,63,67,69,73,75,79,\dots$ (OEIS A000959). Properties shared with the primes: asymptotic density per the prime number theorem ($\#\{L\le x\}\sim x/\ln x$), a Goldbach-type conjecture, twin-lucky pairs ≈ twin-prime frequency, and $L_n > p_n$ for large $n$. **Musical use**: applied to a candidate grid of beats/sections, the lucky positions survive as structural anchors and the rest are "eliminated" — a *position*-based formal skeleton with prime-like statistics, the first such sieve in the DB (025 Xenakis sieves are congruence-based: $x \equiv r \pmod m$; the lucky sieve eliminates by position in the *remaining* set, a fundamentally different operation).

## 5. Reference implementation sketch

```python
"""generators/josephus_permutation.py — JCOC (proposed)."""
from bisect import bisect_left

def survivor(n: int, k: int) -> int:
    """0-based survivor g(n,k) = (g(n-1,k)+k) mod n, O(n), O(1)."""
    g = 0
    for i in range(2, n + 1):
        g = (g + k) % i
    return g          # 1-based: f = g + 1

def survivor_k2(n: int) -> int:
    """Closed form, k=2: f(n)=2l+1, n=2^m+l  (left binary cyclic shift)."""
    m = n.bit_length() - 1
    l = n - (1 << m)
    return 2 * l + 1

def elimination_order(n: int, k: int) -> list[int]:
    """Naive simulation, O(n^2); Fenwick/order-statistics gives O(n log n)."""
    people = list(range(1, n + 1))
    out, idx = [], 0
    while people:
        idx = (idx + k - 1) % len(people)
        out.append(people.pop(idx))
    return out        # out[-1] == survivor (1-based)

def elimination_order_fast(n: int, k: int) -> list[int]:
    """O(n log n) via Fenwick order statistics (k-th remaining)."""
    bit = [0] * (n + 1)
    def add(i, v):
        while i <= n:
            bit[i] += v; i += i & -i
    def sum_(i):
        s = 0
        while i > 0:
            s += bit[i]; i -= i & -i
        return s
    def kth(t):                       # smallest i with prefix sum >= t
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if sum_(mid) >= t: hi = mid
            else: lo = mid + 1
        return lo
    for i in range(1, n + 1): add(i, 1)
    out, pos = [], 0
    for rem in range(n, 0, -1):
        pos = (pos + k - 1) % rem
        i = kth(pos + 1)
        out.append(i); add(i, -1)
    return out

def rotated(order: list[int], s: int) -> list[int]:
    """Start the count at position s: rotation of the elimination order."""
    return order[s:] + order[:s]

def lucky_numbers(N: int) -> list[int]:
    """Sieve of Josephus Flavius: remove every n-th remaining, n = next survivor."""
    a = list(range(1, N + 1, 2))      # start with the odds
    i = 1                             # a[0]=1 never removes anything
    while i < len(a):
        step = a[i]
        if step > len(a): break
        del a[step - 1::step]         # remove every step-th of the remaining
        i += 1
    return a

def tile_cell(order: list[int], pool: list[int], slot: int,
              velocity_arc=None) -> list[tuple]:
    """One cell: n events of `slot` ticks; survivor (last) held to the seam."""
    n = len(order)
    assert len(pool) >= n
    assert slot >= 1
    events = []
    for i, e in enumerate(order):
        start, end = i * slot, (i + 1) * slot
        if i == n - 1:                # survivor: terminal anchor, held to S
            end = (i + 1) * slot      # = n*slot = section length S
        vel = velocity_arc[i] if velocity_arc else (100 - i * (60 // max(n - 1, 1)))
        events.append((pool[e - 1], start, end, max(vel, 1)))
    return events                     # last event ends exactly at S

def plan(schedule, pools, slot=480):
    """Resolve a counting schedule into per-cell event lists."""
    cells = {}
    for (v, (n, k, start, pool_key)) in schedule.items():
        order = rotated(elimination_order_fast(n, k), start % n)
        cells[(v, pool_key)] = tile_cell(order, pools[pool_key], slot)
    return cells
```

Integration: emit one `MusicUnit` per (voice, section) from `tile_cell`, all cells in a section share `S = n*slot`, survivor events end exactly at `S` → `validate()` passes by construction (zero drift is designed in, exactly as in 144/147).

## 6. Verification

`_web148_jcoc/verify_jcoc_math.py` — **19/19 pass**:
permutation property ($E(8,3)=[3,6,1,5,2,8,4,7]$, survivor 7), $k{=}2$ closed form $f(n)=2l+1$ vs recurrence for $n\le 200$ ($f(13)=11$, $f(41)=19$), $f(41,3)=31$ via Halbeisen–Hungerbühler vs simulation (n=5..79), general recurrence $g(n,k)$ vs simulation over an $(n,k)$ sweep, Fenwick $\mathcal{O}(n\log n)$ order statistics == naive $\mathcal{O}(n^2)$ elimination, density arc $n,n-1,\dots,1$, lucky-sieve prefix == OEIS A000959, lucky density $\#\{L\le 10^5\}=8772$ vs $x/\ln x=8686$ (and < $\pi(10^5)=9592$, so $L_n>p_n$ asymptotically), slot tiling (events end exactly at $S$, all rows equal length), rotation property (rotated order is a valid permutation).

## 7. References

- Wikipedia, "Josephus problem" — https://en.wikipedia.org/wiki/Josephus_problem (fetched 2026-11-21). Definition, history (Yodfat, Bachet 1612, Herstein–Kaplansky), $k{=}2$ solution and binary cyclic shift (OEIS A006257), $k{=}3$ Halbeisen–Hungerbühler closed form with $\alpha\approx0.8111$ and $f(41,3)=31$, general recurrence $g(n,k)=(g(n-1,k)+k)\bmod n$, $\mathcal{O}(n)$ and $\mathcal{O}(k\log n)$ algorithms, the medieval 30-people/9th variant.
- Wikipedia, "Lucky number" — https://en.wikipedia.org/wiki/Lucky_number (fetched 2026-11-21). The "sieve of Josephus Flavius", Gardiner, Lazarus, Metropolis & Ulam (1956), position-based elimination, prime-like properties (PNT analogue, Goldbach variant, twin-lucky ≈ twin-prime, $L_n>p_n$).
- Wikipedia, "Counting-out game" — https://en.wikipedia.org/wiki/Counting-out_game (fetched 2026-11-21). Counting-out rhymes; Bolton, *Counting Out Rhymes of Children* (1888); divination-by-lots origin; the Josephus problem as the formal variant.
- Halbeisen, L. & Hungerbühler, N., "The Josephus Problem," *J. Théor. Nombres Bordeaux* 9 (1997) — the $k=3$ closed form, as cited by the Wikipedia article above.
- OEIS A006257 (Josephus $k{=}2$ survivor) and A000959 (lucky numbers).
- Musicom engine: `workflows/unitmatrix_composer.py` (zero-drift gate), `structures/` (MusicUnit, MusicEvent), `rules/set_theory.py` (pool/scale utilities).

## 8. Pitfalls (short list)

1. Counting is inclusive ($k-1$ skipped, $k$-th eliminated) — off-by-one flips the whole permutation; verify against $f(41,3)=31$.
2. 0-based $g$ vs 1-based $f=g+1$ — mixing transposes the cadence note by one.
3. Slot divisibility: $n_j$ events per cell need $S_j$ divisible by $n_j$; the zero-drift gate is a compositional rule here.
4. $k{=}2$'s evens-first contour is the signature shape — don't "fix" it by sorting.
5. Rotation is phase, not new material — change $n$, $k$, or the pool for variety.
6. Lucky-sieve density is asymptotic; small prefixes deviate from $x/\ln x$.
7. Apply humanization after the slot grid; jitter must not cross a seam (the survivor anchor is the seam).
