# Method 141 — Arnold Cat Map Torus Permutation Composition (ACMTPC)

**Layer:** concrete · **Paradigm:** Nature-Led · **Status:** verified prototype (`_web141/verify_141_ACMTPC.py`, 12/12 checks)
**Summary row added to `methods_db.md`:** yes (line 151) · **Method section appended:** line 31278

---

## 1. One-line idea

The UnitMatrix is a **discrete torus**: iterate Arnold's cat map — the
area-preserving shear-and-fold permutation $\Gamma(x,y) = (x{+}y,\, x{+}2y)
\bmod (V,S)$ — and the piece is the **Poincaré-recurrent orbit** of a seed
design: section $s$ is state $\Gamma^s(\mathrm{seed})$, the reprise at the
cat-map period $P$ is a theorem, and the motif aggregate is conserved by
dynamics.

## 2. Why this is not already in the database

`grep -ic` on `methods_db.md` on 2026-11-13: `cat map` = **0**, `anosov` = **0**,
`torus automorphism` = **0**, `lucas` = 0, `pisano` = 0, `knead` = 0,
`arnold` = 1 (Arnold Schoenberg's first name in 065 TTSMC prose — unrelated),
`hyperbolic` = 2 (tanh saturation prose; Kepler eccentricity prose in 115 KORC
— both unrelated to Anosov dynamics).

Nearest neighbours and why they are different:

| Method | Model | Why ACMTPC differs |
|---|---|---|
| 043 SATM | dissipative continuous ODE attractors (Lorenz, Rössler), aperiodic | ACMTPC is **conservative** (area-preserving, det = 1), **discrete** (a permutation of a finite grid), **linear**, and **periodic** (exact reprise at $P$) — no attractor exists |
| 070 CML-C | ring of coupled logistic maps, spatiotemporal chaos | a single linear torus automorphism — no coupling, no nonlinear map, no lattice diffusion |
| 028 CMCG | Hénon/Ikeda maps modulating *grains* | ACMTPC permutes grid *cells* (composition-level), not micro-timing of sound grains |
| 049 IFS | contractive affine maps, attractor = fixed fractal shape | the cat map is **expanding** (hyperbolic, Anosov) — the dynamics is the opposite of contraction |
| 077 DBUC | de Bruijn **torus** — 2D cyclic array, every $k\times k$ patch unique | a combinatorial design object, NOT a dynamical system; no iteration, no period theorem |
| 122 HCSC | Hilbert-curve walk through a grid (adjacent steps) | ACMTPC's step is a global shear-and-fold; adjacent cells land far apart (mixing) |
| 112 CADDC | Costas arrays — distinct displacement vectors | no dynamics, no time evolution, no recurrence |

No DB method composes by iterating an area-preserving toral automorphism;
ACMTPC is the DB's first *conservative* (non-dissipative) chaotic generator.

## 3. Model and math

### 3.1 The map

$$\Gamma: (x, y) \mapsto (x + y,\; x + 2y) \pmod{(n_1, n_2)}, \qquad
A = \begin{pmatrix} 1 & 1 \\ 1 & 2 \end{pmatrix}, \quad \det A = 1$$

- **Bijective** on the grid iff $n_2 \mid n_1$ or $n_1 = n_2$ (square).
  Proof sketch: the kernel condition $(x+y \equiv 0 \bmod n_1,\; x+2y \equiv 0
  \bmod n_2)$ forces $y \equiv 0 \bmod n_2$ iff $n_2 \mid n_1$. Verified:
  bijections on $(8,8), (16,8), (5,5), (12,12), (16,4)$; **16 collisions** on
  $(4,8)$ (negative control).
- **Coupled inverse** (rectangular grids; the plain matrix inverse only works
  on square grids):
  $$y = (y' - x') \bmod n_2, \qquad x = (x' - y) \bmod n_1$$
  Verified round-trip both directions on 16×8 and $(\Gamma^{-1})^{12} = I$.
- **Eigenvalues / Lyapunov**: $\lambda_{1,2} = (3 \pm \sqrt{5})/2$;
  $\Lambda = \ln((3+\sqrt{5})/2) \approx 0.96242$ per iteration (measured slope
  **0.9620** from a two-point simulation over 20 iterations). Two events
  separated by one grid cell are $e^{\Lambda k}$ cells apart after $k$
  iterations — full mixing after $k \approx \ln(N)/\Lambda$.
- **Fibonacci closed form** (Dyson–Falk 1992, p. 604; Trott 2006):
  $$\Gamma^k = \begin{pmatrix} F_{2k-1} & F_{2k} \\ F_{2k} & F_{2k+1} \end{pmatrix}$$
  verified $k = 1..10$. Every section's permutation is a Fibonacci matrix power.

### 3.2 Period = reprise

On an $N \times N$ grid the least period is $P(N) = \pi(N)/2$ (Pisano period
divided by 2; verified $P(2){=}3, P(3){=}4, P(4){=}3, P(5){=}10, P(7){=}8,
P(8){=}6, P(10){=}30, P(75){=}100$), and Dyson–Falk's bound $P \le 3N$ held on
the sweep $N = 2..40$. The demo design grid has $P(16,8) = 12$ — **section
$s+12 \equiv$ section $s$** (Poincaré recurrence, verified over a 41-section
window). Form design rule: choose the grid so $P \ge S$ (all sections distinct)
or $P < S$ (built-in da capo).

### 3.3 Fixed points = anchors

$\#\mathrm{Fix}(\Gamma^k) = \mathrm{Lucas}(2k) - 2$ (OEIS **A004146**;
verified $1, 5, 16, 45, 121, 320$ for $k=1..6$); its Möbius transform
**A032170** counts the prime periodic orbits of each period — a ready-made
motif census. On a discrete $N \times N$ grid the count is the number of
solutions of $(\Gamma^k - I)z \equiv 0 \pmod N$ (brute-force: $5\times5 \to
1,5,1,5,1,5$; $8\times8 \to 1,1,16,1,1,64$ for $k=1..6$). Small-period points
stay put or cycle in small loops while the rest of the grid mixes: place
pedals / recurring chord loops on them, developing material on long orbits.

### 3.4 Shear = melody from harmony

$$\{(0,0),(4,0),(7,0)\} \xrightarrow{\;\Gamma\;} \{(0,0),(4,4),(7,7)\}$$

A vertical chord (same slot, three pitch classes) becomes a diagonal arpeggio
(three distinct slots) after one iteration — same pitch-class bag, rhythm
displacement for free. This is the map's unstable-eigenvector shearing
(direction of slope $\varphi$, the golden ratio).

### 3.5 The read (composition operator)

The piece reads, at section $s$, **column $s \bmod S$ of state $\Gamma^s(\mathrm{seed})$**:

$$\mathrm{cell}(v, s) = \mathrm{seed}\big[\Gamma^{-s}(v,\; s \bmod S)\big]$$

With the linear seed $\mathrm{seed}[v][s] = (v + s) \bmod 8$ on a $16 \times 8$
grid, the diagonal read is **exactly balanced**: the finished piece uses each
of the 8 motifs exactly 16 times (histogram $[16]^8$), while section columns
stay non-degenerate (distinct-motif counts $[8,8,4,8,8,4,8,8]$). The
conservation laws: (a) **per state** — every state is a permutation of the
seed, so the aggregate is constant under the dynamics; (b) **per piece** —
with the right seed the read is a perfect aggregate. Both verified.

### 3.6 Tension curve

$$\bar d(s) = \frac{1}{V}\sum_{v} \frac{d_V(v'_v, v) + d_S(s'_v, s)}{2},
\qquad (v', s') = \Gamma^{-s}(v, s \bmod S)$$

mean torus-displacement of the read cells from their seed positions. Verified
$[0.00, 2.75, 3.75, 3.50, 3.00, 3.00, 1.00, 3.50, 3.50, 5.00, 3.62, 2.50,
0.00]$ for $s = 0..12$: rises from the seed, peaks ($s{=}9$), returns
**exactly to 0 at the reprise** $s = P = 12$. HOME = near the seed / at the
reprise; TENSE = maximal displacement.

### 3.7 Cost

$\mathcal{O}(VS)$ per iteration; $S$ sections → $\mathcal{O}(S^2 V)$;
period discovery $\mathcal{O}(P \cdot VS)$ with $P \le 3\max(V,S)$
(Dyson–Falk bound, so the search is cheap and always terminates). Memory
$\mathcal{O}(VS)$.

## 4. Python implementation sketch

```python
"""generators/cat_map_torus.py — ACMTPC (Method 141)."""
from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer


def gamma(p, n1, n2):
    """Arnold cat map on the discrete torus Z_n1 x Z_n2."""
    x, y = p
    return ((x + y) % n1, (x + 2 * y) % n2)


def gamma_inv(p, n1, n2):
    """Coupled inverse (valid when n2 | n1; on square grids it reduces to
    the matrix inverse [[2,-1],[-1,1]])."""
    xp, yp = p
    y = (yp - xp) % n2
    x = (xp - y) % n1
    return (x, y)


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def cat_map_period(n1, n2):
    """Least P > 0 with Gamma^P == I mod (n1,n2). Dyson-Falk bound: P <= 3*max."""
    probe = (0, 1)
    cur = probe
    for k in range(1, 3 * max(n1, n2) + 5):
        cur = gamma(cur, n1, n2)
        if cur == probe and all(
            _gamma_k((x, y), n1, n2, k) == (x, y)
            for x in range(n1) for y in range(n2)
        ):
            return k
    raise ValueError("period search failed (grid too large?)")


def _gamma_k(p, n1, n2, k):
    cur = p
    for _ in range(k):
        cur = gamma(cur, n1, n2)
    return cur


class CatMapTorus:
    """The permutation engine. rows x cols grid; requires cols | rows (or square)."""

    def __init__(self, rows, cols):
        assert cols % rows == 0 or rows % cols == 0, "grid must be square or S|V"
        self.rows, self.cols = rows, cols
        self.P = cat_map_period(rows, cols)

    def apply(self, grid, steps=1):
        """Return Gamma^steps(grid)."""
        g = [row[:] for row in grid]
        for _ in range(steps):
            ng = [[0] * self.cols for _ in range(self.rows)]
            for v in range(self.rows):
                for c in range(self.cols):
                    nv, nc = gamma((v, c), self.rows, self.cols)
                    ng[nv][nc] = g[v][c]
            g = ng
        return g

    def read_cell(self, grid, v, s):
        """Motif id at UnitMatrix cell (v, s): column s mod S of state Gamma^s."""
        state = self.apply(grid, s)
        return state[v][s % self.cols]

    def tension_curve(self, seed, sections):
        """Mean torus-displacement of read cells from seed positions."""
        out = []
        for s in range(sections):
            tot = 0.0
            for v in range(self.rows):
                sv, sc = v, s % self.cols
                for _ in range(s):
                    sv, sc = gamma_inv((sv, sc), self.rows, self.cols)
                tot += (min(abs(sv - v), self.rows - abs(sv - v))
                        + min(abs(sc - s % self.cols),
                              self.cols - abs(sc - s % self.cols))) / 2.0
            out.append(tot / self.rows)
        return out


def compose_demo(seed, motifs, voices, bars=1, bpm=96, out_path="acmtpc.mid"):
    """Fill an 8-voice UnitMatrix from a 16x8 design torus (voice v = rows 2v,2v+1)."""
    V, S = 16, 8
    torus = CatMapTorus(V, S)
    BAR = 1920  # ticks, at tpb 480, 4 beats
    comp = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    comp.create_matrix(num_voices=len(voices), num_sections=S)
    for name, prog, _ in voices:
        comp.add_voice(name, program=prog, channel=0)
    for s in range(S):
        comp.add_section(f"S{s}", bars=bars)
    for v in range(len(voices)):
        base = voices[v][2]
        for s in range(S):
            m1 = torus.read_cell(seed, 2 * v, s)
            m2 = torus.read_cell(seed, 2 * v + 1, s)
            events = []
            for m in (m1, m2):
                for (slot, pco, dur16, vel) in motifs[m]:
                    events.append(MusicEvent(
                        pitch=base + pco, volume=vel,
                        start_tick=slot * 120, end_tick=(slot + dur16) * 120))
            unit = MusicUnit(events=events)
            unit.add_event(MusicEvent(0, 0, BAR, BAR))  # zero-drift landmark
            comp.fill_voice_section(voices[v][0], f"S{s}", unit)
    ok, msg = comp.validate()
    assert ok, msg
    comp.to_midi(out_path)
    return comp
```

The verified demo uses `seed[v][s] = (v + s) % 8`, 8 motifs of 5–6 notes
each, voices Lead FLUTE 60 / Harmony VIOLIN 64 / Counter STRING_ENSEMBLE 55 /
Pad SYNTH_PAD 48 / Organ CHURCH_ORGAN 41 / Pluck ACOUSTIC_GUITAR 57 /
Horn TRUMPET 62 / Bass BASS 36.

## 5. Verification (12/12)

| # | Check | Result |
|---|---|---|
| 1 | Bijection on square & S\|V grids; collisions on (4,8) | bijective (8,8),(16,8),(5,5),(12,12),(16,4); **16 collisions** on (4,8) |
| 2 | Periods + Dyson–Falk bound | P(2..10,75) = 3,4,3,10,8,6,30,100; P(16,8)=12; sweep 2..40 ≤ 3N |
| 3 | Fibonacci closed form | A^k = [[F_{2k−1},F_{2k}],[F_{2k},F_{2k+1}]], k=1..10 |
| 4 | Lyapunov exponent | measured 0.9620 vs ln((3+√5)/2) = 0.9624 |
| 5 | Continuous fixed points | Lucas(2k)−2 = 1,5,16,45,121,320 (A004146) |
| 6 | Discrete fixed-point census | 5×5 → 1,5,1,5,1,5; 8×8 → 1,1,16,1,1,64 |
| 7 | Shear: chord → arpeggio | {0,4,7}@slot0 → pcs [0,4,7], slots [0,4,7] |
| 8 | State conservation + balanced read | every state = 8 motifs × 16; piece histogram [16]^8 exact |
| 9 | Poincaré recurrence | section s+12 ≡ s over 41-section window |
| 10 | Tension curve | [0, 2.75, 3.75, 3.5, 3, 3, 1, 3.5, 3.5, 5, 3.62, 2.5, 0]; exact reprise at s=12 |
| 11 | Engine end-to-end | validate OK, 64 cells, MIDI 5259 B, exact aggregate |
| 12 | Determinism | identical construction → byte-identical MIDI |

Prototype: 8 voices × 8 sections × 1 bar, tpb 480, bpm 96, MIDI
`_web141/acmtpc_141.mid` (5259 B), WAV `_web141/acmtpc_141.wav` (3 916 844 B).

## 6. Musical Elements Framework

- **PITCH**: row axis = register/pitch-class circle (wrap = octave equivalence).
  Unstable eigenvector (slope φ) shears stacks into rising diagonal lines; the
  stable direction compresses. Pitch-class bag conserved (check 7); register
  assigned at realization via the voice band map.
- **RHYTHM**: column axis = metric circle; every iteration displaces slots
  (t → p + 2t mod T) — chords become arpeggios, downbeats become syncopation,
  no rhythmic rules written. Time wraps mod S → anacrusis across seams.
- **HARMONY**: identity = motif-id co-occurrence in a column — a multiset
  invariant of the dynamics; short-period points (A004146) host pedals and
  loops; Fibonacci-scaled section distances.
- **STRUCTURE**: sections = powers of Γ; period P = form length; Γ⁻¹ =
  retrograde; the piece is a Poincaré-recurrent orbit (loops/da-capo exact);
  tension curve = macro-form readout.
- **TEXTURE**: conservative — density constant, placement changes: seed
  clusters dissolve into uniform scatter (mixing) then reconverge at the
  reprise ("inhale/exhale"); collisions = densification dial; voice pairs
  (2 design rows per instrument) = per-cell two-motif polyphony.

## 7. UnitMatrix Integration

**Voices = rows**: 16 design rows → 8 musical voices (voice v = rows 2v,
2v+1, same register band, two motif streams per cell).

**Sections = columns = one iteration**: section s = read of state Γ^s(seed);
cell (v, s) = motifs at rows {2v, 2v+1}, column s mod 8 of state s. Extend to
P = 12 for the full tension arc and the exact reprise. Zero drift by
construction (terminal landmark at section_len; validate() True).

**Cells = MusicUnit**: two motifs' notes at 16th slots, transposed into the
voice band, landmark-padded to 1920 ticks.

**Candidate code path:** `generators/cat_map_torus.py` — `CatMapTorus`,
`TorusDesign`, `ACMTPCGenerator` (see sketch above); sibling of
`generators/markov_constraint.py`.

## 8. References

- Arnold, V. I., & Avez, A. (1968). *Ergodic Problems in Classical Mechanics*. Benjamin.
- Dyson, F. J., & Falk, H. (1992). "Period of a Discrete Cat Mapping." *Amer. Math. Monthly* 99(7), 603–614. doi:10.1080/00029890.1992.11995900.
- Franks, J. M. (1977). "Invariant Sets of Hyperbolic Toral Automorphisms." *Amer. J. Math.* 99(5), 1089–1095. doi:10.2307/2374001.
- Gaspari, G. (1994). "The Arnold Cat Map on Prime Lattices." *Physica D* 73, 352–372. doi:10.1016/0167-2789(94)90105-8.
- Chen, G., Mao, Y., & Chui, C. K. (2004). "A Symmetric Image Encryption Scheme Based on 3D Chaotic Cat Maps." *Chaos, Solitons & Fractals* 21, 749–761. doi:10.1016/j.chaos.2003.12.022.
- Akritas, P., Antoniou, I. E., & Pronko, G. P. (2001). "On the Torus Automorphisms: Analytic Solution, Computability and Quantization." *Chaos, Solitons & Fractals* 12, 2805–2814. doi:10.1016/S0960-0779(01)00094-7.
- Sloane, N. J. A. (ed.). OEIS A004146 (fixed points of iterates), A032170 (prime periodic orbits).
- Salter, J. R. (2009). "Chaos in Music." PhD diss., UNC Greensboro.
- Trott, M. (2006). *The Mathematica GuideBook for Numerics*, §2.4; Weisstein, E. W., "Arnold's Cat Map," MathWorld; Wikipedia, "Arnold's cat map" (rev. 2026-08-21).
- Web cache: `_web141/` (`wiki_arnold_cat_map.html/.txt`, `mathworld.html/.txt`, `oa1.json`, `oa2.json`, `cr_*.json`, `oeis.json`, `bing1/2.html`, `ddg1.html`, `s2.json` (429), `verify_141_ACMTPC.py`, `verify_141_output.txt`, `acmtpc_141.mid`, `acmtpc_141.wav`).
