# Multi-Objective Evolutionary Pareto Composition (MOEPC) — Method 098

## Quick Reference

| Attribute | Value |
|---|---|
| **Method ID** | 098 |
| **Acronym** | MOEPC |
| **Paradigm** | Stochastic |
| **Layer** | concrete |
| **Primary Elements** | Pitch, Rhythm, Harmony, Structure, Texture |
| **Tonal Gravity** | Moderate (Pareto-guided, multi-objective fitness) |
| **Metric Binding** | Grid-Locked / Continuous |
| **Memory Depth** | Macro / Pareto Front |
| **Time Complexity** | $\mathcal{O}(I \cdot P \cdot N \cdot M)$ |

## Summary Table Row

```
| **098** | concrete | Multi-Objective Evolutionary Pareto Composition (MOEPC) | **Stochastic** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Pareto-guided, multi-objective fitness) | Grid-Locked / Continuous | Macro / Pareto Front | $\mathcal{O}(I \cdot P \cdot N \cdot M)$ | Evolves multiple conflicting musical objectives (harmonic quality, melodic quality, rhythmic coherence, voice independence) via NSGA-II, returning a Pareto front of trade-off compositions. The front itself defines macro-form. |
```

## Source

- Jeong, J., Kim, Y. & Ahn, C. W. (2017). "A multi-objective evolutionary approach to automatic melody generation." *Expert Systems with Applications* 90, 50–61. doi:10.1016/j.eswa.2017.08.014.
- De Prisco, R., Zaccagnino, G. & Zaccagnino, R. (2019). "EvoComposer: An Evolutionary Algorithm for 4-Voice Music Compositions." *Evolutionary Computation* 28(4), 621–658. doi:10.1162/evco_a_00265.
- Scirea, M., Togelius, J., Eklund, P. W. & Risi, S. (2016). "MetaCompose: A compositional evolutionary music composer." In *Proc. 5th Int'l Conf. Evolutionary and Biologically Inspired Music, Sound, Art and Design* (EvomusArt), pp. 202–217.
- Deb, K., Pratap, A., Agarwal, S. & Meyarivan, T. (2002). "A fast and elitist multiobjective genetic algorithm: NSGA-II." *IEEE Trans. Evolutionary Computation* 6(2), 182–197.
- Lopes, F. M., Oliveira, C. M. & Costa, R. M. (2017). "Evolutionary methods for automatic melody composition based on Zipf's law and Fux's rules." *Journal of New Music Research* 46(4), 337–352.

## Layer

**concrete** — generates concrete pitch/rhythm/harmony events organized into UnitMatrix cells. The evolutionary search directly optimizes note-level representations (chromosomes encoding pitch, onset, duration, velocity per voice/time-slot), producing realizable MusicalEvents. Feeds generators/ via the evolved population's decoded individuals, and the Pareto front directly maps to UnitMatrix voice×section layouts.

## Paradigm

**Stochastic** — the method is a population-based metaheuristic with stochastic operators (crossover, mutation, tournament selection) guided by non-dominated sorting and crowding distance. There is no deterministic rewrite rule, no nature-inspired physical simulation, and no learned neural network. The stochastic nature of variation and selection means repeated runs produce different compositions.

## Extended Description

### Mathematical Foundation

MOEPC solves the general multi-objective optimization problem:

Minimize $\mathbf{f}(\mathbf{x}) = [f_1(\mathbf{x}), f_2(\mathbf{x}), \ldots, f_M(\mathbf{x})]^T$

subject to $g_j(\mathbf{x}) \leq 0$, $j = 1, \ldots, J$

where $\mathbf{x} \in \mathbb{X}$ is a chromosome encoding a complete or partial composition (pitch, onset, duration, velocity per voice per time slot), and each $f_i$ is a musical objective function. For $M=2$, the two objectives are deliberately conflicting (e.g., harmonic quality vs. melodic quality, or stability vs. tension).

**Pareto dominance**: $\mathbf{x}_A \prec \mathbf{x}_B$ iff $\forall i \in \{1,\ldots,M\}: f_i(\mathbf{x}_A) \leq f_i(\mathbf{x}_B)$ and $\exists j: f_j(\mathbf{x}_A) < f_j(\mathbf{x}_B)$.

**Pareto front**: $\mathcal{PF} = \{ \mathbf{x} \in \mathbb{X} \mid \nexists \mathbf{x}' \in \mathbb{X}: \mathbf{x}' \prec \mathbf{x} \}$ — the set of all non-dominated solutions.

**NSGA-II procedure** (Deb et al. 2002):

1. **Initialization**: Generate $P$ chromosomes. Each $C = (c_{v,t,s})$ is a 3D tensor over voices $v \in [1,V]$, time slots $t \in [1,T]$, parameters $s \in \{\text{PC}, \text{octave}, \text{onset}, \text{dur}, \text{vel}\}$.
2. **Non-dominated sorting**: For each solution, compute (a) domination count $n_i$ = number of solutions dominating $i$, (b) set $S_i$ = solutions dominated by $i$. Front $\mathcal{F}_1$ = all with $n_i = 0$; $\mathcal{F}_{k+1}$ = solutions dominated only by $\mathcal{F}_k$.
3. **Crowding distance**: For each front $\mathcal{F}_k$, sort by each objective $f_m$, then $d_i = \sum_{m=1}^M \frac{f_m(i+1) - f_m(i-1)}{f_m^{\max} - f_m^{\min}}$.
4. **Selection**: $i$ beats $j$ if rank$_i$ < rank$_j$ OR (rank$_i$ = rank$_j$ AND $d_i > d_j$).
5. **Crossover**: Musical operators — chord-preserving crossover (swap contiguous section blocks), voice-exchange crossover (swap voice assignments), harmonic crossover (blend chord voicings).
6. **Mutation**: Pitch-shift ($\pm$1–3 semitones, probability $p_m$), duration-jitter (scale 0.5×–2×), voice-leading repair (correct parallel fifths/octaves), rhythm-shift (move onset by $\pm \Delta t$).
7. **Replacement**: Combine $\mathcal{P}_t \cup \mathcal{Q}_t$ (size $2P$), non-dominated sort, fill new $\mathcal{P}_{t+1}$ front-by-front, filling last front by crowding distance.
8. **Terminate**: After $I$ generations or stagnation of hypervolume indicator.

### Objective Functions

For the **EvoComposer** instantiation (De Prisco et al. 2019), two objectives:

1. **Harmonic objective** $f_h$: Evaluate chord choices per time slot against corpus-derived transition probabilities and music-theory rules. For each chord $c_t$ at time $t$:
   - $p_{\text{transition}}(c_t \mid c_{t-1})$ from Bach chorale statistics
   - $p_{\text{voicing}}(c_t)$ = compactness × completeness × range score
   - $p_{\text{non-harmonic}}(\cdot)$ = probability that a non-harmonic tone is correctly resolved
   - $f_h = -\log(\prod_{t} p_{\text{transition}} \cdot p_{\text{voicing}} \cdot p_{\text{resolution}})$

2. **Melodic objective** $f_m$: Evaluate each voice's melodic line for:
   - Stepwise motion frequency (corpus-derived: Bach chorales have ~70% stepwise motion)
   - Leap management (leaps > P5 are rare; leaps > P5 followed by step in opposite direction)
   - Range control (each voice stays within its typical tessitura)
   - Cadential formulas (suspension-resolution patterns)
   - $f_m = \sum_{v=1}^4 w_v \cdot \text{melodic\_score}(v)$

For the **stability-tension** instantiation (Jeong et al. 2017):

1. **Stability**: $\text{Stability} = \frac{1}{N} \sum_{t} [\text{consonance}(c_t) + \text{tonal\_center\_strength}(\text{mel}_t)]$
2. **Tension**: $\text{Tension} = \frac{1}{N} \sum_{t} [\text{dissonance}(c_t) + \text{chromatic\_density}(\text{mel}_t) + \text{interval\_variance}(\text{mel}_t)]$

### Python Implementation Sketch

```python
import numpy as np
from typing import List, Tuple, Callable
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

# --- Chromosome representation ---
class CompositionChromosome:
    """3D tensor: voices × time_slots × parameters"""
    def __init__(self, V: int, T: int):
        # pitch: [pitch_class (0-11), octave (2-7)]
        # rhythm: [onset (ticks), duration (ticks)]
        # velocity: [velocity (0-127)]
        self.pc = np.random.randint(0, 12, (V, T))      # pitch classes
        self.oct = np.random.randint(3, 6, (V, T))       # octaves
        self.onset = np.zeros((V, T), dtype=int)         # onset in ticks
        self.dur = np.random.choice([240, 480, 720, 960], (V, T))  # duration
        self.vel = np.random.randint(60, 110, (V, T))    # velocity
    
    def to_pitch(self, v: int, t: int) -> int:
        return self.pc[v, t] + 12 * self.oct[v, t]

class MOEPCComposer:
    """Multi-Objective Evolutionary Pareto Composition engine"""
    
    def __init__(self, n_voices=4, n_slots=16, pop_size=100, 
                 n_generations=100, crossover_rate=0.8, mutation_rate=0.1):
        self.V = n_voices
        self.T = n_slots
        self.P = pop_size
        self.I = n_generations
        self.pc = crossover_rate
        self.pm = mutation_rate
    
    def harmonic_objective(self, chromo: CompositionChromosome) -> float:
        """Evaluate harmonic quality: chord grammar, voicing, voice-leading"""
        score = 0.0
        for t in range(self.T):
            chord = [chromo.to_pitch(v, t) % 12 for v in range(self.V)]
            # Chord grammar: prefer I→IV→V→I progressions
            score += self._chord_grammar_score(chord, t)
            # Voicing compactness: penalize wide spreads
            pitches = sorted([chromo.to_pitch(v, t) for v in range(self.V)])
            score -= (pitches[-1] - pitches[0]) * 0.01
            # Voice-leading: penalize parallel fifths/octaves
            if t > 0:
                intervals_prev = [chromo.to_pitch(v, t-1) for v in range(self.V)]
                intervals_curr = [chromo.to_pitch(v, t) for v in range(self.V)]
                for v1 in range(self.V):
                    for v2 in range(v1+1, self.V):
                        d_prev = abs(intervals_prev[v1] - intervals_prev[v2]) % 12
                        d_curr = abs(intervals_curr[v1] - intervals_curr[v2]) % 12
                        if d_prev in (0, 7) and d_curr in (0, 7):
                            score -= 5.0  # parallel perfect interval penalty
        return score
    
    def melodic_objective(self, chromo: CompositionChromosome) -> float:
        """Evaluate melodic quality: smoothness, range, tonal centering"""
        score = 0.0
        for v in range(self.V):
            pitches = [chromo.to_pitch(v, t) for t in range(self.T)]
            for t in range(1, self.T):
                interval = abs(pitches[t] - pitches[t-1])
                if interval <= 2:
                    score += 1.0  # stepwise = good
                elif interval > 12:
                    score -= 2.0  # large leap = bad
            # Tonal centering: prefer tonic and dominant
            tonic_pc = 0  # C major
            for t in range(self.T):
                pc = pitches[t] % 12
                if pc == tonic_pc:
                    score += 0.5
                elif pc in (tonic_pc + 7, tonic_pc + 4):  # dominant, mediant
                    score += 0.2
        return score
    
    def _chord_grammar_score(self, chord_pcs: List[int], t: int) -> float:
        """Score chord quality based on pitch-class set"""
        from rules.set_theory import normal_form
        pc_set = frozenset(chord_pcs)
        nf = normal_form(chord_pcs)
        # Prefer triads and seventh chords
        if len(pc_set) == 3: score = 3.0
        elif len(pc_set) == 4: score = 2.0
        else: score = 0.0
        return score
    
    def non_dominated_sort(self, objectives: np.ndarray) -> List[np.ndarray]:
        """Return list of front indices (NSGA-II fast non-dominated sort)"""
        P = len(objectives)
        domination_count = np.zeros(P, dtype=int)
        dominated_sets = [set() for _ in range(P)]
        fronts = []
        
        for i in range(P):
            for j in range(P):
                if i == j: continue
                if all(objectives[i] <= objectives[j]) and any(objectives[i] < objectives[j]):
                    dominated_sets[i].add(j)
                elif all(objectives[j] <= objectives[i]) and any(objectives[j] < objectives[i]):
                    domination_count[i] += 1
            if domination_count[i] == 0:
                fronts.append(i)
        
        # Simplified: return front 0 (non-dominated)
        return [np.array(fronts)]
    
    def crowding_distance(self, objectives: np.ndarray, front: np.ndarray) -> np.ndarray:
        """Compute crowding distance within a front"""
        M = objectives.shape[1]
        dist = np.zeros(len(front))
        for m in range(M):
            order = np.argsort(objectives[front, m])
            mmin, mmax = objectives[front, m].min(), objectives[front, m].max()
            if mmax - mmin == 0: continue
            dist[order[0]] = np.inf
            dist[order[-1]] = np.inf
            for k in range(1, len(order)-1):
                dist[order[k]] += (objectives[front[order[k+1]], m] 
                                   - objectives[front[order[k-1]], m]) / (mmax - mmin)
        return dist
    
    def crossover(self, p1: CompositionChromosome, p2: CompositionChromosome) -> Tuple[CompositionChromosome, CompositionChromosome]:
        """Section-block crossover: swap a contiguous block of time slots"""
        c1, c2 = CompositionChromosome(self.V, self.T), CompositionChromosome(self.V, self.T)
        # Copy
        for v in range(self.V):
            for t in range(self.T):
                c1.pc[v,t], c1.oct[v,t], c1.dur[v,t], c1.vel[v,t] = p1.pc[v,t], p1.oct[v,t], p1.dur[v,t], p1.vel[v,t]
                c2.pc[v,t], c2.oct[v,t], c2.dur[v,t], c2.vel[v,t] = p2.pc[v,t], p2.oct[v,t], p2.dur[v,t], p2.vel[v,t]
        # One-point crossover at midpoint
        mid = self.T // 2
        for v in range(self.V):
            c1.pc[v, mid:], c2.pc[v, mid:] = p2.pc[v, mid:].copy(), p1.pc[v, mid:].copy()
            c1.oct[v, mid:], c2.oct[v, mid:] = p2.oct[v, mid:].copy(), p1.oct[v, mid:].copy()
        return c1, c2
    
    def mutate(self, chromo: CompositionChromosome) -> CompositionChromosome:
        """Pitch-shift mutation with small probability"""
        for v in range(self.V):
            for t in range(self.T):
                if np.random.random() < self.pm:
                    # Pitch shift: +/- 1-3 semitones
                    shift = np.random.choice([-3, -2, -1, 1, 2, 3])
                    new_pc = (chromo.pc[v,t] + shift) % 12
                    oct_shift = (chromo.pc[v,t] + shift) // 12
                    chromo.pc[v,t] = new_pc
                    chromo.oct[v,t] = max(2, min(7, chromo.oct[v,t] + oct_shift))
                if np.random.random() < self.pm * 0.5:
                    # Duration jitter
                    chromo.dur[v,t] = int(chromo.dur[v,t] * np.random.uniform(0.5, 2.0))
        return chromo
    
    def evolve(self) -> List[CompositionChromosome]:
        """Run NSGA-II evolution and return Pareto front"""
        # Initialize population
        pop = [CompositionChromosome(self.V, self.T) for _ in range(self.P)]
        
        for gen in range(self.I):
            # Evaluate objectives
            objs = np.array([(self.harmonic_objective(c), self.melodic_objective(c)) 
                             for c in pop])
            
            # Non-dominated sort
            fronts = self.non_dominated_sort(-objs)  # maximize → negate for minimization
            
            # Selection + variation → offspring
            offspring = []
            while len(offspring) < self.P:
                # Tournament selection (rank + crowding)
                i1, i2 = np.random.randint(0, self.P, 2)
                selected = i1  # simplified: pick first
                if np.random.random() < self.pc:
                    # Crossover
                    c1, c2 = self.crossover(pop[selected], pop[np.random.randint(0, self.P)])
                    offspring.append(self.mutate(c1))
                    if len(offspring) < self.P:
                        offspring.append(self.mutate(c2))
                else:
                    offspring.append(self.mutate(pop[selected]))
            
            # Elitist replacement
            combined = pop + offspring
            comb_objs = np.array([(self.harmonic_objective(c), self.melodic_objective(c)) 
                                  for c in combined])
            fronts = self.non_dominated_sort(-comb_objs)
            
            # Select top P by front priority + crowding distance
            new_pop = []
            for front_idx in fronts:
                if len(new_pop) + len(front_idx) <= self.P:
                    new_pop.extend([combined[i] for i in front_idx])
                else:
                    dist = self.crowding_distance(-comb_objs, front_idx)
                    order = np.argsort(-dist)
                    remaining = self.P - len(new_pop)
                    for k in order[:remaining]:
                        new_pop.append(combined[front_idx[k]])
                    break
            pop = new_pop
        
        # Return Pareto front (front 0)
        final_objs = np.array([(self.harmonic_objective(c), self.melodic_objective(c)) 
                               for c in pop])
        fronts = self.non_dominated_sort(-final_objs)
        pareto_front = [pop[i] for i in fronts[0]]
        return pareto_front
    
    def to_unitmatrix(self, chromo: CompositionChromosome, bpm=120, ticks_per_beat=480) -> UnitMatrix:
        """Decode a Pareto-optimal chromosome into a UnitMatrix"""
        # Map time slots to ticks (e.g., 1 slot = 1 beat)
        ticks_per_slot = ticks_per_beat
        composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=ticks_per_beat, beats_per_bar=4)
        composer.create_matrix(num_voices=self.V, num_sections=1)
        composer.add_section("A", bars=4)
        
        voice_names = ["Soprano", "Alto", "Tenor", "Bass"][:self.V]
        for v in range(self.V):
            composer.add_voice(voice_names[v], program=MidiInstrument.CHURCH_ORGAN, channel=v)
            events = []
            for t in range(self.T):
                pitch = chromo.to_pitch(v, t)
                start = chromo.onset[v, t] if chromo.onset[v, t] > 0 else t * ticks_per_slot
                end = start + chromo.dur[v, t]
                events.append(MusicEvent(pitch=pitch, volume=chromo.vel[v, t],
                                         start_tick=start, end_tick=end))
            from workflows.unitmatrix_composer import create_note_unit
            composer.fill_voice_section(voice_names[v], "A", create_note_unit(events))
        
        return composer
```

## Musical Elements Framework

See full method section in `methods_db.md` — detailed mapping of PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE to the multi-objective framework.

## UnitMatrix Integration

**Voices**: The chromosome $C$ has an explicit voice dimension. Voice assignment to UnitMatrix rows is 1:1. Multiple Pareto-optimal solutions can be decoded and assembled.

**Sections**: Two strategies: (A) single-population multi-section for global coherence, (B) per-section sub-populations for maximal section contrast.

**Cells**: Decoded from Pareto-optimal individuals, validated via `composer.validate()` for zero-drift.

## Candidate Code Path

```
generators/evolutionary/
├── __init__.py          # register MOEPC in METHOD_REGISTRY
├── chromosome.py        # CompositionChromosome class
├── objectives.py        # Harmonic, melodic, rhythmic, texture objective functions
├── nsga2.py             # NSGA-II core: non-dominated sort, crowding distance, selection
├── operators.py         # Musical crossover and mutation operators
├── moepc_composer.py    # MOEPCComposer main class
└── test_moepc.py        # Unit tests + Pareto front verification
```

## Distinctive Contribution

MOEPC is the **first multi-objective method** in the methods DB. All prior optimization-based methods (003 Genetic, 055 SAMC, 073 HSIC) use single-objective/scalarized fitness. The Pareto-front output concept — where the evolutionary algorithm returns a *family* of trade-off solutions rather than one optimum — is fundamentally different from:

- **003 Genetic Genome Selection**: single weighted-sum objective → one solution
- **055 SAMC**: single energy functional → one solution (via annealing)
- **002 Markov / 086 HMM**: stochastic sampling from conditional distributions → one sequence
- **073 HSIC**: single fitness with three operators → one solution per run

Additionally, the front-as-form concept — selecting different front points for different sections — has no analogue in any existing DB method.

## References

1. Deb, K., Pratap, A., Agarwal, S. & Meyarivan, T. (2002). "A fast and elitist multiobjective genetic algorithm: NSGA-II." *IEEE Trans. Evolutionary Computation* 6(2), 182–197.
2. Jeong, J., Kim, Y. & Ahn, C. W. (2017). "A multi-objective evolutionary approach to automatic melody generation." *Expert Systems with Applications* 90, 50–61.
3. De Prisco, R., Zaccagnino, G. & Zaccagnino, R. (2019). "EvoComposer: An Evolutionary Algorithm for 4-Voice Music Compositions." *Evolutionary Computation* 28(4), 621–658.
4. Scirea, M., Togelius, J., Eklund, P. W. & Risi, S. (2016). "MetaCompose: A compositional evolutionary music composer." In *Proc. EvomusArt*, pp. 202–217.
5. Lopes, F. M., Oliveira, C. M. & Costa, R. M. (2017). "Evolutionary methods for automatic melody composition based on Zipf's law and Fux's rules." *Journal of New Music Research* 46(4), 337–352.
6. Zitzler, E. & Thiele, L. (1999). "Multiobjective evolutionary algorithms: A comparative case study and the strength Pareto approach." *IEEE Trans. Evolutionary Computation* 3(4), 257–271.