# Method 132 — Balanced Incomplete Block Design Composition (BIBDC)

**Paradigm:** Rules-Based
**Layer:** concrete (emits per-cell `MusicUnit` content; feeds `generators/`)
**One-liner:** the piece's ensemble schedule *is* a 2-$(v,k,\lambda)$ block design — voices are points, sections are blocks, every pair of voices sounds together in exactly $\lambda$ sections.
**Registered:** 2026-11-02 · **DB lines:** 29 524 → 29 613 (+89)
**Verification scripts:** `verify_132_BIBDC.py`, `verify_132b_kirkman.py`, `bibdc_sketch.py`

---

## 1. The object

A **balanced incomplete block design** (BIBD) 2-$(v,k,\lambda)$ is a $v$-element point set $\mathcal{P}$ together with $b$ blocks $B_1,\dots,B_b\subseteq\mathcal{P}$, $|B_m|=k$, such that every 2-subset of $\mathcal{P}$ is contained in exactly $\lambda$ blocks.

Two counting identities follow by double-counting incidences $(i,m)$ with $i\in B_m$, and pairs-through-a-point:

$$v\,r \;=\; b\,k, \qquad \lambda\,(v-1) \;=\; r\,(k-1), \qquad r=\frac{\lambda(v-1)}{k-1},\qquad b=\frac{v\,r}{k}=\frac{\lambda\,v(v-1)}{k(k-1)} .$$

**"Incomplete"** means $b<\binom{v}{k}$: only a vanishing fraction of all possible $k$-voice ensembles is ever used ($\lambda=1,k=3,v=7$: 7 of the 35 possible trios).

**Economy theorem.** For $\lambda=1$ the design is a *minimum* pair cover: $b_{\min}=v(v-1)/(k(k-1))$. With $k=3$ this is the **Steiner triple system** (STS), $b=v(v-1)/6$.

**Existence (STS).** A triple system S(2,3,$v$) exists **iff** $v\equiv1$ or $3 \pmod 6$ (necessity: $3\mid v(v-1)$ from $3\mid b\cdot 6$ and $v-1$ even from the degree count; sufficiency: Bose 1939 / Skolem 1957). Admissible $v\le19$: 7, 9, 13, 15, 19.

**Classification (STS).** Up to isomorphism: STS(7) unique (Fano plane), STS(9) unique (affine plane $AG(2,3)$), two STS(13), **80** STS(15), 11 084 874 829 STS(19).

**Resolvability.** A **parallel class** is a set of $v/k$ pairwise disjoint blocks covering $\mathcal{P}$. A design that partitions into $(v-1)/2$ parallel classes is **resolvable** = a **Kirkman triple system**. Resolvable STS($v$) exists **iff** $v\equiv3\pmod 6$ (Ray-Chaudhuri & Wilson 1971) — but resolvability is a property of the *individual design*, not of the order (see §6, Pitfall 2).

**Dual.** Transposing the incidence matrix $M\in\{0,1\}^{v\times b}$ gives a design with parameters $(b,\,v,\,k,\,r,\,\lambda)$. Self-dual iff $v=b$ (symmetric design), e.g. STS(7) where $r=k=3$.

**Automorphism.** The Fano plane's automorphism group is $\mathrm{PSL}(2,7)$ of order 168; verified independently here by exhaustive enumeration: the number of **labelled** STS(7) is 30 $=7!/168$. So one schedule admits 168 distinct voice assignments.

---

## 2. Musical mapping

| Design object | Musical object | UnitMatrix |
|---|---|---|
| point $i$ | voice / instrument / timbre | row |
| block $B_m$ | section: the exact set of voices sounding | column |
| incidence $i\in B_m$ | voice $i$ plays in section $m$ | sounding cell |
| non-incidence | voice rests through the section | **padded** rest cell |
| $k$ | chord size = voice count per section | sounding cells per column |
| $r$ | number of sections each voice plays | sounding cells per row |
| $\lambda$ | how often each duo meets | pair-coverage constant |
| block order | the form (free — balance is order-independent) | column permutation |
| parallel class | movement: ensemble split into simultaneous groups | column group |
| dual design | voices↔sections swapped | matrix transpose |

### The four laws BIBDC buys you

1. **Fairness.** Every voice gets exactly $r$ sections; every section exactly $k$ voices. Constant ensemble density $k/v$.
2. **Economy.** If every duo must meet, $b_{\min}=v(v-1)/(k(k-1))$ blocks suffice and are all used — no wasted section.
3. **Provable closure.** Each block introduces exactly $\binom{k}{2}$ pairs, so unmet-pair count
   $$N_m=\binom{v}{2}-m\binom{k}{2}$$
   for $\lambda=1$ (after $m$ blocks, any order) — monotone decreasing, hitting $0$ exactly at the last block. An *order-independent* tension curve. Verified (Fano): 18, 15, 12, 9, 6, 3, 0 forward **and** reversed.
4. **Exact seams.** In STS(7) every two blocks intersect in exactly one point (verified: $|B_i\cap B_j|=1$ for all $\binom{7}{2}=21$ block pairs) ⇒ every chord change is a **single-common-tone** move, the maximally parsimonious connection.

Proof of the last: blocks are 3-subsets of a 7-set, so intersection $\ge 3+3-7=-1$ … more directly, count: $\sum_{i<j}|B_i\cap B_j|=\sum_{x}\binom{r_x}{2}=7\binom{3}{2}=21$ equals the number $\binom{7}{2}=21$ of block pairs, so every intersection is exactly 1.

---

## 3. Verified numbers (2026-11-02)

| check | result |
|---|---|
| Fano STS(7): $b$, $r$, pairs | 7, 3, 21 — all pairs once, all degrees 3 ✔ |
| STS(9) / 13 / 15 via backtracking | $b=12/26/35$, $r=4/6/7$, all pairs once ✔ |
| STS(7) block-pair intersections | all 21 pairs $=1$ ✔ |
| STS(7) novelty curve | 18,15,12,9,6,3,0 (forward = reversed) ✔ |
| $AG(2,3)$ resolvable | 4 parallel classes × 3 trios ✔ |
| STS(15) resolvable | constructed, 7 classes × 5 trios, 105 pairs once ✔ (found on random attempt 24; heuristic STS(15)s are typically *not* resolvable) |
| STS(13) resolvable | **None** — consistent with $v\not\equiv3\pmod6$ ✔ |
| labelled STS(7) | 30 $=7!/168$ ⇒ $|\mathrm{Aut}|=168$ ✔ |
| counting identities | $vr=bk$, $\lambda(v-1)=r(k-1)$ for $(7,3,1),(9,3,1),(13,3,1),(15,3,1),(7,3,2),(9,4,3),(6,3,2)$ ✔ |
| cell plan (49 cells) | 21 sounding, 3 per row, 3 per column ✔ |

---

## 4. Implementation sketch (tested)

```python
import itertools
from collections import Counter

class BIBD:
    def __init__(self, v, k, lam, blocks):
        self.v, self.k, self.lam = v, k, lam
        self.blocks = [tuple(sorted(b)) for b in blocks]
        self.b = len(self.blocks)
        self.r = lam * (v - 1) // (k - 1)

    def audit(self):                      # invariants: pairs == lam, degree == r
        pairs, deg = Counter(), Counter()
        for B in self.blocks:
            for x in B:
                deg[x] += 1
            for p in itertools.combinations(B, 2):
                pairs[p] += 1
        ok = (all(pairs[p] == self.lam for p in itertools.combinations(range(self.v), 2))
              and all(deg[x] == self.r for x in range(self.v))
              and self.v * self.r == self.b * self.k)
        return ok, dict(b=self.b, r=self.r, n_pairs=len(pairs))

    def se(self, i, j):                   # seam common tones
        return sorted(set(self.blocks[i]) & set(self.blocks[j]))

    def novelty_curve(self, order=None):
        order = order if order is not None else range(self.b)
        seen, curve = set(), []
        for m in order:
            for p in itertools.combinations(self.blocks[m], 2):
                seen.add(p)
            curve.append(self.v * (self.v - 1) // 2 - len(seen))
        return curve

    def dual(self):
        inc = [[i in B for B in self.blocks] for i in range(self.v)]
        return BIBD(self.b, self.r, self.lam,
                    [tuple(i for i in range(self.v) if inc[i][j]) for j in range(self.b)])

    def resolve(self):                    # parallel classes, or None (the usual case)
        used = [False] * self.b; classes = []
        def rec():
            free = [i for i in range(self.b) if not used[i]]
            if not free:
                return True
            i = free[0]; used[i] = True
            cls, cover = [i], set(self.blocks[i])
            def extend():
                if len(cover) == self.v:
                    classes.append(list(cls))
                    if rec(): return True
                    classes.pop(); return False
                for j in range(self.b):
                    if used[j] or (cover & set(self.blocks[j])): continue
                    used[j] = True; cls.append(j); cover.update(self.blocks[j])
                    if extend(): return True
                    cover.difference_update(self.blocks[j]); cls.pop(); used[j] = False
                return False
            if extend(): return True
            used[i] = False; return False
        return classes if rec() else None

FANO = BIBD(7, 3, 1, [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)])
# FANO.audit() -> (True, {'b': 7, 'r': 3, 'n_pairs': 21})
# FANO.novelty_curve() -> [18, 15, 12, 9, 6, 3, 0]
# FANO.dual().blocks == FANO.blocks -> True   (symmetric design)

SEATS = [0, 2, 4, 5, 7, 9, 11]
LADDER = [0, 12, 7, 19, 14, 5, 24]

def cell_plan(design, section_ticks=1920, subdiv=4):
    step = section_ticks // subdiv
    plan = {(i, m): [] for m in range(design.b) for i in range(design.v)}
    for m, B in enumerate(design.blocks):
        for j, i in enumerate(B):
            pitch = 60 + SEATS[i] + LADDER[m % len(LADDER)]
            plan[(i, m)] = [(pitch, j * step, step * (subdiv - j))]
    return plan        # empty list => rest cell, must still be padded to section_ticks
```

musicom fill (the only sanctioned workflow):

```python
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
from structures import MidiInstrument

def render(design, out, bpm=96, bars_per_section=4):
    section_len = 4 * bars_per_section * 480          # BAR = 1920 ticks
    c = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    c.create_matrix(num_voices=design.v, num_sections=design.b)
    for i in range(design.v):
        c.add_voice(f"V{i}", program=MidiInstrument.values[i], channel=i if i != 9 else 10)
    for m in range(design.b):
        c.add_section(f"S{m}", bars=bars_per_section)
    plan = cell_plan(design, section_ticks=section_len)
    for (i, m), evs in plan.items():
        if evs:
            p, st, dur = evs[0]
            c.fill_voice_section(f"V{i}", f"S{m}", create_note_unit(p, dur, start=st))
        else:
            c.fill_voice_section(f"V{i}", f"S{m}", create_note_unit(0, 0))  # padded rest
    ok, msg = c.validate()          # MUST be True (zero drift)
    assert ok, msg
    c.to_midi(out)
```

**Complexity.** Bose construction of STS($v$): $\mathcal{O}(v^2)$. Generic backtracking: fast in practice (8–75 search nodes for $v=7..15$ measured). Pair audit $\mathcal{O}(v^2)$. Event emission $\mathcal{O}(bk)$ = $\mathcal{O}(v^3)$ worst case, trivially small.

**Bose construction** (for $v=6t+3$): points $\mathbb{Z}_{2t+1}\times\{0,1,2\}$; blocks $\{(x,0),(x,1),(x,2)\}$ and, for each $x$ and each $j=1..t$, $\{(x,0),(x+j,1),(x+2j,2)\}$ with arithmetic mod $2t+1$ (with the sign convention that each unordered pair is produced once). For $v=6t+1$ use Skolem sequences. If in doubt, backtrack — the search is cheap.

---

## 5. Arrangement notes (practical)

- **Fano consort (7 voices, 7 sections, trios).** Each player sounds in 3 of 7 sections; every duo shares exactly one section; adjacent sections share exactly one player (a "relay" line). Excellent for antiphonal chamber writing where the *personnel* is the form.
- **AG(2,3) quartet (9 voices, 12 sections).** Not symmetric: $b=12$, $k=3$, $r=4$. Resolvable into 4 movements of 3 simultaneous trios — each movement is a tutti partition (all 9 players, three subgroups), and every duo meets exactly once across the 4 movements.
- **Schoolgirl set (15 voices, 35 sections).** The textural extreme: 7 movements of 5 trios; at any instant 3 of 15 sound. Ideal as a "society" piece, or as an orchestration generator for a 15-player ensemble where the schedule is the composition.
- **$\lambda=2$ (14 sections of 3, 7 voices):** statement-and-recapitulation at the pair level — each duo meets twice, once in each half, so memorability doubles.
- **Seat ladder.** Fixed seats make each voice a pedal. Displace by `LADDER[m]` (block ordinal) to get contour; keep displacements small (0, 5, 7, 12, 14, 19) so the harmony stays a recognisable family.
- **Rest cells.** 4/7 of a Fano matrix is silence. Score them explicitly; they are where the ear hears the rotation.

---

## 6. Pitfalls

1. **Admissibility.** $v\equiv1,3\pmod6$ only. Pad with silent dummy voices (8 players → design on 9), or use $\lambda\ge2$, or change $k$.
2. **Resolvability is per-design.** Measured here: a heuristic STS(15) had no parallelism at all; a resolvable one appeared on the 24th random construction. Build a Kirkman system deliberately and *test* the resolution.
3. **Zero drift.** Rest cells must be padded to `section_len`; 57% of a Fano grid is rests, so this is the default case, not an edge case.
4. **$k$ caps chord size.** Fixed-$k$ designs give fixed-size sonorities. Doubling voices changes effective $\lambda$ — recompute and report it.
5. **$\lambda=1$ refuses repetition.** Pair novelty ends at 0 and never returns; hooks need $\lambda=2$ or repeated blocks (with the pair audit updated).
6. **The design gives content, not form.** Any block order is equally balanced, so order must be chosen musically; the novelty curve cannot tell you the shape.
7. **Self-duality is conditional** ($v=b$).
8. **Automorphism $\ne$ transposition.** 168 relabelings are orchestrations, not key changes.
9. **No disjoint blocks in STS(7)** — complements are tacet sets of 4, never blocks.
10. **Don't file it under "more combinatorics".** The balanced object is *pairwise co-incidence between voices*, not within-set differences (090 GRDC, 112 CADDC), not space partitions (083 QTSC, 111 VTCC), not incentives (123 GTBRC).

---

## 7. References

- Kirkman, T. P. (1847). "On a problem in combinatorics." *Cambridge and Dublin Mathematical Journal* 2, 191–204.
- Kirkman, T. P. (1850). Query VI. *The Lady's and Gentleman's Diary*, 48.
- Steiner, J. (1853). "Combinatorische Aufgabe." *J. reine angew. Math.* 45, 181–182.
- Cole, F. N. (1922). "Kirkman parades." *Bull. Amer. Math. Soc.* 28, 435–437.
- Bose, R. C. (1939). "On the construction of balanced incomplete block designs." *Ann. Eugenics* 9, 353–399.
- Skolem, T. (1957). "On certain distributions of integers in pairs with given differences." *Math. Scand.* 5, 57–68.
- Ray-Chaudhuri, D. K., & Wilson, R. M. (1971). "Solution of the Kirkman schoolgirl problem." *Proc. Amer. Math. Soc.* 28, 115–124.
- Beth, T., Jungnickel, D., & Lenz, H. (1999). *Design Theory* (2nd ed.). Cambridge UP.
- Colbourn, C. J., & Dinitz, J. H., eds. (2006). *Handbook of Combinatorial Designs* (2nd ed.). Chapman & Hall/CRC.
- Stinson, D. R. (2003). *Combinatorial Designs: Constructions and Analysis*. Springer.
- Wikipedia: "Steiner system", "Block design", "Kirkman's schoolgirl problem" (fetched 2026-11-02; extracts cached in `_web132/`).
