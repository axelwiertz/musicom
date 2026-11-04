# Method 134 — Cellular Sheaf Cohomology Composition (CSCC)

- **Paradigm:** Rules-Based
- **Layer:** abstract (feeds `rules/subset_network.py`; concrete feeder candidate `generators/sheaf_projection.py`)
- **DB entry:** `methods_db.md` § "Cellular Sheaf Cohomology Composition (CSCC) (Method 134)"
- **Verification harness:** `verify_134_CSCC.py`, `verify_134b_CSCC.py`

---

## 1. One-line idea

Compose the *form* as a **cellular sheaf** over a section graph: each section carries a harmonic state
space (a stalk), each seam carries a linear restriction map naming which coordinates must agree, and the
composition is controlled by three computable numbers — the **coherence budget** $\dim H^0$, the
**rigidity** $\dim H^1$, and the **measured incoherence** $\|\delta x^\*-b\|$ — plus a **cut set**
(spanning tree) that says where cadences can fall.

## 2. Why this is not a re-skin of an existing method

| Existing | What it constrains | What CSCC adds |
|---|---|---|
| 011 voice-leading graph search | shortest path in a chord graph | no linear structure; CSCC solves a *linear system* over all sections at once |
| 104 parsimonious subset sequences | greedy single-note moves | local, order-dependent; CSCC is global and order-free |
| 129 subshift of finite type | forbidden *symbols* | symbolic, no gluing equation; CSCC's constraints are linear equalities between section states |
| 133 z-relations | set-class identity flips | class-to-class relation; CSCC relates *states* across a graph |
| 030 reaction–diffusion / 036 sandpile | field evolution on a lattice | dynamical; CSCC is static algebra with a cohomological obstruction |

Prior art in *theory*, none in the DB: cellular sheaves (Curry 2014; Ghrist 2014), the sheaf Laplacian
(Hansen–Ghrist 2019), the Matrix-Tree theorem (Kirchhoff 1847). Musical precedents exist for the
*objects* (Lewin's transformational networks = group-valued edge labels; Shepard/Risset = a loop whose
holonomy is a transposition) but not for the composition method.

## 3. Extended mathematics

### 3.1 The sheaf

Section graph $G=(V,E)$, connected components $c$. For each vertex $v$ a stalk $\mathcal F(v)\cong\mathbb R^{d_v}$;
for each edge $e=uv$ a stalk $\mathcal F(e)\cong\mathbb R^{d_e}$ and linear restriction maps

$$\rho_{u\triangleleft e}:\mathcal F(u)\to\mathcal F(e),\qquad \rho_{v\triangleleft e}:\mathcal F(v)\to\mathcal F(e).$$

Cochains: $C^0=\bigoplus_{v}\mathcal F(v)$, $C^1=\bigoplus_{e}\mathcal F(e)$ (0-cochains = an assignment of a
harmonic state to every section; 1-cochains = an assignment of seam data to every seam).

### 3.2 Coboundary, cohomology, Euler–Poincaré

$$(\delta x)_e=\rho_{u\triangleleft e}x_u-\rho_{v\triangleleft e}x_v,\qquad
H^0=\ker\delta,\qquad H^1=C^1/\operatorname{im}\delta .$$

$$\boxed{\ \dim H^0=\sum_v d_v-\operatorname{rank}\delta,\qquad
\dim H^1=\sum_e d_e-\operatorname{rank}\delta\ }$$

$$\dim H^0-\dim H^1=\sum_v d_v-\sum_e d_e\qquad(\text{Euler–Poincaré; verified 8/8})$$

$H^0$ = assignments obeying **every** seam (the plan's coherence budget); $H^1$ = seam data that **no**
assignment can produce (rigidity / redundancy of the demands).

### 3.3 Three recipes

**R1 — common-tone (gluing).** $\rho$ = 0/1 selection of shared pcs. Verified on ii7–V7–Imaj7–vi7 in C:
seams share $\{2,5\},\{7,11\},\{0,4,7\},\{0,9\}$ ⇒ $\sum d_e=9$, $\operatorname{rank}\delta=9$,
$\dim H^0=39$ of 48, $H^1=0$ — the loop closes, coherence ratio $0.81$.

**R2 — transposition (drift).** $\rho_{u\triangleleft e}=T_k$, $\rho_{v\triangleleft e}=I$ ⇒ the cocycle demands
$x_v=T_kx_u$. Around a loop, $h=\prod_e T_{k_e}=T_{\sum k_e}$, and

$$\dim H^0=\dim\ker(I-h)=\#\{\text{orbits of }h\text{ on }\mathbb Z_{12}\}.$$

Verified: $h=T_{+4}\Rightarrow 4$ orbits $\{0,4,8\},\{1,5,9\},\{2,6,10\},\{3,7,11\}$; $h=T_{+5}\Rightarrow 1$;
$h=T_{+12}=I\Rightarrow 12$. Musical reading: a lap transposing by $+4$ returns with four major-third
orbits intact; a lap transposing by $+5$ keeps **one** pc and drags eleven — Shepard's endless scale
(1964) / Risset's glissando (1969) in harmonic space.

**R3 — permutation (voice exchange).** $\rho$ = permutation matrices: "voice $i$ of $u$ becomes voice
$\pi(i)$ of $v$". Verified for $p_{01}=(2,1,0),p_{12}=(1,2,0),p_{23}=(0,2,1),p_{30}=(1,2,0)$: product
$=(0\,1\,2)$, one orbit ⇒ $\dim H^0=1,\ \dim H^1=1$ — exactly one voice returns to its own register.

### 3.4 Tension = least-squares repair

Compose seam demands $b\in C^1$ and solve the sheaf-Laplacian normal equations

$$\min_x\|\delta x-b\|_2^2\ \Longrightarrow\ (\delta^\top\delta)\,x=\delta^\top b,\qquad
\ker(\delta^\top\delta)=H^0 .$$

Per-seam residual $r_e=\|(\delta x^\*-b)|_e\|$ is the **tension curve**; $\|r\|$ is the part of the demand no
harmonic state can honour. Verified on the voice-exchange loop with a unit demand at every seam:
$\|r\|=2/\sqrt3=1.1547$, uniform $1/3$ per coordinate. To report in semitones, pull $r$ back through the
pc/semitone embedding — raw residuals are in stalk units and are not comparable across $d_v$.

### 3.5 Cadence = cut = spanning tree

If every seam map is onto its image, a **forest** satisfies $H^1=0$ (verified for path and star), so all
obstruction lives in the cycle space, $\dim=|E|-|V|+c$. Consistency is therefore restored by cutting one
seam per independent cycle — i.e. by choosing a spanning tree of honoured seams. Kirchhoff:

$$\tau(G)=\det L_{11}\quad(\text{any cofactor of the graph Laplacian}).$$

Verified: $\tau(C_4)=4$, $\tau(C_5)=5$, $\tau(K_4)=16$, $\tau(\text{path}_3)=1$. Each un-cut edge is a seam
the piece commits to; each cut edge is a place a cadence may fall.

### 3.6 Tension grammar

| function | operation |
|---|---|
| HOME | a point of $H^0$ near the home chord, $r=0$ |
| LIFT | raise $\dim H^0$ (share more coordinates / lower $d_e$) |
| TENSE | demand $b\notin\operatorname{im}\delta$, or add a loop (cycle-space dim ↑) |
| TURN | choose another spanning tree, or apply the holonomy to the reprise |

## 4. Verified numbers (2026-11-04, exact Fraction elimination)

| sheaf | $\lvert V\rvert$ | $\lvert E\rvert$ | $\sum d_v$ | $\sum d_e$ | $\operatorname{rank}\delta$ | $\dim H^0$ | $\dim H^1$ |
|---|---|---|---|---|---|---|---|
| path 0–1–2 (masks {0,4,7},{0,4}) | 3 | 2 | 36 | 5 | 5 | 31 | 0 |
| star (forest) | 3 | 2 | 36 | 3 | 3 | 33 | 0 |
| ii7–V7–Imaj7–vi7 (C4) | 4 | 4 | 48 | 9 | 9 | 39 | 0 |
| $T_{+1}$×4 (lap $+4$) | 4 | 4 | 48 | 48 | 44 | 4 | 4 |
| $T_{+1}$×5 (lap $+5$) | 5 | 5 | 60 | 60 | 59 | 1 | 1 |
| $T_{+1}$×12 (lap $0$) | 12 | 12 | 144 | 144 | 132 | 12 | 12 |
| voice-exchange C4 ($\mathbb R^3$) | 4 | 4 | 12 | 12 | 11 | 1 | 1 |

Euler–Poincaré: 8/8. Forest⇒$H^1=0$: 2/2. $\tau$: C4 4, C5 5, K4 16, path 1. Repair residual 1.1547.

## 5. Python implementation sketch

```python
# rules/subset_network.py — CSCC (Method 134)
from fractions import Fraction
import itertools
import numpy as np


class CellularSheaf:
    """Stalks per vertex, restriction-map pairs per edge."""

    def __init__(self, dims: dict, edges: list):
        # edges: [(u, v, A_u, A_v, tag)] with A_u: d_e x d_u, A_v: d_e x d_v
        self.dims = dict(dims)
        for (u, v, A_u, A_v, _t) in edges:
            assert A_u.shape[0] == A_v.shape[0], f"seam {u}-{v}: d_e mismatch"
            assert A_u.shape[1] == self.dims[u] and A_v.shape[1] == self.dims[v], \
                f"seam {u}-{v}: restriction map does not match stalk dims"
        self.edges = edges

    # ---- delta -------------------------------------------------------
    def coboundary(self):
        verts = sorted(self.dims)
        off, n = {}, 0
        for v in verts:
            off[v] = n
            n += self.dims[v]
        de = sum(A_u.shape[0] for _, _, A_u, A_v, _ in self.edges)
        D = [[0] * n for _ in range(de)]
        r = 0
        for (u, v, A_u, A_v, _t) in self.edges:
            k = A_u.shape[0]
            for i in range(k):
                for j in range(self.dims[u]):
                    if A_u[i, j]:
                        D[r + i][off[u] + j] += int(A_u[i, j])
                for j in range(self.dims[v]):
                    if A_v[i, j]:
                        D[r + i][off[v] + j] -= int(A_v[i, j])
            r += k
        return D, off, de

    # ---- exact rank (float rank flips near tolerance!) ---------------
    @staticmethod
    def rank(M):
        A = [[Fraction(x) for x in row] for row in M]
        rows, cols, r = len(A), (len(A[0]) if A else 0), 0
        for c in range(cols):
            piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
            if piv is None:
                continue
            A[r], A[piv] = A[piv], A[r]
            p = A[r][c]
            A[r] = [x / p for x in A[r]]
            for i in range(rows):
                if i != r and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [a - f * b for a, b in zip(A[i], A[r])]
            r += 1
            if r == rows:
                break
        return r

    # ---- H^0 / H^1 ---------------------------------------------------
    def cohomology(self):
        D, off, de = self.coboundary()
        dv = sum(self.dims.values())
        rk = self.rank(D)
        h0, h1 = dv - rk, de - rk
        assert h0 - h1 == dv - de, "Euler-Poincare violated — malformed sheaf"
        return dict(h0=h0, h1=h1, rank=rk, dv=dv, de=de)

    # ---- harmonic repair ---------------------------------------------
    def repair(self, demands=None):
        D, off, de = self.coboundary()
        A = np.array(D, dtype=float)
        b = np.zeros(de) if demands is None else np.asarray(demands, dtype=float)
        x, *_ = np.linalg.lstsq(A, b, rcond=None)
        res = A @ x - b
        return x, res                       # res = per-seam tension curve

    # ---- holonomy of a loop ------------------------------------------
    def holonomy(self, cycle):
        """cycle = ordered list of (edge_index, direction); returns the product matrix."""
        h = None
        for ei, fwd in cycle:
            _, _, A_u, A_v, _t = self.edges[ei]
            G = np.linalg.pinv(A_v) @ A_u           # transport u -> v
            h = G if h is None else G @ h           # order matters unless maps commute
        return h

    def drift_orbits(self, h):
        """For a transposition/permutation holonomy: orbits = pcs that survive a lap."""
        seen, orbits = set(), []
        for i in range(h.shape[0]):
            if i in seen:
                continue
            c, j = [], i
            while j not in seen:
                seen.add(j)
                c.append(j)
                j = int(np.argmax(h[:, j]))
            orbits.append(c)
        return orbits


def spanning_trees(n_vertices, edges):
    """Enumerate seam cuts: every spanning tree = one cadential closure."""
    E = list(range(len(edges)))
    out = []
    for combo in itertools.combinations(E, n_vertices - 1):
        parent = list(range(n_vertices))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        ok = True
        for ei in combo:
            u, v = edges[ei][0], edges[ei][1]
            ru, rv = find(u), find(v)
            if ru == rv:      # cycle
                ok = False
                break
            parent[ru] = rv
        if ok and len({find(i) for i in range(n_vertices)}) == 1:
            out.append(combo)
    return out
```

## 6. UnitMatrix realisation

```python
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (UnitMatrixComposer, create_note_unit,
                                           _unit_from_events)

plan = sheaf.cohomology()                  # {'h0': 39, 'h1': 0, ...}
x, res = sheaf.repair(demands)             # per-section state, per-seam tension

composer = UnitMatrixComposer(bpm=96, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=max(dims.values()), num_sections=len(sections))
for name, program in voice_plan:           # rows = stalk coordinates
    composer.add_voice(name, program=program, channel=chan)
for j, sec in enumerate(sections):         # columns = vertices
    composer.add_section(sec, bars=bars[j])

for v, name in enumerate(voice_plan):
    for j, sec in enumerate(sections):
        events = projection_feeder(x[sec], v, section_len)   # stalk -> pitches
        composer.fill_voice_section(name, sec, _unit_from_events(events, section_len))

ok, msg = composer.validate()              # zero-drift gate — MUST be True
composer.to_midi("out/sheaf134.mid")
```

Rows = stalk coordinates (a *player* row needs identity restriction maps; a *line* row may permute).
Columns = section-graph vertices. Cells = `MusicUnit`, padded with silent units so every row ends at the
section length (the usual zero-drift rule).

## 7. References

1. Curry, J. M. (2014). *Sheaves, Cosheaves and Applications*. PhD thesis, University of Pennsylvania.
2. Ghrist, R. (2014). *Elementary Applied Topology*, ch. 2. Createspace.
3. Hansen, J., & Ghrist, R. (2019). Toward a spectral theory of cellular sheaves. *J. Appl. Comput. Topol.* 3, 315–358.
4. Kirchhoff, G. (1847). Über die Auflösung der Gleichungen, auf welche man bei der Untersuchung der linearen Vertheilung galvanischer Ströme geführt wird. *Ann. Phys. Chem.* 72, 497–508.
5. Lewin, D. (1987/1998). *Generalized Musical Intervals and Transformations*. Yale UP / Oxford UP.
6. Shepard, R. N. (1964). Circularity in judgments of relative pitch. *JASA* 36(12), 2346–2353.
7. Risset, J.-C. (1969). *Mutant* (tape); the Risset glissando.
8. Cohn, R. (1997). Neo-Riemannian operations, parsimonious trichords, and their Tonnetz representations. *JMT* 41(1), 1–66.
9. Forte, A. (1973). *The Structure of Atonal Music*. Yale UP (pc-set vocabulary used inside stalks).

## 8. Pitfalls (compressed)

$H^1\neq$ tension (it also counts free seam coordinates); $H^0$ scales with stalk dimension (use a ratio);
forest $\Rightarrow H^1=0$ always; invertible-transport and projection recipes need separate code paths;
holonomy is order-dependent (L/R/P do not commute); nonzero holonomy = modulation, not return; residual
units are stalk units, not semitones; decide player-vs-line once; float rank is unreliable (use exact
Fraction elimination); $\tau(G)$ counts labelled trees (enumerate, don't sample); $\dim H^0>1$ leaves the
plan under-determined (choose min-norm or home projection); pad unequal $d_v$ sections to zero-drift; fix
the coordinate basis before building maps.
