# Report 137 — Tropical (Max-Plus) Algebra Composition (TMPC)

**Run date:** 2026-11-07 (scheduled cron research job)
**Status:** COMPLETE — method appended, table row added, standalone file written, verification passed.

---

## 1. Identity card

| Field | Value |
|---|---|
| **Method ID** | **137** |
| **Method name** | Tropical (Max-Plus) Algebra Composition |
| **Acronym** | TMPC |
| **Paradigm** | **Rules-Based** (deterministic idempotent-semiring algebra; no randomness, corpus, fitness or learning) |
| **Layer** | **concrete** (LAYER_ARCHITECTURE.md) — emits resolved onset/pitch/duration events into UnitMatrix cells |
| **One-line description** | Composes in the idempotent max-plus semiring so the piece is a timed event graph: the max cycle mean is the tempo, the max-plus eigenvector is the groove, the critical-graph cyclicity is the bar, the tropical determinant is the bijective voice exchange, and tropical polynomial roots are the modulation pivots. |
| **Candidate code path** | `generators/tropical_maxplus.py` (`TropMat.mul/pow`, `max_cycle_mean`, `eigenvector`, `cyclicity`, `kleene_star`, `trop_det`, `trop_roots`, `TropicalPlan.to_events`) |
| **Standalone file** | `/opt/data/projects/Research/CompositionMethods/method_137_TMPC.md` |
| **Report file** | `/opt/data/projects/Research/CompositionMethods/report_137.md` |
| **methods_db.md lines — before** | **30 461** |
| **methods_db.md lines — after** | **30 547** |
| **Delta** | **+86** (84-line method section + 1 table row + 1 added pitfall line) |
| **Section location** | starts line 30 464 (`# Tropical (Max-Plus) Algebra Composition (TMPC) (Method 137)`), runs to EOF |
| **Table row location** | line 147 (immediately after the `**136**` row) |
| **ID resolution** | max of `method_*.md`/`report_*.md` file scan (136) and summary-table scan (136) → **137**; ID 137 was free (no file, no table row) |
| **Next free ID** | **138** |

## 2. Full summary-table row (exactly as inserted)

| **137** | concrete | Tropical (Max-Plus) Algebra Composition (TMPC) | **Rules-Based** | Rhythm, Pitch, Harmony, Structure, Texture | Moderate (max-plus eigenvector = fixed center; no functional harmony) | Continuous / Fluid (event-time schedules; grid optional) | Macro/Form (Kleene star) | $\mathcal{O}(n^3)$ per multiply, $\mathcal{O}(n^3)$ Kleene star | Composes in the idempotent max-plus semiring ($\oplus=\max$, $\otimes=+$, so $a\oplus a=a$ and there is no subtraction): the piece is a timed event graph with $x^{(k)}=A^{\otimes k}\otimes x^{(0)}$ and $x^{(k)}_i=\max_j(A_{ij}+x^{(k-1)}_j)$, i.e. every onset is the latest of its causal predecessors' requirements (verified: $A^{\otimes k}$ = brute-force max weight over all exact-length-$k$ walks, $k=1..4$). The max cycle mean $\lambda$ (Karp 1978; verified against brute-force cycles on 50 matrices) is the asymptotic tempo (measured increments exactly 5 at $k=24..29$); the eigenvector $A\otimes v=\lambda\otimes v$ is the steady-state groove offset (measured $v-5k\to(-4,0,-1)$); the critical graph's cyclicity $c$ is the bar ($A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}$, verified $c=2,3,4$); the tropical determinant (max over permutations = assignment) is the bijective voice exchange (6×6 = 48 over 720 permutations); tropical polynomial roots are the modulation pivots ($0\oplus3x\oplus0x^2\to\{-3,+3\}$, $r_1+r_2=a_0-a_2$, $\max(r_1,r_2)=a_1-a_2$ verified); Kleene star $A^*$ = all-pairs longest path = form arcs (DAG check 0→2=5, 0→3=8); dequantization $h\log(e^{x/h}+e^{y/h})\to\max$ gives a continuous humanized↔grid-locked knob (error 4.5e-6 at $h=0.1$). Feeds generators/tropical_maxplus.py. |

## 3. Layer classification (done first, per spec)

**concrete.** The decisive test in LAYER_ARCHITECTURE.md is what the method's primary output *is*.

- The max-plus state vector $x^{(k)}$ is literally a vector of **absolute onset times**, and $A^{\otimes k}$ is a schedule. Resolving a schedule into `MusicEvent(pitch, volume, start_tick, end_tick)` per cell is immediate, so the method fills UnitMatrix cells → **concrete**.
- It also produces a genuine *abstract* sub-plan ($\lambda$ = tempo curve, $v$ = groove offsets, $c$ = bar, block decomposition = form) — the only method in the DB whose abstract and concrete outputs are the *same numbers* read at different scales. But "abstract" is reserved for methods that stop at pools/subsets/tension curves with no events; TMPC goes all the way to events, so it is tagged concrete and the abstract part is documented in the MEF/UnitMatrix sections.
- Not absolute: no sound production, no synthesis, no mixing.

## 4. Paradigm classification

**Rules-Based.** One substitution (max for +, + for ×) generates everything; there is no sampling, no corpus, no objective function, no gradient. Determinism is exact up to floating point, and $\lambda$ is rational (denominator $\le n$) so the musical invariants can be checked exactly with `fractions.Fraction`.

## 5. Novelty evidence

- `grep -ci` on `methods_db.md` **before** entry: `tropical` = 0, `max-plus` = 0, `min-plus` = 0, `semiring` = 0, `idempotent` = 0, `kleene` = 0, `newton polygon` = 0. `\bTAC\b` = 0, but `TAC` as a substring hits 616 times — hence the acronym **TMPC** (0 hits).
- arXiv (2026-11-07, cached `_web138/q_*.xml`): `"tropical semiring" AND music` → 0; `"tropical geometry" AND music` → 0; `"max-plus" AND music` → 1 (signal-processing paper); `"max-plus algebra" AND composition` → 1 (Network Calculus library); `tropical AND "rhythm"` → 4 (circadian/HRV, land cover). No musical prior art found.
- Nearest DB neighbours and why they differ: **011** voice-leading graph search (one additive shortest path; no eigenvalue/period/rank), **050** optimal transport (measure-splitting, entropy; TMPC has no measure, its assignment is a permutation), **051** spectral Laplacian (symmetric operator, real spectrum; TMPC has no spectral theorem and its $\lambda$ is a max cycle mean), **121** IET (measure-preserving), **125** LDSC (discrepancy), **123** game theory (payoff fixed point), **044** persistent homology (metric filtration).
- TMPC is the DB's first **idempotent-semiring** method.

## 6. Verification (all numbers in the text are measured, not asserted)

Artifacts: `_web138/verify_137_TAC.py` + `_web138/verify_137_output.txt`, `_web138/probe_karp.py`, `_web138/tmpc_sketch.py` + `_web138/tmpc_sketch_output.txt`, cached `_web138/wiki_tropical_geometry.txt` (30 748 B).

| # | Claim | Result |
|---|---|---|
| 0 | semiring axioms ($\oplus,\otimes$ over 2000 random triples) | idempotent / commutative / associative / distributive / identities — all True |
| 1 | $(A^{\otimes k})_{ij}$ = max weight of an exact-length-$k$ walk | matches brute force over all $n^{k+1}$ paths, $k=1..4$ |
| 2 | Karp $\lambda$ = max cycle mean | matches brute-force simple cycles on 50 random 3×3; all sources agree |
| 3 | $A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}$ | exact for $c=2,3,4$ at $k=3c$ |
| 4 | tropical determinant = max over permutations | 3×3 = 11; 6×6 = 48 over all 720 permutations |
| 5 | tropical roots of $0\oplus3x\oplus0x^2$ | $\{-3,+3\}$; $r_1+r_2=0$, $\max=3$; convex envelope |
| 6 | Kleene star = longest path on a DAG | $0\to2=5$ direct, $0\to3=8$ via 2 |
| 7 | $\lambda$ = asymptotic per-step increment | increments exactly 5 at $k=24..29$ (λ = 5) |
| 8 | $\lambda$ rational, denominator $\le n$ | 200/200 random matrices |
| 9 | dequantization error | 3.1e-1 (h=1), 4.5e-6 (h=0.1), 0 (h=0.01) |
| 10 | eigenvector by relaxation + eigen-equation assertion | $v=(0,0,0.5,0)$ on the 4-cycle demo, $A\otimes v=\lambda+v$ entrywise |

**Working demo of the sketch** (4 voices, critical 4-cycle, waits 1 / 0.5 / 1.5 / 1): $\lambda=1.0$ beat/step, $c=4$, $v=(0,0,0.5,0)$, onsets close the bar exactly at $k=4$, $\operatorname{tdet}=20$, roots $\{-3,3\}$.

## 7. Quirks / pitfalls actually hit during this job

1. **Karp's formula nesting was wrong in my first two implementations.** `min_v max_k (F_n[v]-F_k[v])/(n-k)` (the "textbook-looking" form) matched brute force only **147/300** matrices; `max_v min_k` matched **300/300**. `_web138/probe_karp.py` is the probe that settled it. Now Pitfall 6 in the DB.
2. **Karp needs a fixed source and an irreducible matrix.** Initialising $F_0=[0,0,\dots,0]$ (walks starting anywhere) gives wrong values; and for reducible matrices the result is source-dependent (a real property, not a bug — one $\lambda$ per strongly connected component). Counterexample used: `[[-5,9,3],[-inf,6,3],[-4,1,-5]]`.
3. **Normalised power iteration does not converge when $c>1$.** It orbits with period $c$. On the 4-cycle demo it returned $(0,0,0,0)$ instead of $(0,0,0.5,0)$. Fixed with a reduced-system relaxation plus an explicit eigen-equation assert; promoted to Pitfall 12 in the DB, and the "candidate code path" line was corrected.
4. **`float('-inf')` differences produce NaN** (`inf - inf`), which silently poisons every max downstream. All routines guard with `!= NEG` before subtracting — required by the Karp formula itself, not just defensive coding.
5. **First Kleene-star assertion was wrong** (asserted $0\to3=6$; the true longest path is $0\to2\to3=8$ because the direct edge of weight 5 beats the two-step route of 3). Fixed and re-verified — max-plus "shortest path" intuitions invert.
6. **Tropical-root scan needed a tie tolerance.** A 0.001 sweep lands the corners at exactly ±3.0; without a `1e-9` tie window the envelope-slope detector reports spurious breaks at floating-point noise.
7. **Acronym collision:** `TAC` matches 616 times inside words (`tactile`, `contact`, `tactics`); `\bTAC\b` = 0 but confusion risk is real → used **TMPC** (0 hits).
8. **arXiv over `http://` returned 0 bytes; `https://` worked.** All responses cached in `_web138/`.
9. **Patch hygiene (as warned):** verified zero literal `\\` in the appended text and table row (`count(chr(92)*2) == 0`), and verified the row starts with a single `|` with exactly 11 pipes = 10 columns, matching the header.
10. **DB append order:** `methods_db.md` interleaves method sections with SP-* sound sections, so `>>` lands TMPC after the SP-135 section at EOF rather than numerically adjacent to 136 — the same way 136 sits mid-file. Harmless: the summary table is the index.

## 8. Musical Elements Framework — condensed

- **PITCH** — $A_{ij}$ = interval in semitones; path sums = melody; $\lambda$ = drift rate (modulation engine); tropical roots = pivot tones. Fold to a scale *after* the recursion only.
- **RHYTHM** — the home turf: onsets $x^{(k)}$, waits $A_{ij}$, tempo $\lambda$, groove $v$, bar $c$; coincidence = chord; max = critical path = locked groove by definition.
- **HARMONY** — $\operatorname{tdet}$ = bijective voice exchange; tropical rank = independent voice count; tropical convex hull = the voicing space.
- **STRUCTURE** — block-triangular = one-way form; irreducible = returning section; each SCC its own $\lambda$ (poly-tempo); Kleene star = arc planning; $c$ = column length.
- **TEXTURE** — row out-degree = density; rank = distinctness; $-\infty$ = silence; $h$ = blend from hard to smeared.

## 9. UnitMatrix integration — condensed

- **Voices = rows = states** (a voice is its dependency row, not a stored melody).
- **Sections = columns = $k$-windows** of length $c$ (or matrix blocks); per-column $\lambda$ = tempo map.
- **Cells = MusicUnit**: firing → event (pitch from interval path, onset from $x^{(k)}$, duration to next firing of the same voice, velocity from out-degree or dequantized weight); coincident firings → chord unit; pad to `section_len` via `_unit_from_events` (zero-drift is *not* automatic — different voices have different firing counts).
- **Cost:** $O(n^3)$ per multiply, $O(n^3\log k)$ per power, $O(n^3)$ Karp, $O(n^3)$ Hungarian for $\operatorname{tdet}$, $O(d\log d)$ roots.

---

## 10. Appended method section (verbatim, as it now stands in methods_db.md)

# Tropical (Max-Plus) Algebra Composition (TMPC) (Method 137)

### Source

- **Cuninghame-Green, R. A. (1979).** *Minimax Algebra*, Lecture Notes in Economics and Mathematical Systems 166, Springer — the first systematic account of max-plus ("minimax") algebra: $\max$ in place of $+$, $+$ in place of $\times$, and the analysis of linear systems over it.
- **Cohen, G., Dubois, D., Quadrat, J.-P., & Viot, M. (1985).** "A linear-system-theoretic view of discrete-event processes and its use for performance evaluation in manufacturing." *IEEE Transactions on Automatic Control* 30(3), 210–220 — the founding paper of max-plus as the algebra of *discrete-event* dynamics; it introduces the state recursion $x(k)=A\otimes x(k-1)$ used throughout this method.
- **Baccelli, F., Cohen, G., Olsder, G. J., & Quadrat, J.-P. (1992).** *Synchronization and Linearity: An Algebra for Discrete Event Systems.* Wiley — the standard reference: timed event graphs, eigenvalue as asymptotic cycle time, eigenvector as steady-state schedule, cyclicity as period.
- **Karp, R. M. (1978).** "A characterization of the minimum cycle mean in a digraph." *Discrete Mathematics* 23, 309–311 — the max/min cycle-mean characterization and the $O(n^3)$ eigenvalue algorithm.
- **Simon, I. (1988).** "Recognizable sets with multiplicities in the tropical semiring." *MFCS 1988*, LNCS 324, 107–120 — the tropical semiring in computer science; the name honours the Brazilian school (Imre Simon, São Paulo).
- **Pin, J.-É. (1998).** "Tropical semirings." In J. Gunawardena (ed.), *Idempotency*, Publications of the Newton Institute 11, Cambridge University Press, 50–69.
- **Litvinov, G. L. (2007).** "The Maslov dequantization, idempotent and tropical mathematics: a brief introduction." *Journal of Mathematical Sciences* 135(5), 3061–3083 — dequantization $x\oplus_h y=h\log(e^{x/h}+e^{y/h})\to\max(x,y)$ as $h\to0^{+}$; the expression knob used in PITCH/TEXTURE below.
- **Butkovič, P. (2010).** *Max-linear Systems: Theory and Algorithms.* Springer Monographs in Mathematics — algorithms: Karp, Howard policy iteration, cyclicity, Kleene star, matrix powers.
- **Develin, M., & Sturmfels, B. (2004).** "Tropical convexity." *Documenta Mathematica* 9, 1–27 — tropical polytopes, tropical rank, tropical convex hulls (the voicing-space reading).
- **Maclagan, D., & Sturmfels, B. (2015).** *Introduction to Tropical Geometry.* AMS Graduate Studies in Mathematics 161 — tropical polynomials, roots, the tropical fundamental theorem, and the min/max convention.
- **Joswig, M. (2021).** *Essentials of Tropical Combinatorics.* AMS — tropical rank, tropical determinant/assignment view.
- **Wikipedia, "Tropical geometry"** (raw wikitext cached `_web138/wiki_tropical_geometry.txt`, 30 748 bytes) — the algebraic definition; note it states the *min* convention, while this method uses the *max* convention (see Pitfalls 1).
- **arXiv prior-art check (2026-11-07, cached `_web138/q_*.xml`)**: `all:"tropical semiring" AND all:music` → **0**; `all:"tropical geometry" AND all:music` → **0**; `all:"max-plus" AND all:music` → 1 ("Sparse Hybrid Linear-Morphological Networks" — signal processing, not composition); `all:"max-plus algebra" AND all:composition` → 1 (Nancy, a Network Calculus library); `all:tropical AND all:"rhythm"` → 4 (circadian/HRV and land-cover papers, none musical). No musical use of the tropical semiring found.
- **Novelty check (2026-11-07)** `grep -ci` on `methods_db.md` before entry: `tropical` = 0, `max-plus` = 0, `min-plus` = 0, `semiring` = 0, `idempotent` = 0, `kleene` = 0, `newton polygon` = 0. Adjacent-but-different: **011** voice-leading graph search (one additive shortest path; no eigenvalue, no periodicity, no tropical rank), **050** optimal transport (measure-splitting transport with an entropy term; TMPC's assignment is a permutation and there is no measure), **051** spectral graph Laplacian (real eigen-decomposition of a symmetric operator; TMPC's eigenvalue is a max-cycle-mean of a non-symmetric matrix over an *idempotent* semiring), **121** interval exchange (measure-preserving piecewise isometry), **125** low-discrepancy (van der Corput/Halton), **123** game-theoretic best response (fixed-point iteration over payoffs), **044** persistent homology (filtration of a metric space). TMPC is the DB's first *idempotent-semiring* method.
- **Reference prototype verified for this document:** `_web138/verify_137_TAC.py`, log `_web138/verify_137_output.txt` — eight checks, all pass: semiring axioms (2000 random triples), $A^{\otimes k}$ = exact-length-$k$ max walk (brute force, $k=1..4$), Karp $\lambda$ vs brute-force simple cycles (50 matrices, all sources agree), cyclicity $A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}$ ($c=2,3,4$), tropical determinant $6\times6=48$ over all 720 permutations, tropical roots of $0\oplus3x\oplus0x^2=\{ -3,+3\}$, Kleene star = longest paths on a DAG, and the asymptotic increment $=\lambda$ exactly at $k=40$. Extra probes: $\lambda$ rational with denominator $\le n$ (200/200); soft-max/dequantization error $3.1\times10^{-1}$ at $h=1$, $4.5\times10^{-6}$ at $h=0.1$, $0$ at $h=0.01$.

### Layer

**concrete** — TMPC resolves onsets, pitches and durations: the state vector of the timed event graph *is* a schedule of absolute event times, written into UnitMatrix cells as `MusicEvent`s. The $\lambda$/eigenvector/cyclicity triple is a planning quantity (tempo, groove, bar), so the method also carries an abstract sub-plan, but its primary output is a resolved event schedule. Feeds `generators/` (candidate module `generators/tropical_maxplus.py`: `TropMat.mul`, `TropMat.pow`, `max_cycle_mean`, `eigenvector`, `cyclicity`, `kleene_star`, `trop_det`, `trop_roots`, `TropicalPlan.to_events`).

### Paradigm

**Rules-Based** — deterministic algebra over an idempotent semiring. No randomness, no corpus, no fitness function, no learning. The same matrix and initial vector give a byte-identical schedule; the only nondeterminism is floating-point rounding (use `fractions.Fraction` when exact equality matters — $\lambda$ is always rational with denominator $\le n$).

### Description

**Tropical (Max-Plus) Algebra Composition (TMPC)** composes in the idempotent semiring $(\mathbb{R}\cup\{-\infty\},\oplus,\otimes)$ with

$$a\oplus b=\max(a,b),\qquad a\otimes b=a+b .$$

Addition is idempotent ($a\oplus a=a$), so this is *not* a ring: there is no subtraction, no inverse, and no way to "undo" a transition. Everything the method does follows from one substitution — $\max$ where you expected $+$, $+$ where you expected $\times$.

The musical object is a **timed event graph**. Each node is a voice (or a chord-state); $A_{ij}\in\mathbb{R}\cup\{-\infty\}$ is the wait that voice $i$ must observe after a firing of $j$ before it may fire again — or, in the pitch reading, the interval from state $j$ to state $i$, with $-\infty$ marking forbidden moves. With $x^{(k)}$ the vector of $k$-th firing times,

$$x^{(k)}=A^{\otimes k}\otimes x^{(0)},\qquad x^{(k)}_i=\max_j\left(A_{ij}+x^{(k-1)}_j\right),$$

so **voice $i$'s $k$-th onset is the latest of every causal predecessor's requirement**. Max-plus is literally the algebra of "wait for the slowest predecessor", and that is exactly how a groove locks. Verified: $A^{\otimes k}_{ij}$ equals the brute-force maximum weight over all walks of exactly $k$ edges (all $n^{k+1}$ paths enumerated, $k=1..4$, $3\times3$ matrix).

- **$\lambda$ = tempo.** The max cycle mean $\lambda(A)$ is the asymptotic weight per step, $A^{\otimes k}\approx\lambda k$ entrywise. Measured by power iteration: increments exactly $5$ for $k=24..29$ on a matrix whose self-loop has weight 5. In duration units $\lambda$ is the steady-state inter-onset interval — the **tempo**. Because it is a *cycle mean*, tempo is set by the slowest loop, never by an average; and $\lambda$ is rational with denominator $\le n$ (verified 200/200 random matrices), so tempo ratios are always simple.
- **Eigenvector = groove.** $A\otimes v=\lambda\otimes v$; $v$ is the steady-state *offset* pattern of the voices — the micro-timing skeleton of the groove. Measured in the aperiodic case ($c=1$): $v-5k\to(-4,\,0,\,-1)$, a fixed three-voice offset. Warning: plain power iteration only converges when $c=1$ (see Pitfalls 12).
- **Cyclicity = bar.** The cyclicity $c$ of the critical graph gives exact periodicity $A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}$ (verified $c=2,3,4$ at $k=3c$). $c$ is the number of steps after which the system returns to itself up to a constant — the bar length, and it is derived, not chosen.
- **Tropical determinant = voice exchange.** $\operatorname{tdet}(M)=\max_{\sigma}\sum_i M_{i\sigma(i)}$ is the maximum-weight perfect matching (assignment problem): which line goes to which voice so total motion is maximal. Verified: $6\times6$ case $=48$ by brute force over all 720 permutations; $3\times3$ sample $=11$.
- **Tropical roots = pivots.** A tropical polynomial $p(x)=\max_i(a_i+i x)$ is convex and piecewise linear; its roots are the breakpoints where two terms tie. For $p(x)=0\oplus3x\oplus0x^2$ the roots are $\{-3,+3\}$, factoring with $r_1+r_2=a_0-a_2=0$ and $\max(r_1,r_2)=a_1-a_2=3$ (verified). A degree-$d$ tropical polynomial has at most $d$ roots (tropical fundamental theorem) and, being envelope corners, the roots arrive **pre-ordered** — a free scale-degree ordering with a hard cap on how many pivot tones a passage may have.
- **Kleene star = form.** $A^{*}=\sup_{k\ge0}A^{\otimes k}$ is the all-pairs longest path (verified on a DAG: $0\to2=5$ direct, $0\to3=8$ through 2) — the extreme arc from here to there, which is what a formal plan asks.
- **Dequantization = expression knob.** Replacing $\max$ with a soft max, $x\oplus_h y=h\log(e^{x/h}+e^{y/h})\to\max(x,y)$ as $h\to0^{+}$ (measured error $3.1\times10^{-1}$ at $h=1$, $4.5\times10^{-6}$ at $h=0.1$, $0$ at $h=0.01$). Large $h$ smears the "wait for the slowest" into a weighted blend — legato, overlapping, human; $h\to0$ restores the hard maximum — quantized, machine-locked. One continuous control between humanized and grid-locked, with the matrix unchanged.
- **Idempotency is an aesthetic law.** $a\oplus a=a$: *repeating a statement adds nothing*. In max-plus only what exceeds the previous event is heard; a literal repeat is absorbed. TMPC's counterpoint is therefore inherently "always at the ceiling" — variation must raise the maximum, never restate it. This is the method's signature and its main limitation.

### Musical Elements Framework

- **PITCH**: $A_{ij}$ = interval in semitones from state $j$ to state $i$; the path sum accumulated by $A^{\otimes k}$ is the melodic trajectory, and $\lambda$ is the *drift rate* in semitones per step (a key that rises $\lambda$ semitones per phrase never returns — a built-in modulation engine). Tropical roots of the pitch polynomial give the pivot tones where two interpretations are equally admissible: exactly the notes to hold across a modulation. Fold to a scale only *after* the recursion (see Pitfalls 8).
- **RHYTHM**: the home turf. Onsets are $x^{(k)}$, waits are $A_{ij}$, tempo is $\lambda$, the groove's phase pattern is $v$, the bar is $c$. Simultaneity is free: voices whose firing times coincide *are* a chord. Because the recursion takes a max, the rhythm is a critical path — every note is as late as its slowest prerequisite allows, which is the formal definition of a locked groove.
- **HARMONY**: $\operatorname{tdet}$ assigns lines to voices (a permutation, so no voice splitting and no crossing unless the permutation says so); tropical rank — the largest $r$ with a tropically nonsingular $r\times r$ minor — counts the *independent* voices, i.e. the true polyphonic thickness. Tropical convexity (Develin–Sturmfels) gives the set of voicings closed under pairwise max: a chord space with corners rather than a continuous manifold.
- **STRUCTURE**: the block structure of $A$ *is* the form. Block-triangular $A$ = a one-way form (sections that never return); an irreducible block = a returning section; each strongly connected component carries its own $\lambda$, so a reducible matrix is a multi-tempo piece by construction. Kleene star plans the arc; $c$ fixes column lengths.
- **TEXTURE**: density = number of finite entries per row (out-degree) — sparse rows are thin, solo lines; dense rows are tutti. $\lambda$ blends the parts into one pulse, $h$ blends them into one smear; tropical rank sets how many layers remain distinguishable. $-\infty$ entries are silences, and they are compositional material, not an implementation detail.

### UnitMatrix Integration (Voices & Sections)

**Voices = rows = states.** Row $v$ is state $v$; its finite entries say what it may wait for / move to. A row's firing sequence is its line. Because $x^{(k)}_i=\max_j(A_{ij}+x^{(k-1)}_j)$, a voice is defined by its *dependencies*, not by a stored melody — the melody is a by-product of the wait matrix, which makes re-orchestration a matrix edit rather than a rewrite. Per-voice child seed (`seed*101 + row`) keeps multi-row runs reproducible when $h$-blending or tie-breaking is randomized.

**Sections = columns = $k$-windows.** Cut the firing index $k$ into windows of length $c$ (the cyclicity) or into blocks of the matrix's block decomposition; each column holds the firings whose index falls in its window. Re-estimating $\lambda$ per column yields an explicit *tempo map*; $\lambda$ may only decrease if a section is meant to relax, because the max cannot be lowered by adding paths.

**Cells = MusicUnit.** Each firing $x^{(k)}_i$ becomes an event (pitch from the interval path, onset from $x^{(k)}_i$, duration to the next firing of the same voice, velocity from row out-degree or from the dequantized weight). Firings that coincide within a tick become one chord unit. Every cell must end at the section's terminal landmark — pad with a rest or a sustained note via `_unit_from_events(events, section_len)`; zero-drift is not automatic here because different voices have different firing counts, exactly as with any other feeder.

**Candidate code path:** `generators/tropical_maxplus.py` — `TropMat.mul(A,B)` ($\max$-$+$, $O(n^3)$), `TropMat.pow(A,k)` ($O(n^3\log k)$ by squaring, or $O(kn^3)$ iterated), `max_cycle_mean(A)` (Karp, $O(n^3)$), `eigenvector(A)` (relax $v_i=\max_j(A_{ij}+v_j)-\lambda$ for $n$ rounds from a reference node, $O(n^3)$; do **not** use plain power iteration — it orbits with period $c$ when $c>1$, see Pitfalls 12), `cyclicity(A)` (period of the critical graph, $O(n^2)$ given the critical edges), `kleene_star(A)` ($O(n^4)$ naive, $O(n^3\log n)$ by repeated squaring), `trop_det(M)` ($O(n^3)$ Hungarian), `trop_roots(coeffs)` (upper-envelope corners, $O(d)$ or $O(d\log d)$), `TropicalPlan.to_events(...)` (fold to pitch, quantize to ticks, pad to `section_len`), wired to the standard `UnitMatrixComposer.fill_voice_section → validate() → to_midi()` spine.

### Pitfalls

1. **Two conventions, one name.** Most of the literature and the cached Wikipedia article use *min*-plus ($\oplus=\min$); this method uses *max*-plus. They are isomorphic by negation ($A\mapsto-A$ turns max-cycles into min-cycles) but a mixed file silently computes the opposite of what it documents. Declare the convention in the module docstring and assert on a known $2\times2$ fixture.
2. **No subtraction, so no inverse.** Max-plus has no additive inverse: you cannot "retrograde" by negating a matrix, and you cannot interpolate halfway between two events. Retrogrades must be re-derived from the transposed/reversed graph, and any "average" of two schedules must be computed outside the semiring. Treat this as a compositional constraint, not a bug.
3. **$-\infty$ is not zero.** In code, `float('-inf')` propagates correctly through $+$ but `inf - inf` is `NaN`; a single `NaN` in a matrix destroys every max downstream. Use `None` with explicit skips, or `-1e18` with a guard, and never take a difference of two $-\infty$ entries (the Karp formula does exactly that — skip unreachable $v$).
4. **The eigenvalue needs irreducibility.** $\lambda$ and a unique (up to scaling) eigenvector exist for irreducible matrices; a reducible matrix has one $\lambda$ *per strongly connected component* and the global rate is the maximum. That is musically useful (poly-tempo form) but it means "the tempo" is undefined for a block-triangular piece — state which component you mean.
5. **Cyclicity is not the period of the matrix.** $c$ is the period of the *critical* graph only; the transient before the critical graph is reached is at most $n$ steps. Assuming periodicity from $k=0$ produces a groove that is right at the end and wrong at the start — start the repeated window after the transient.
6. **Karp's nesting is easy to invert — I did, twice.** On 300 random matrices, the textbook-looking `min_v max_k (F_n[v]-F_k[v])/(n-k)` matched brute force only 147/300; the dual `max_v min_k (...)` matched 300/300 for every source (`_web138/probe_karp.py`). Always validate an eigenvalue routine against brute-force cycle enumeration on small matrices before trusting it on a large one.
7. **Finite-$k$ is not asymptotic.** $A^{\otimes k}$ oscillates around $\lambda k$ with a bounded residual; a piece built on $k\le8$ steps may show a local rate very different from $\lambda$. Print the residual $A^{\otimes k}-\lambda k$ and check it has settled (it becomes periodic with period $c$).
8. **Fold after, never inside.** Mapping interval sums to a scale ($\bmod$ 12, or a scale-degree table) inside the recursion breaks additivity and destroys the entire $\lambda$/cyclicity theory. Compute the linear schedule first, then fold the resulting pitches; keep the unfolded path in provenance.
9. **Pitch saturation.** With $\lambda=0.5$ semitone per step, 64 steps accumulate 32 semitones — three octaves of drift. Either choose small rational $\lambda$ (denominator $\le n$ keeps them simple), or plan the fold as a registral arch, or use $\lambda$ as a *tension* parameter rather than a literal transposition rate.
10. **$h$-blending changes the algebra, not just the sound.** Soft max is no longer idempotent, so periodicity and exact repetition disappear as $h$ grows — by design (it is the humanizing knob), but it also means a $h>0$ render cannot be validated by checking $A^{\otimes(k+c)}=\lambda c\otimes A^{\otimes k}$. Run the structural checks at $h=0$ and apply the blend at render time.
11. **Zero-drift.** Voices have different firing counts per window; every cell must still end at `section_len`. Pad with rests or sustained tones through `_unit_from_events`, then `validate()` — the same rule as every other concrete feeder.
12. **Power iteration fails on periodic matrices.** Normalised power iteration $x\mapsto A\otimes x$, $x\mapsto x-\max(x)$ finds the eigenvector only when $c=1$; with $c>1$ the iterates orbit with period $c$ and no fixed point is ever reached. Measured: on a critical 4-cycle with waits 1, 0.5, 1.5, 1 it returned the constant vector $(0,0,0,0)$, while the true eigenvector is $(0,0,0.5,0)$ — verified by the eigen-equation $A\otimes v=\lambda+v$ entrywise. Use the reduced-system relaxation (or Howard's policy iteration) instead, and always assert the eigen-equation before using $v$ as a groove.
13. **Not a re-skin of adjacent methods.** 011 finds *one* additive shortest path (no eigenvalue, no period, no rank); 050 transports a measure with entropy (TMPC has no measure and its assignment is a permutation); 051 diagonalizes a symmetric operator (TMPC's $\lambda$ is a max cycle mean over an idempotent semiring and there is no spectral theorem); 121 is measure-preserving and 125 is discrepancy-driven. The signature artifacts — $\lambda$ as tempo, $v$ as groove, $c$ as bar, $\operatorname{tdet}$ as voice exchange — have no counterpart in any of them. If a passage should accumulate tension by *addition*, that is not TMPC: max-plus never sums two paths, it only keeps the larger.
