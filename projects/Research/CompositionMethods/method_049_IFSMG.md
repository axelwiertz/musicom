# Method 049: Iterated Function Systems Musical Generation (IFSMG)

## Overview
**Paradigm**: Rules-Based (Deterministic Fractal)  
**Method ID**: 049  
**Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture  
**Tonal Gravity**: Variable (Attractor-guided)  
**Metric Binding**: Continuous / Fluid  
**Memory Depth**: Macro / Fractal  
**Time Complexity**: $\mathcal{O}(M \cdot N)$ where $M$ = iterations, $N$ = transformations  

## Source
Adapted from Barnsley's Iterated Function Systems (1988) and the Chaos Game algorithm for fractal generation. Originally developed for image compression and fractal art (Barnsley ferns, Sierpinski triangles). Applied to music composition by Jean-François Allouche and extended by Gary Lee Nelson for algorithmic melody generation. This formulation maps affine transformations to pitch-time-velocity space for self-similar musical structures.

## Description
Iterated Function Systems Musical Generation (IFSMG) uses a set of contractive affine transformations in 3D pitch-time-velocity space to generate self-similar musical patterns. Each transformation $w_i$ is defined as:

$$w_i \begin{pmatrix} p \\ t \\ v \end{pmatrix} = \begin{pmatrix} a_{11}^{(i)} & a_{12}^{(i)} & a_{13}^{(i)} \\ a_{21}^{(i)} & a_{22}^{(i)} & a_{23}^{(i)} \\ a_{31}^{(i)} & a_{32}^{(i)} & a_{33}^{(i)} \end{pmatrix} \begin{pmatrix} p \\ t \\ v \end{pmatrix} + \begin{pmatrix} e_1^{(i)} \\ e_2^{(i)} \\ e_3^{(i)} \end{pmatrix}$$

where $(p, t, v)$ are pitch (MIDI), time (ticks), and velocity. Starting from a seed point, the Chaos Game algorithm randomly selects transformations according to probabilities $p_i$ (with $\sum p_i = 1$) and iterates:

$$\mathbf{x}_{n+1} = w_{i_n}(\mathbf{x}_n)$$

The resulting attractor is a fractal point cloud in pitch-time-velocity space. Each point becomes a musical event. The self-similar structure creates motifs that echo at multiple time scales.

## Musical Elements Framework

- **PITCH**: Pitch coordinate $p$ of each IFS point, quantized to active scale. Transformations with $|a_{11}| < 1$ compress pitch range (motivic diminution); $|a_{11}| > 1$ expands it (augmentation). Cross-coupling terms $a_{12}, a_{13}$ create pitch-time and pitch-velocity correlations.

- **RHYTHM**: Time coordinate $t$ determines onset positions. Transformations with $|a_{22}| < 1$ create rhythmic acceleration (notes closer together); $|a_{22}| > 1$ creates deceleration. The fractal structure produces nested rhythmic patterns: short motifs within longer phrases, mirroring the self-similarity.

- **HARMONY**: Vertical slices at fixed time windows form chord clusters. The IFS attractor's geometry determines harmonic density. Transformations with strong pitch-time coupling ($a_{12} \neq 0$) create voice-leading paths that naturally avoid parallel fifths/octaves through fractal dispersion.

- **STRUCTURE**: Macro-form emerges from the IFS attractor's global shape. Different transformation sets create different formal archetypes: linear IFS = through-composed; cyclic IFS = rondo-like; tree-branching IFS = theme-and-variations. Section boundaries align with attractor basin transitions.

- **TEXTURE**: Point density in pitch-time space determines textural thickness. High-probability transformations create dense regions (melodic focus); low-probability transformations create sparse regions (textural relief). Velocity dimension adds dynamic shaping: high-velocity points = accents, low-velocity = background.

## UnitMatrix Integration (Voices & Sections)

- **Rows (Voices)**: Partition the IFS point cloud by pitch range or transformation history. Lead voice = points from high-probability transformations; Bass = points with lowest pitch in each time window; Pad = mid-range sustained points.

- **Columns (Sections)**: Each section uses a distinct IFS parameter set (transformation matrices $w_i^{(s)}$ and probabilities $p_i^{(s)}$). Section transitions = smooth interpolation between IFS parameter sets.

- **Cells** $U_{v, s}$:
  - `{PITCH}`: MIDI pitches from IFS points assigned to voice $v$ in section $s$, quantized to scale.
  - `{RHYTHM}`: Onset ticks from time coordinates $t$ of IFS points, sorted and deduplicated.
  - `{TEXTURE}`: Velocity values from IFS $v$-coordinate, scaled to MIDI range. Density = points per unit time.

- **Mapping Flow**:
  1. Define $N$ affine transformations $w_1, \ldots, w_N$ with probabilities $p_1, \ldots, p_N$.
  2. Choose seed point $\mathbf{x}_0 = (p_0, t_0, v_0)$.
  3. Run Chaos Game for $M$ iterations: $\mathbf{x}_{n+1} = w_{i_n}(\mathbf{x}_n)$ where $i_n \sim \text{Categorical}(p_1, \ldots, p_N)$.
  4. Discard first 1000 points (transient).
  5. Segment remaining points by time coordinate into sections.
  6. Partition points by pitch range into voices.
  7. Quantize pitch to scale; map time to ticks; scale velocity to MIDI range.
  8. Write $(pitch, tick, velocity)$ into $U_{v, s}$.

## Python Implementation

```python
import numpy as np

def ifs_music_generation(transformations, probabilities, seed, num_iterations=100000, 
                          discard=1000, scale_pitches=None):
    """
    Generate musical events using Iterated Function Systems.
    
    Args:
        transformations: list of (3x3 matrix, 3x1 translation) tuples
        probabilities: list of selection probabilities (must sum to 1)
        seed: initial point (pitch, time, velocity)
        num_iterations: total Chaos Game iterations
        discard: number of initial transient points to discard
        scale_pitches: MIDI pitches of active scale for quantization
    
    Returns:
        events: list of (pitch, time, velocity) tuples
    """
    N = len(transformations)
    probs = np.array(probabilities)
    assert abs(probs.sum() - 1.0) < 1e-6, "Probabilities must sum to 1"
    
    # Precompute cumulative probabilities for fast selection
    cumprobs = np.cumsum(probs)
    
    point = np.array(seed, dtype=float)
    events = []
    
    for i in range(num_iterations):
        # Select transformation by probability
        r = np.random.random()
        idx = np.searchsorted(cumprobs, r)
        idx = min(idx, N - 1)
        
        A, b = transformations[idx]
        point = A @ point + b
        
        if i >= discard:
            events.append(point.copy())
    
    events = np.array(events)
    
    # Quantize pitch to scale if provided
    if scale_pitches is not None:
        scale = np.array(sorted(scale_pitches))
        for i in range(len(events)):
            nearest = scale[np.argmin(np.abs(scale - events[i, 0]))]
            events[i, 0] = nearest
    
    # Clamp pitch to MIDI range
    events[:, 0] = np.clip(events[:, 0], 0, 127)
    
    # Normalize velocity to MIDI range [40, 120]
    v_min, v_max = events[:, 2].min(), events[:, 2].max()
    if v_max > v_min:
        events[:, 2] = 40 + 80 * (events[:, 2] - v_min) / (v_max - v_min)
    else:
        events[:, 2] = 80
    
    return events


def create_barnsley_musical_ifs(root_pitch=60, tempo_ticks=480):
    """
    Create a musical IFS inspired by Barnsley's fern, mapped to pitch-time-velocity.
    Returns transformations that produce branching, self-similar melodic structures.
    """
    # Transformation 1: Stem (high probability, narrow pitch range, ascending)
    A1 = np.array([
        [0.15, 0.0,  0.0],   # pitch: slight compression
        [0.0,  0.85, 0.0],   # time: moderate compression (faster)
        [0.0,  0.0,  0.2]    # velocity: strong compression
    ])
    b1 = np.array([root_pitch * 0.85, tempo_ticks * 0.15, 10])
    
    # Transformation 2: Right leaf (medium probability, ascending pitch)
    A2 = np.array([
        [0.5,  0.1,  0.0],
        [0.1,  0.5,  0.0],
        [0.0,  0.0,  0.3]
    ])
    b2 = np.array([root_pitch * 0.2 + 5, tempo_ticks * 0.3, 20])
    
    # Transformation 3: Left leaf (medium probability, descending pitch)
    A3 = np.array([
        [0.5,  -0.1, 0.0],
        [-0.1, 0.5,  0.0],
        [0.0,  0.0,  0.3]
    ])
    b3 = np.array([root_pitch * 0.2 - 5, tempo_ticks * 0.3, 20])
    
    # Transformation 4: Base (low probability, wide pitch jump)
    A4 = np.array([
        [0.2,  0.0,  0.0],
        [0.0,  0.3,  0.0],
        [0.0,  0.0,  0.1]
    ])
    b4 = np.array([root_pitch * 0.5, tempo_ticks * 0.5, 50])
    
    transformations = [
        (A1, b1), (A2, b2), (A3, b3), (A4, b4)
    ]
    probabilities = [0.55, 0.20, 0.20, 0.05]
    
    return transformations, probabilities


# Example usage:
if __name__ == "__main__":
    root = 60  # Middle C
    ticks_per_beat = 480
    
    transforms, probs = create_barnsley_musical_ifs(root, ticks_per_beat)
    
    # C major scale
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
    
    events = ifs_music_generation(
        transforms, probs,
        seed=(root, 0, 50),
        num_iterations=50000,
        discard=1000,
        scale_pitches=scale
    )
    
    print(f"Generated {len(events)} events")
    print(f"Pitch range: {events[:, 0].min():.0f} - {events[:, 0].max():.0f}")
    print(f"Time range: {events[:, 1].min():.0f} - {events[:, 1].max():.0f}")
    print(f"Velocity range: {events[:, 2].min():.0f} - {events[:, 2].max():.0f}")
```

## Pitfalls

1. **Non-contractive transformations**: If spectral radius $\rho(A_i) \geq 1$, IFS diverges. Ensure all $|a_{jj}^{(i)}| < 1$ for diagonal dominance.
2. **Degenerate attractor**: If all transformations are identical, attractor = single point. Ensure transformations are distinct.
3. **Pitch range explosion**: Even with $|a_{11}| < 1$, translation terms $e_1$ can push pitches outside MIDI range. Clamp to $[0, 127]$ and quantize.
4. **Time coordinate drift**: IFS time coordinates may not align with musical meter. Post-process: sort by time, snap to grid, deduplicate.
5. **Velocity saturation**: IFS velocity coordinates may exceed MIDI range. Normalize: $v_{midi} = 40 + 50 \cdot (v - v_{min}) / (v_{max} - v_{min})$.
6. **Sparse texture**: If probabilities are too uniform, attractor is diffuse. Use skewed probabilities (e.g., $p = [0.5, 0.3, 0.2]$) for focused structure.
7. **No self-similarity**: If transformations are too similar, fractal dimension ≈ 1 (line). Increase transformation diversity for dimension > 1.
8. **Section-boundary discontinuities**: Abrupt IFS parameter changes create jumps. Use cross-fade: $w^{(blend)} = (1-\alpha) w^{(s)} + \alpha w^{(s+1)}$.
9. **Voice allocation collisions**: Multiple voices may claim same pitch-time region. Use pitch-range partitioning with hysteresis (±2 semitone guard bands).
10. **Computational cost**: $M = 10^6$ iterations needed for dense attractor. Pre-generate and cache point cloud; subsample for different sections.

## Hybridization Patterns

- **IFSMG + 002 Markov**: Use IFS for macro-form and section-level structure; use Markov chains for local melodic detail within each IFS-defined region.
- **IFSMG + 026 DPSM**: IFS generates the base pitch-time structure; DPSM phase-shifted layers add continuous flowing texture over the fractal skeleton.
- **IFSMG + 023 Tendency Masking**: Use IFS attractor shape as the tendency mask corridor $[L(t), U(t)]$, then sample stochastically within the fractal-defined bounds.
- **IFSMG + 040 Perlin Noise**: Replace IFS velocity dimension with Perlin noise for smoother dynamic evolution while keeping IFS pitch-time fractal structure.

## References
- Barnsley, M. F. (1988). *Fractals Everywhere*. Academic Press.
- Allouche, J.-F. (1991). "Automatic generation of melodic lines using iterated function systems." Proceedings of the International Computer Music Conference.
- Nelson, G. L. (1994). "The use of chaos in algorithmic composition." Computer Music Journal, 18(3), 42-55.
- Pickover, C. A. (1990). *Computers, Pattern, Chaos, and Beauty*. St. Martin's Press.
- Mandelbrot, B. B. (1982). *The Fractal Geometry of Nature*. W. H. Freeman.
- Roads, C. (1996). *The Computer Music Tutorial*. MIT Press. (Chapter 18: Algorithmic composition.)
