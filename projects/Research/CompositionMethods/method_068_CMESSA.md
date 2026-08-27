# Method 068 — Chemical Master Equation Stochastic Simulation (CME-SSA)

**Paradigm:** Stochastic
**Acronym:** CME-SSA
**Primary Elements:** Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity:** Strong (Tension-species)
**Metric Binding:** Continuous / Fluid
**Memory Depth:** Local / Count-State
**Time Complexity:** $\mathcal{O}(E \cdot R)$ direct, $\mathcal{O}(E \log R)$ next-reaction

---

## 1. Overview

Composition is posed as the **exact stochastic simulation of a chemical reaction network**. The musical state is a vector of non-negative integer *counts* — notes sounding per voice, tension species, motif copies, dissonance molecules — and composition is a sequence of *reaction events* fired at stochastically-correct times. The time-evolution of the state is governed by the **Chemical Master Equation (CME)**, the forward Kolmogorov equation over the probability distribution of counts, and it is sampled exactly by the **Gillespie Stochastic Simulation Algorithm (SSA)**.

Two numbers determine everything at each step:

1. The **sojourn time** $\tau$, the exponentially-distributed waiting time until the next event — this *is* the inter-onset interval, i.e. the rhythm.
2. The **reaction index** $j$, drawn proportionally to each reaction's propensity — this *is* the identity of the next musical event, i.e. the pitch/register/harmony/dynamics.

Because propensities are functions of the current counts (mass-action form $a \propto N$), the network self-regulates: note-offs grow with active notes (phrase decay), resolution grows with tension (cadence pull), migration grows with register occupancy (voice-leading). There is no grid — events fire on the real line — so the output is inherently continuous and flowing.

---

## 2. Theory

### 2.1 The Chemical Master Equation

Let $x \in \mathbb{Z}_{\ge 0}^{S}$ be the vector of species counts and $R$ the number of reaction channels. Reaction $j$ transforms $x \to x + \nu_j$ where $\nu_j$ is the stoichiometry vector, with **propensity** $a_j(x)$ (probability per unit time that reaction $j$ fires, given state $x$). The probability $P(x, t)$ that the system is in state $x$ at time $t$ obeys

$$
\frac{\partial P(x,t)}{\partial t}
= \sum_{j=1}^{R}\Big[ a_j(x-\nu_j)\,P(x-\nu_j,\,t) - a_j(x)\,P(x,\,t) \Big].
$$

This is the **Chemical Master Equation**. The deterministic reaction-rate ODE $\dot{x} = \sum_j \nu_j a_j(x)$ describes only the *mean* $\langle x \rangle$; the CME captures the full stochastic fluctuation structure that is musically essential (timing jitter, density bursts, cadence variability).

### 2.2 The Gillespie Direct Method

The joint density that the *next* reaction is channel $j$ and it occurs after a waiting time $\tau$ is

$$
p(\tau, j \mid x, t) = a_j(x)\,\exp\!\Big(-\tau\, a_0(x)\Big),
\qquad a_0(x) = \sum_{j=1}^{R} a_j(x).
$$

The direct-method SSA samples this exactly:

1. Initialize $t = 0$, $x = x_0$.
2. Compute $a_0(x) = \sum_j a_j(x)$.
3. Draw $\tau = \frac{1}{a_0}\ln\!\big(\tfrac{1}{u_1}\big)$ with $u_1 \sim \mathrm{Uniform}(0,1)$.
4. Draw $j$ as the smallest index with $\sum_{j'=1}^{j} a_{j'}(x) > u_2\, a_0$, for $u_2 \sim \mathrm{Uniform}(0,1)$.
5. Update $x \leftarrow x + \nu_j$, $t \leftarrow t + \tau$, record the event, repeat.

The waiting time being exactly exponential is the source of the "organic" timing: it is the inter-onset interval distribution of a memoryless process whose rate is modulated by the *musical* state itself, yielding natural rubato — accelerando where activity is high, breathing space where it is low.

### 2.3 Musical propensities (mass-action forms)

| Reaction | Stoichiometry | Propensity | Musical meaning |
|---|---|---|---|
| onset | $\varnothing \to N_v$ | $a_{on}(v,p) = k_{on}^{(v)}\, w^{(s)}(p)\, f(N_v)$ | note in voice $v$ at pitch $p$, weighted by tonal gravity $w^{(s)}$ |
| note-off | $N_v \to \varnothing$ | $a_{off}(v) = k_{off}^{(v)}\, N_v$ | phrase decay (grows with sounding count) |
| migration | $P_i \to P_{i\pm1}$ | $a_{mig} = k_{mig}\,\mathrm{step}(|p-p'|)\,N_p$ | melodic tendency (stepwise favored) |
| tension-up | $T_s \to T_{s+1}$ | $a_{up}(s) = k_{up}\, L_s(t)$ | harmonic lift (gated by section input) |
| resolution | $T_s \to T_{s-1}$ | $a_{res}(s) = k_{res}\, T_s$ | cadence pull (grows with tension) |

The mass-action dependence $a \propto N$ is exactly what makes the system self-regulating and convergent.

### 2.4 Regimes and variants

- **Exact SSA** (direct method): $\mathcal{O}(R)$ per event. Correct to all fluctuations.
- **Next-Reaction Method** (Gibson & Bruck 2000): dependency graph + indexed priority queue → $\mathcal{O}(\log R)$ per event, exact.
- **tau-leaping** (Gillespie 2001): batch many reactions per step with a Poisson draw, trading exactness for speed in dense regimes (texture climaxes).

---

## 3. Musical Elements Framework

- **PITCH** — encoded as species labels. Scale degrees are pitch species with reactivity weights (chord tones high). Onset propensity draws pitch proportionally to tonal gravity; migration reactions with stepwise-favoring rates recover melodic contour (a discrete-rate analogue of 048 RBMPD's drift).
- **RHYTHM** — the emergent inter-event time $\tau \sim \mathrm{Exp}(a_0)$. No grid. High $a_0$ → short $\tau$ → dense rhythm. State-dependent $a_0$ gives rubato and phrase structure.
- **HARMONY** — a tension ladder $T_0 \to T_1 \to \dots \to T_K$ with interconversion reactions. Resolution propensity $\propto T_s$ = cadence pull; lift gated by section input. The expected occupancy $\mathbb{E}[T_s]$ is the continuous HOME/LIFT/TENSE/TURN tension curve (the kinetic counterpart to 050 OTVL's $W_p$).
- **STRUCTURE** — staged propensity schedules: a section-advance "clock" reaction switches parameter regimes (Verse/Chorus) at stochastically-scheduled times; state carries across the switch for smooth joins. Alternatively, positive feedback + saturating decay produces self-organized build/break arcs (kinetic cousin of 036 ASAR).
- **TEXTURE** — the active-note count $\sum_v N_v$ at each event. Voice independence = reaction localization (no reaction writes two voices); vertical coherence = shared tension species read by all voice propensities.

---

## 4. UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)** = species sub-networks. Each voice owns onset/off/migration reactions reading the shared tension species but writing only its own note count. The reaction's owner voice is identified by the species it writes.
- **Columns (Sections)** = propensity parameter regimes over clock intervals $[t_s, t_{s+1})$. Section lengths can be stochastic (section-advance reaction), so columns breathe rather than sit on a rigid bar grid.
- **Cells** $U_{v,s}$:
  - `{PITCH}` — pitch-class species written by the latest onset/migration reaction in voice $v$.
  - `{RHYTHM}` — the accumulated sampled sojourn times (inter-onset intervals) within the cell.
  - `{HARMONY}` — tension species $T_s$ / dissonance count at the cell's event times.
  - `{TEXTURE}` — instantaneous active-note count $\sum_v N_v$.

**Mapping flow:** declare species + reactions → set tempo constant $\kappa$ → run SSA to target length → bin events into sections → quantize pitches to scale/grid → resolve onsets/offs into note units → fill cells → `validate()` + `to_midi()` via the musicom engine (see AGENTS.md).

---

## 5. Python Implementation Sketch

```python
from __future__ import annotations
import numpy as np

class CME_Gillespie:
    """Exact SSA (direct method) over a musical reaction network."""
    def __init__(self, n_species, stoichiometry, propensities, tempo=1.0, rng=None):
        self.x = np.zeros(n_species, dtype=float)
        self.nu = stoichiometry          # list of delta vectors, one per reaction
        self.a = propensities            # list of callables a_j(x, t) -> float >= 0
        self.tempo = tempo               # global rate scale (notes/sec target)
        self.rng = rng or np.random.default_rng()

    def run(self, t_max, x0=None):
        if x0 is not None:
            self.x[:] = x0
        t, events = 0.0, []
        while t < t_max:
            a = np.array([p(self.x, t) for p in self.a]) * self.tempo
            a0 = a.sum()
            if a0 <= 0.0:
                break
            tau = np.log(1.0 / self.rng.random()) / a0       # sojourn time = IOI
            r2 = self.rng.random() * a0
            acc, j = 0.0, -1
            for k in range(len(a)):
                acc += a[k]
                if acc > r2:
                    j = k
                    break
            self.x += self.nu[j]
            t += tau
            events.append((t, j, self.x.copy()))
        return events


# ---- Example network: 2-voice tonal sketch ----
# species indices:
#   0: LEAD_notes   1: BASS_notes   2: TENSION   3: DISSONANCE
# reactions (delta, propensity):
#   (0) lead onset:  delta=[+1,0,0,+1],  a = 0.8 * chord_weight(t)
#   (1) lead off:    delta=[-1,0,0,-1],  a = 0.4 * x[0]
#   (2) bass onset:  delta=[0,+1,0,0],   a = 0.5 * (x[2] > 0)   # bass locked to tension
#   (3) bass off:    delta=[0,-1,0,0],   a = 0.3 * x[1]
#   (4) tension up:  delta=[0,0,+1,0],   a = 0.1 * lift_input(t)
#   (5) resolution:  delta=[0,0,-1,0],   a = 0.2 * x[2]          # cadence pull
#
# Each (t, j) event -> note unit; pitch from a per-reaction scale table,
# duration = time to the matching off event. Then UnitMatrixComposer
# validate() + to_midi() (never hand-roll mido).
```

---

## 6. Pitfalls

1. **Propensity → 0 deadlock** — all channels off stops the loop early. Keep a floor onset/rest propensity $\ge \epsilon$.
2. **Grid drift** — continuous event times must be quantized to ticks only at the last step; append the silent padding event at `total_section_ticks - 1` (MIDI-tail-truncation pitfall).
3. **Explosive density** — positive feedback can drive $a_0 \to \infty$. Cap $a_0$ or use tau-leaping; add a refractory species.
4. **Rate-scale tuning** — normalize $\kappa$ so steady-state mean $a_0$ matches target notes/sec; verify the IOI histogram.
5. **Non-idiomatic pitch** — pure mass-action has no melodic memory. Use stepwise-favoring migration reactions or a last-pitch-dependent weight.
6. **Tension-ladder monotonicity** — make $a_{res} \propto T_s$ (mass-action guarantees eventual resolution) and gate the up-reaction behind a section/lift input.

---

## 7. References

- Gillespie, D. T. (1976). "A general method for numerically simulating the stochastic time evolution of coupled chemical reactions." *Journal of Computational Physics* 22(4), 403–434.
- Gillespie, D. T. (1977). "Exact stochastic simulation of coupled chemical reactions." *Journal of Physical Chemistry* 81(25), 2340–2361.
- Gibson, M. A., and Bruck, J. (2000). "Efficient exact stochastic simulation of chemical systems with many species and many channels." *Journal of Physical Chemistry A* 104(9), 1876–1889.
- Gillespie, D. T. (2001). "Approximate accelerated stochastic simulation of chemically reacting systems." *Journal of Chemical Physics* 115(4), 1716–1733.
- van Kampen, N. G. (2007). *Stochastic Processes in Physics and Chemistry*, 3rd ed., Elsevier (master-equation formalism, Ch. V–VII).

---

## 8. Related Methods in the Musicom Catalog

| Method | State space | Event timing | Tension mechanism | Grid |
|---|---|---|---|---|
| 002 Markov | discrete states | fixed grid steps | transition weights | Grid-Locked |
| 045 HPSEC | point process | self-exciting intensity | excitation kernel | Continuous |
| 036 ASAR | 2D sandpile | avalanche cascade | critical toppling | Grid-Locked |
| 061 GPC | continuous Gaussian | kernel/prior | anchor conditioning | Continuous |
| **068 CME-SSA** | **integer counts** | **exact exponential sojourns** | **tension-species reactions** | **Continuous** |

- Integer-count, continuous-time counterpart to **061 GPC** (continuous Gaussian states).
- Rate-balanced sibling of **045 HPSEC** (the excitation kernel is a special-case propensity).
- Stochastic foil to the deterministic constraint methods **033 WFCGS** / **056 SCCC**.
- Discrete-rate analogue of **048 RBMPD**'s drift (melodic tendency via migration reactions).
