# Method 143 — Fokker Periodicity Block Composition (FPBC)

**Layer:** abstract · **Paradigm:** Rules-Based · **Status:** verified prototype (`_web143/verify_143_FPBC.py`, **20/20 checks pass**)
**Summary row added to `methods_db.md`:** yes (line 153) · **Method section appended:** lines 31501–31582 (82 lines)

---

## 1. One-line idea

Composition = **folding a just-intonation prime-factor lattice by its commas**:
choose $n$ unison vectors (near-unison intervals), quotient $\mathbb{Z}^n$ by their
sublattice, and the resulting finite abelian group — the **periodicity block** —
is simultaneously the pitch pool, the scale, the temperament, and the macro-form
cycle: $|\det U|$ notes (12, 19, 31 — Fokker's own organ tuning), each an exact
just ratio, with the block's periodicity making the reprise a theorem and the
comma pump making enharmonic tension measurable.

## 2. Why this is not already in the database

`grep -ic` on `methods_db.md` on 2026-11-15: `fokker` = **2** (both are
*Fokker–Planck equation* prose in 107 SDEC — the diffusion equation, not the
tuning theorist; see Pitfall 1), `unison vector` = **0**, `meantone` = **0**,
`pythagorean` = **0**, `31-et` = **0**, `smith normal` = **0**, `hnf` = **0**,
`temperament` as a method = 0 (13 prose hits); `lattice` = 142 but **every** hit
uses the word as *grid/neighborhood* (064 MRF, 070 CML, 078 Ising, 088 Voronoi);
`periodicity` = 60, all unrelated prose; `microtonal` = 42 prose mentions but
only **one** microtonal method: 131 TDRPC (Partch's tonality diamond).

| Method | What it does | Why FPBC differs |
|---|---|---|
| 131 TDRPC | bounded odd-limit ratio diamond + oto/uto hexads (an identity *pool*) | FPBC is a *lattice quotient* — the block IS the scale and the temperament; no identity rows, no hexads |
| 114 FSBC | unbounded Farey/Stern–Brocot rational tree (rhythm + 12-TET pitch) | no commas, no quotient, no microtonality |
| 025 Sieve | modular congruence sets mod $m$ (Xenakis) | cosets of a *cyclic* $\mathbb{Z}_m$, not quotients by *multi-dimensional* sublattices |
| 069 CWCC | well-formed Christoffel scales (Sturmian step patterns) | related cyclic step patterns, but built by morphisms, not by lattice folding |
| 113 PCFSC | Fourier sets over $\mathbb{Z}_{12}$ | 12-TET fixed; no tuning theory |

**No DB method computes a lattice quotient by unison vectors. FPBC is the DB's
first temperament/periodicity-block method and its second microtonal method.**

## 3. The math

### 3.1 The lattice

Fix a prime limit. 5-limit → the 2-dimensional lattice $\mathbb{Z}^2$ with basis
the perfect fifth $(1,0)$ (ratio $3/2$) and the just major third $(0,1)$
(ratio $5/4$). 7-limit → $\mathbb{Z}^3$ adding the harmonic seventh
$(0,0,1)$ (ratio $7/4$). A point $p=(p_3,p_5,p_7)$ is the octave-reduced ratio

$$r(p) = \mathrm{oct}_2\!\left(3^{p_3}\,5^{p_5}\,7^{p_7}\right)
\in [1,2), \qquad \mathrm{oct}_2(x) = x\,2^{-\lfloor\log_2 x\rfloor}.$$

The 2-axis is the octave-reduction coordinate, not a lattice axis — octave
equivalence is assumed throughout (the source states this explicitly).

### 3.2 Unison vectors and the quotient

A **unison vector** is a lattice interval close to $1$ — a comma. The canonical
ones (all verified in the prototype):

| Comma | Ratio | Lattice vector | Size |
|---|---|---|---|
| syntonic comma | $81/80$ | $(4,-1,0)$ | 21.5 c |
| diesis | $128/125$ | $(0,-3,0)$ | 41.1 c |
| 3125/3072 | $3125/3072$ | $(-1,5,0)$ | 29.6 c |
| septimal kleisma | $225/224$ | $(2,2,-1)$ | 8.0 c |
| 1029/1024 | $1029/1024$ | $(1,0,3)$ | 8.4 c |

Choosing $n$ linearly independent unison vectors $u_1,\dots,u_n$ spans a
sublattice $U=\langle u_i\rangle \subseteq \mathbb{Z}^n$; **identifying pitches
separated by a comma folds the lattice** — the quotient $\mathbb{Z}^n/U$ is a
finite abelian group, and a set of coset representatives is the **periodicity
block** $\mathcal{B}(U)$. The fundamental-domain theorem gives the size:

$$|\mathcal{B}(U)| = |\det U|$$

(the area/volume of the tile spanned by the unison vectors = the number of
lattice points inside it). Verified: $\det\begin{pmatrix}4&-1\\0&-3\end{pmatrix}
=-12$, $\det\begin{pmatrix}4&-1\\-1&5\end{pmatrix}=19$,
$\det\begin{pmatrix}4&-1&0\\2&2&-1\\1&0&3\end{pmatrix}=31$.

### 3.3 Enumerating the block (exact arithmetic)

Wikipedia's membership criterion with origin anchor: $p \in \mathcal{B}(U)$ iff
$\lfloor p \cdot U^{-1} \rfloor = \mathbf{0}$ — the lattice points in the
half-open fundamental parallelepiped $U\cdot[0,1)^n$. With exact `Fraction`
arithmetic (no floats), the prototype enumerates:

- **12-block** (81/80, 128/125): $1/1,\ 27/25,\ 144/125,\ 6/5,\ 32/25,\ 27/20,\
  36/25,\ 192/125,\ 8/5,\ 216/125,\ 9/5,\ 48/25$ — 12 unique ratios, sorted step
  pattern **$[133.2, 111.7, 70.7, 111.7, 92.2, 111.7, 111.7, 70.7, 133.2, 70.7,
  111.7, 70.7]$ cents** (an *unequal* chromatic — the justness of the
  temperament lives in those inequalities).
- **19-block** (81/80, 3125/3072): 19 unique ratios.
- **31-block** (81/80, 225/224, 1029/1024): 31 unique ratios — Fokker's organ.

The standard 5-limit chromatic $\{1/1, 16/15, 9/8, 6/5, 5/4, 4/3, 45/32, 3/2,
8/5, 5/3, 16/9, 15/8\}$ is a *different transversal of the same quotient* — both
transversals verified to map bijectively onto the 12 pcs of 12-ET (Pitfall 2:
block content is anchor-dependent).

### 3.4 Cyclicity — the tuning map is the quotient map

The equal-temperament mapping $\varphi:\mathbb{Z}^n\to\mathbb{Z}_m$,
$\varphi(p)=\sum_i p_i \lfloor m\log_2(\text{prime}_i)\rceil \bmod m$
(e.g. 12-ET: $19a+28b \bmod 12$; 31-ET: $49a+72b+87c \bmod 31$) is the quotient
map when $U=\ker\varphi$. Verified for all three blocks:

1. every unison vector lies in $\ker\varphi$;
2. the $m$ block members map bijectively onto $\mathbb{Z}_m$.

Both subgroups have index $m$, so $U=\ker\varphi$ and
$\mathbb{Z}^n/U \cong \mathbb{Z}_m$ — **cyclic**. (Sanity: gcd of all
unison-vector entries $=1$, i.e. the Smith-normal-form invariant $d_1=1$; a
non-cyclic quotient like $\mathbb{Z}_2\oplus\mathbb{Z}_6$ is possible with bad
commas — Pitfall 7.) This is exactly the source's claim: "identifying the $m$
pitches of the periodicity block with $m$-equal tuning gives equal tuning
approximations of the just ratios."

### 3.5 Periodicity and the comma pump

Because $U\subseteq\ker\varphi$, translating the block by any unison vector
returns the *identical tempered pc set* (verified: $\mathcal{B}+(4,-1)$ has pc
set $\{0..11\}$ exactly) — the block tiles the lattice, and the reprise is a
theorem (the same conservative-dynamics logic as 141 ACMTPC's cat-map period).
But the *just ratios* drift: $\mathcal{B}+(4,-1)$ shares **0** exact ratios
with $\mathcal{B}$ — every ratio multiplies by $81/80$ (21.5 c). That is the
**comma pump**: enharmonic equivalence in the temperament, real drift in just
intonation. Walking a section through the block's group structure accumulates
microtonal tension that resolves when the pump closes on the unison.

### 3.6 Modulation = non-unison transposition

Transposing by a non-unison lattice vector is a genuine modulation. Measured
seams on the 12-block (exact-ratio overlap between $\mathcal{B}$ and
$\mathcal{B}+t$):

| $t$ | Interval | Common exact ratios |
|---|---|---|
| $(1,0)$ | perfect fifth $3/2$ | 8/12 |
| $(0,1)$ | major third $5/4$ | 8/12 |
| $(1,1)$ | $15/8$ | 5/12 |

The overlap is the concrete layer's common-tone voice-leading material.

## 4. Verified results (2026-11-15, `_web143/verify_143_FPBC.py`, log `verify_143_output.txt`)

**20/20 checks pass** (exact `Fraction` arithmetic throughout):

| # | Check | Result |
|---|---|---|
| 1 | 12-block: $\|\det U\|=12$ | det $=-12$ ✓ |
| 2 | 12-block: 12 lattice points | count $=12$ ✓ |
| 3 | 12-block: 12 unique octave-reduced ratios | unique $=12$ ✓ |
| 4 | all ratios in $[1,2)$ (0 c = 1/1, max 1129.3 c) | ✓ |
| 5 | standard 5-limit chromatic is a transversal (12 distinct cosets) | pcs $=\{0..11\}$ ✓ |
| 6 | 12-ET pcs all distinct | $\{0..11\}$ ✓ |
| 7 | periodicity: $\mathcal{B}+81/80$ has identical pc set | ✓ |
| 8 | constant structure (Wilson): ratio → unique step count | ✓ |
| 9 | 19-block: $\|\det U\|=19$ | ✓ |
| 10 | 19-block: 19 lattice points | ✓ |
| 11 | 19-ET pcs all distinct | ✓ |
| 12 | 31-block: $\|\det U\|=31$ | ✓ |
| 13 | 31-block: 31 lattice points | ✓ |
| 14 | 31-block: 31 unique ratios | ✓ |
| 15 | 31-ET pcs all distinct (Fokker organ) | ✓ |
| 16 | cyclic: 12-block $U=\ker\varphi$, bijects onto $\mathbb{Z}_{12}$ | ✓ |
| 17 | cyclic: 19-block bijects onto $\mathbb{Z}_{19}$ | ✓ |
| 18 | cyclic: 31-block bijects onto $\mathbb{Z}_{31}$ | ✓ |
| 19 | modulation by non-unison vector changes the ratio set | 5/12 common ratios ✓ |
| 20 | unison-vector transposition = comma pump (81/80 shift) | 0 shared ratios; 21.5 c ✓ |

Step pattern (measured): $[133.2, 111.7, 70.7, 111.7, 92.2, 111.7, 111.7, 70.7,
133.2, 70.7, 111.7, 70.7]$ cents.

## 5. Python implementation sketch (`rules/fokker_blocks.py`, abstract layer)

```python
from fractions import Fraction as F

class PrimeLattice:
    """Z^n with basis primes; point p -> octave-reduced just ratio."""
    def __init__(self, primes=(3, 5)): self.primes = primes
    def ratio_of(self, p):
        r = F(1)
        for a, q in zip(p, self.primes): r *= F(q) ** a
        while r >= 2: r /= 2
        while r < 1:  r *= 2
        return r
    def cents(self, r): return 1200.0 * (r.numerator.bit_length() - r.denominator.bit_length())  # approx; use math.log2

def inv_matrix(U):
    """Exact inverse of an n x n integer matrix via Gauss-Jordan on Fractions."""
    n = len(U)
    A = [[F(x) for x in row] for row in U]
    aug = [row[:] + [F(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = next(r for r in range(col, n) if aug[r][col])
        aug[col], aug[piv] = aug[piv], aug[col]
        pv = aug[col][col]; aug[col] = [x / pv for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col]:
                f = aug[r][col]; aug[r] = [a - f * b for a, b in zip(aug[r], aug[col])]
    return [[row[n + j] for j in range(n)] for row in aug]

class FokkerBlock:
    """The periodicity block: coset representatives of Z^n / U."""
    def __init__(self, U, box=10):
        self.U = U; self.n = len(U); self.Uinv = inv_matrix(U)
        self.pts = self._enumerate(box)
        assert len(self.pts) == abs(self._det(U)), "|det| mismatch"
    def _det(self, U):  # 2x2 / 3x3 only (n <= 3)
        if self.n == 2: return U[0][0]*U[1][1] - U[0][1]*U[1][0]
        a,b,c = U[0]; d,e,f = U[1]; g,h,i = U[2]
        return a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)
    def _enumerate(self, box):
        from itertools import product
        pts = []
        for p in product(*[range(-box, box+1)] * self.n):
            q = [sum(F(p[i]) * self.Uinv[i][j] for i in range(self.n)) for j in range(self.n)]
            if all(x.numerator // x.denominator == 0 for x in q):  # floor == 0
                pts.append(p)
        return pts
    def et_pcs(self, step_map):
        """step_map = [m, s3, s5, ...]; pc = sum(p_i*s_i) mod m."""
        m = step_map[0]
        return sorted({sum(a*s for a, s in zip(p, step_map[1:])) % m for p in self.pts})

# The three verified blocks
B12 = FokkerBlock([[4,-1],[0,-3]])        # 81/80 + 128/125      -> 12-ET
B19 = FokkerBlock([[4,-1],[-1,5]])        # 81/80 + 3125/3072    -> 19-ET
B31 = FokkerBlock([[4,-1,0],[2,2,-1],[1,0,3]], box=10)  # 81/80+225/224+1029/1024 -> 31-ET
assert B12.et_pcs([12,19,28]) == list(range(12))
assert B19.et_pcs([19,30,44]) == list(range(19))
assert B31.et_pcs([31,49,72,87]) == list(range(31))
```

Concrete feeder (future, `generators/fokker_block_realize.py`): map each block
ratio to MIDI pitch + pitch-bend (or a just renderer), snap block members to
scale-degree roles per voice, fill cells via `create_note_unit` /
`_unit_from_events`, gate with `validate()` — the abstract plan emits no events,
so it cannot drift.

## 6. UnitMatrix mapping

- **Voices = rows = block layers**: bass takes low block members, lead walks the
  sorted step pattern, pad holds a transposed copy; register = per-voice octave
  placement; seam obligations = common-tone ratio sets (Pitfall 3 in the DB
  section: ratios, not semitones).
- **Sections = columns = block regions**: column $j$ = (limit, unison-vector
  set $U_j$, transposition $t_j$, register); transposition sequence = key
  scheme; comma-pump count per column = tension curve; a change of $U_j$ = a
  temperament change (macro-form event).
- **Cells = MusicUnit (abstract form)**: ratio subset + role labels + seam
  obligations per $(v,j)$.

## 7. References

1. Wikipedia, "Fokker periodicity block" (rev. 2025-10-18; fetched 2026-11-15,
   cached `_web143/74025fbe.bin`).
2. Fokker, A. D. (1969). "Unison vectors and periodicity blocks in the
   three-dimensional (3-5-7-)harmonic lattice of notes." *Proc. Koninklijke
   Nederlandsche Akademie van Wetenschappen* B72(3).
3. Erlich, P. (1999). "A Gentle Introduction to Fokker Periodicity Blocks."
4. Wikipedia, "Adriaan Fokker" (fetched 2026-11-15, cached
   `_web143/wiki_fokker.html`).
5. Wikipedia, "31 equal temperament" (fetched 2026-11-15, cached
   `_web143/ceb86da1.bin`).
6. Wilson, E. — "constant structures" (via the FPB article: "each interval
   occurs always subtended by the same number of steps").
