# Method 144 — Langford–Skolem Distance-Pairing Composition (LSPC)

**Paradigm:** Rules-Based · **Layer:** concrete · **DB row:** 144 · **Feeds:** `generators/langford_pairing.py`

---

## 1. The object

A **distance-pairing sequence** of order $n$ is a word of length $2n$ over $\{1,\dots,n\}$ in which every symbol occurs exactly twice, and the two occurrences of $k$ are at a *prescribed* distance that depends on $k$:

| family | slots | law | exists iff | reference |
|---|---|---|---|---|
| **Langford** $L(2,n)$ | $2n$ | $j-i = k+1$ ($k$ slots *between*) | $n \equiv 0,3 \pmod 4$ | Langford 1958; Priday 1959; Davies 1959 |
| **Skolem** | $2n$ | $j-i = k$ | $n \equiv 0,1 \pmod 4$ | Skolem 1957 |
| **hooked Skolem** | $2n+1$ | $j-i = k$, one hook slot | $n \equiv 2,3 \pmod 4$ | O'Keefe 1961; Simpson 1983 |

The three existence sets are complementary, so **every $n \ge 1$ admits a piece**. $n\equiv0$: Langford *and* Skolem; $n\equiv1$: Skolem; $n\equiv2$: hooked Skolem only; $n\equiv3$: Langford *and* hooked.

Canonical small cases (verified):

```
Langford n=3:  2 3 1 2 1 3        (mirror 3 1 2 1 3 2)
Langford n=4:  4 1 3 1 2 4 3 2
Skolem   n=4:  4 2 3 2 4 3 1 1
Skolem   n=5:  5 2 4 2 3 5 4 3 1 1
Langford n=8:  8 3 7 2 6 3 2 4 5 8 7 6 4 1 5 1     (the demo piece)
```

## 2. Invariants (all measured, see `_web144_lspc/`)

- **Perfect cover (Langford / Skolem).** $2n$ slots, $2n$ events, $0$ empty, density $= 1.000$. Every subdivision of the grid is used exactly once; no slot is doubled, none is skipped. The hooked family is the exception by theorem: one mandatory hole, density $2n/(2n+1)$ (0.923 at $n{=}6$, 0.973 at $n{=}18$).
- **Complete lag spectrum.** Langford $\{j-i\} = \{2,\dots,n+1\}$; Skolem $\{1,\dots,n\}$ — every delay occurs exactly once. Hence the block is a canon at *every* delay in the admissible range, and the autocorrelation is flat.
- **Sum laws.** Langford $\sum_k (k+1) = n(n+3)/2$; Skolem $\sum_k k = n(n+1)/2$. Measured: 7→35, 8→44, 12→90 (Langford); 4→10, 9→45, 25→325 (Skolem).
- **Counts.** Oriented Langford solutions $= 2 \times$A014552: $L(3)=2$, $L(4)=2$, $L(7)=52$, $L(8)=300$, $L(11)=35584$ (vs $1,1,26,150,17792$). Skolem counts $=$ A004075 exactly: $n{=}4$: 6, $n{=}5$: 10, $n{=}8$: 504, $n{=}9$: 2656, zero for $n\equiv2,3$.
- **Interlacing ratio.** Number of voice pairs whose intervals cross, over $\binom{n}{2}$; measured on first solutions: $n{=}3$: 2/3, $n{=}4$: 4/6, $n{=}7$: 11/21, $n{=}8$: 15/28, $n{=}11$: 25/55, $n{=}12$: 26/66 — decreasing in $n$ (0.667 → 0.394), i.e. large blocks auto-stratify.
- **Symmetry.** Reversal preserves the law. Relabelling $k \mapsto n+1-k$ **does not** (measured $n{=}7$): the label *is* the distance.
- **Totality.** A valid piece was constructed for every $n = 1..35$ in the theorem's family; $n{=}36$ exceeded the prototype's 5 M-node search budget (existence is not in doubt — Davies' construction covers all $n\equiv0,3$).

## 3. Why the residue classes are forced (parity proof)

Count slots by parity. A pair at distance $k+1$ has endpoints of **opposite** parity iff $k+1$ is odd, i.e. iff $k$ is even; a pair with $k$ odd has both endpoints of the **same** parity.

- The $\lfloor n/2 \rfloor$ even symbols consume $\lfloor n/2 \rfloor$ even and $\lfloor n/2 \rfloor$ odd slots.
- That leaves $\lceil n/2 \rceil$ even and $\lceil n/2 \rceil$ odd slots for the $\lceil n/2 \rceil$ odd symbols, each of which must occupy two same-parity slots.
- Splitting $a$ odd-symbol pairs as even-type and $\lceil n/2 \rceil - a$ as odd-type requires $2a = \lceil n/2 \rceil$: **$\lceil n/2 \rceil$ must be even**, i.e. $n \equiv 0$ or $3 \pmod 4$.

Check: $n=4$ → 2 even ✓; $n=7$ → 4 ✓; $n=11$ → 6 ✓; $n=3$ → 2 ✓. Failures: $n=1,2,5,6,9,10$ → $\lceil n/2 \rceil$ odd ✓ (all give zero solutions in the exhaustive search). Skolem's law is the same count with opposite parity pairing, forcing $n \equiv 0,1$; the hook adds one slot and flips the parity, repairing $n \equiv 2,3$ (measured: plain fails and hooked succeeds for $n = 2,3,6,7,10$).

## 4. Algorithm

### 4.1 Exact cover (production route)

Each symbol $k$ contributes a set of candidate tiles $\{i, i+d_k\}$ for $i = 0..2n-1-d_k$. Choosing one tile per symbol with pairwise-disjoint slots and total coverage $2n$ is an **exact cover**: rows = (symbol, start) candidates, columns = the $2n$ slots, plus $n$ "one tile per symbol" secondary columns. Knuth's Algorithm X / dancing links solves it (TAOCP 4A §7.1.1). Since coverage is automatic once $n$ disjoint 2-tiles are placed, the constraint is just "one tile per symbol, no overlap".

### 4.2 Reference implementation sketch

```python
"""generators/langford_pairing.py — LSPC block solver (sketch)."""
from __future__ import annotations
import random

DIST = {"langford": lambda k: k + 1, "skolem": lambda k: k}

def family(n: int) -> str:
    """Which grammar the voice count admits (totality)."""
    if n % 4 in (0, 3):
        return "langford"
    if n % 4 == 1:
        return "skolem"
    return "hooked_skolem"                      # n % 4 == 2

def solve(n: int, fam: str | None = None, seed: int = 0,
          budget: int = 2_000_000) -> tuple[int, ...] | None:
    """Return a slot->symbol tuple of length 2n (+1 hook for hooked_skolem)."""
    fam = fam or family(n)
    hook = fam == "hooked_skolem"
    L = 2 * n + (1 if hook else 0)
    d = DIST["langford" if fam == "langford" else "skolem"]
    rng = random.Random(seed)
    slots = [-1] * L
    nodes = 0

    def rec(k: int) -> bool:
        nonlocal nodes
        nodes += 1
        if nodes > budget or k == 0:
            return k == 0
        step = d(k)
        starts = list(range(0, L - step))
        rng.shuffle(starts)                      # seeded solution choice
        for i in starts:
            if slots[i] < 0 and slots[i + step] < 0:
                slots[i] = slots[i + step] = k
                if rec(k - 1):
                    return True
                slots[i] = slots[i + step] = -1
        return False

    # rec() places symbols largest-first (best pruning); rng.shuffle above is the
    # only stochastic input, so the seed fully determines the chosen solution.
    if not rec(n):
        return None
    return tuple(max(s, 0) for s in slots)        # fill the hook (if any) with 0

def audit(seq, n, fam) -> dict:
    pos: dict[int, list[int]] = {}
    for i, s in enumerate(seq):
        if s > 0:
            pos.setdefault(s, []).append(i)
    d = DIST["langford" if fam == "langford" else "skolem"]
    lags = [pos[k][1] - pos[k][0] for k in range(1, n + 1)]
    cross = sum(1 for a in range(1, n + 1) for b in range(a + 1, n + 1)
                if (pos[a][0] < pos[b][0] < pos[a][1] < pos[b][1])
                or (pos[b][0] < pos[a][0] < pos[b][1] < pos[a][1]))
    return dict(law=all(l == d(k) for k, l in zip(range(1, n + 1), lags)),
                density=sum(1 for s in seq if s) / len(seq),
                lags=lags, crossings=cross, pairs=n * (n - 1) // 2)
```

### 4.3 Matrix fill

```python
from structures import MusicEvent, MusicUnit
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit

def realize(seq, n, slots_per_bar=4, tpb=480, scale=(0,2,4,5,7,9,11,12), root=48):
    bars = len(seq) // slots_per_bar
    sec = slots_per_bar * tpb
    c = UnitMatrixComposer(bpm=120, ticks_per_beat=tpb, beats_per_bar=slots_per_bar)
    c.create_matrix(n, bars)
    for k in range(1, n + 1):
        c.add_voice(f"V{k}", program=12, channel=k - 1)
    for b in range(bars):
        c.add_section(chr(65 + b), bars=1)
    for k in range(1, n + 1):
        for b in range(bars):
            evs = [(i % slots_per_bar) * tpb
                   for i, s in enumerate(seq)
                   if s == k and i // slots_per_bar == b]
            if not evs:
                unit = create_empty_unit(sec)
            else:
                events = [MusicEvent(pitch=root + scale[k - 1], volume=96,
                                     start_tick=o, end_tick=min(o + tpb, sec))
                          for o in evs]
                end = max(e.end_tick for e in events)
                if end < sec:                       # terminal landmark: zero drift
                    events.append(MusicEvent(pitch=0, volume=0,
                                             start_tick=end, end_tick=sec))
                unit = MusicUnit(events=events)
            c.fill_voice_section(f"V{k}", chr(65 + b), unit)
    ok, msg = c.validate()
    assert ok, msg
    return c
```

## 5. Musical reading

- **Voice = symbol.** Each row speaks exactly twice per block; its two onsets are separated by a fixed delay. The row's identity *is* its return time.
- **Complete echo spectrum.** Because every delay class occurs exactly once, the block contains one canon at each lag 2..n+1 simultaneously — a "self-accompanying monophony" whose counterpoint is fully determined by the arithmetic.
- **Perfect hocket.** Density 1.0 means the block has no rests and no doubles: maximum event count with zero reinforcement. Written for percussion or plucked/struck timbres the sequence reads as an interlocking pattern; written for sustained voices it reads as a dense canon.
- **Form from the voice count.** The residue class of $n$ decides Langford / Skolem / hooked; the hook is the block's single mandatory rest (a structural breath). Blocks repeat with transposition (key scheme) or rotation (phase shift, law-preserving).
- **Texture dial.** Interlacing ratio: high = woven counterpoint, low = stratified layers. Since the ratio *falls* with $n$ on arbitrary solutions, choose solutions by crossing count if you want a tangled large ensemble.

## 6. Relation to existing methods

| method | object | how LSPC differs |
|---|---|---|
| 090 GRDC (Golomb ruler) | one set of marks, all pairwise distances distinct | LSPC has *n distinct 2-point tiles*, each used once, differences $\{1..n\}$ — a rainbow pair-tiling |
| 112 CADDC (Costas array) | 2D permutation with distinct displacement vectors | LSPC is 1D, and the permutation is *given* by the distances |
| 111 VTCC (Vuza canon) | one motif, tiled by translates of a set | LSPC's tile vocabulary is n different pairs, each translated exactly once |
| 129 ABGC / 138 HCC | combinatorial structure as form | LSPC's structure is an exact cover with a *provable* total-density invariant |
| 002 Markov / 053 stochastic | probability over next event | LSPC is deterministic given the solution; randomness only picks which solution |

OEIS itself names the Skolem case "super perfect rhythmic tiling of $[0,2n-1]$ with pairs" (A004075) — the correct citation to use when placing LSPC in tiling-canons theory.

## 7. References

1. Langford, C. D. (1958). "Problem" (2781), *Mathematical Gazette* 42(341), 228. doi:10.2307/3610395.
2. Priday, C. J. (1959). "On Langford's Problem I." *Math. Gaz.* 43, 250–255.
3. Davies, R. O. (1959). "On Langford's Problem II." *Math. Gaz.* 43, 253–255.
4. Skolem, T. (1957). "On certain distributions of integers in pairs with given differences." *Math. Scand.* 5, 57–68. doi:10.7146/math.scand.a-10490.
5. O'Keefe, E. S. (1961). "Verallgemeinerung eines Skolemschen Problems." *Math. Scand.*
6. Simpson, J. E. (1983). "Langford sequences: perfect and hooked." *Discrete Math.* 44(1), 97–104. doi:10.1016/0012-365X(83)90008-0.
7. Nordh, G. (2008). "Perfect Skolem sets." *Discrete Math.* 308(9), 1653–1664. arXiv:math/0506155.
8. Knuth, D. E. (2008). *TAOCP* Vol. 4A, §7.1.1 (Langford = exact cover).
9. OEIS A014552, A176127, A004075 (fetched 2026-11-16).
10. Wikipedia, "Langford pairing" (rev. 2026-09-03).
11. Assarpour, A., Bar-Noy, A., Liu, O. (2015). "Counting the Number of Langford Skolem Pairings." arXiv:1507.00315.

## 8. Prototype artifacts

```
_web144_lspc/verify_lspc.py            # existence, counts, audit, symmetries (output: verify_lspc_output.txt)
_web144_lspc/verify_lspc2.py           # Skolem counts vs A004075, hooked repair (output: verify_lspc2_output.txt)
_web144_lspc/verify_lspc3.py           # totality n=1..35, worked pieces, scaling (output: verify_lspc3_output.txt)
_web144_lspc/compose_lspc_demo.py      # engine demo, 8x4 UnitMatrix (output: compose_demo_output.txt)
_web144_lspc/lspc_144_langford8.mid    # 375 B, 16 notes, validate() -> OK
_web144_lspc/lspc_144_demo_report.json # measured demo invariants
```
