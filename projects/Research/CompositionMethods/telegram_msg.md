# New Method: Kuramoto Oscillator Phase Synchronization (KOPS)

Hey Axel! New method in database.

### **Method 038: Kuramoto Oscillator Phase Synchronization (KOPS)**

- **Source**: Kuramoto (1975) / Chemical Oscillations, Waves, and Turbulence / Nonlinear Dynamics.
- **PITCH**: Normalized oscillator phase $\theta_v(t) \pmod{2\pi}$ is mapped to a target pitch scale. In uncoupled states, pitches drift dynamically; as synchronization increases ($R(t) \to 1$), the pitches converge toward the collective mean phase, establishing stable, focused tonal centers.
- **RHYTHM**: Note-on events trigger whenever an oscillator's phase wraps around $2\pi$ (zero-crossing with positive derivative). Tempo and triggers are governed by instant phase velocities. The rhythm transitions from asynchronous, multi-tempo polyrhythms to locked homophonic unisons.
- **HARMONY**: Vertical phase alignments define the chord structures. Desynchronized states produce dense, microtonal clusters and spectral friction; coupling phase-locks the voices, creating clean consonant intervals and parallel voice leading.
- **STRUCTURE**: Driven by the global coupling strength $K_s(t)$. Low coupling represents high complexity, tension, and development phases; high coupling drives global phase transitions, resulting in synchronized, stable climaxes.
- **TEXTURE**: Highly fluid and organic. Slowly evolves from independent, decentralized contrapuntal lines into a singular, unified homophonic choral texture.

#### **UnitMatrix Mapping**:
- **Rows (Voices)**: Assigned to individual coupled oscillators (Voice 1 = Oscillator A, Voice 2 = Oscillator B, etc.).
- **Columns (Sections)**: Successive chronological windows governed by unique coupling factors $K_s$ and natural frequency arrays $\omega_{i, s}$.
- **Cells**: `{PITCH: Scale-quantized values from normalized phase angles, RHYTHM: Rhythmic triggers from phase-wrapping crossings, TEXTURE: Velocity, duration, and panning vectors scaled by the order parameter r(t) and phase velocity}`.

*Appended to `/opt/data/projects/Research/CompositionMethods/methods_db.md`.*
