# Method 109 — Spiking Neural Network Composition (SNN-C)

**Acronym**: SNN-C
**Paradigm**: Nature-Led
**Layer**: concrete
**Next free ID**: 110

## Summary Table Row

|| **109** | concrete | Spiking Neural Network Composition (SNN-C) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Strict (Mode/Synaptic-guided) | Grid-Locked / Continuous | Meso / Spike-Train | $\mathcal{O}(N \cdot T)$ simulation | Generates musical compositions using a multi-region spiking neural network of Izhikevich neurons with STDP learning. Hippocampal memory stores motif sequences via spike-timing-dependent plasticity; prefrontal cortex encodes mode/scale/style knowledge; thalamic theta-gamma oscillators drive metric hierarchy; insula system controls tension/release trajectory. Spike trains decoded to pitch (population-rate), duration (ISI), velocity (peak firing). Biologically-plausible Nature-Led counterpart to 059 ESN-RC / 037 FHN; non-backpropagation foil to 054 ATS / 046 VAE-LSI. |

## Extended Description

Spiking Neural Network Composition (SNN-C) is a brain-inspired computational model that generates musical sequences using a multi-region spiking neural network of Izhikevich neurons with spike-timing-dependent plasticity (STDP). Unlike rate-coded neural networks (RNNs, transformers, ESNs), SNNs communicate via discrete spike events (action potentials) in continuous time, where the *exact timing* of each spike carries information — a fundamentally different computational substrate that is closer to biological neural computation.

### Architecture: Four Brain-Region Subsystems

**1. Hippocampal Memory System** — a recurrent spiking network that stores musical sequences (note transitions, chord progressions, rhythmic patterns) via STDP. The CA3 region's recurrent collaterals form auto-associative memories of motif patterns; CA1's feed-forward connections pattern-complete partial cues into full motifs; dentate gyrus separates overlapping patterns. Memory recall is triggered by injecting a partial spike-train pattern; the network completes the sequence via attractor dynamics.

**2. Prefrontal Knowledge System** — a feed-forward spiking network encoding stylistic rules, mode/scale constraints, and structural form templates. Synaptic weights encode learned distributions of pitch transitions, interval classes, and duration classes from a training corpus. This system biases hippocampal output toward style-appropriate outputs (genre, composer, mode-conditioned). Mode-conditioning uses tonality-selective neural populations whose firing patterns correspond to Krumhansl-Schmuckler key profiles.

**3. Thalamic Clock/Oscillation System** — a pacemaker network of intrinsically bursting (IB) Izhikevich neurons generating theta (4–8 Hz) and gamma (30–80 Hz) band oscillations. Theta encodes bar-level periodicity; gamma encodes note-level timing. Phase-locking between theta and gamma (PLV) provides hierarchical metric binding — high PLV yields rigid grid, low PLV yields swung/fluid time. Oscillation frequencies adapt to tempo via thalamocortical relay cells with activity-dependent adaptation currents.

**4. Insula Emotion System** — a spiking network encoding the emotional valence trajectory (HOME/LIFT/TENSE/TURN) over the composition. Emotional states modulate gain of prefrontal→hippocampal connections and firing thresholds of hippocampal CA3 neurons via dopamine-modulated conductances.

### Neuron Model: Izhikevich (2003)

Each neuron follows the 2D ODE system:

$$ \frac{dv}{dt} = 0.04 v^2 + 5v + 140 - u + I $$
$$ \frac{du}{dt} = a(bv - u) $$

with after-spike reset: if $v \geq 30$ mV, then $v \leftarrow c$, $u \leftarrow u + d$.

The four dimensionless parameters $(a, b, c, d)$ determine the firing class:
- **Regular spiking** (RS): $(0.02, 0.2, -65, 8)$ — cortex, hippocampus (tonic firing)
- **Intrinsically bursting** (IB): $(0.02, 0.2, -55, 4)$ — thalamus (burst generation)
- **Fast spiking** (FS): $(0.1, 0.2, -65, 2)$ — inhibitory interneurons
- **Low-threshold spiking** (LTS): $(0.02, 0.25, -65, 0.05)$ — thalamic relay

### Learning: Spike-Timing-Dependent Plasticity (STDP)

Synaptic weights $w_{ij}$ are updated via the Bi–Poo pair-based STDP rule (1998):

$$ \Delta w_{ij} = \begin{cases} A_+ e^{-\Delta t / \tau_+} & \text{if } \Delta t > 0 \text{ (pre before post)} \\ -A_- e^{\Delta t / \tau_-} & \text{if } \Delta t < 0 \text{ (post before pre)} \end{cases} $$

where $\Delta t = t_{\text{post}} - t_{\text{pre}}$, $A_+ = 0.01$, $A_- = 0.0105$, $\tau_+ = 20$ ms, $\tau_- = 20$ ms. STDP is local, unsupervised, and Hebbian: frequently co-occurring spike sequences strengthen their connections → motif learning.

### Decoding Spike Trains to Musical Events

For each voice-population in each section-time window:

1. **Pitch decoding**: A tonotopic sheet of 12 pitch-class columns (C, C#, ..., B). The firing rate $r_i(t)$ of column $i$ over a decoding window $W$ (typically 50 ms, aligned to gamma cycles) is $r_i = \frac{N_{\text{spikes}}(i, W)}{W}$. The winning pitch is $p^* = \arg\max_i r_i$, with a softmax probability $P(p_i) = e^{\beta r_i} / \sum_j e^{\beta r_j}$. Temperature $\beta$ controls pitch entropy.

2. **Duration decoding**: Inter-spike interval (ISI) of the winning column between consecutive gamma-cycle rate peaks. $d^* = \text{quantize}(ISI_{\text{mean}})$ to the nearest duration class (whole, half, quarter, eighth, etc.).

3. **Velocity decoding**: Peak firing rate of the winning column within the decoding window maps to velocity via a linear mapping: $v = \text{clip}(r_{\text{peak}} / r_{\text{max}} \cdot 127, 0, 127)$.

4. **Onset detection**: An onset event is triggered when the winning column's firing rate exceeds a threshold $\theta_{\text{onset}}$ (typically $0.3 \cdot r_{\text{max}}$). No onset = rest.

### Composition Algorithm

1. **Training phase**: Present a corpus of MIDI sequences as spike trains via Poisson rate encoding. The hippocampal CA3 network learns motif sequences via STDP; the prefrontal network learns mode/scale transition statistics; the insula network learns tension/release profiles from harmonic analysis of the corpus.

2. **Composition phase**:
   a. **Form design**: The prefrontal form-template network generates a sequence of section tokens (e.g., intro, verse, chorus, bridge, outro) as 20-ms sustained firing patterns in a population of prefrontal neurons.
   b. **Section execution**: For each section $s$:
      - Set the insula target tension level for this section
      - Set thalamic theta-gamma PLV target (metric density)
      - Inject partial cue spike pattern into hippocampal CA3 → pattern completion → full motif spike train
      - Decode spike train to per-voice note events via population-rate decoding
      - Apply prefrontal scale/mode filter to constrain pitch output
   c. **Macro-form assembly**: Concatenate section outputs; insula tension trajectory ensures HOME→LIFT→TENSE→TURN arc.

3. **UnitMatrix filling**: Decoded note events are assembled into per-voice per-section $MusicUnit$ cells via `create_note_unit(pitch, duration_ticks)`.

### Mathematical Foundations

**Izhikevich neuron bifurcations**: The $v$–$u$ system is a planar dynamical system. For $(a, b, c, d) = (0.02, 0.2, -65, 8)$, the nullclines intersect at a stable fixed point; injected current $I$ pushes the system across a saddle-node bifurcation initiating the limit cycle (spike). The quadratic form $0.04v^2+5v$ ensures a well-defined threshold — unlike LIF models, the Izhikevich model has an exact thresholdless spike initiation zone.

**STDP convergence**: For a periodic pre-synaptic spike train at frequency $f_{\text{pre}}$ and uniformly distributed post-synaptic Poisson spikes at rate $f_{\text{post}}$, the expected weight change is $\mathbb{E}[\Delta w] = A_+ \tau_+ f_{\text{post}} - A_- \tau_- f_{\text{pre}}$. Setting $f_{\text{post}} < \frac{A_- \tau_-}{A_+ \tau_+} f_{\text{pre}}$ yields LTD; $>$ yields LTP. The fixed point defines the firing-rate homeostasis of the musical memory.

**Theta–gamma coupling**: The phase-locking value (PLV) between two oscillators:

$$ \text{PLV} = \left| \mathbb{E}\left[ e^{i(\phi_{\text{theta}} - \phi_{\text{gamma}})} \right] \right| $$

PLV = 1: perfect locking → rigid metric; PLV = 0: no locking → a-rhythmic. The number of gamma cycles per theta half-cycle = $f_{\text{gamma}} / (2 f_{\text{theta}})$ = metric subdivision.

**Population decoding accuracy**: For $N$ independent Poisson spiking neurons with rate $r$ in a decoding window $W$, the variance of the rate estimate is $\sigma^2 = r/(N W)$. The accuracy of pitch decoding (distinguishing two columns with rates $r_1$, $r_2$) is:

$$ d' = \frac{|r_1 - r_2|}{\sqrt{(r_1 + r_2)/(2 N W)}} $$

For typical values ($r = 40$ Hz for winning column, $r = 5$ Hz for losing, $N = 20$, $W = 50$ ms), $d' \approx 12$ — easily discriminable.

## Python Implementation Sketch

```python
import numpy as np
from typing import Dict, List, Tuple, Optional

# --- Izhikevich Neuron ---
class IzhikevichNeuron:
    """Two-dimensional Izhikevich spiking neuron model."""
    
    def __init__(self, a: float, b: float, c: float, d: float, 
                 v_init: float = -65.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.v = v_init  # membrane potential (mV)
        self.u = b * v_init  # recovery variable
        self.spikes: List[float] = []  # spike times (ms)
    
    def step(self, I: float, dt: float = 0.1, t: float = 0.0):
        """Euler integration with 0.1 ms timestep."""
        # Membrane potential update (quadratic)
        dv = (0.04 * self.v**2 + 5 * self.v + 140 - self.u + I) * dt
        self.v += dv
        
        # Recovery variable update (linear)
        self.u += self.a * (self.b * self.v - self.u) * dt
        
        # After-spike reset
        if self.v >= 30.0:
            self.spikes.append(t)
            self.v = self.c
            self.u += self.d
    
    def reset(self, v_init: float = -65.0):
        self.v = v_init
        self.u = self.b * v_init
        self.spikes.clear()


# --- STDP Synapse ---
class STDPSynapse:
    """Spike-timing-dependent plasticity synapse."""
    
    def __init__(self, w_init: float = 0.5, A_plus: float = 0.01, 
                 A_minus: float = 0.0105, tau_plus: float = 20.0,
                 tau_minus: float = 20.0, w_max: float = 1.0):
        self.w = w_init
        self.A_plus = A_plus
        self.A_minus = A_minus
        self.tau_plus = tau_plus
        self.tau_minus = tau_minus
        self.w_max = w_max
        self.last_pre: Optional[float] = None
        self.last_post: Optional[float] = None
    
    def pre_spike(self, t: float):
        """Pre-synaptic spike at time t."""
        if self.last_post is not None:
            dt = self.last_post - t  # post - pre (negative)
            self.w = min(self.w_max, max(0.0, 
                self.w + self.A_minus * np.exp(dt / self.tau_minus)))
        self.last_pre = t
    
    def post_spike(self, t: float):
        """Post-synaptic spike at time t."""
        if self.last_pre is not None:
            dt = t - self.last_pre  # post - pre (positive)
            self.w = min(self.w_max, max(0.0,
                self.w + self.A_plus * np.exp(-dt / self.tau_plus)))
        self.last_post = t
    
    def current(self, pre_spiked: bool) -> float:
        """Synaptic current contribution (weighted by pre-spike)."""
        return self.w if pre_spiked else 0.0


# --- Spike-Train Decoder ---
class PopulationRateDecoder:
    """Decode spike trains to pitch/duration/velocity."""
    
    def __init__(self, num_pitch_columns: int = 12, 
                 window_ms: float = 50.0, 
                 theta_onset: float = 12.0,  # Hz threshold
                 beta: float = 1.0):
        self.num_columns = num_pitch_columns
        self.window = window_ms
        self.theta_onset = theta_onset
        self.beta = beta
    
    def decode(self, spike_trains: List[List[float]], 
               t_start: float, t_end: float) -> Dict:
        """Decode a window of spike trains to one musical event."""
        window_spikes = [
            len([s for s in train if t_start <= s <= t_end])
            for train in spike_trains
        ]
        rates = [n / (self.window / 1000.0) for n in window_spikes]
        
        # Pitch: softmax over rates
        exp_rates = np.exp(self.beta * np.array(rates))
        probs = exp_rates / exp_rates.sum()
        pitch = int(np.random.choice(self.num_columns, p=probs))
        
        # Onset detection
        has_onset = rates[pitch] >= self.theta_onset
        
        # Duration: placeholder — decoded from ISI in practice
        duration = 480  # 1 quarter note at 120 BPM
        
        # Velocity: linear mapping from peak firing rate
        velocity = min(127, max(0, int(rates[pitch] / 100.0 * 127)))
        
        return {
            'pitch': pitch + 60,  # MIDI offset
            'onset': has_onset,
            'duration_ticks': duration,
            'velocity': velocity
        }


# --- Spiking Neural Network Composer ---
class SNNComposer:
    """Multi-region SNN composition engine."""
    
    def __init__(self, bpm: int = 120, ticks_per_beat: int = 480,
                 dt: float = 0.1):
        self.bpm = bpm
        self.ticks_per_beat = ticks_per_beat
        self.dt = dt
        self.decoder = PopulationRateDecoder()
        self._build_network()
    
    def _build_network(self):
        """Build the multi-region spiking network."""
        # Hippocampus: 100 RS neurons
        self.hippocampus = [
            IzhikevichNeuron(0.02, 0.2, -65, 8) for _ in range(100)
        ]
        # Thalamus: 20 IB neurons (theta) + 40 IB neurons (gamma)
        self.thalamus_theta = [
            IzhikevichNeuron(0.02, 0.2, -55, 4) for _ in range(20)
        ]
        self.thalamus_gamma = [
            IzhikevichNeuron(0.02, 0.2, -55, 4) for _ in range(40)
        ]
        # Prefrontal: 50 FS neurons
        self.prefrontal = [
            IzhikevichNeuron(0.1, 0.2, -65, 2) for _ in range(50)
        ]
        # Insula: 30 LTS neurons
        self.insula = [
            IzhikevichNeuron(0.02, 0.25, -65, 0.05) for _ in range(30)
        ]
    
    def compose_section(self, section_token: str, 
                        num_bars: int, 
                        beats_per_bar: int = 4,
                        theta_plv_target: float = 0.8) -> Dict[str, List]:
        """Generate a section's note events from SNN dynamics."""
        # Set prefrontal section token as tonic firing pattern
        token_pattern = hash(section_token) % 256
        for i, neuron in enumerate(self.prefrontal):
            neuron.reset(-65 + (i % 10) * 2)
        
        # Simulate for the section duration
        section_ms = num_bars * beats_per_bar * 60000 / self.bpm
        total_steps = int(section_ms / self.dt)
        
        # Run simulation
        pitch_trains = {v: [[] for _ in range(12)] for v in range(4)}
        
        for step in range(total_steps):
            t = step * self.dt  # current time in ms
            
            # Thalamic oscillators: theta drive
            for i, n in enumerate(self.thalamus_theta):
                freq_theta = 6.0  # Hz
                I_theta = 3.0 * (1 + np.sin(2 * np.pi * freq_theta * t / 1000))
                n.step(I_theta, self.dt, t)
            
            # Thalamic oscillators: gamma drive
            for i, n in enumerate(self.thalamus_gamma):
                freq_gamma = 40.0  # Hz
                I_gamma = 3.0 * (1 + np.sin(2 * np.pi * freq_gamma * t / 1000))
                n.step(I_gamma, self.dt, t)
            
            # Hippocampus: receive thalamic input + recurrent connections
            theta_active = sum(1 for n in self.thalamus_theta if n.v >= 30)
            gamma_active = sum(1 for n in self.thalamus_gamma if n.v >= 30)
            
            for i, n in enumerate(self.hippocampus):
                I = 0.0
                # Theta-gating: gamma spikes only pass during theta active
                if theta_active > 5:
                    I += gamma_active * 0.02
                I += np.random.randn() * 0.5  # noise current
                n.step(I, self.dt, t)
            
            # Collect spikes per pitch column every gamma cycle
            if step % int(1000 / (40 * self.dt)) == 0:  # every gamma period
                for v in range(min(4, 4)):
                    col = (step // 100) % 12
                    spike_count = sum(
                        n.v >= 30 for n in self.hippocampus[v*25:(v+1)*25]
                    )
                    pitch_trains[v][col].append(t if spike_count > 3 else None)
        
        # Decode spike trains to per-voice note events
        voices = {}
        for v in range(4):
            events = []
            for pos in range(num_bars * beats_per_bar * 4):  # 16th grid
                t_win_start = pos * 60000 / (self.bpm * 4)
                t_win_end = t_win_start + 60000 / (self.bpm * 4)
                
                # Build spike train for this window
                win_trains = [
                    [s for s in pitch_trains[v][c] 
                     if s is not None and t_win_start <= s <= t_win_end]
                    for c in range(12)
                ]
                
                result = self.decoder.decode(
                    win_trains, t_win_start, t_win_end
                )
                if result['onset']:
                    events.append((
                        result['pitch'],
                        int(pos * self.ticks_per_beat / 4),  # start tick
                        result['duration_ticks'],
                        result['velocity']
                    ))
            voices[f"voice_{v}"] = events
        
        return voices
    
    def compose(self, section_plan: List[str], 
                bars_per_section: List[int]) -> Dict[str, List]:
        """Compose a full piece from a section plan."""
        full_piece = {}
        for section, bars in zip(section_plan, bars_per_section):
            section_events = self.compose_section(section, bars)
            for voice_name, events in section_events.items():
                if voice_name not in full_piece:
                    full_piece[voice_name] = []
                # Shift by section offset
                offset = sum(bars_per_section[:len(full_piece) // 4])
                offset_ticks = offset * 4 * self.ticks_per_beat
                shifted = [(p, s + offset_ticks, d, v) for p, s, d, v in events]
                full_piece[voice_name].extend(shifted)
        return full_piece


# Example usage
if __name__ == "__main__":
    composer = SNNComposer(bpm=120)
    section_plan = ["intro", "verse", "chorus", "verse", "chorus", "outro"]
    bars_per_section = [2, 4, 4, 4, 4, 2]
    piece = composer.compose(section_plan, bars_per_section)
    for voice, events in piece.items():
        print(f"{voice}: {len(events)} events")
```

## UnitMatrix Integration

Each UnitMatrix **voice** corresponds to one spiking neural population (25 Izhikevich RS neurons) with its own tonotopic pitch range, STDP-weight matrix, and population decoder. Voices are distinct cortical minicolumns receiving shared thalamic clock input but maintaining separate recurrent connectivity.

Each **section** corresponds to a theta oscillation cycle period, with a distinct prefrontal section-token firing pattern that gates:
- **HOME/LIFT/TENSE/TURN**: via insula→hippocampus gain modulation
- **Metric binding**: via thalamic theta–gamma PLV target
- **Voicing**: via which populations are active
- **Register**: via active tonotopic range (center frequency + spread)

## Candidate Code Path

```
generators/snn_composer.py
```

Implementation as `generators/snn_composer.py` containing `IzhikevichNeuron`, `STDPSynapse`, `PopulationRateDecoder`, and `SNNComposer` classes. The `SNNComposer.compose(section_plan, bars_per_section)` method returns a dictionary of per-voice note event lists that can be filled into a `UnitMatrix`.

## References

- Liang, Q. & Zeng, Y. (2021). "Stylistic Composition of Melodies Based on a Brain-Inspired Spiking Neural Network." *Frontiers in Systems Neuroscience* 15, 639484.
- Liang, Q., Zeng, Y. & Tang, M. (2025). "Mode-conditioned music learning and composition: a spiking neural network inspired by neuroscience and psychology." *arXiv:2411.14773*.
- Zeng, Y. et al. (2023). "BrainCog: A spiking neural network based, brain-inspired cognitive intelligence engine." *Patterns* 4, 100789.
- Izhikevich, E. M. (2003). "Simple model of spiking neurons." *IEEE Transactions on Neural Networks* 14(6), 1569–1572.
- Izhikevich, E. M. (2007). *Dynamical Systems in Neuroscience*. MIT Press.
- Bi, G. & Poo, M.-M. (1998). "Synaptic modifications in cultured hippocampal neurons: dependence on spike timing, synaptic strength, and postsynaptic cell type." *Journal of Neuroscience* 18(24), 10464–10472.
- Maass, W. (1997). "Networks of spiking neurons: The third generation of neural network models." *Neural Networks* 10(9), 1659–1671.
- Krumhansl, C. L. & Schmuckler, M. A. (1984). "Key-finding in music: An algorithm based on pattern matching to the pitch-class profile." (Krumhansl-Schmuckler key-finding algorithm.)