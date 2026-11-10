# Method 139 — Latin Square & Orthogonal-Array Composition (LSAC)

**Paradigm:** Rules-Based · **Layer:** abstract · **Registered:** 2026-11-10
**Candidate code path:** `rules/subset_network.py` (`LatinSquare`, `GraecoLatinPair`, `MOLSField`, `SudokuGrid`, `SDRCompletion`, `TransversalSearch`, `TensionOrder`, `LSACPlan.to_design`); concrete feeder later: `generators/latin_square.py`
**Prototype:** `_web139/verify_139_LSAC.py` (runs on the musicom python; log `_web139/verify_139_output.txt`; **29 checks, all pass**)

---

## 1. The idea in one line

Lay the piece out as a **Latin square (or Latin rectangle / orthogonal array / Sudoku grid) over the UnitMatrix** — rows = voices, columns = sections, symbols = pitch classes — so that **every voice and every section is a complete aggregate**, an orthogonal second square makes the piece a **complete factorial design** (every $(pc \times \mathrm{attribute})$ pair exactly once), and the 240-year-old existence theorems of Euler / Hall / Tarry / Bose–Shrikhande–Parker hand you the tension curve for free.

## 2. The combinatorics

**Latin squares (Euler 1782; Choi Seok-jeong 1700).** An $n{\times}n$ array over $n$ symbols, each occurring exactly once per row and per column. Euler founded the theory in "Recherches sur une nouvelle espèce de quarrés magiques" (1782), naming the arrays for his Latin-alphabet symbols; Choi Seok-jeong had already published order-9 orthogonal Latin squares in his *Gusuryak* (~1700), built to make a magic square summing to 369. Every group table is a Latin square; the **cyclic square** $L(i,j)=(ai+bj)\bmod n$ is Latin iff $\gcd(a,n)=\gcd(b,n)=1$.

**Counting.** Reduced squares (OEIS A000315): $1, 1, 1, 4, 56, 9408, 16942080, 535281401856, 377597570964258816$ for $n=1..9$; totals $L(n)=n!(n{-}1)!\,R(n)$ (A002860): $L(9)\approx 5.52{\times}10^{27}$, $L(12)\approx 1.62{\times}10^{44}$. Isotopy classes (row/column/symbol permutations): $1,1,1,2,2,22,564,1676267,115618721533$; main (paratopy) classes: $1,1,1,2,2,12,147,283657,19270853541$ (McKay–Meynert–Myrvold 2007). The form space is astronomical but *classifiable* — a composer's freedom is bounded by a taxonomy.

**Orthogonality (Graeco-Latin squares; Euler's 36 officers).** Two order-$n$ Latin squares are **orthogonal** when the $n^2$ ordered cell pairs are all distinct. Euler posed the *36 officers problem* (6 regiments × 6 ranks in a $6{\times}6$ grid, each line one of each) in 1779 and conjectured no pair exists for $n\equiv2\pmod4$. Resolution: **Tarry (1901)** proved order 6 impossible; **Bose–Shrikhande–Parker (1959)** built counterexamples for $n=10$ (Parker, one hour on a UNIVAC — among the first combinatorics problems solved by computer; *Scientific American*, Nov 1959 cover) and all $n\ge10$: **orthogonal pairs exist for every $n>1$ except $2$ and $6$**.

**MOLS and orthogonal arrays (Rao 1947).** A set of $k$ pairwise-orthogonal squares = **MOLS($n$)**; at most $n-1$ exist, and $n-1$ of them (a *complete* set) exist iff $n$ is a prime power (finite-field construction) — equivalently an affine plane of order $n$, equivalently an orthogonal array $\mathrm{OA}(n^2, n{+}1, n, 2)$: an $n^2\times(n{+}1)$ table where every pair of columns carries each ordered pair of symbols exactly once (Rao's design-of-experiments formalism; "Hyper-Graeco-Latin" designs in the statistics literature). For non-prime-power orders the count of MOLS is a research problem; order 10 has no complete set (no order-10 plane; Lam 1991). Musically: at prime-power orders you get **up to $n{+}1$ mutually balanced attribute dimensions**.

**Sudoku (order 9 + boxes).** A Sudoku grid is an order-9 Latin square with the 3×3 box rule. Grid count $6{,}670{,}903{,}752{,}021{,}072{,}936{,}960$ (Felgenhauer–Jarvis 2005); $5{,}472{,}730{,}538$ essentially different (Russell–Jarvis 2006); the minimum clue set forcing a unique solution is **17** (McGuire–Tugemann–Civario 2012, exhaustive proof). Solving $n^2\times n^2$ Sudoku is NP-complete (Yato & Seta 2003); practical MRV backtracking handles 9×9 in milliseconds (verified).

**Feasibility: Hall's marriage theorem (1935).** A partial assignment of symbols extends to a full Latin square iff a system-of-distinct-representatives condition holds for every row/column demand set. Consequences: **every Latin rectangle completes to a Latin square** (add rows, Hall-guaranteed; verified 3×9→9×9); **any partial square with $\le n-1$ filled cells always completes** (verified 3× with 8 cells of order 9); general completion is **NP-complete** (Colbourn 1984).

**Transversals (rainbow matchings).** A transversal = $n$ cells, one per row, column, and symbol: a thread through the whole design. **Ryser's conjecture (1967):** every odd-order Latin square has a transversal (verified: cyclic order 5). The cyclic square $(i{+}j)\bmod n$ of **even** order has none (verified orders 6, 8). Guaranteed *partial* transversals: size $\ge 2n/3$ (Koksma 1969), $\ge n-\sqrt n$ (Woolbright 1978), $\ge n-11\log_2^2 n$, $\ge n-O(\log n/\log\log n)$ (Hatami–Shor 2008; verified order-8: size 7 = $n-1$).

**Sampling & complexity.** Jacobson–Matthews (1996): a Markov chain on "almost-Latin" arrays that is irreducible over all order-$n$ squares — the uniform sampler. Quick-but-biased alternative: randomized row extension (verified: 50/50 valid, diverse). Storage $\mathcal{O}(n^2)$; the JM chain mixes polynomially (practical burn-in thousands of steps); construction is deterministic per seed.

## 3. The musical mapping

| Design object | Musical reading |
|---|---|
| rows = voices, columns = sections | the UnitMatrix itself — the design *is* the form map |
| symbol set | pitch classes / scale degrees of the piece |
| row = permutation | every voice is an aggregate: one of each pc over the cycle (a twelve-tone "row" in set sense, unordered) |
| column = permutation | every section is a complete aggregate chord (12-pc column = dodecaphonic harmony) |
| Latin rectangle $r{\times}n$ | non-square UnitMatrix: $r$ voices each a permutation; each section an $r$-pc chord, no pc repeated within the section |
| Graeco-Latin mate (2nd square) | a second attribute domain (duration class / articulation / velocity class); **every $(pc\times\mathrm{attr})$ pair exactly once** — a complete factorial design |
| MOLS set / OA($n^2,n{+}1,n,2$) | up to $n{+}1$ mutually balanced musical attributes (pc, duration, articulation, register, density…) at prime-power orders |
| Sudoku 3×3 boxes | phrase-level aggregates: every 3-voice×3-section block is also complete — three-level hierarchical completeness |
| 17-clue minimum | the provably most economical compositional skeleton that still determines the piece uniquely |
| Hall/SDR completion | the *feasibility theorem* for skeleton-first writing: any Latin rectangle / $\le n-1$ cells complete |
| transversal (rainbow matching) | a through-composed thread: one note per voice, section, and pc — a melody spanning the whole design |
| Ryser / even-cyclic no-transversal | odd orders guarantee a thread; even cyclic squares forbid one (thread-less = tension device) |
| isotopy (row/col/symbol perms) | re-voicing / re-ordering sections / transposition — design-preserving transformations |
| paratopy (conjugate) | form rotation: sections↔voices↔symbols (rotate the piece 90°) |
| reduced-square / isotopy-class counts | "how many structurally different pieces of order $n$ exist" — the form taxonomy |
| prime-power order | HOME: complete MOLS = full attribute balance, maximal evenness of co-occurrence |
| order 6 (Tarry) / order 2 | TENSE: no orthogonal mate exists — structural impossibility as tension |
| order 10 (Bose–Shrikhande–Parker) | LIFT: a mate exists but no complete set (no order-10 plane, Lam 1991) — partial balance, the Eulerian surprise |
| Jacobson–Matthews chain | uniform sampling over the whole design space (seeded; the stochastic option of a Rules-Based method) |

## 4. Musical Elements Framework

- **PITCH**: symbols = pitch classes; row = voice's aggregate pc-plan; column = section's simultaneity set; isotopy symbol-renaming = transposition (fix pc 0 = tonic or plan the key scheme); pc→pitch resolution (scale map + register ladder) delegated to the concrete layer.
- **RHYTHM**: second (Graeco-Latin) square = duration classes; every $(pc, \mathrm{dur})$ pair exactly once — rhythmic variety exhausted by the design budget; per-cell duration class → archetype (Euclidean pattern / arpeggio / sustain) in the concrete layer; Sudoku boxes balance duration classes per phrase; transversal steps = one-note-per-cell thread rate.
- **HARMONY**: columns = chord sets ($n=12$: twelve-pc aggregate columns; $r{\times}n$ rectangle: $r$-note chords); orthogonality = "no repeated combined pair" law; MOLS columns = $n{+}1$ mutually balanced harmonic dimensions; the Eulerian-order taxonomy IS the tension curve.
- **STRUCTURE**: the design is the macro-form ($n$ sections × $n$ voices); Sudoku boxes = phrase grouping; transversals = through-composed arcs; isotopy = re-voicing/re-order/re-key; paratopy = form rotation; class counts = form space taxonomy.
- **TEXTURE**: extra OA columns carry articulation/register/density classes, mutually balanced; row/column orthogonality = voice independence by construction (no shared pc inside a column); aggregate columns force full-spectrum density per section.

## 5. UnitMatrix Integration (Voices & Sections)

**Voices = rows.** Row $v$ = voice $v$'s aggregate plan (a pc-permutation over the $n$ sections). In an $r{\times}n$ rectangle, $r$ voices each hold a permutation (4×12: four aggregate melodies, 4-pc section chords). Voice independence = orthogonality: no two voices share a pc in any section.

**Sections = columns.** Column $j$ = section $j$'s simultaneity set (the harmonic content); the column sequence = the progression; Sudoku boxes group sections into aggregate-complete phrases; column order is an isotopy parameter (reordering is legitimate surgery).

**Cells = MusicUnit.** The abstract plan fixes each cell's pc (from $L_1$) and attribute class (from $L_2$/OA columns). The concrete feeder resolves pc→pitch in the voice's register, attribute class→rhythmic archetype + velocity/articulation, pads to `section_len` via `_unit_from_events`, then the standard `UnitMatrixComposer` spine → `validate()` (zero-drift gate) → `to_midi()`. Verified plan: the 9×9 Sudoku design (9 voices × 9 sections; every row/column/3×3-box a complete 9-pc set over the nonatonic $\{0,2,4,5,7,9,11,1,3\}$).

## 6. Implementation sketch (runs on the musicom python — `_web139/verify_139_LSAC.py`)

```python
import random, itertools

def cyclic(n, a=1, b=1):                       # Latin iff gcd(a,n)=gcd(b,n)=1
    return [[(a*i + b*j) % n for j in range(n)] for i in range(n)]

def is_latin(M, n):
    return all(sorted(r) == list(range(n)) for r in M) and \
           all(sorted(M[i][c] for i in range(n)) == list(range(n)) for c in range(n))

def orthogonal(L1, L2, n):                     # Graeco-Latin check
    return len({(L1[i][j], L2[i][j]) for i in range(n) for j in range(n)}) == n*n

def gl_pair(L1, L2, n):
    return is_latin(L1, n) and is_latin(L2, n) and orthogonal(L1, L2, n)

def mols_field(p):                             # complete MOLS set over Z_p (prime)
    return [cyclic(p, a=a) for a in range(1, p)]  # a=1..p-1: pairwise orthogonal

def latin_rectangle(r, n):                     # r voices x n sections, r < n
    rows = [[(i*j) % n for j in range(n)] for i in range(r)]  # any r rows of a square
    return rows

def complete_rect(R, n):                       # Hall-guaranteed: extends to a square
    rows = [list(x) for x in R]
    while len(rows) < n:
        r = len(rows)
        allowed = [set(range(n)) - {rows[i][c] for i in range(r)} for c in range(n)]
        def bt(c, row, used):
            if c == n: return True
            for v in sorted(allowed[c] - used):
                if v not in {row2[c] for row2 in rows}:
                    row[c] = v
                    if bt(c+1, row, used | {v}): return True
            return False
        newrow = [-1]*n
        assert bt(0, newrow, set()), "Hall violated (cannot happen for rectangles)"
        rows.append(newrow)
    return rows

def sudoku_solve(givens, limit=2):             # MRV backtracking (17-clue fast)
    b = [list(map(int, givens[r*9:(r+1)*9])) for r in range(9)]
    sols = []
    def cands(b, r, c):
        used = set(b[r]) | {b[i][c] for i in range(9)}
        R, C = r//3*3, c//3*3
        used |= {b[i][j] for i in range(R, R+3) for j in range(C, C+3)}
        return [v for v in range(1, 10) if v not in used]
    def bt(b):
        if len(sols) >= limit: return
        best, bc = None, None
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    cs = cands(b, r, c)
                    if not cs: return
                    if bc is None or len(cs) < len(bc):
                        best, bc = (r, c), cs
                        if len(cs) == 1: break
            if bc and len(bc) == 1: break
        if best is None:
            sols.append([row[:] for row in b]); return
        r, c = best
        for v in bc:
            b[r][c] = v; bt(b); b[r][c] = 0
    bt(b)
    return sols

def transversal(M, n):                         # rainbow matching search
    for perm in itertools.permutations(range(n)):
        if len({M[i][perm[i]] for i in range(n)}) == n:
            return [(i, perm[i]) for i in range(n)]
    return None

def tension_order(n):                          # HOME/TENSE/LIFT taxonomy
    if n in (2, 6): return 'TENSE'             # no orthogonal mate at all (Tarry)
    if n in (3, 5, 7, 9, 11, 13): return 'HOME'  # prime powers: complete MOLS
    return 'LIFT'                              # mate exists, no complete set (BSP/Lam)

# Musical plan: 9x9 Sudoku design -> per-cell pc matrix (digits 1..9 -> pcs)
PC = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11, 8: 1, 9: 3}
GIVEN = "000000010400000000020000000000050407008000300001090000300400200050100000000806000"
S = sudoku_solve(GIVEN)[0]                       # unique solution (17 clues, verified)
plan = [[PC[S[i][j]] for j in range(9)] for i in range(9)]
# every row, column, and 3x3 box is a permutation of the 9 pcs  (verified)
```

The abstract plan (pc + duration-class matrices) is then handed to the concrete feeder: per voice a register ladder, per cell a rhythmic archetype from its duration class, `create_note_unit` fills, `validate()` gates, `to_midi()` exports — the standard spine (AGENTS.md).

## 7. References

- Euler, L. (1782). "Recherches sur une nouvelle espèce de quarrés magiques." *Verhandelingen van het Zeeuws Genootschap* 9, 85–239 — Latin squares, the 36 officers, the $n\equiv2\pmod4$ conjecture.
- Choi Seok-jeong (1700). *Gusuryak* (九數略) — order-9 orthogonal Latin squares + magic square (369), 67 years before Euler.
- Tarry, G. (1901). "Le problème des 36 officiers." *CR Assoc. Franç. Av. Sci.* — order 6 impossible.
- Bose, R. C., Shrikhande, S. S. (1959). *PNAS* 45(5), 734–737; Parker, E. T. (1959). *PNAS* 45(6), 859–862 — Euler's conjecture false for all $n\ge10$; Gardner, M. (1959). *Scientific American*, Nov.
- Hall, P. (1935). "On representatives of subsets." *J. London Math. Soc.* 10, 26–30 — SDR/marriage theorem.
- Rao, C. R. (1947). "Factorial experiments derivable from combinatorial arrangements of arrays." *JRSS Suppl.* 9, 128–139 — orthogonal arrays $\mathrm{OA}(N,k,v,t)$.
- Dénes, J., & Keedwell, A. D. (1974). *Latin Squares and their Applications.* Academic Press.
- Jacobson, M. T., & Matthews, P. (1996). "Generating uniformly distributed random Latin squares." *J. Combin. Designs* 4(6), 405–437.
- Colbourn, C. J. (1984). "The complexity of completing partial Latin squares." *Discrete Appl. Math.* 8(1), 25–30.
- Ryser, H. J. (1967). "Neuere Probleme der Kombinatorik." (transversal conjecture); Woolbright (1978), *JCTA* 24, 235–237 ($n-\sqrt n$); Hatami & Shor (2008), *JCTA* 115(7), 1103–1113 ($n-O(\log n/\log\log n)$).
- Felgenhauer, B., & Jarvis, F. (2005). arXiv:math/0504469 (6.67e21 grids); Russell, E., & Jarvis, F. (2006). arXiv:math/0605559 (5.47e9 essentially different); McGuire, G., et al. (2012). arXiv:1201.0749 (no 16-clue).
- Lam, C. W. H. (1991). "The search for a finite projective plane of order 10." *Amer. Math. Monthly* 98(4), 305–318.
- McKay, B. D., Meynert, A., & Myrvold, W. (2007). "Small Latin squares, quasigroups and loops." *J. Combin. Designs* 15(1), 98–119.
- Wikipedia: "Latin square", "Mutually orthogonal Latin squares", "Sudoku", "Hall's marriage theorem", "Orthogonal array" (cached `_web139/w_*.txt`, 2026-11-10).
- DB novelty check (2026-11-10): `latin square`=1 (Costas-array SP bibliography only), `sudoku`/`graeco`/`orthogonal array`/`MOLS`/`SDR`/`isotopy`/`Jacobson`/`rainbow matching`/`marriage theorem` all = 0. Adjacent-but-different: 065 TTSMC (serial matrix = one special order-12 Latin square), 111 VTCC (rhythm tiling canons), 125 LDSC (1D low-discrepancy sequences), 076 PTM-ASC (1D automatic sequences), 113 PCFSC / 133 ZRNC (pc-set networks without orthogonality/completion machinery).
- Verified prototype: `_web139/verify_139_LSAC.py` — 29 checks, all pass (see DB ### Source).

## 8. Pitfalls (full list in the DB section)

A Latin square is square — use Latin rectangles for $r\neq n$ (1) · the Eulerian void: orders 2/6 have no orthogonal mate, order 10 has one but no complete MOLS set (2) · even cyclic squares are thread-less; odd orders always have a transversal (3) · not a re-skin of 065's serial matrix / 111's tiling canons / 125's sequences (4) · abstract layer: emit the plan, not the notes (5) · aggregate columns are dense — thin via rectangles or arpeggiation (6) · isotopy changes keys — pin pc 0 = tonic (7) · Sudoku uniqueness needs ≥ 17 clues (8) · completion is NP-complete — stay in the Hall-guaranteed regime for skeletons (9) · only Jacobson–Matthews samples uniformly — document and seed the sampler (10) · pc ≠ pitch — register/voicing lives in the concrete layer (11) · transversals may not exist/be unique — search, don't assume (12) · the linear $\mathbb{Z}_n$ construction only gives G-L pairs at prime orders — use finite fields/Klein for 4, 8, 9 (13).
