# Strange Attractor Trajectory Mapping (SATM) (Method 043)

## **Paradigm**: Nature-Led (Chaos Theory / Deterministic Chaos)

## **Description**
Strange Attractor Trajectory Mapping (SATM) uses deterministic chaotic dynamical systems—specifically strange attractors like the Lorenz, Rössler, or Aizawa attractors—to generate complex, non-repeating musical patterns. Unlike random stochastic methods, strange attractors produce bounded yet aperiodic trajectories in phase space that never exactly repeat but remain within defined bounds. This creates organic, evolving musical material with long-term coherence but no short-term predictability.

The method maps the continuous 3D trajectory coordinates $(x(t), y(t), z(t))$ of a strange attractor to musical parameters: pitch height, rhythmic density, and harmonic tension. The deterministic nature ensures reproducibility while the chaotic sensitivity to initial conditions allows infinite variation.

## **Mathematical Foundation**

### Lorenz Attractor
The classic Lorenz system is defined by three coupled ordinary differential equations:

$$\frac{dx}{dt} = \sigma(y - x)$$
$$\frac{dy}{dt} = x(\rho - z) - y$$
$$\frac{dz}{dt} = xy - \beta z$$

Where:
- $\sigma = 10$ (Prandtl number)
- $\rho = 28$ (Rayleigh number)
- $\beta = 8/3$ (geometric factor)

These parameters produce the iconic "butterfly" strange attractor with two lobes and chaotic switching between them.

### Rössler Attractor
Simpler system with one manifold:

$$\frac{dx}{dt} = -y - z$$
$$\frac{dy}{dt} = x + ay$$
$$\frac{dz}{dt} = b + z(x - c)$$

Where $a = 0.2$, $b = 0.2$, $c = 5.7$ produce a single-loop attractor with periodic folding.

### Numerical Integration
The system is solved using 4th-order Runge-Kutta (RK4) integration with step size $h$:

$$k_1 = h \cdot f(t_n, \mathbf{y}_n)$$
$$k_2 = h \cdot f(t_n + \frac{h}{2}, \mathbf{y}_n + \frac{k_1}{2})$$
$$k_3 = h \cdot f(t_n + \frac{h}{2}, \mathbf{y}_n + \frac{k_2}{2})$$
$$k_4 = h \cdot f(t_n + h, \mathbf{y}_n + k_3)$$
$$\mathbf{y}_{n+1} = \mathbf{y}_n + \frac{1}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

## **Musical Elements Framework**

### **PITCH**
The $z$-coordinate (vertical height in Lorenz space) maps directly to MIDI pitch values. The attractor's bounded range $[z_{min}, z_{max}]$ is linearly or logarithmically scaled to a target pitch range (e.g., MIDI 36-84, covering C2-C6). 

- **Quantization**: Continuous $z$ values are quantized to the nearest pitch in the active scale (major, minor, pentatonic, or custom).
- **Voice allocation**: Different voices use different coordinate mappings (Voice 1: $z \to$ pitch, Voice 2: $x \to$ pitch, Voice 3: $y \to$ pitch) to create contrapuntal independence from the same attractor.
- **Register stability**: The attractor's natural clustering around certain regions creates registral focus points without explicit planning.

### **RHYTHM**
Rhythmic density and event timing are derived from the trajectory's velocity and curvature in phase space.

- **Velocity-based triggering**: The instantaneous speed $v(t) = \sqrt{\dot{x}^2 + \dot{y}^2 + \dot{z}^2}$ controls inter-onset intervals. Fast trajectory segments trigger dense rhythmic events; slow segments produce sparse, sustained notes.
- **Curvature-based accents**: High curvature $\kappa(t)$ (rapid directional changes) triggers accented events or metric shifts.
- **Lobe transitions**: In the Lorenz attractor, switching between the two lobes (detected by sign change in $x$) marks structural phrase boundaries or section transitions.

### **HARMONY**
Vertical harmonic combinations emerge from sampling multiple attractor coordinates simultaneously across voices.

- **Simultaneous sampling**: At each time step $t$, all active voices sample their respective coordinates $(x_v(t), y_v(t), z_v(t))$ and map to pitches. The resulting vertical stack forms the instantaneous chord.
- **Consonance control**: The raw attractor-derived pitches are filtered through a consonance constraint (e.g., only allow intervals within the active scale, or apply voice-leading rules to smooth jumps).
- **Tension mapping**: The attractor's distance from its fixed points (unstable equilibria) correlates with harmonic tension. Trajectories near fixed points produce stable, consonant harmonies; trajectories far from fixed points produce dissonant, tense clusters.

### **STRUCTURE**
The macro-form is governed by the attractor's global topology and recurrence properties.

- **Poincaré sections**: Define a hyperplane in phase space (e.g., $x = 0$). Each time the trajectory crosses this plane marks a structural boundary (phrase end, section change).
- **Recurrence quantification**: Calculate the recurrence time $T_r$ (time between successive returns to a small neighborhood). Short recurrence times = repetitive sections; long recurrence times = developmental, non-repeating sections.
- **Attractor switching**: For multi-section forms, switch between different attractors (Lorenz → Rössler → Aizawa) or different parameter sets to create contrasting sections while maintaining chaotic coherence.

### **TEXTURE**
Texture density and voice distribution are controlled by the attractor's local dimensionality and Lyapunov stability.

- **Local dimensionality**: In regions where the attractor is quasi-1D (trajectory nearly periodic), use sparse monophonic texture. In regions where it's quasi-3D (fully chaotic), activate all voices for dense polyphony.
- **Lyapunov exponent**: The largest Lyapunov exponent $\lambda_1$ measures chaos strength. High $\lambda_1$ (strong chaos) = high textural complexity and voice independence. Low $\lambda_1$ (weak chaos, near-periodic) = homophonic or unison texture.
- **Spatial distribution**: Map the 3D attractor coordinates to spatial positions (pan, reverb send, frequency band) to create evolving stereo or surround sound fields.

## **UnitMatrix Integration (Voices & Sections)**

### **Rows (Voices)**
Each voice $v$ is assigned a coordinate mapping function $M_v: \mathbb{R}^3 \to \text{MIDI}$ that transforms the attractor trajectory into a pitch stream.

- **Voice 1 (Lead)**: $M_1(x,y,z) = \text{quantize}(z \cdot k_1 + c_1, \text{Scale})$
- **Voice 2 (Counter-melody)**: $M_2(x,y,z) = \text{quantize}(x \cdot k_2 + c_2, \text{Scale})$
- **Voice 3 (Harmony pad)**: $M_3(x,y,z) = \text{quantize}(y \cdot k_3 + c_3, \text{Scale})$
- **Voice 4 (Bass)**: $M_4(x,y,z) = \text{quantize}(z \cdot k_4 + c_4, \text{Scale}) - 24$ (octave down)

Where $k_v$ are scaling factors and $c_v$ are offset constants to separate voice ranges.

### **Columns (Sections)**
Sections are defined by attractor parameter sets or topological regions.

- **Section A**: Lorenz attractor with $\sigma=10, \rho=28, \beta=8/3$ (classic butterfly)
- **Section B**: Rössler attractor with $a=0.2, b=0.2, c=5.7$ (single loop)
- **Section C**: Lorenz with $\rho=99$ (intermittent chaos, periodic windows)
- **Section D**: Aizawa attractor (toroidal, different topology)

Transitions between sections use parameter interpolation over $N_{crossfade}$ steps to avoid discontinuities.

### **Cells**
Each cell $U_{v,s}$ contains:

- **{PITCH}**: Sequence of MIDI pitches generated by integrating the attractor for $N_{steps}$ time steps within section $s$, applying voice $v$'s mapping function $M_v$, and quantizing to the active scale.
  
- **{RHYTHM}**: Event trigger pattern derived from the trajectory velocity $v(t)$. Threshold $\theta_v$ determines active vs. resting states:
  $$\text{trigger}[t] = \begin{cases} 1 & \text{if } v(t) > \theta_v \\ 0 & \text{otherwise} \end{cases}$$
  
- **{TEXTURE}**: Density coefficient $\delta_{v,s}$ based on local Lyapunov exponent $\lambda_1(t)$ averaged over section $s$:
  $$\delta_{v,s} = \frac{1}{T_s} \int_{t \in s} \max(0, \lambda_1(t)) \, dt$$
  High $\delta$ = full velocity, rich timbre. Low $\delta$ = soft velocity, sparse timbre.

### **Mapping Flow**

1. **Initialize attractor**: Choose strange attractor type (Lorenz, Rössler, etc.) and set parameters $(\sigma, \rho, \beta)$ or $(a, b, c)$.

2. **Set initial conditions**: Choose starting point $(x_0, y_0, z_0)$ near (but not exactly at) an unstable fixed point to ensure chaotic trajectory.

3. **Integrate trajectory**: Use RK4 integration with step size $h = 0.01$ to generate trajectory $\{(x(t), y(t), z(t))\}_{t=0}^{T}$ for total duration $T$.

4. **Segment into sections**: Divide the trajectory into $S$ sections based on Poincaré crossings or manual time boundaries.

5. **Map to voices**: For each section $s$ and voice $v$:
   - Extract the trajectory segment for section $s$.
   - Apply voice $v$'s mapping function $M_v$ to convert coordinates to MIDI pitches.
   - Quantize pitches to the active scale.
   - Calculate velocity from trajectory speed $v(t)$.
   - Calculate texture density from local Lyapunov exponent.

6. **Write to UnitMatrix**: Populate cells $U_{v,s}$ with the generated pitch sequences, rhythm triggers, and texture coefficients.

7. **Validate and export**: Run the UnitMatrix validation gate to ensure zero drift, then export to MIDI.

## **Implementation Requirements (Python/NumPy)**

```python
import numpy as np
from scipy.integrate import solve_ivp
from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit

def lorenz_system(t, state, sigma=10.0, rho=28.0, beta=8/3):
    """Lorenz attractor ODE system."""
    x, y, z = state
    return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

def generate_strange_attractor_trajectory(duration, sr, initial_conditions, params):
    """
    Generate 3D trajectory from Lorenz attractor.
    
    Args:
        duration: Total time in seconds
        sr: Sample rate for integration (not audio rate)
        initial_conditions: (x0, y0, z0) starting point
        params: (sigma, rho, beta) Lorenz parameters
    
    Returns:
        t: Time array
        trajectory: (N, 3) array of [x, y, z] coordinates
    """
    t_span = (0, duration)
    t_eval = np.linspace(0, duration, int(duration * sr))
    
    sol = solve_ivp(
        lorenz_system,
        t_span,
        initial_conditions,
        args=params,
        t_eval=t_eval,
        method='RK45',
        rtol=1e-8,
        atol=1e-10
    )
    
    return sol.t, sol.y.T  # trajectory shape: (N, 3)

def trajectory_to_pitch(trajectory_coord, pitch_min=36, pitch_max=84, scale='major'):
    """
    Map continuous coordinate to quantized MIDI pitch.
    
    Args:
        trajectory_coord: 1D array of continuous values (e.g., z-coordinates)
        pitch_min: Minimum MIDI pitch
        pitch_max: Maximum MIDI pitch
        scale: 'major', 'minor', 'pentatonic', or 'chromatic'
    
    Returns:
        pitches: 1D array of quantized MIDI pitches
    """
    # Normalize to [0, 1]
    coord_min, coord_max = trajectory_coord.min(), trajectory_coord.max()
    normalized = (trajectory_coord - coord_min) / (coord_max - coord_min)
    
    # Scale to pitch range
    raw_pitches = pitch_min + normalized * (pitch_max - pitch_min)
    
    # Quantize to scale
    scale_intervals = {
        'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic': [0, 2, 4, 7, 9]
    }
    
    intervals = scale_intervals.get(scale, scale_intervals['major'])
    
    pitches = []
    for p in raw_pitches:
        # Find nearest scale degree
        octave = int(p // 12)
        pitch_class = int(p) % 12
        
        # Find closest interval
        distances = [abs(pitch_class - i) for i in intervals]
        closest_idx = np.argmin(distances)
        quantized_pc = intervals[closest_idx]
        
        quantized_pitch = octave * 12 + quantized_pc
        pitches.append(quantized_pitch)
    
    return np.array(pitches)

def trajectory_velocity_to_rhythm(trajectory, threshold=0.5):
    """
    Convert trajectory speed to rhythmic trigger pattern.
    
    Args:
        trajectory: (N, 3) array of [x, y, z] coordinates
        threshold: Speed threshold for triggering events
    
    Returns:
        triggers: Binary array (1 = trigger, 0 = rest)
    """
    # Calculate instantaneous velocity
    dx = np.diff(trajectory[:, 0])
    dy = np.diff(trajectory[:, 1])
    dz = np.diff(trajectory[:, 2])
    
    speed = np.sqrt(dx**2 + dy**2 + dz**2)
    
    # Normalize speed to [0, 1]
    speed_norm = (speed - speed.min()) / (speed.max() - speed.min())
    
    # Threshold to binary triggers
    triggers = (speed_norm > threshold).astype(int)
    
    # Prepend 1 for first event
    triggers = np.concatenate([[1], triggers])
    
    return triggers

def compose_with_strange_attractor(num_voices, num_sections, section_duration, bpm=120):
    """
    Compose a piece using Strange Attractor Trajectory Mapping.
    
    Args:
        num_voices: Number of voices (rows in UnitMatrix)
        num_sections: Number of sections (columns in UnitMatrix)
        section_duration: Duration of each section in bars
        bpm: Tempo
    
    Returns:
        UnitMatrix: Composed matrix ready for MIDI export
    """
    composer = UnitMatrixComposer(bpm=bpm, ticks_per_beat=480, beats_per_bar=4)
    composer.create_matrix(num_voices=num_voices, num_sections=num_sections)
    
    # Add voices
    voice_names = ["Lead", "Counter", "Pad", "Bass"][:num_voices]
    instruments = [
        MidiInstrument.FLUTE,
        MidiInstrument.OBOE,
        MidiInstrument.STRING_ENSEMBLE_1,
        MidiInstrument.ACOUSTIC_BASS
    ][:num_voices]
    
    for i, (name, inst) in enumerate(zip(voice_names, instruments)):
        composer.add_voice(name, program=inst, channel=i)
    
    # Add sections
    section_names = [f"S{i+1}" for i in range(num_sections)]
    for name in section_names:
        composer.add_section(name, bars=section_duration)
    
    # Generate attractor trajectory
    total_duration = num_sections * section_duration * 4  # 4 beats per bar
    trajectory_sr = 100  # Integration sample rate (not audio rate)
    initial_conditions = (1.0, 1.0, 1.0)  # Near unstable fixed point
    params = (10.0, 28.0, 8/3)  # Lorenz parameters
    
    t, trajectory = generate_strange_attractor_trajectory(
        total_duration, trajectory_sr, initial_conditions, params
    )
    
    # Map trajectory to voices and sections
    ticks_per_section = section_duration * 4 * 480  # beats * ticks_per_beat
    
    for section_idx, section_name in enumerate(section_names):
        # Extract trajectory segment for this section
        start_idx = section_idx * int(total_duration * trajectory_sr / num_sections)
        end_idx = (section_idx + 1) * int(total_duration * trajectory_sr / num_sections)
        section_trajectory = trajectory[start_idx:end_idx]
        
        # Map each voice
        for voice_idx, voice_name in enumerate(voice_names):
            # Choose coordinate mapping for this voice
            coord_idx = voice_idx % 3  # Cycle through x, y, z
            
            # Extract coordinate and map to pitch
            coord = section_trajectory[:, coord_idx]
            
            # Set pitch range per voice
            if voice_name == "Bass":
                pitch_min, pitch_max = 36, 48  # C2-C3
            elif voice_name == "Lead":
                pitch_min, pitch_max = 72, 84  # C5-C6
            else:
                pitch_min, pitch_max = 60, 72  # C4-C5
            
            pitches = trajectory_to_pitch(coord, pitch_min, pitch_max, scale='major')
            
            # Generate rhythm from velocity
            triggers = trajectory_velocity_to_rhythm(section_trajectory, threshold=0.3)
            
            # Create note events for triggered pitches
            events = []
            for i, (pitch, trigger) in enumerate(zip(pitches, triggers)):
                if trigger and i < len(pitches):
                    # Calculate tick position
                    tick_pos = int(i * ticks_per_section / len(pitches))
                    
                    # Create note event (quarter note duration)
                    event = MusicEvent(
                        pitch=int(pitch),
                        velocity=90,
                        start_tick=tick_pos,
                        duration_ticks=480
                    )
                    events.append(event)
            
            # Create MusicUnit with events
            if events:
                unit = MusicUnit(events=events)
                composer.set_unit(voice_name, section_name, unit)
    
    # Validate before export
    is_valid, msg = composer.validate()
    if not is_valid:
        raise ValueError(f"UnitMatrix validation failed: {msg}")
    
    return composer
```

## **Pitfalls and Considerations**

1. **Initial condition sensitivity**: Strange attractors are highly sensitive to initial conditions. Small changes in $(x_0, y_0, z_0)$ produce completely different trajectories. Document initial conditions for reproducibility.

2. **Transient removal**: The first ~1000 integration steps may show transient behavior before settling onto the attractor. Discard this warm-up period before mapping to music.

3. **Coordinate scaling**: Raw attractor coordinates can have very different ranges (e.g., Lorenz $x \in [-20, 20]$, $z \in [0, 50]$). Normalize each coordinate independently before pitch mapping.

4. **Quantization artifacts**: Aggressive quantization to diatonic scales can destroy the attractor's fine structure. Use chromatic or extended scales to preserve chaotic detail, or apply gentle quantization with voice-leading smoothing.

5. **Rhythmic coherence**: Pure velocity-based rhythm can produce overly dense or sparse sections. Apply rhythmic constraints (e.g., minimum inter-onset interval, metric grid snapping) to maintain musicality.

6. **Lyapunov exponent calculation**: Computing the largest Lyapunov exponent requires specialized algorithms (Wolf's method, Kantz's method). For real-time use, approximate with local trajectory divergence over short windows.

7. **Attractor switching**: When transitioning between attractors or parameter sets, interpolate parameters smoothly over 100-500 steps to avoid discontinuous jumps in the musical output.

## **Verification and Testing**

1. **Visualize trajectory**: Plot the 3D trajectory $(x, y, z)$ to confirm it forms the expected attractor shape (butterfly for Lorenz, ribbon for Rössler).

2. **Check boundedness**: Verify that all trajectory coordinates remain within expected bounds (Lorenz: $x, y \in [-25, 25]$, $z \in [0, 50]$).

3. **Test reproducibility**: Run the composition twice with identical initial conditions and parameters. Output should be bit-identical.

4. **Validate UnitMatrix**: Run `composer.validate()` to ensure zero track drift before MIDI export.

5. **Listen for chaos**: The output should sound complex and non-repeating but not random. There should be long-term coherence (return to similar regions) but no short-term predictability.

## **References**

- Lorenz, E. N. (1963). "Deterministic Nonperiodic Flow." Journal of the Atmospheric Sciences, 20(2), 130-141.
- Rössler, O. E. (1976). "An Equation for Continuous Chaos." Physics Letters A, 57(5), 397-398.
- Strogatz, S. H. (2015). "Nonlinear Dynamics and Chaos: With Applications to Physics, Biology, Chemistry, and Engineering." Westview Press.
- Xenakis, I. (1992). "Formalized Music: Thought and Mathematics in Composition." Pendragon Press. (For comparison with stochastic methods)

## **Example Usage**

```python
# Compose a 4-voice, 8-section piece using Lorenz attractor
composer = compose_with_strange_attractor(
    num_voices=4,
    num_sections=8,
    section_duration=2,  # 2 bars per section
    bpm=120
)

# Export to MIDI
composer.to_midi("/opt/data/projects/Research/outputs/satm_piece/output.mid")

# Visualize
from ai.utils.visualizer import write_grid_visualization
write_grid_visualization(composer.matrix, "/opt/data/projects/Research/outputs/satm_piece/visualization.png")
```

## **Extensions and Variants**

1. **Multi-attractor hybridization**: Use different attractors for different voices (Lead: Lorenz, Bass: Rössler) to create independent chaotic streams.

2. **Coupled attractors**: Connect multiple attractors via coupling terms to create synchronized or anti-phase chaotic interactions.

3. **Controlled chaos**: Add small periodic forcing terms to the ODEs to create quasi-periodic behavior with chaotic embellishments.

4. **Fractal attractors**: Use fractional-order chaotic systems (e.g., fractional Lorenz) to generate multi-scale self-similar patterns.

5. **Machine learning integration**: Train a neural network to predict attractor parameters from desired musical characteristics (mood, energy, complexity).
