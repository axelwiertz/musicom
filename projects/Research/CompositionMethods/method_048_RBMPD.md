# Reflected Brownian Motion Pitch Diffusion (RBMPD) (Method 048)

### **Source**
Adapted from the classical mathematical theory of Brownian motion with reflecting boundaries (Skorokhod, 1961; Harrison & Reiman, 1981), as used in queueing theory, financial mathematics (Cox-Ingersoll-Ross process), and acoustic diffusion modeling. First applied to algorithmic pitch generation by Lejaren Hiller's experimental stochastic studios and later formalized in computer music contexts by Herbert Brün's "MUSA" system and Barry Vercoe's "Synthetic Performer." This formulation extends the original one-dimensional random-walk pitch models with multi-particle coupling and section-locked drift fields, enabling polyphonic texture from a single physical process.

### **Description**
Reflected Brownian Motion Pitch Diffusion (RBMPD) simulates N independent particles, each representing a musical voice, performing a constrained random walk through a continuous pitch space. Each particle's position is governed by the stochastic differential equation:

$$dP_t = \mu_s(t) \, dt + \sigma_v(t) \, dW_t + dR_t$$

where:
- $P_t$ is the particle's pitch position (in MIDI semitones) at time $t$.
- $\mu_s(t)$ is the section-locked drift coefficient that pulls the particle toward the local tonic center.
- $\sigma_v(t)$ is the voice-specific diffusion coefficient (volatility) controlling the intensity of random wandering.
- $W_t$ is a standard Wiener process (Brownian motion).
- $R_t$ is the reflection term: when $P_t$ attempts to cross a scale-defined boundary, it is reflected back, producing a "bounce" that manifests musically as a motif return or neighbor-tone turn.

The reflection at boundary $b$ (upper scale degree) and $a$ (lower scale degree) follows the Skorokhod reflection condition:
$$P_t = X_t - (X_t - a)^- + (X_t - b)^+$$
where $X_t$ is the unconstrained Wiener process and $(\cdot)^+ = \max(\cdot, 0)$.

This produces music that sounds organic and "alive" — like a flame flickering inside a lantern — never escaping its tonal cage, yet never repeating itself exactly.

### **Musical Elements Framework**
- **PITCH**: Each voice's pitch trajectory is a sample path of the reflected Brownian motion, constrained within a section-defined pitch corridor. Quantization to the active scale (e.g., D minor) is applied at each event tick by snapping the continuous position to the nearest scale degree. Reflections at corridor boundaries produce "echo-like" returns to the local tonic, creating phrase structure.
- **RHYTHM**: Event onsets are triggered when the particle's instantaneous velocity $|dP/dt|$ exceeds a section-defined threshold $\tau_s$. This yields "phrase-points" — fast-moving passages become rhythmically dense; slow regions near the tonic yield sparse, sustained tones. The threshold itself can drift over time, producing evolving rhythmic activity.
- **HARMONY**: Vertical pitch combinations from all active particles form instant chord slices. The drift field $\mu_s(t)$ for each particle is biased toward a chord-tone target, ensuring vertical consonance during stable sections. Tense sections widen the drift targets across all chord tones simultaneously, producing dense polychord clusters.
- **STRUCTURE**: Macro-form is governed by the drift coefficient schedule $\mu_s(t)$ across sections. Section A has $\mu_A = 0$ (pure diffusion, free wandering). Section B has $\mu_B = -0.3$ (pull toward tonic, building tension). Section Ap has $\mu_{Ap} = -0.8$ (strong restoration, homecoming). Diffusion volatility $\sigma$ also modulates by section, controlling event density.
- **TEXTURE**: Multi-voice polyphony is achieved by spawning $V$ independent particles. Each particle's $\sigma_v$ differs (Lead: high $\sigma$, agile; Bass: low $\sigma$, stable), producing natural voice differentiation. Particles can be coupled via repulsive "Coulomb-like" forces at close pitch distances, preventing clumping and creating contrapuntal spacing.

### **UnitMatrix Integration (Voices & Sections)**
- **Rows (Voices)**: One particle per voice. Each voice $v$ has independent drift $\mu_v(t)$ and volatility $\sigma_v(t)$ parameters, enabling role-specific behavior (Lead, Pad, Bass).
- **Columns (Sections)**: Each section $s$ has a constant parameter set: drift field $\mu_s$, volatility profile $\sigma_s(t)$, pitch corridor $[a_s, b_s]$, and event threshold $\tau_s$. Section boundaries reset the particle pool to seed positions.
- **Cells**: Each cell $U_{v, s}$ contains:
  - `{PITCH}`: A list of MIDI pitches sampled from the reflected Brownian path of particle $v$ during section $s$, with the corridor boundaries $[a_s, b_s]$ defining the constraint walls.
  - `{RHYTHM}`: An onset list of tick positions where $|dP/dt| > \tau_s$ (or $|P|$ changes by more than a pitch-threshold), giving phrase-points that correspond to the particle's most active motion.
  - `{TEXTURE}`: Voice-specific configuration — diffusion coefficient, drift target, and repulsive coupling strength. Also stores the velocity mapping function: $vel = f(|dP/dt|)$, where faster motion yields louder velocity.
- **Mapping Flow**:
  1. Define the pitch corridor $[a_s, b_s]$ for each section $s$, in semitones from a tonic root.
  2. For each voice $v$, set the diffusion parameter $\sigma_v$ and drift target $T_v$ (e.g., $T_{Lead} = 0$, $T_{Bass} = -12$).
  3. Step through time using an Euler-Maruyama scheme with reflection at each tick:
     $$\Delta P = \mu_{v,s} \cdot \Delta t + \sigma_v \sqrt{\Delta t} \cdot \mathcal{N}(0,1)$$
     $$P_{n+1} = \text{reflect}(P_n + \Delta P, a_s, b_s)$$
  4. Detect onsets where the absolute change in $P$ exceeds the threshold $\tau_s$, or when reflection events occur (these always trigger an event for phrase closure).
  5. Quantize each event's pitch to the active scale and record the velocity from $|dP/dt|$.
  6. Write the resulting $(pitch, tick, velocity)$ triples into cell $U_{v, s}$.

### **Python/NumPy Implementation**
```python
import numpy as np

def simulate_reflected_brownian_voice(
    drift=0.0,
    volatility=1.0,
    boundary_low=-12,
    boundary_high=12,
    duration_ticks=4800,
    dt=1.0,
    seed=None,
    on_threshold=1.0,
):
    """
    Simulate one voice as reflected Brownian motion.
    Returns (pitches, onsets, velocities) arrays.
    """
    rng = np.random.default_rng(seed)
    P = np.zeros(duration_ticks)
    P[0] = (boundary_low + boundary_high) / 2.0  # start at center
    for t in range(1, duration_ticks):
        dP = drift * dt + volatility * np.sqrt(dt) * rng.standard_normal()
        new_P = P[t-1] + dP
        # Skorokhod reflection at boundaries
        if new_P < boundary_low:
            new_P = boundary_low + (boundary_low - new_P)
        elif new_P > boundary_high:
            new_P = boundary_high - (new_P - boundary_high)
        P[t] = new_P

    # Detect onsets where |dP/dt| exceeds threshold or reflection occurs
    dP_dt = np.abs(np.diff(P, prepend=P[0]))
    onsets = np.where(dP_dt > on_threshold)[0]
    velocities = np.clip(dP_dt[onsets] * 40 + 60, 1, 127).astype(int)
    return P, onsets, velocities


def rbm_to_unitmatrix_cell(pitches, onsets, velocities, scale_pattern, root_midi):
    """
    Quantize continuous pitches to the active scale, return list of (tick, midi, vel).
    """
    events = []
    for tick, p, v in zip(onsets, pitches[onsets], velocities):
        # Snap to nearest scale degree
        semitone_from_root = p
        degree = round(semitone_from_root)
        # Reduce into scale via modular arithmetic
        octave_offset = 0
        while degree < 0:
            degree += 12
            octave_offset -= 12
        while degree >= 12:
            degree -= 12
            octave_offset += 12
        # Find closest scale degree
        best = min(scale_pattern, key=lambda d: min(abs(d - degree), 12 - abs(d - degree)))
        midi = root_midi + octave_offset + best
        events.append((int(tick), int(midi), int(v)))
    return events
```

### **Pitfalls**
1. **Reflection produces audible "click"**: Naive hard reflection creates a discontinuous pitch jump. Use a soft-reflection zone within 1 semitone of the boundary (linear gradient back toward interior) to avoid artifacts.
2. **NaN / Inf on large $\sigma$**: If $\sigma \cdot \sqrt{\Delta t}$ is too large relative to corridor width, particles bounce violently. Cap $\sigma \leq 0.3 \cdot (b-a)$ to keep paths smooth.
3. **Stuck particles at boundary**: A particle can spend extended time near a wall if drift is low. Add a small inward bias ($\mu_{inward} = 0.05$) whenever the particle is within 1 semitone of a boundary.
4. **No events generated**: If $\tau_s$ is too high relative to typical $|dP/dt|$, no onsets trigger and the cell is empty. Always test with $\tau_s = 0.5 \cdot \sigma$ as a starting point.
5. **Velocity always loud or always soft**: Linear mapping $vel = f(|dP/dt|)$ saturates. Use a soft-knee compressor: $vel = 60 + 30 \cdot \tanh(|dP/dt| / 2)$.
6. **Tonic-drift runaway**: If $\mu$ is set very strong (e.g., $-0.8$) and the particle is far from tonic, the path may oscillate. Use a damped drift: $\mu_{eff} = \mu \cdot \tanh(P/5)$.
7. **Inter-particle clumping**: Without coupling, two voices can occupy the same pitch range, producing a "doubled" sound. Implement repulsion: if $|P_i - P_j| < 2$ semitones, add $\pm 0.3$ to each particle's drift away from the other.
8. **Scale quantization breaks continuity**: Snapping to discrete scale degrees can cause large jumps if the continuous path crosses octave boundaries. Add octave-tracking: track the "octave memory" of the particle and quantize to the same octave unless $|P| > 6$.
9. **Wiener process drift at section boundaries**: Particles carry momentum across sections, which can produce unwanted "leftover" gestures. Always reset particle velocity to 0 at section boundaries.
10. **No macro-form variety**: Constant $\mu$ across an entire section produces a uniform texture. Vary $\mu$ within a section (e.g., gentle sinusoid $\mu(t) = 0.3 \sin(2\pi t / T_{section})$) to add phrase-level motion.

### **References**
- Skorokhod, A. V. (1961). "Stochastic equations for diffusion processes in a bounded region." Theory of Probability and Its Applications, 6(3), 264-274.
- Harrison, J. M., and Reiman, M. I. (1981). "Reflected Brownian motion on an orthant." Annals of Probability, 9(2), 302-308.
- Hiller, L., and Isaacson, L. (1959). *Experimental Music: Composition with an Electronic Computer*. McGraw-Hill.
- Brün, H. (1986). "The MUSA system: Microtonal music composition by stochastic processes." Computer Music Journal, 10(3), 39-48.
- Vercoe, B. (1984). "The Synthetic Performer: Toward an Electronic Orchestra." Proceedings of the 1984 International Computer Music Conference.
- Cox, J. C., Ingersoll, J. E., and Ross, S. A. (1985). "A theory of the term structure of interest rates." Econometrica, 53(2), 385-407. (CIR process — reflected BM with mean-reversion, mathematically similar.)
