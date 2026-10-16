# Report: Method 117 — Particle Swarm Optimization Composition (PSOC)

**Date:** 2026-10-16  
**Agent:** methods-research cron job  
**Paradigm:** Stochastic  
**Layer:** concrete  
**One-line description:** Population-based metaheuristic where particles (candidate compositions) move through a continuous-dimensional parameter space via velocity-attraction to personal and global best positions, guided by a weighted musical fitness landscape.

---

## Summary Table Row

| **117** | concrete | Particle Swarm Optimization Composition (PSOC) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Fitness-guided, Key-bound) | Grid-Locked / Continuous | Macro / Global Optimum | $\mathcal{O}(I \cdot P \cdot D \cdot N)$ | Population of particles (candidate compositions) evolves via velocity-attraction to personal/global best positions. Continuous-valued positions encode note parameters per-voice per-section; fitness landscape guides convergence toward tonal, melodic, rhythmic, harmonic, textural, and structural objectives. Continuous-velocity metaheuristic counterpart to GA (003), SA (055), ACO (041) with fundamentally different search dynamics — vector-field guidance rather than recombination, cooling, or pheromone. |

---

## Line Count Analysis

| Metric | Before | After | Delta |
|---|---|---|---|
| methods_db.md total lines | 25773 | 25854 | +81 |
| Summary table rows | 116 | 117 | +1 |
| Detail sections | (PNC section end at 25518) | (+81 SP-115) | +81 lines appended |

The 81-line increase comprises 1 new summary table row (inserted after line 126) + blank separator + the full PSOC method section appended at the end of the file.

---

## Standalone File

**Path:** `/opt/data/projects/Research/CompositionMethods/method_117_PSOC.md`  
**Size:** 8565 bytes  
**Contents:** Full mathematical write-up (encoding, dynamics, fitness function), Python implementation sketch, classification table, UnitMatrix integration guide, relationship to 6 existing methods, references (6 sources), and append-info footer.

---

## Report File

**Path:** `/opt/data/projects/Research/CompositionMethods/report_117.md` (this file)

---

## Candidate Code Path

`generators/metaheuristic_psoc.py` in the `generators/` module. Fitness sub-scores ($f_{\text{tonal}}$, $f_{\text{melodic}}$, $f_{\text{rhythmic}}$, $f_{\text{harmonic}}$, $f_{\text{texture}}$, $f_{\text{structure}}$) should live in `rules/musical_fitness.py`. The PSOC driver combines fitness composition, swarm initialization, velocity clamping, and per-section seeding into a `PSOC.compose()` entry point.

---

## Complete Method Section Text (appended)

```
# Particle Swarm Optimization Composition (PSOC) (Method 117)

### Source

Kennedy, J. & Eberhart, R. (1995). "Particle swarm optimization." *Proceedings of IEEE International Conference on Neural Networks (ICNN 1995)*, vol. 4, pp. 1942–1948, IEEE Press. — Shi, Y. & Eberhart, R. (1998). "A modified particle swarm optimizer." *Proceedings of IEEE International Conference on Evolutionary Computation (ICEC 1998)*, pp. 69–73. — Clerc, M. & Kennedy, J. (2002). "The particle swarm: explosion, stability, and convergence in a multidimensional complex space." *IEEE Trans. Evolutionary Computation* 6(1), 58–73. — Bratton, D. & Kennedy, J. (2007). "Defining a standard for particle swarm optimization." *Proc. IEEE Swarm Intelligence Symposium*, pp. 1–6. (SPSO-2007/2011 standard.) — He, Y. (2023). "Application of Particle Swarm Optimization Algorithm in the Production of Original Songs for College Students on Campus." *ICIEAI 2023*, ACM, https://doi.org/10.1145/3660043.3660094. — GitHub: modbrin/music-pso, "Composing music algorithmically using Particle Swarm Optimization" (2019).

### Layer

**concrete** — generates concrete pitch, rhythm, and harmony events that fill UnitMatrix cells. Each particle's position vector directly encodes note parameters (pitch, onset, duration, velocity) across all voices; the converged global-best solution is decoded into per-cell MusicUnit contents. Feeds generators/ directly via particle-position decoding and fitness evaluation.

### Paradigm

**Stochastic** — population-based metaheuristic with stochastic velocity/position updates. Composition emerges from the guided random movement of the swarm through a continuous-dimensional search space, driven by personal-best attraction and global-best emulation. No deterministic rewrite rules, no neural training, and no nature-inspired dynamics beyond the swarm abstraction.

### Description

**Particle Swarm Optimization Composition (PSOC)** frames composition as a continuous-valued optimization problem. A population of P particles (candidate compositions) moves through a D-dimensional search space where each dimension encodes one musical parameter. The swarm iteratively refines positions under a fitness landscape that encodes tonal, melodic, rhythmic, harmonic, textural, and structural musical preferences. PSOC is the continuous-valued, population-based, velocity-driven metaheuristic counterpart to GA (003, discrete crossover/mutation), SA (055, single-trajectory temperature-cooling), ACO (041, discrete-pheromone graph), Boids (031, no objective — flocking kinematics only), and HSIC (073, music-inspired operator per solution slot, not velocity).

**Particle encoding**: Each particle \vec{x}_i \in \mathbb{R}^D concatenates per-note parameter vectors across all voices and sections. For V voices each with N notes:

\vec{x}_i = [\underbrace{p_{1,1}, o_{1,1}, d_{1,1}, v_{1,1}}_{\text{note 1}}, \ldots, \underbrace{p_{V,N}, o_{V,N}, d_{V,N}, v_{V,N}}_{\text{note }V\cdot N}]

where p \in [0,127] = MIDI pitch, o \in [0,1] = fractional onset within the bar, d \in [0,1] = fractional duration, v \in [0,127] = MIDI velocity. Total dimensionality D = 4 \cdot V \cdot N.

**Swarm dynamics** (standard PSO, Shi & Eberhart 1998 with linear inertia decay):

\vec{v}_i(t+1) = w(t)\, \vec{v}_i(t) + c_1 r_1 \odot (\vec{p}_i - \vec{x}_i(t)) + c_2 r_2 \odot (\vec{g} - \vec{x}_i(t))

\vec{x}_i(t+1) = \vec{x}_i(t) + \vec{v}_i(t+1)

where \vec{v}_i = velocity, \vec{x}_i = position, \vec{p}_i = personal best, \vec{g} = global best, r_1,r_2 \sim U(0,1), c_1=c_2=2.0, w(t) = 0.9 - 0.5\cdot(t/T_{\max}).

**Fitness function**: Six normalized sub-scores combined: f_{\text{tonal}} (scale deviation, 0.25), f_{\text{melodic}} (stepwise preference, 0.15), f_{\text{rhythmic}} (metric alignment, 0.15), f_{\text{harmonic}} (chord-tone alignment, 0.25), f_{\text{texture}} (event density, 0.10), f_{\text{structure}} (motivic coherence, 0.10).

**Key innovation**: Unlike GA (003) which combines solutions via crossover/mutation, PSOC particles move through CONTINUOUS space via velocity-attraction — melodic contour, rhythmic offset, and velocity are smoothly interpolated between personal and global solutions. The inertia-weight schedule w(t) controls exploration-exploitation analogously to SA's temperature but operates on a population.

**Convergence**: The swarm runs for T_{\max} = 200--1000 iterations or until plateau. The global-best \vec{g} decodes to a UnitMatrix: each 4-tuple (p,o,d,v) becomes a MusicEvent. For multi-section forms, each section is optimized independently with the global-best ending frame of section m-1 seeding section m.

### Musical Elements Framework

**PITCH**: Continuous encoding p \in [0,128). Velocity-attraction interpolates between personal and global pitch sequences. f_{\text{tonal}} penalizes scale deviation via squared-distance gradient toward nearest scale tone.

**RHYTHM**: Onset/duration (o_j,d_j) pairs. f_{\text{rhythmic}} evaluates metric alignment via kernel offset from downbeat. Overlap penalty \sum_j \max(0, o_j+d_j - o_{j+1}) prevents collisions.

**HARMONY**: Multi-voice coupling through f_{\text{harmonic}} evaluating chord-tone membership at each strong beat. Root presence, voicing type, parallel-motion penalty, and voice-leading parsimony are evaluated.

**STRUCTURE**: Section-specific fitness landscapes f^{(m)} with per-section parameters. Seed inheritance propagates motifs across seams. f_{\text{structure}} rewards within-section autocorrelation (development) and between-section dissimilarity (contrast).

**TEXTURE**: f_{\text{texture}} enforces per-voice target densities and registral span. Swarm self-regulates note density through velocity-attraction on onset spacing.

### UnitMatrix Integration (Voices & Sections)

**Voices**: Each voice v occupies 4N contiguous dimensions. Coupled through f_{\text{harmonic}} and f_{\text{texture}}. Percussion: MIDI keys 35--81, f_{\text{rhythmic}} dominates.

**Sections**: Each section m has own fitness landscape f^{(m)}. Section m receives section m-1's ending events as seed (padded/truncated to dimensionality). Form schedule designed or optimized by outer discrete PSO.

**Cell filling**: Decoded from \vec{g}: pitch rounded, onset grid-aligned, duration scaled, velocity clamped. Zero-drift: \sum d_j\cdot\text{bar\_ticks} = \text{section\_ticks}.

### Pitfalls

1. **Premature convergence**: diversity archive, ring topology, or added turbulence.
2. **Fitness function design**: weight tuning via grid search or meta-optimizer.
3. **Dimensionality explosion**: cooperative coevolution or section decomposition.
4. **Velocity explosion**: clamping |v_i^d| \leq V_{\max}=0.2 and position reflection.
5. **Rhythm collision**: aggressive overlap/silence-gap penalties.
6. **Per-section seeding breaks voice-leading**: encode min. final 2 bars of seed.
7. **Tuning c_1 \approx c_2**: constriction factor \chi = 2/|2-\varphi-\sqrt{\varphi^2-4\varphi}| with \varphi = c_1+c_2 > 4.
8. **Determinism**: set rng seed for reproducibility; report mean over K runs.
```

---

## Verification Results

```
$ wc -l methods_db.md
25854 methods_db.md

$ grep -n "**117**" methods_db.md
127:| **117** | concrete | Particle Swarm Optimization Composition (PSOC) | **Stochastic** | ...

$ grep -c "PSOC" methods_db.md
10  (summary row + 9 occurrences in detail section)
```

---

## Quirks and Pitfalls Encountered

1. **Backslash doubling**: The `write_file` tool doubles LaTeX backslashes (e.g., `\\vec` becomes `\\\vec` in the JSON round-trip?). Fixed with `sed -i '25775,25854s/\\\\/\\/g'` — but sed's own escaping is a nested maze. Verified correct via `od -c`.
2. **Table row pipe prefix**: The `patch` tool inserted `||| **117**` (triple pipe) because the matched context `|||### Source` included the triple pipe. Excess pipe removed with a second patch. Verified matching line 126 format with `od -c`.
3. **Sequence of operations**: Must write temp file → append with cat → delete temp. Cannot use `>>` redirect with the write_file tool because it overwrites. The three-step temp-file workflow avoids this.
4. **Standalone file also needs backslash check**: The `write_file` for `method_117_PSOC.md` used single backslashes in the write call — verified no double-escapes via `grep -n '\\\\'`.
5. **Free ID tracking**: Max ID was 116 (Petri Net Composition). Checked both the summary table scan AND the file listing of `method_*.md` and `report_*.md` for IDs 001--116. No gap at 058 interferes because 058 doesn't exist in the DB. Next free ID = 118.

---

## Next Free ID

**118** (after accounting for all existing numeric IDs 001--117 in the summary table and standalone file listing).

---

*Report generated 2026-10-16 by the methods-research cron job.*