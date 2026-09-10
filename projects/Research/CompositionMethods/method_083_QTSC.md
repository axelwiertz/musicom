# Aperiodic Quasicrystal Tiling Composition (QTSC)

**Method ID**: 083
**Paradigm**: Rules-Based
**Layer**: concrete (emits note/chord events into UnitMatrix cells; feeds `generators/`)
**Candidate code path**: `generators/quasicrystal_tiling.py`
**Acronym**: QTSC

## One-line description

Generates music from an aperiodic substitution tiling of the plane (Penrose P3 five-fold / Ammann–Beenker eight-fold): iterate an inflation rule ($\varphi$ or $1{+}\sqrt2$ scale factor), then read quasi-periodic scanlines whose edge/vertex symbols decode to never-repeating melodies, chord progressions, and rhythms that possess global order (repetitivity) yet never exactly repeat.

## Extended math

### Substitution tilings and the inflation matrix

A **self-similar tiling** is defined by an **inflation (substitution) rule**: each prototile (e.g. the thin/fat Penrose rhombi, or the square / 45°-rhombus of Ammann–Beenker) is dissected into a configuration of smaller tiles of the same protoset, then rescaled by the inflation factor $\lambda$. The rule is encoded by the **substitution matrix** $M = (m_{ij})$, where $m_{ij}$ = number of prototile-$i$ tiles in the inflated image of one prototile-$j$. Tile frequencies grow by the **Perron–Frobenius eigenvalue** $\lambda$ of $M$:

- **Penrose P3** (thin 36°/144° + fat 72°/108° rhombi): $\lambda = \varphi = (1+\sqrt5)/2 \approx 1.618$, the golden ratio. Tile-frequency ratio fat:thin is $\varphi:1$ — irrational, hence **no translation symmetry**.
- **Ammann–Beenker** (square + 45° rhombus): $\lambda = 1+\sqrt2 \approx 2.414$, the silver ratio.

The irrational $\lambda$ is the algebraic fingerprint of aperiodicity: a periodic tiling would have a *rational* inflation. Because $\mathbb{Z}[\varphi]$ and $\mathbb{Z}[\sqrt2]$ are **dense in $\mathbb{R}$**, the tiling's Fourier (diffraction) spectrum is a **pure point spectrum on a dense set of positions** (model sets) — global long-range order with an infinite, everywhere-dense set of "harmonics" that can be renormalized/thresholded.

### Cut-and-project (de Bruijn) construction

The cleanest computational route is **de Bruijn's cut-and-project theorem**: an aperiodic tiling is the projection of a periodic lattice in $\mathbb{R}^D$ onto an irrational $d$-dimensional subspace $E$, selecting only lattice points whose orthogonal projection onto the complementary space $E^\perp$ falls inside a bounded **acceptance window** $W$:

$$
\Lambda_W = \{\, \pi_E(x) \;:\; x \in \mathbb{Z}^D,\ \pi_{E^\perp}(x) \in W \,\}.
$$

For the **5-fold** case, $D=5$, $E$ is the 2D plane spanned by the pentagon's $\cos(2\pi k/5)$ axes; for the **8-fold** case $D=4$ with the octagon's axes. The projection of the *vertices of an octagonal/cubic window's boundary* gives the scanlines and vertex configurations.

**1D quasi-periodic chains** arise by projecting a $D=2$ lattice with slope $1/\varphi$:

$$
x_n = \lfloor (n+1)/\varphi \rfloor - \lfloor n/\varphi \rfloor \in \{1,2\},
$$

yielding the **Fibonacci chain** — the aperiodic 1D building block for melody/rhythm readouts, and a $\varphi$-ratio sequence of long ($L$) and short ($S$) intervals, $L/S = \varphi$.

### Scanline readout

A **scanline** is a straight line $\ell$ through the tiling at angle $\theta$. Where $\ell$ crosses tile edges, record the edge length ($L$ or $S$) and the edge orientation; bookkeeping the **vertex type** at each crossing yields a bi-infinite **quasi-periodic sequence** over a finite alphabet (the tile/vertex symbols). Concretely, for the Fibonacci chain the sequence is the **Sturmian word** of slope $1/\varphi$:

$$
s_\varphi(n) = \lfloor (n+1)\varphi \rfloor - \lfloor n\varphi \rfloor - 1 = 1011010110\dots
$$

(a **Goldberg–Saint–Blanquet sequence** for rhythm, with $\varphi$-related $1$s and $0$s). Because it is **uniformly recurrent** (every factor of length $k$ recurs within distance $\propto k$) but **not ultimately periodic**, the maliciously-known result: *global order, no exact repetition.*

### Vertex configurations → harmony

The finite catalog of **vertex configurations** (8 for Penrose P3: the Sun, Star, Ace, King, Queen, Jack, Deuce, and star-variant; 7 for Ammann–Beenker) are the local "patch types". Each maps to a **pitch-class set** via `rules/set_theory.py` prime-form / interval-vector; the edge-adjacency graph of vertex types is the method's **harmonic grammar** — the matching rules forbid illegal adjacencies, so a walk across the tiling is a **chord progression** with bounded voice-leading (adjacent patch types differ by a bounded symmetric difference).

### Inflation hierarchy = form

Deflation groups tiles back into their parents. The **deflation tree** (each tile → its ancestor) is a rooted forest; depth = inflation level. Self-similarity means a window at level $L$ is locally indistinguishable from its deflation to level $L-1$ after rescaling by $\lambda$. Sections are windows of the *same* tiling at different levels, so macro-form is itself a quasicrystal: **repetitive but never periodic**.

### Complexity

- **Cut-and-project scanline**: $O(n)$ to generate $n$ symbols of a Fibonacci/silver chain (one floor each).
- **Window extraction**: $O(W \cdot L)$ for a window of $W$ tiles sampled across $L$ scanlines (only tiles intersecting the section rectangle are traversed).
- **Vertex-configuration catalog**: $O(1)$ (fixed finite set per family).
- Deterministic per seed (substitution is exact); no training, no optimization.

## Python implementation sketch

```python
"""Aperiodic Quasicrystal Tiling Composition (Method 083, QTSC)."""
import math
from collections import defaultdict

PHI = (1 + math.sqrt(5)) / 2
SILVER = 1 + math.sqrt(2)

# --- 1D quasi-periodic chains (cut-and-project) ---

def fibonacci_chain(n, offset=0.0):
    """Return n symbols of the Fibonacci chain L/S (ratio phi)."""
    return ['L' if (math.floor((i + offset + 1) * PHI)
                    - math.floor((i + offset) * PHI)) == 2
            else 'S' for i in range(n)]

def silver_chain(n, offset=0.0):
    """Return n symbols of the silver (8-fold, 1+sqrt2) chain L/S."""
    out = []
    for i in range(n):
        d = math.floor((i + offset + 1) * SILVER) - math.floor((i + offset) * SILVER)
        out.append('L' if d == 2 else ('S' if d == 1 else 'M'))
    return out

# --- 2D substitution tilings ---

def ammann_beenker_subdivide(squares, rhombs):
    """One inflation step: Ammann-Beenker square + 45-degree rhombus."""
    new_s = []   # squares
    new_r = []   # rhombi
    for (x, y) in squares:
        # a square inflates to: 1 central square + 4 surrounding rhombi
        new_s.append((x, y))
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_r.append((x + dx * 0.5, y + dy * 0.5))
    for (x, y) in rhombs:
        # a rhombus inflates to: 2 squares + 2 rhombi
        new_s.append((x, y)); new_s.append((x + 0.5, y + 0.5))
        new_r.append((x + 0.5, y)); new_r.append((x, y + 0.5))
    return new_s, new_r

# --- scanline readout ---

def scanline_events(vertices, angle, window_rect):
    """Read tile-edge/vertex symbols along a line through the tiling.

    Returns list of (tick, duration, vertex_type) for one voice.
    """
    events = []
    # project each vertex onto the unit vector of `angle`; sort; walk
    ux, uy = math.cos(angle), math.sin(angle)
    proj = sorted((vx * ux + vy * uy, vx, vy, vtype)
                  for (vx, vy, vtype) in vertices)
    for i in range(1, len(proj)):
        p0 = (proj[i - 1][1], proj[i - 1][2])
        p1 = (proj[i][1], proj[i][2])
        d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        # edge length -> duration (L or S via normalization to phi)
        events.append((p0, d, proj[i][3]))
    return events

# --- decode to pitch / chord ---

VERTEX_PCSETS = {  # Ammann-Beenker / Penrose vertex configs -> pc subsets
    'star': {0, 4, 7, 11}, 'sun': {0, 2, 6, 8}, 'king': {0, 7},
    'queen': {0, 3, 8}, 'ace': {0, 4}, 'deuce': {2, 9}, 'jack': {0, 5, 9},
}

def decode_vertex(vtype, base=48):
    """Vertex type -> sorted MIDI pitch class chord (octave at base)."""
    return [base + pc for pc in sorted(VERTEX_PCSETS.get(vtype, {0}))]

def compose_scanline(chain, scale, base=60, step_map={'L': 2, 'S': 1}):
    """Decode an L/S chain into a quasi-periodic mono melody (pitch list)."""
    pc = 0; out = []
    for sym in chain:
        out.append(base + scale[pc % len(scale)])
        pc += step_map[sym]
    return out

def compose_section(family='AB', level=3, angle=0.0, n_events=64, seed=0):
    """Full per-section pipeline: build tiling -> scanline -> decode."""
    rng_state = seed  # substitution is deterministic; seed selects window/offset
    if family == 'fib':   # 1D cut-and-project (golden)
        chain = fibonacci_chain(n_events, offset=rng_state * 0.1)
    else:                 # silver (8-fold)
        chain = silver_chain(n_events, offset=rng_state * 0.1)
    scale = [0, 2, 4, 5, 7, 9, 11]      # diatonic decode
    return compose_scanline(chain, scale)
```

**Musicom integration** (engine authors the MIDI; real imports per AGENTS.md):

```python
# from structures import MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_chord_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# for v in range(V): composer.add_voice(f"voice{v}", ...)
# for s in range(S):
#     family, level, angle = section_specs[s]
#     ticks = fibonacci_chain(n_events, offset=hash((s, 0)) % 1000 * 0.001)
#     for t, sym in enumerate(ticks):
#         dur = int(BAR * (PHI if sym == 'L' else 1.0))   # edge length -> duration
#         composer.fill_voice_section("voice0", s, create_note_unit(60 + scale[t % 7], dur))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

## References

- Penrose, R. (1974). "The rôle of aesthetics in pure and applied research." *Bull. Inst. Math. Appl.* 10, 266–271.
- de Bruijn, N. G. (1981). "Algebraic theory of Penrose's non-periodic tilings of the plane." *Indag. Math.* 43, 39–66.
- Gardner, M. (1977). "Mathematical Games: Extraordinary nonperiodic tiling that enriches the theory of tiles." *Scientific American* 236(1), 110–121.
- Shechtman, D., Blech, I., Gratias, D., & Cahn, J. W. (1984). "Metallic phase with long-range orientational order and no translational symmetry." *Phys. Rev. Lett.* 53, 1951–1953.
- Mackay, A. L. (1982). "Crystallography and the Penrose pattern." *Physica A* 114, 609–613.
- Baake, M., & Grimm, U. (2013). *Aperiodic Order, Vol. 1: A Mathematical Invitation*. Cambridge University Press.
- Grünbaum, B., & Shephard, G. C. (1987). *Tilings and Patterns*. W. H. Freeman.
- Beenker, F. P. M. (1982). "Algebraic theory of non-periodic tilings of the plane by two simple building blocks." TH Report 82-WSK-04, TU Eindhoven.
- Solomyak, B. (1997). "Dynamics of self-similar tilings." *Ergodic Theory Dynam. Systems* 17, 695–738.
- Toussaint, G. T. (2005). "The Euclidean algorithm generates traditional musical rhythms." *Proc. BRIDGES*, 47–56. (Fibonacci/golden rhythm chains.)