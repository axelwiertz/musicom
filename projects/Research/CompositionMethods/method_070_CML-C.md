# Method 070 — Coupled Map Lattice Composition (CML-C)

> **Paradigm:** Nature-Led (Physical/Emergent)
> **One-liner:** Generates music from the spatiotemporal chaos of a ring of diffusively coupled logistic maps — site state → pitch, Lyapunov exponent → rhythm, cluster synchronization → harmony, Kaneko pattern regime → macro-form.

---

## 1. Overview

Coupled Map Lattice Composition (CML-C) treats composition as the *spatiotemporal dynamics* of a lattice of coupled chaotic oscillators. Each lattice site is a discrete-time logistic map; sites are coupled diffusively to their nearest neighbours on a ring. The resulting system (Kaneko 1983–1993) exhibits a rich phase diagram of spatiotemporal patterns — frozen random patterns, pattern selection (traveling waves), defect turbulence, and fully developed turbulence — all of which transfer directly to musical parameters. Because the dynamics are deterministic, CML-C is **seedable and fully reproducible**; because they are chaotic, the output is **non-repeating** with stable statistical texture.

Where 043 SATM (Strange Attractor Trajectory Mapping) drives music from a *single* 3-D chaotic attractor (temporal chaos only) and 028 CMCG uses coupled maps merely to modulate granular-synthesis micro-timing (a DSP role), CML-C uses the *lattice itself* — both time and space — as chaotic compositional degrees of freedom. The lattice index is the natural bridge to the UnitMatrix: sites → voices (rows) or harmonic slots (columns), and synchronization clusters → chord/voicing groups.

---

## 2. The Core Dynamical System

### 2.1 The coupled logistic lattice

The canonical diffusive CML on a ring of $L$ sites is

$$x_i(t+1) = (1-\varepsilon)\,f\big(x_i(t)\big) + \frac{\varepsilon}{2}\Big[f\big(x_{i-1}(t)\big) + f\big(x_{i+1}(t)\big)\Big],\qquad i = 1,\dots,L \pmod L,$$

with the local map

$$f(x) = 1 - a\,x^2,\qquad a \in [1.4,\, 2.0],\qquad x_i \in [-1,\,1].$$

- **$a$** (nonlinearity) tunes the local map from period-1 → period-2 → … → chaos (the logistic map's period-doubling cascade reaches chaos at $a \approx 1.40115$ and full chaos at $a = 2$).
- **$\varepsilon$** (coupling strength) trades *local* chaotic independence ($\varepsilon = 0$: $L$ decoupled maps) against *global* synchronization ($\varepsilon \to 1$: consensus).
- **$L$** (lattice size) is the polyphony knob.

### 2.2 The invariant density (why the raw pitch fold is U-shaped)

At $a = 2$ the logistic map is conjugate to the Bernoulli shift via $x = \sin(\pi u/2)$, and its invariant density is

$$\pi(x) = \frac{1}{\pi\sqrt{1-x^2}},\qquad x\in(-1,1).$$

This density concentrates mass near the edges $x \to \pm 1$, so a raw linear pitch fold produces a **bimodal register distribution** (phrases hug the extremes). Flattening it to uniform is the change of variable

$$\tilde{x} = \frac{2}{\pi}\arcsin(x),$$

which is exactly the conjugacy inverse — $\tilde{x}$ is uniform on $[-1,1]$. Use $\tilde{x}$ for middle-register tessitura; use raw $x$ for dramatic register-extreme melodies.

### 2.3 Lyapunov exponent — the rhythm knob

The largest Lyapunov exponent of the coupled system,

$$\lambda(a,\varepsilon) = \lim_{t\to\infty}\frac{1}{t}\log\frac{\|\delta x(t)\|}{\|\delta x(0)\|},$$

computed from the tangent dynamics $Df(x) = -2ax$, separates the regimes:

- $\lambda > 0$ (chaotic): a site's orbit visits continuously many distinct states → **dense event stream**.
- $\lambda < 0$ (periodic/phase-locked): the orbit cycles through few states → **sparse, regular pulse**.

Rhythmic density is therefore an *emergent* function of the local dynamical regime rather than a hard-coded grid.

### 2.4 Cluster synchronization — the harmony knob

For sufficiently large $\varepsilon$, subsets of adjacent sites lock into **synchronization clusters**: all sites in a cluster evolve on (nearly) the same orbit, so their states stay within a small distance $\delta$ for a long window $W$. Clusters merge and split only through bifurcations (Kaneko 1990), giving *discrete, controllable* harmonic events from *continuous* dynamics:

- **cluster merge** = a voicing collapses to unison/octave doubling,
- **cluster split** = a chord arpeggiates into independent voices,
- **cluster count** = number of chord tones.

### 2.5 The Kaneko phase diagram — the macro-form knob

| Regime | $(a,\varepsilon)$ neighbourhood | Musical role |
|---|---|---|
| Frozen random pattern | high $a$, high $\varepsilon$ | static section / ostinato (fixed spatial pattern persists) |
| Pattern selection | intermediate | traveling-wave motifs, spatial period-2 → verse-chorus alternation, phasing |
| Defect turbulence | low $\varepsilon$ | development (wandering defects = modulating passage) |
| Fully developed turbulence | high $a$, low $\varepsilon$ | climax / dense finale |

A composition *is* a scripted trajectory through this phase diagram.

---

## 3. Musical Elements Framework (decoding the lattice)

- **PITCH** — fold site state to scale: $p_i(t) = \mathrm{round}\big(60 + R\,\tilde{x}_i(t)\big)$ quantized to the active scale; $R$ = register span in semitones. Neighbour coupling pulls nearby sites toward consonance.
- **RHYTHM** — onsets at velocity peaks $|x_i(t{+}1) - x_i(t)| > \theta$, with $\theta$ scaled by the local Lyapunov regime $\lambda(a_s,\varepsilon_s)$.
- **HARMONY** — the section's cluster partition at step $t$ is the chord; cluster merges/splits are the chord changes; $\varepsilon$ sets harmonic coherence.
- **STRUCTURE** — the $(a_s,\varepsilon_s)$ regime of each section is the macro-form (frozen → pattern → turbulent arcs).
- **TEXTURE** — spatiotemporal fluctuation amplitude $D(t) = \tfrac{1}{L}\sum_i (x_i(t)-\bar x(t))^2$ maps to note count/velocity; cluster size maps to block-chord density.

---

## 4. UnitMatrix Integration

- **Rows (Voices):** mode (1) *one-site-per-voice* — site $i$ drives voice $v$, its state trace is the pitch contour; mode (2) *cluster-per-voice* — each synchronization cluster drives one voice with its representative state $\langle x\rangle_{\mathrm{cluster}}$; cluster split/merge dynamically re-voices the matrix.
- **Columns (Sections):** each section $s$ = a phase-diagram point $(a_s,\varepsilon_s)$ + a duration $T_s$ (CML steps → bars). Carry the final state vector $x_i(T_s)$ into the next section for seamless joins.
- **Cells $U_{v,s}$:** `{PITCH}` = folded state; `{RHYTHM}` = velocity-peak onsets; `{HARMONY}` = cluster structure; `{TEXTURE}` = fluctuation amplitude → velocity/density.

**Engine:** fill `UnitMatrix` cells then `composer.validate()` + `composer.to_midi()` per `AGENTS.md` — never hand-roll `mido`.

---

## 5. Full Python Implementation (NumPy)

```python
from __future__ import annotations
import numpy as np

# ---------- dynamics ----------
def cml_step(x: np.ndarray, a: float, eps: float) -> np.ndarray:
    """One diffusive CML step on a ring of coupled logistic maps."""
    f = 1.0 - a * x * x
    left = np.roll(f, 1)          # f(x_{i-1})
    right = np.roll(f, -1)        # f(x_{i+1})
    return (1.0 - eps) * f + 0.5 * eps * (left + right)

def evolve_cml(L: int, T: int, a: float, eps: float,
               x0: np.ndarray | None = None, seed: int = 0) -> np.ndarray:
    """Evolve L sites for T steps -> (T, L) state matrix. Carries state across sections."""
    if x0 is None:
        x0 = np.random.default_rng(seed).uniform(-1.0, 1.0, size=L)
    x = x0.astype(float).copy()
    states = np.empty((T, L))
    for t in range(T):
        states[t] = x
        x = cml_step(x, a, eps)
    return states, x          # return (states, final state) for section chaining

# ---------- decoding ----------
def flatten(x: np.ndarray) -> np.ndarray:
    """U-shape -> uniform density change of variable (arcsin conjugacy)."""
    return (2.0 / np.pi) * np.arcsin(np.clip(x, -1.0, 1.0))

def state_to_pitch(x: float, scale: np.ndarray,
                   center: int = 60, R: int = 24, uniform: bool = True) -> int:
    """Fold a lattice state into the nearest scale degree (MIDI)."""
    y = flatten(np.asarray(x)) if uniform else x
    idx = int(np.clip((y + 1.0) / 2.0 * len(scale), 0, len(scale) - 1))
    octave = int(round(R * y / 12.0))
    return int(center + scale[idx] + 12 * octave)

def lyapunov_density(a: float, eps: float, L: int = 64, T: int = 2000) -> float:
    """Finite-time largest Lyapunov exponent (chaos = +, periodic = -)."""
    rng = np.random.default_rng(1)
    x = rng.uniform(-1, 1, size=L)
    y = x + 1e-8
    lam = 0.0
    for _ in range(T):
        x1 = cml_step(x, a, eps)
        y1 = cml_step(y, a, eps)
        d = np.linalg.norm(y1 - x1)
        if d > 0:
            lam += np.log(d / np.linalg.norm(y - x))
        x, y = x1, x1 + (y1 - x1) * (1e-8 / max(d, 1e-12))
    return lam / T

def detect_clusters(x: np.ndarray, delta: float = 0.02, window: int = 4) -> list[list[int]]:
    """Synchronization clusters via persistent pairwise proximity (hysteresis)."""
    L = x.shape[0]
    seen: list[bool] = [False] * L
    clusters: list[list[int]] = []
    for i in range(L):
        if seen[i]:
            continue
        cluster = [i]
        seen[i] = True
        for j in range(i + 1, L):
            if seen[j]:
                continue
            if np.all(np.abs(x[i] - x[j]) < delta):   # persistence window = full slice
                cluster.append(j)
                seen[j] = True
        clusters.append(cluster)
    return clusters

# ---------- composition script ----------
def compose_section(L: int, a: float, eps: float, T: int,
                    scale: np.ndarray, theta: float,
                    x0: np.ndarray | None = None, uniform: bool = True):
    """Evolve one section and decode it into per-voice pitch + onset events."""
    states, x_final = evolve_cml(L, T, a, eps, x0=x0)
    velocities = np.abs(np.diff(states, axis=0))          # (T-1, L)
    pitches = [[state_to_pitch(states[t, i], scale, uniform=uniform)
                for t in range(T)] for i in range(L)]
    onsets = [np.flatnonzero(np.r_[False, velocities[:, i] > theta]).tolist()
              for i in range(L)]
    return {"pitches": pitches, "onsets": onsets, "states": states, "x_final": x_final}

# ---------- musicom integration sketch (engine authors the MIDI) ----------
# sections = [(1.95, 0.6, 128, "verse"), (1.98, 0.9, 128, "chorus"),
#             (1.90, 0.2, 256, "development"), (2.00, 0.1, 128, "climax")]
# scale = np.array([0, 2, 4, 5, 7, 9, 11])   # major
# x0 = None
# for (a, eps, T, name) in sections:
#     out = compose_section(L=8, a=a, eps=eps, T=T, scale=scale, theta=0.05, x0=x0)
#     x0 = out["x_final"]                      # carry state -> seamless joins
#     # ... fill UnitMatrix cells U[i, section] from out["pitches"]/out["onsets"] ...
# composer.validate(); composer.to_midi(out_path)   # per AGENTS.md
```

---

## 6. Pitfalls

1. **Turbulence = white noise.** In the fully-developed regime ($a\to 2$, $\varepsilon\to 0$) site states are near-independent noise → incoherent pitch. Keep pitched material in pattern-selection/frozen regimes ($\varepsilon \gtrsim 0.3$, $a \lesssim 1.95$); reserve turbulence for percussion/dense textural sections, or raise $\varepsilon$ to force consonant clusters.
2. **Cluster chatter.** A $\delta$-threshold without persistence flickers at cluster boundaries. Require a persistence window $W$ (hysteresis) or a moving-average correlation before reassigning membership.
3. **U-shaped pitch distribution.** The logistic invariant density concentrates at register extremes; apply the $\arcsin$ change of variable to flatten, or deliberately exploit the U-shape for extreme-register drama.
4. **Staccato in turbulent sections.** Velocity-peak onset detection in chaos can fire erratically. Layer a continuous fill voice from a *frozen-regime* synchronized cluster, and/or low-pass the onset signal by raising $\theta$.
5. **Section-boundary seams.** Resetting the lattice at each section start jumps the state. Carry $x_i(T_s)$ forward as the next section's initial state.
6. **Lyapunov-threshold fragility.** Near the $\lambda = 0$ bifurcation line, tiny seed changes flip periodic↔chaotic. Sample parameters well inside a regime, or measure $\lambda$ and set $\theta$ from the measurement.

---

## 7. References

- Kaneko, K. (1983). "Transition from Torus to Chaos Accompanied by Frequency Lockings with Symmetry Breaking." *Progress of Theoretical Physics* 69(5), 1427–1442.
- Kaneko, K. (1984). "Period-doubling of kink-antikink patterns, quasiperiodicity in antiferro-like structures and spatial intermittency in coupled logistic lattice." *Progress of Theoretical Physics* 72(3), 480–486.
- Kaneko, K. (1989). "Pattern dynamics in spatiotemporal chaos: Pattern selection, diffusion of defect and pattern competition intermittency." *Physica D* 34(1–2), 1–41.
- Kaneko, K. (1990). "Clustering, coding, switching, hierarchical ordering, and control in a network of chaotic elements." *Physica D* 41, 137–172.
- Kaneko, K. (ed.) (1992). *Theory and Applications of Coupled Map Lattices*. John Wiley & Sons.
- Eckmann, J.-P., & Ruelle, D. (1985). "Ergodic theory of chaos and strange attractors." *Reviews of Modern Physics* 57(3), 617–656.
- Pressing, J. (1988). "Nonlinear maps as generators of musical design." *Computer Music Journal* 12(2), 35–46.
- Bidlack, R. (1992). "Chaotic systems as simple (but complex) compositional algorithms." *Computer Music Journal* 16(3), 33–47.
- Crutchfield, J. P., & Kaneko, K. (1987). "Phenomenology of spatiotemporal chaos." In *Directions in Chaos*, World Scientific, 272–353.
