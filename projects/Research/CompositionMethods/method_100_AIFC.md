# Method 100 — Active Inference Composition (AIFC)

**ID**: 100
**Paradigm**: AI-Driven
**Layer**: concrete
**Acronym**: AIFC

## One-line Description

Casts composition as closed-loop active inference: a multi-level hierarchical generative model (section/chord/note scales) drives event-by-event selection by minimizing variational free energy, balancing prior preference fulfillment (tonal gravity, meter, voice-leading, form) with epistemic information gain.

## Full Summary Table Row

```
| **100** | concrete | Active Inference Composition (AIFC) | **AI-Driven** | Pitch, Rhythm, Harmony, Structure, Texture | Strong (Prior-guided, HOME/LIFT/TENSE/TURN) | Grid-Locked / Continuous | Macro / Generative Model Horizon | $O(T * d^2)$ per step, $O(T * D * d^2)$ learn | Casts composition as closed-loop active inference: a multi-level hierarchical generative model drives note-by-note event selection by minimizing expected free energy. Prior preferences encode tonal gravity, metric binding, voice-leading, and macro-form. Multi-agent (one per voice) with shared form + harmonic state. |
```

## Extended Description

**Active Inference Composition (AIFC)** is grounded in the free-energy principle (Friston 2010) and its application to music (Friston & Friston 2016). It treats composition as a closed-loop perception-action process where an agent:

1. Maintains a **hierarchical generative model** of music with temporal depth: slow (section/form, 4–16 bar scale), medium (chord/harmonic function, 1–4 beat scale), fast (note/ornamentation, sub-beat scale).
2. At each step, **infers the hidden state** (tonal function, metric position, section identity) from the current event by minimizing variational free energy $F$.
3. **Selects the next event** by minimizing *expected* free energy $G(a)$, which balances:
   - **Pragmatic value** — fulfilling prior preferences (tonic on downbeats, stepwise motion, cadence closure)
   - **Epistemic value** — information gain that resolves uncertainty (exploration of harmonic regions, motivic development)

### Mathematical Core

**Variational free energy** (perception/state-update):

$$F(t) = D_{KL}[Q(\mathbf{s}_{1:t}) \parallel P(\mathbf{s}_{1:t})] - \mathbb{E}_Q[\ln P(\mathbf{o}_{1:t} \mid \mathbf{s}_{1:t})]$$

**Expected free energy** (action/event-selection):

$$G(a) = \underbrace{D_{KL}[Q(\mathbf{o}_{t+1} \mid a) \parallel P(\mathbf{o}_{t+1} \mid \mathbf{C})]}_{\text{pragmatic}} + \underbrace{\mathbb{E}_{Q(\mathbf{s}_{t+1} \mid a)}[H[P(\mathbf{o}_{t+1} \mid \mathbf{s}_{t+1})]}_{\text{epistemic}}$$

where $\mathbf{C}$ encodes prior preferences — the "taste" of the composer-agent.

### Hierarchical Generative Model

Three temporal scales:

| Level | State variable | Temporal resolution | Musical interpretation |
|---|---|---|---|
| Slow ($\mathbf{s}^{(3)}$) | Section ID, tonality, tempo | Every 4–16 bars | Form (intro, verse, chorus, bridge, outro) |
| Medium ($\mathbf{s}^{(2)}$) | Chord/function, metric position | Every 1–4 beats | Harmonic progression, groove pattern |
| Fast ($\mathbf{s}^{(1)}$) | Pitch class, onset flag, duration | Every note/event | Note-level ornamentation, articulation |

Higher levels contextualize lower ones: section determines chord repertoire, chord determines available pitch classes.

## Musical Elements Framework

| Element | Mapping |
|---|---|
| **PITCH** | Fast-level state $\mathbf{s}^{(1)}$: pitch class & octave. Likelihood $P(o \mid s^{(1)}, s^{(2)})$ biases chord tones. Prior $\mathbf{C}$ prefers stepwise motion, tonic at phrase boundaries. Epistemic value drives exploratory pitches (leading tones, tritones). |
| **RHYTHM** | Medium-level metric position + IOI class. Slow level sets global meter. Action space includes "wait" (rest/continuation). Prior prefers downbeat onsets, regular subdivisions. Syncopation emerges from epistemic seeking. |
| **HARMONY** | Medium-level chord/function transitions $P(s^{(2)}_{t+1} \mid s^{(2)}_t, s^{(3)})$ = harmonic grammar. Prior $\mathbf{C}$ profiles HOME/LIFT/TENSE/TURN per section. Authentic cadence (V→I) has high pragmatic value at section end. |
| **STRUCTURE** | Slow-level markov chain $P(s^{(3)}_{t+1} \mid s^{(3)}_t)$ defines form. Each section carries its own harmonic repertoire, metric profile, duration distribution, dynamic envelope. Form unfolds autonomously through state transitions. |
| **TEXTURE** | Multi-agent (one per UnitMatrix voice) with shared slow state but independent fast/medium beliefs. Cross-voice coupling in joint generative model enforces voice-leading constraints. Shared form + harmonic state ensures vertical coherence. |

## UnitMatrix Integration

- **Rows (Voices)**: Each voice = one active inference agent (or one dimension of multi-D action space). Voice-specific priors encode registral range, typical interval sizes, rhythmic density.
- **Columns (Sections)**: Each section = a distinct slow-level state $\mathbf{s}^{(3)}$ with associated transition/preference/duration parameters. The state transition triggers a new column.
- **Cells (MusicUnit)**: The trace of fast-level events $\mathbf{o}_t$ emitted by voice $v$ during the slow-level dwell time in section $s$.

## Python Implementation Sketch

```python
class ActiveInferenceComposer:
    """
    Generates a UnitMatrix via active inference (free-energy minimization).
    
    Three-level hierarchical generative model:
      s3 (slow): section type, tonality, tempo — transitions every 4-16 bars
      s2 (medium): chord/function, metric position — transitions every 1-4 beats  
      s1 (fast): pitch class, onset flag, duration — transitions every note
    
    Action: choose (pitch_class, onset_flag, duration, velocity) minimizing
    expected free energy G(a) = pragmatic_value + epistemic_value
    """
    
    def __init__(self, bpm=120, resolution=480):
        # Generative model parameters
        # s3: section_id, global_key, tempo, meter
        self.num_sections = 6  # intro, verse, chorus, verse, chorus, outro
        self.form_grammar = np.array([...])  # P(s3_t+1 | s3_t)
        # s2: chord function within section context
        self.harmonic_grammars = {...}  # per-section chord transition matrices
        # s1: pitch/onset/duration given (s2, s3)
        self.likelihood = {...}  # P(o_t | s1_t, s2_t, s3_t)
        # Prior preferences C (expected free energy target)
        self.preferences = {...}  # per-section preference profiles
        # Variational parameters
        self.temperature = 1.0
        self.epistemic_weight = 0.3
        
    def expected_free_energy(self, action, beliefs):
        """
        G(a) = KL[Q(o|a) || P(o|C)] + E_Q(s|a)[H[P(o|s)]]
        """
        pragmatic = kl_divergence(
            self.predict_observation(action, beliefs),
            self.preferences[beliefs['section']]
        )
        epistemic = expected_entropy(
            self.predict_observation(action, beliefs),
            self.likelihood
        )
        return pragmatic + self.epistemic_weight * epistemic
    
    def compose(self, num_voices=4):
        """
        Main composition loop.
        Returns: list of MusicEvent per voice
        """
        events = {v: [] for v in range(num_voices)}
        beliefs = self.initialize_beliefs()
        
        for step in range(max_steps):
            # 1. Perception: update beliefs from current observation
            beliefs = self.update_beliefs(beliefs, last_observation)
            
            # 2. Action selection: choose next event for each voice
            for voice in range(num_voices):
                # Enumerate candidate actions
                candidates = self.get_candidates(beliefs, voice)
                G = [self.expected_free_energy(a, beliefs) for a in candidates]
                # Sample action proportional to exp(-G/temperature)
                action = candidates[np.argmin(G)]
                # Or: sampled = softmax(-G/temp)
                events[voice].append(action_to_event(action))
            
            # 3. Check section transition
            beliefs = self.maybe_transition_section(beliefs, step)
        
        return events
    
    def to_unitmatrix(self, events, section_boundaries):
        """Assemble events into UnitMatrix rows/columns."""
        matrix = UnitMatrix(num_voices=len(events), 
                           num_sections=len(section_boundaries)-1)
        for v_id, evts in events.items():
            for section_idx, (start, end) in enumerate(
                zip(section_boundaries[:-1], section_boundaries[1:])):
                cell_events = [e for e in evts if start <= e.start_tick < end]
                matrix.set_cell(v_id, section_idx, MusicUnit(cell_events))
        return matrix
```

## Candidate Code Path

The method would live in `generators/aifc_composer.py` under `musicom/generators/`, alongside other concrete-layer generators. Core modules:
- `generators/aifc_composer.py` — main ActiveInferenceComposer class
- `generators/aifc_generative_model.py` — hierarchical generative model specification
- `generators/aifc_preferences.py` — prior preference profile templates (pop, classical, minimalism)
- `rules/realize.py` — would already handle the concrete→events bridge

The method feeds `generators/` via the variational inference loop that outputs per-cell MusicEvents, ready for `validate()` → `to_midi()`.

## References

1. Friston, K. J. & Friston, D. A. (2016). "A Free Energy Formulation of Music Generation and Perception: Helmholtz Revisited." *The Routledge Handbook of Music and Artificial Intelligence* (Ch. 18).
2. Friston, K. J. (2010). "The free-energy principle: a unified brain theory?" *Nature Reviews Neuroscience* 11, 127–138.
3. Friston, K. J., Parr, T. & Zeidman, P. (2018). "Bayesian model reduction and active inference." *PLoS ONE* 13(12), e0209306.
4. Parr, T. & Friston, K. J. (2019). "Generalised free energy and active inference." *Biological Cybernetics* 113, 495–511.
5. Kämäräinen, T. (2024). "Generative music and the free energy principle." *Proc. Int'l Conf. on Computational Creativity* (ICCC).
6. Pearce, M. T. et al. (2010). "Unsupervised statistical learning underpins computational, behavioural, and neural manifestations of musical expectation." *Neuroimage* 50(1), 302–313.
7. Rohrmeier, M. A. & Koelsch, S. (2012). "Predictive information processing in music cognition." *Int. J. Psychophysiol.* 83(2), 164–175.