# Method 078 — Ising Model Equilibrium Composition (IMEC)

**Paradigm**: Stochastic (equilibrium statistical mechanics)
**Layer**: Concrete
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity**: Moderate (Field/Temperature-guided)
**Metric Binding**: Grid-Locked / Continuous
**Memory Depth**: Meso / Spin-Lattice
**Time Complexity**: $\mathcal{O}(I \cdot V \cdot S)$

## One-line description
Compose music by simulating a 2D Ising spin lattice (rows = voices, columns = time slots) at thermal equilibrium via Metropolis / Wolff cluster sampling, then reading the equilibrium spin configuration out as pitch (spin value), rhythm (column magnetization), harmony (external tonic field $h$), structure (temperature schedule $T(s)$), and texture (cluster-size distribution).

---

## Extended Mathematics

### The Ising Hamiltonian
On a $V \times S$ lattice of spins $\sigma_{v,t} \in \{+1, -1\}$ (voice $v$, time slot $t$), with anisotropic nearest-neighbor couplings and a uniform external field:

$$H(\sigma) = -J_h \sum_{v=1}^{V}\sum_{t=1}^{S} \sigma_{v,t}\sigma_{v,t+1} \;-\; J_v \sum_{v=1}^{V}\sum_{t=1}^{S} \sigma_{v,t}\sigma_{v+1,t} \;-\; h \sum_{v,t} \sigma_{v,t}$$

(cyclic boundary conditions in both directions). At inverse temperature $\beta = 1/(k_B T)$, the probability of a configuration is the Boltzmann weight $p(\sigma) = e^{-\beta H}/Z$ with partition function $Z = \sum_\sigma e^{-\beta H}$.

### Order parameter and the phase transition
The **magnetization per spin**

$$M = \frac{1}{VS}\sum_{v,t} \sigma_{v,t}$$

is the order parameter. In $d{=}2$ on the square lattice the model has a continuous (second-order) transition at the Onsager temperature

$$T_c = \frac{2J}{k_B \ln(1+\sqrt{2})} \approx 2.269\,\frac{J}{k_B}$$

(for isotropic $J_h = J_v = J$). Below $T_c$ the symmetry is broken: $|M| \sim |t|^\beta$ with $\beta_{\text{Ising}} = 1/8$, $t = (T-T_c)/T_c$. The **correlation length** diverges as $\xi \sim |t|^{-\nu}$ with $\nu = 1$. Exactly at $T_c$ the system is **scale-free**: spin clusters are fractal with fractal dimension $d_f = 187/96 \approx 1.95$ (Coniglio–Klein 1980), and the cluster-size distribution is a power law $P(s) \sim s^{-\tau}$, $\tau = 2 + d/d_f \approx 2.03$ in 2D.

### Musical interpretation of the phase diagram
- **$T \ll T_c$ (ordered)**: one giant aligned cluster dominates; $\langle M \rangle \approx \pm 1$; consensus pitch, few domain walls, metrically strong and repetitive → **chorus/statement**.
- **$T = T_c$ (critical)**: clusters of all sizes coexist (power-law), self-similar motif hierarchy, maximal correlation length, organic tension → **development section**.
- **$T \gg T_c$ (disordered)**: spins decorrelate, $\langle M \rangle \approx 0$, white-noise texture → **breakdown/outro**.

### Field as chord function
The external field $h$ breaks the up/down symmetry and gives an explicit tonal bias: $h > 0$ (HOME) aligns spins to $+1$ (consonant/chord tones), $h < 0$ (TENSE) aligns to $-1$ (chromatic/passing tones), $|h|$ controls the strength of the pull. A field *trajectory* $h(s)$ over sections is a chord-progression plan (LIFT = rising $h$, TURN = sign change). Because the magnetization responds continuously to $h$, the field is a soft (annealed) tonal-gravity controller rather than a hard key constraint — hence "Moderate" gravity.

### Metropolis dynamics
Single-spin update: propose flip $\sigma_{v,t}\to -\sigma_{v,t}$; energy change

$$\Delta E = 2\sigma_{v,t}\big(J_h(\sigma_{v,t-1}+\sigma_{v,t+1}) + J_v(\sigma_{v-1,t}+\sigma_{v+1,t}) + h\big)$$

accept with probability $\min(1, e^{-\beta \Delta E})$. $I$ sweeps ($I \cdot V \cdot S$ proposed flips) thermalize a section.

### Wolff cluster update
Near $T_c$ Metropolis suffers critical slowing down (autocorrelation time $\tau \sim \xi^z$, $z \approx 2.17$). Wolff (1989) builds a connected cluster of like spins with bond probability $p_{\text{add}} = 1 - e^{-2\beta J}$ and flips the whole cluster, eliminating slowing down. A Wolff flip flips a whole coherent harmonic region at once — the natural "reharmonization" operator.

---

## Python implementation sketch

```python
from __future__ import annotations
import numpy as np
rng = np.random.default_rng(42)

def metropolis_sweep(S: np.ndarray, J_h: float, J_v: float, h: float,
                     beta: float, sweeps: int) -> np.ndarray:
    V, T = S.shape
    for _ in range(sweeps * V * T):
        v, t = rng.integers(0, V), rng.integers(0, T)
        nb = (S[(v - 1) % V, t] + S[(v + 1) % V, t]) * J_v \
           + (S[v, (t - 1) % T] + S[v, (t + 1) % T]) * J_h
        dE = 2 * S[v, t] * (nb + h)
        if dE <= 0 or rng.random() < np.exp(-beta * dE):
            S[v, t] *= -1
    return S

def wolff_flip(S: np.ndarray, J_h: float, J_v: float, beta: float):
    V, T = S.shape
    sv, st = rng.integers(0, V), rng.integers(0, T)
    target = S[sv, st]
    stack, cluster = [(sv, st)], {(sv, st)}
    p_add = 1.0 - np.exp(-2 * beta * max(J_h, J_v))
    while stack:
        v, t = stack.pop()
        for nv, nt in ((v - 1, t), (v + 1, t), (v, t - 1), (v, t + 1)):
            nv %= V; nt %= T
            if (nv, nt) not in cluster and S[nv, nt] == target and rng.random() < p_add:
                cluster.add((nv, nt)); stack.append((nv, nt))
    for (v, t) in cluster:
        S[v, t] *= -1
    return S, len(cluster)

def anneal_section(V: int, T: int, T_phys: float, h: float,
                   J_h: float = 1.0, J_v: float = 1.0,
                   sweeps: int = 200, hot_start: bool = True) -> np.ndarray:
    beta = 1.0 / T_phys
    S = rng.choice([-1, 1], size=(V, T)) if hot_start else np.ones((V, T), int)
    for _ in range(sweeps):
        metropolis_sweep(S, J_h, J_v, h, beta, 1)
        if T_phys < 2.5:                       # use cluster flips near/at Tc
            S, _ = wolff_flip(S, J_h, J_v, beta)
    return S

def readout(S: np.ndarray, h: float, scale_cons: list, scale_chrom: list):
    """Spin -> (pitch, velocity). +1 = consonant (field-aligned), -1 = passing."""
    V, T = S.shape
    col_mag = S.sum(axis=0) / V                 # column magnetization -> onset density
    events = []
    for v in range(V):
        for t in range(T):
            s = S[v, t]
            if s == -1 and abs(col_mag[t]) < 0.3:
                continue                         # rest: weak-beat passing slots
            pool = scale_cons if s == +1 else scale_chrom
            pitch = pool[(v + t) % len(pool)]
            vel = int(64 + 40 * abs(col_mag[t]))
            events.append((v, t, pitch, vel))
    return events, col_mag
```

**Musicom integration** (engine authors the MIDI; sketch only — real imports per `AGENTS.md`):
```python
# from structures import MusicUnit
# from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit
# composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
# composer.create_matrix(num_voices=V, num_sections=S)
# for s, (T_s, h_s) in enumerate(section_specs):
#     grid = anneal_section(V, slots_per_section, T_s, h_s, J_h, J_v)
#     for v in range(V):
#         for t, spin in enumerate(grid[v]):
#             if spin == +1:
#                 pitch = pitch_from(spin, h_s, neighborhood_mag(grid, v, t))
#                 composer.fill_voice_section(v, s, create_note_unit(pitch, dur, tick=t))
# ok, msg = composer.validate()   # MUST be True before to_midi (per AGENTS.md)
```

---

## UnitMatrix Integration (Voices & Sections)
- **Rows (Voices)** = spin-lattice rows. Voice $v$ = spin chain $\sigma_{v,\cdot}$. Vertical coupling $J_v$ makes aligned columns form consonant voicings; independent rows give counterpoint.
- **Columns (Sections)** = time blocks, each assigned a $(T_s, h_s)$ pair. Each section = anneal to equilibrium at $T_s$ in field $h_s$, then read out.
- **Cells (MusicUnit)** = one spin → note (rest if weak-magnetized passing slot), pitch from scale pool keyed by spin sign + register, velocity from column magnetization.
- Zero-drift preserved: fixed $V \times S$ lattice, fixed readout, engine-authored MIDI with `validate()` gate.

---

## References
- Lenz, W. (1920). "Beiträge zum Verständnis der magnetischen Erscheinungen in festen Körpern." *Physikalische Zeitschrift* 21, 613–615.
- Ising, E. (1925). "Beitrag zur Theorie des Ferromagnetismus." *Zeitschrift für Physik* 31, 253–258.
- Onsager, L. (1944). "Crystal statistics. I. A two-dimensional model with an order-disorder transition." *Physical Review* 65(3–4), 117–149.
- Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H., & Teller, E. (1953). "Equation of state calculations by fast computing machines." *Journal of Chemical Physics* 21(6), 1087–1092.
- Swendsen, R. H., & Wang, J.-S. (1987). "Nonuniversal critical dynamics in Monte Carlo simulations." *Physical Review Letters* 58(2), 86–88.
- Wolff, U. (1989). "Collective Monte Carlo updating for spin systems." *Physical Review Letters* 62(4), 361–364.
- Coniglio, A., & Klein, W. (1980). "Clusters and Ising critical droplets: a renormalisation group approach." *Journal of Physics A: Mathematical and General* 13(8), 2775–2780.
- Nierhaus, G. (2009). *Algorithmic Composition: Paradigms of Automated Music Generation*. Springer.
