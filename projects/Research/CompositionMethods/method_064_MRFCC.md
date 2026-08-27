# Markov Random Field Constraint Composition (MRFCC) — Method 064

**Paradigm:** Stochastic (energy-based, undirected graphical model)
**Acronym:** MRFCC
**Primary Elements:** Pitch, Rhythm, Harmony, Structure, Texture
**Tonal Gravity:** Strong (Energy-guided) | **Metric Binding:** Grid-Locked / Continuous | **Memory Depth:** Meso / Lattice Neighborhood | **Time Complexity:** O(I · V · S · K)

---

## 1. Core Idea

MRFCC models the entire UnitMatrix as a **2D Markov Random Field** — a lattice of discrete random variables where each cell `U_{v,s}` holds a pitch/rhythm/velocity token. Unlike a Markov chain (002), which is a directed 1D sequence, the MRF is **undirected and 2D**: each cell's conditional distribution depends only on its **Markov blanket** — the horizontal neighbors (same voice, adjacent sections → melodic context) and vertical neighbors (same section, adjacent voices → harmonic context). Composition is **Gibbs sampling**: repeatedly resample each cell from its full conditional until the grid reaches the equilibrium distribution defined by the clique potentials. Every musical rule (tonal gravity, melodic smoothness, voice-leading, groove) is a soft energy term, so constraints compete and resolve statistically.

## 2. Mathematics

### Hammersley–Clifford factorization

By the Hammersley–Clifford theorem (Besag 1974), any positive joint distribution with local conditional structure factorizes over the cliques C of the lattice graph:

```
P(x) = (1/Z) · exp( −Σ_{c∈C} E_c(x_c) )
```

- `Z` = partition function (intractable — never computed; Gibbs only needs conditional ratios)
- `E_c` = clique potential (energy) over clique c
- Cliques: singletons (one cell), horizontal pairs, vertical pairs, 2×2 blocks

### Full conditional (the Gibbs workhorse)

For a cell with alphabet A (e.g. 12 pitch classes × 8 onset offsets), the probability of candidate `a`:

```
P(x_{v,s}=a | rest) ∝ exp( −E_pitch(a) − E_dens(a)
                          − E_mel(a, x_{v,s−1}) − E_mel(x_{v,s+1}, a)
                          − Σ_{u~v} E_vert(a, x_{u,s})
                          − E_block(...) )
```

Normalize over the alphabet (softmax over −energy). Temperature T divides the energies; annealing T down sharpens the distribution (bridge to 055 SAMC).

### Clique potentials (the musical rules)

| Clique | Potential | Musical role |
|---|---|---|
| Singleton | `E_pitch` = distance from chord tones of active function (HOME/LIFT/TENSE/TURN) | Tonal gravity |
| Singleton | `E_dens` = (note count − target)² | Texture density |
| Horizontal pair | `E_mel` = interval size penalty (conjunct reward, leap penalty) | Melodic smoothness |
| Vertical pair | `E_vert` = consonance reward (interval class ∈ {0,3,4,7,8,9}), dissonance penalty | Harmony / voice-leading |
| 2×2 block | `E_block` = metric accent alignment + parallel fifth/octave penalty | Groove + counterpoint |

## 3. Musical Elements Framework

- **PITCH**: Cell state is a pitch token over the active scale/chord alphabet. Singleton potential is lowest at chord tones → equilibrium mass concentrates on idiomatic pitches. Horizontal pair potential rewards stepwise motion; vertical pair potential makes simultaneous pitches consonant.
- **RHYTHM**: Onset offset is part of the cell state (or a second coupled lattice layer). Groove potential over 2×2 blocks rewards metric strong beats; density potential sets target onsets per cell. Syncopation survives where other potentials make it worthwhile — organic, not grid-locked.
- **HARMONY**: Vertical pair potentials score simultaneous (voice, voice) pairs for consonance and penalize parallel fifths/octaves across adjacent sections (2×2 block compares consecutive vertical pairs). Chord-function labels condition singleton potentials → functional harmony cell-by-cell + voice-leading across section boundaries.
- **STRUCTURE**: The section grid is the macro-form scaffold. Section-level potential scores cadence placement at boundaries; section labels can themselves be Gibbs-resampled variables → macro-form is part of the equilibrium. Horizontal potentials weakened across boundaries for phrase contrast.
- **TEXTURE**: Voice independence emerges from vertical potentials (unison/parallel-collapse penalty) + per-voice singleton potentials (register bias, density target). Adding a voice = adding a row of variables + vertical cliques.

## 4. UnitMatrix Integration

- **Rows (Voices)**: each voice = a lattice row; cells = variables x_{v,1..S}. Vertical cliques couple rows pairwise → vertical coherence (consonance); horizontal potentials + register biases → horizontal independence.
- **Columns (Sections)**: each section = a column; its chord-function label conditions every cell's singleton potential. Horizontal cliques carry melodic continuity across boundaries.
- **Cells**: `{PITCH}` = pitch token; `{RHYTHM}` = onset offset; `{TEXTURE}` = density steered by singleton potential.

**Mapping flow**: build lattice → define potentials → initialize (001 skeleton / 002 Markov / noise) → blocked Gibbs until energy plateau → read equilibrium grid → fill UnitMatrix → validate zero-drift → export via musicom engine.

## 5. Python Implementation Sketch

```python
import numpy as np

# Alphabet: 12 pitch classes x 8 onset offsets = 96 discrete states
N_PC, N_ONSET = 12, 8
K = N_PC * N_ONSET

def decode(state):
    """state -> (pitch_class, onset_offset)."""
    return state // N_ONSET, state % N_ONSET

def encode(pc, onset):
    return pc * N_ONSET + onset

def singleton_energy(state, chord_tones, target_density, n_notes):
    """Tonal gravity + texture density."""
    pc, onset = decode(state)
    tonal = 0.0 if pc in chord_tones else 2.0          # chord tones cheap
    dens = (n_notes - target_density) ** 2 * 0.5
    return tonal + dens

def horizontal_energy(a, b):
    """Melodic smoothness: reward small intervals, penalize leaps."""
    pc_a, _ = decode(a); pc_b, _ = decode(b)
    interval = abs(pc_a - pc_b) % 12
    interval = min(interval, 12 - interval)             # shortest path
    return interval * 0.4                               # 0 = unison, 4.8 = tritone

def vertical_energy(a, b):
    """Consonance reward / dissonance penalty between simultaneous voices."""
    pc_a, _ = decode(a); pc_b, _ = decode(b)
    interval = abs(pc_a - pc_b) % 12
    interval = min(interval, 12 - interval)
    consonant = {0, 3, 4, 7, 8, 9}
    return 0.0 if interval in consonant else 1.5

def block_energy(cell, grid, v, s, strong_beats):
    """2x2 block: metric accent alignment + parallel-motion penalty."""
    pc, onset = decode(cell)
    groove = 0.0 if onset in strong_beats else 0.8
    parallel = 0.0
    if s > 0 and v > 0:
        # compare vertical intervals across adjacent sections
        cur = abs(decode(grid[v, s])[0] - decode(grid[v-1, s])[0]) % 12
        prv = abs(decode(grid[v, s-1])[0] - decode(grid[v-1, s-1])[0]) % 12
        if cur == prv and cur in (0, 7):                # parallel unison/fifth
            parallel = 3.0
    return groove + parallel

def full_conditional(grid, v, s, chord_tones, strong_beats, T=1.0):
    """Energy of every candidate state for cell (v,s), given all others."""
    V, S = grid.shape
    energies = np.zeros(K)
    for a in range(K):
        E = singleton_energy(a, chord_tones[s], target_density=4, n_notes=4)
        if s > 0:
            E += horizontal_energy(a, grid[v, s-1])
        if s < S - 1:
            E += horizontal_energy(grid[v, s+1], a)
        for u in range(V):
            if u != v:
                E += vertical_energy(a, grid[u, s])
        E += block_energy(a, grid, v, s, strong_beats)
        energies[a] = E
    p = np.exp(-energies / T)
    return p / p.sum()

def gibbs_sample(grid, chord_tones, strong_beats, sweeps=200, T0=2.0, T1=0.3):
    """Blocked Gibbs sampling with temperature annealing."""
    V, S = grid.shape
    for i in range(sweeps):
        T = T0 + (T1 - T0) * (i / sweeps)               # anneal down
        # random sweep order; resample one random cell per micro-step
        for _ in range(V * S):
            v, s = np.random.randint(V), np.random.randint(S)
            p = full_conditional(grid, v, s, chord_tones, strong_beats, T)
            grid[v, s] = np.random.choice(K, p=p)
    return grid

# Example: 4 voices x 8 sections, C major chord tones per section
V, S = 4, 8
grid = np.random.randint(0, K, size=(V, S))             # noise init
chord_tones = [ {0, 4, 7}, {5, 9, 0}, {7, 11, 2}, {0, 4, 7} ] * 2  # I-V-vii°-I x2
strong_beats = {0, 4}                                    # downbeat + mid-bar
grid = gibbs_sample(grid, chord_tones, strong_beats)
print(grid)  # equilibrium UnitMatrix states -> decode to MIDI via musicom engine
```

## 6. Pitfalls

1. **Slow mixing / grid-lock**: strong potentials freeze cells at local minima → single repeated chord. Fix: anneal T high→low, blocked Gibbs, randomized sweep order, monitor energy trace.
2. **Partition-function blindness**: Z intractable → likelihood not computable, only sampling. Fix: never normalize; use pseudo-likelihood (Besag) or contrastive divergence if a likelihood is required.
3. **Voice collapse**: weak vertical potentials → unison collapse (cf. FHNS 037 / GPC 061). Fix: strong parallel-motion penalty + per-voice register biases; verify per-voice pitch entropy.
4. **Boundary artifacts**: edge cells have truncated neighborhoods → drift to singleton prior. Fix: clamp boundaries to skeleton/chord tones, or periodic horizontal wrap for loop forms.
5. **Off-grid drift**: continuous onset offsets land between ticks → validation failure. Fix: quantize onsets inside the alphabet; run `composer.validate()` before export.
6. **Cost explosion**: K = |alphabet| multiplies every sweep. Fix: factor pitch/rhythm into coupled layers, prune alphabet to scale+chord tones, blocked row updates.

## 7. Comparison With Related Methods

| Method | Relation to MRFCC |
|---|---|
| 002 Markov | directed 1D chain; MRFCC = undirected 2D — context flows all 4 directions, later sections constrain earlier ones |
| 022 MCWS | 1D wavefront; MRFCC = full 2D lattice with vertical (harmonic) cliques |
| 033 WFCGS | deterministic hard-constraint collapse; MRFCC = probabilistic soft-potential version with equilibrium distribution |
| 055 SAMC | anneals global energy by Metropolis; MRFCC = spatial-decomposition version (local cliques, blocked updates) |
| 061 GPC | continuous-time Bayesian prior; MRFCC = discrete-grid Bayesian counterpart |

## 8. References

- Besag, J. (1974). "Spatial Interaction and the Statistical Analysis of Lattice Systems." *JRSS-B* 36(2). (Hammersley–Clifford theorem; pseudo-likelihood.)
- Geman, S. & Geman, D. (1984). "Stochastic Relaxation, Gibbs Distributions, and the Bayesian Restoration of Images." *IEEE TPAMI* 6(6). (Gibbs sampling.)
- Pachet, F. & Roy, P. (2011). "Markov constraints: steerable generation of Markov sequences." *Constraints* 16(2). (Steerable Markov generation — conceptual ancestor.)
- Hadjeres, G., Pachet, F., & Nielsen, F. (2017). "DeepBach: a Steerable Model for Bach Chorales Generation." *ICML 2017*. arXiv:1612.01010. (Chorale as graphical model; pseudo-Gibbs sampling.)
- Wang, Z., et al. (2020). "Melody Harmonization Using Orderless NADE, Chord Balancing, and Blocked Gibbs Sampling." arXiv:2010.13468. (Blocked Gibbs for harmonization.)
- Hammersley, J. M. & Clifford, P. (1971). "Markov fields on finite graphs and lattices." (Unpublished; factorization theorem origin.)
