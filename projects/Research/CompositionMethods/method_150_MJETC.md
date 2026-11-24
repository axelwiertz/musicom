# Method 150 — Mandelbrot–Julia Escape-Time Composition (MJETC)

- **ID:** 150
- **Paradigm:** Nature-Led (deterministic complex dynamical system $z \mapsto z^2 + c$; no sampling, no training, no physical ODE — the structure is a theorem of complex dynamics: connectedness locus, hyperbolic components, escape radius, period-doubling universality. Same family as 043 SATM / 115 KORC / 141 ACMTPC: deterministic dynamical geometry as the generative law.)
- **Layer:** concrete (LAYER_ARCHITECTURE.md) — one orbit iterate = one note event (pitch, onset, duration, velocity) filling a UnitMatrix cell; the (parameter-plane waypoint path, per-voice $c$/$z_0$ assignment, pitch ladder, tick scale) tuple is the plan, the simulated orbits are the realized cells.
- **Family:** complex-dynamics iteration. Siblings: 043 SATM (real ODE attractors — no parameter-plane grammar), 049 IFSMG (contractive affine maps — $z^2+c$ is non-affine, escape-time structured), 048 RBMPD / 053 LFC (stochastic walks — MJETC is deterministic), 030 RDTP / 070 CML-C (real-valued fields — complex plane), 002 Markov / 086 HMM (probabilistic — no escape-time determinism). **MJETC is the DB's first complex-dynamics / escape-time method.**
- **One-liner:** compose from the escape-time dynamics of the quadratic family $f_c(z) = z^2 + c$: iterate the critical orbit from $z_0 = 0$; the escape time $\tau(c)$ (first $n$ with $|z_n| > 2$) and the orbit itself map to pitch, duration, velocity and density; the Mandelbrot set's hyperbolic components (period-1 cardioid, period-2 bulb disk, period-3 bulbs, Feigenbaum cascade 1→2→4→8→16→chaos, period-3 window at −1.7549) supply a harmonic/metric grammar with the component **period** as the musical cycle length; the parameter-plane waypoint path = macro-form; Julia sets give the voices (connected field iff $c \in M$, Cantor dust iff $c \notin M$); the Green's function $G(c) = \lim 2^{-n}\log|z_n|$ is the continuous tension/pitch potential.

---

## 1. The mathematics

**Definition (Mandelbrot set).** $M = \{c \in \mathbb{C} : (f_c^n(0))_{n \ge 0} \text{ is bounded}\}$, $f_c(z) = z^2 + c$, i.e. $z_{n+1} = z_n^2 + c$, $z_0 = 0$. Equivalently $M$ is the **connectedness locus**: $c \in M \iff J(f_c)$ connected (Fatou–Julia). The boundary of $M$ is the **bifurcation locus** — near any boundary point the dynamics change abruptly under arbitrarily small parameter changes: the boundary is exactly the set of *musically unstable* parameters.

**Escape radius theorem.** If $|z_k| > 2$ for some $k$ then the orbit diverges. Proof: for $|z_k| > 2$ and $|c| \le |z_k|$ (true for all $k$ once $|z_k| > 2$ since $|c| \le 2$ on $M$), $|z_{k+1}| = |z_k^2 + c| \ge |z_k|^2 - |c| > |z_k|(|z_k| - 1) > |z_k|$ — the modulus strictly increases and diverges. Verified: 2000/2000 sampled bailouts satisfy the criterion exactly (check 1). Hence the **escape time** $\tau(c) = \min\{n : |z_n| > 2\}$ is well-defined for every $c \notin M$ and is the workhorse of the method.

**Hyperbolic components.** The interior of $M$ is conjecturally a union of hyperbolic components, each indexed by the **period** $p$ of its attracting cycle (density of hyperbolicity is open). Verified periods: cardioid (period 1, $c(\mu) = \frac{\mu}{2}(1 - \frac{\mu}{2})$, $|\mu| < 1$ — attracting fixed point); period-2 bulb = the *exact* disk $|c + 1| \le 1/4$ (attracting 2-cycle); period-3 bulbs at $c \approx -0.1226 + 0.7449i$ (upper) and $c \approx -1.7549$ (real "airplane"); superstable centres (critical orbit returns to 0 after exactly $p$ steps) found numerically: $c = -1$ ($p=2$), $-1.3107015$ ($p=4$), $-1.3815475$ ($p=8$), $-1.3969453$ ($p=16$) — all verified exact (check 4). **The period is the musical period.**

**Feigenbaum cascade.** Along the real axis the periods double $2 \to 4 \to 8 \to 16 \to \cdots$ accumulating at the Feigenbaum point $c_\infty \approx -1.401155189$ with universal ratio $\delta = 4.6692\ldots$ (Feigenbaum 1978); beyond it a chaotic band interspersed with periodic windows (period 3 at $c \approx -1.7549$, containing a mini-Mandelbrot — verified escape-time spike, check 8). The cascade is a built-in **metric-modulation ladder**; the period-3 window is a built-in **self-similar recapitulation** (mini-M copies of $M$ at arbitrarily small scales; exact self-similarity at Misiurewicz points).

**Green's function / Boettcher coordinate.** Douady–Hubbard: the complement of $M$ is conformally isomorphic to the complement of the unit disk via $\Phi$; the potential $G(c) = \log|\Phi(c)| = \lim_{n\to\infty} 2^{-n} \log|z_n(c)|$ is the capacity potential of $M$ — **continuous** in $c$ (verified: max $|\Delta G| = 3.3\times10^{-6}$, ratio max/mean 1.05 over 20k points — pure slope, no staircase, check 2) while raw $\tau$ is integer-staircased. The same Boettcher coordinate on the Julia-side gives $|\psi(f(z))| = |\psi(z)|^2$ (Wikipedia: Julia set).

**Julia sets.** $J(f_c)$ = boundary of the filled set $\{z_0 : |f_c^n(z_0)| \text{ bounded}\}$; iteration on $J$ is repelling/chaotic. $c \in M \Rightarrow J$ connected; $c \notin M \Rightarrow J$ is a Cantor set ("Fatou dust"). Verified via the critical orbit (Fatou–Julia): bounded for $c = -1.1$, escaping for $c = 1.1$; filled-set fractions 0.126 vs 0.00000 (check 6). **Connectedness = coherence, Cantor dust = total independence — the texture dial.**

**Symmetry.** $\tau(\bar c) = \tau(c)$ exactly (verified, check 5): conjugate parameters generate mirror melodies — free canon material and a redundancy trap.

## 2. Musical mapping (Musical Elements Framework + UnitMatrix)

**PITCH.** (a) *Escape-count reading*: $\tau \bmod 12 \to$ pc, or $\tau$ scaled to a ladder — quantized, staircased, harsh (a documented pitfall). (b) *Orbit reading*: the orbit $z_0, z_1, \dots$ is the melody — map $(\mathrm{Re}\, z_n, \mathrm{Im}\, z_n)$ (normalized per section) to the ladder. Interior orbits carry built-in tonal gravity: in the cardioid every orbit sinks monotonically to the attracting fixed point (verified: distance $\to 5.2\times10^{-12}$; $c=-1$ enters the exact 2-cycle $\{0,-1\}$ — check 9), so **HOME is a fixed point of the dynamics**, not a convention. Period-$p$ cycles oscillate among $p$ values = the motif; near-boundary orbits wander widely = TENSE; Misiurewicz/chaotic orbits = aperiodic angular motion. (c) *Potential reading*: $G(c)$ (or a large-radius smooth count $\nu = n - \log_2(\log|z_n|/\log R)$, $R \ge 256$) gives continuous pitch gradients across sections — the escape-time image made legato. External-ray angle $\arg \Phi(c)$ = a second pc source.

**RHYTHM.** Escape time is the duration dial ($\tau$ large near the boundary = long; small = short); the **cycle period $p$** is the ostinato length (period-3 bulb ⇒ 3-note loop; cascade ⇒ 1→2→4→8→16 foldings = metric growth); iteration index → tick grid (grid-locked: onset $= n \cdot \mathrm{step}$) or scaled (continuous). The escape-time field over a section = onset-density map (boundary filigree dense, interior sparse); Buddhabrot (density of escaping orbits) = a statistical rhythm layer.

**HARMONY.** The hyperbolic-component grammar: period-1 cardioid = one stable sonority (HOME); period-2 bulb (exact disk $|c+1| \le 1/4$) = binary alternation; period-3 bulbs = triadic cycles; higher periods = richer cycles. A chord = the simultaneous cycle values of a section's orbits; multiple voices share $c$ per section (Julia field) → vertical coherence by construction. The real-axis cascade = a modulation ladder through increasing periods; chaotic band + windows = TENSE; Misiurewicz points = preperiodic anchors whose Julia sets echo $M$ (self-similar harmony). No functional tonality: boundedness and period replace tonic/dominant.

**STRUCTURE.** The signature axis: macro-form = the parameter-plane waypoint path $c(t)$ (HOME: cardioid → LIFT: climb toward the boundary/external ray → TENSE: chaotic band, Misiurewicz climax → TURN: return to the cardioid; the period-3 window at $-1.7549$ recapitulates the whole set at smaller scale — self-similar form made audible). The Feigenbaum cascade is a built-in development (verified periods 2,4,8,16 at superstable centres); sections = waypoint regions; seams = parameter jumps or continuous curve samples; the boundary crossing = the "bifurcation locus" seam where everything changes.

**TEXTURE.** Escape-time field = the texture table (rows = voices, columns = time slots, cell = bounded/escaped + $\tau$ class → sustain vs event); Buddhabrot = statistical texture; interior/exterior stratification = pedal/mass vs pointillistic layers; per-voice $c$ = stratified Julia textures; shared $c$ with per-voice $z_0$ = hocketed independent streams over one harmonic field; $c \notin M$ = "Fatou dust" pointillism (total voice independence).

**UnitMatrix integration.** *Rows = voices = orbits*: `{z0_seed | c_trajectory, pitch_reading (orbit|escape|green), ladder, step_to_tick, cell_event_budget}`; shared-$c$ per section (Julia field, vertical coherence) or per-voice-$c$ (stratified fields; conjugate pairs = mirror canons). *Columns = sections = parameter waypoints*: `{c_region (cardioid|2-bulb|p-bulb|cascade step|chaotic band|window), waypoint c_j, max_iter, velocity_arc, texture_map}`. *Cells = MusicUnit*: orbit segment mapped to events — pitch = chosen reading, onset = iteration × step, duration = clamped (escape time / cycle period / sustained-to-seam), velocity = growth class. Fixed per-cell event counts (truncate + cycle-repeat interior orbits) and durations clamped to the seam (140's $\min(d_n, L - t_n)$ pattern) → **rows equal length by construction**, `validate()` passes, `to_midi()` exports, any SP renderer produces audio.

## 3. Python implementation sketch (generators/mandelbrot_escape.py — proposed)

```python
"""generators/mandelbrot_escape.py — MJETC (proposed)."""
import numpy as np

R = 2.0                    # escape radius: |z|>2 provably diverges

def escape_time(c, max_iter=512, R=2.0, smooth=False):
    """Vectorized escape time for complex c. Returns int array (or float if smooth).
    smooth uses the large-radius correction nu = n - log2(log|z_n|/log R); for
    continuous values use R >= 256 and max_iter ~ 1024, or use green_function()."""
    c = np.asarray(c, dtype=np.complex128)
    z = np.zeros_like(c); n = np.zeros(c.shape, dtype=np.int32)
    alive = np.ones(c.shape, dtype=bool)
    for _ in range(max_iter):
        z[alive] = z[alive] ** 2 + c[alive]
        alive &= np.abs(z) <= R
        n[alive] += 1
    if smooth:
        out = n.astype(float) + 1.0
        m = np.abs(z)
        ok = (m > 0) & (n < max_iter)
        out[ok] -= np.log2(np.log(m[ok]) / np.log(R))
        return out
    return n

def green_function(c, max_iter=512, big=1e100):
    """G(c) = lim 2^-n log|z_n| (capacity potential of M), overflow-safe."""
    c = np.asarray(c, dtype=np.complex128)
    z = np.zeros_like(c); G = np.zeros(c.shape)
    done = np.zeros(c.shape, dtype=bool)
    for n in range(1, max_iter + 1):
        z = z * z + c
        huge = np.abs(z) > big
        new = huge & ~done
        G[new] = np.log(np.abs(z[new])) / (2.0 ** n)
        done |= huge
        if done.all():
            break
    return G                       # interior survivors stay 0 (G -> 0 inside M)

def cycle_period(c, max_iter=4096, tol=1e-7, window=256):
    """Period of the attracting cycle for the critical orbit; 0 if escapes; -1 aperiodic.
    NOTE: fails at parabolic points (bulb roots, multiplier 1) — use superstable/near
    superstable centres as section anchors."""
    z, hist = 0j, [0j]
    for i in range(1, max_iter):
        z = z * z + c
        if abs(z) > 2.0:
            return 0
        for j in range(max(i - window, 0), i):
            if abs(z - hist[j]) < tol:
                return i - j
        hist.append(z)
    return -1

def superstable_center(p, lo, hi, steps=40000):
    """c minimizing |f^p_c(0)| on [lo,hi] — the exact centre of the period-p bulb."""
    cg = np.linspace(lo, hi, steps).astype(np.complex128)
    z = np.zeros_like(cg)
    for _ in range(p):
        z = z * z + cg
    return cg[np.argmin(np.abs(z))]

def orbit_events(c, z0, reading="orbit", ladder=None, max_events=32, max_iter=512):
    """One voice's orbit segment -> (pitch, onset, duration, velocity) events."""
    z = complex(z0); events = []
    for n in range(max_events):
        z = z * z + c
        if abs(z) > 2.0:                     # escaped: short note, loud-ish, then stop
            events.append((pc_from(z, reading), n, 1, 100)); break
        events.append((pc_from(z, reading), n, 1, int(20 * abs(z) + 10)))
    return events

def julia_field(c, seeds, steps=64):
    """(voices x time) bounded/escaped texture table for one section's harmonic field."""
    z = np.asarray(seeds, dtype=np.complex128)
    field = np.zeros((len(seeds), steps), dtype=bool)
    for t in range(steps):
        z = z * z + c
        field[:, t] = np.abs(z) <= 2.0
    return field

# Composition path: design parameter path c(t) -> per-section c_s, per-voice z0
# -> simulate orbits (vectorized O(V*S*I)) -> detect periods/escape times
# -> map to MusicEvents -> group by voice -> MusicUnit per cell (fixed event
#    budget, durations clamped to the seam) -> validate() -> to_midi() -> SP render.
```

## 4. References

- **Wikipedia: "Mandelbrot set"** (fetched 2026-11-24; cached `_web150_mjetc/wiki_mandelbrot.txt` + `.html`). Definition; connectedness locus; cardioid/bulbs; escape-time algorithm; Buddhabrot; Feigenbaum self-similarity; Misiurewicz points; density of hyperbolicity.
- **Wikipedia: "Julia set"** (fetched 2026-11-24; cached `_web150_mjetc/wiki_julia.txt`). Filled set, Cantor dust, escape radius $R^2 - R \ge |c|$, Boettcher potential $|\psi(f(z))| = |\psi(z)|^2$.
- **Weisstein, E. W. "Mandelbrot Set." MathWorld** (fetched 2026-11-24; cached `_web150_mjetc/mathworld_mandelbrot.txt`).
- **Douady, A. & Hubbard, J. H. (1984–85).** *Étude dynamique des polynômes complexes I–II.* Publ. Math. Orsay. / "Exploring the Mandelbrot set" in *The Mandelbrot Set, Theme and Variations* (MSRI 1989). Connectedness; Boettcher coordinate; external rays.
- **Feigenbaum, M. J. (1978).** "Quantitative universality for a class of nonlinear transformations." *J. Stat. Phys.* 19, 25–52.
- **Madden, C. (1999).** *Fractals in Music: Introductory Mathematics for Musical Analysis.* High Art Press.
- **Pressing, J. (1988).** "Nonlinear maps as generators of musical design." *Computer Music Journal* 12(2), 35–46.
- **Bidlack, R. (1992).** "Chaotic systems as simple electronic musical instruments." *Perspectives of New Music* 30(1).
- **Verified prototype:** `_web150_mjetc/verify_mjetc.py` → `_web150_mjetc/verify_mjetc_results.txt` — **10/10 checks pass**.
- **Novelty check (2026-11-24):** no existing method composes from $z^2+c$ / escape-time dynamics (grep audit in the DB section; nearest neighbours 043/049/040/048/053/030/070 are real-domain or stochastic).

## 5. Pitfalls (summary)

Parabolic points defeat naive period detection → anchor at superstable centres; raw $\tau$ is staircased → use $G$ or large-$R$ smooth count; $\tau \to \infty$ at the boundary → cap iterations and budget cells; overflow → bail at $|z|>2$ (verified sufficient); "bounded" ≠ membership → confirm with the period test; real-axis paths are flat (conjugate symmetry) → keep 2D paths, use conjugates deliberately; zero drift → fixed cell budgets + seam clamping; chaotic regions have no cadence → resolve by returning to the cardioid.
