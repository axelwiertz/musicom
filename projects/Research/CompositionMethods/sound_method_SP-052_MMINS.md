# CORDIS-ANIMA Modular Mass-Interaction Network Synthesis (MMINS) — Method SP-052

**Paradigm**: Physical modeling — modular lumped mass-interaction network.
**Layer**: Synthesis Engines.
**Origin**: Claude Cadoz, Annie Luciani, Jean-Loup Florens — ACROE laboratory, Grenoble, France (1979–1993).

---

## 1. Concept

CORDIS-ANIMA models a sounding object as a **network of lumped physical modules** simulated at audio sample rate. There is no oscillator and no render stage: the displacement of a mass point *is* the audio signal. The module vocabulary is tiny and closed:

| Module | Role | Law |
|---|---|---|
| **MAT** | point mass (inertia) | $F = M\,\ddot{x}$ |
| **SOL** | fixed ground (infinite mass) | $x = 0$ |
| **LIA** | viscoelastic link (spring + damper) | $F = -K(x_i - x_j) - Z(v_i - v_j)$ |
| **RES** | pure damper | $F = -Z(v_i - v_j)$ |
| **FRO** | nonlinear friction (stick-slip bowing) | static hold $F_s$, kinetic $F_d < F_s$ |
| **BUT** | unilateral stop (impact/rattle) | $F = -K\,\max(x_i - x_j - x_{\text{lim}}, 0)$ |

Arbitrary graph topology = arbitrary instrument: a chain = string, a 2D grid = membrane, a chain + FRO = bowed string, masses + BUT = shaker rattle. The formalism also unifies gesture and instrument — the excitation is itself a network that strikes/bows/plucks the instrument network (Cadoz's "instrumental universe").

## 2. Technical Mechanics

### 2.1 Integration (centered finite difference / leapfrog / Verlet)

Newton's second law discretized at sample period $T = 1/f_s$:

$$x(n+1) = 2\,x(n) - x(n-1) + \frac{T^2}{M}\,F(n)$$

Velocity reconstructed as $v(n) = (x(n) - x(n-1))/T$. Each MAT carries only two state variables.

### 2.2 Per-sample simulation loop

1. **Force pass**: zero all mass forces; add external excitations $F_{\text{ext}}$; for each link compute $F_{ij}$ and accumulate into both endpoints with opposite signs (Newton's third law).
2. **Integration pass**: for each MAT, update $x(n+1)$ from the net force.
3. **Output**: $y(n) = x_k(n)$ — displacement of the chosen output mass (or weighted sum over several).

### 2.3 Stability

The scheme is conditionally stable. The stiffest mode $\omega_0 = \sqrt{K/M}$ must satisfy $\omega_0 T \ll 2$ (equivalently $T \ll 2\sqrt{M/K}$). Running at 44.1 kHz makes the time step the audio period; stiff links (high $K$, low $M$) are the binding constraint.

### 2.4 Modal structure = timbre

The network's stiffness matrix (assembled from the link graph) determines the modal spectrum. A chain of $N$ masses has $N$ eigenmodes (string-like harmonic series with dispersion); a 2D grid has $N_x N_y$ (membrane, inharmonic); a tree = branching resonator. Damping $Z$ sets per-mode decay; FRO/BUT inject broadband energy (bow noise, impact transients).

### 2.5 Complexity

$\mathcal{O}(N_{\text{masses}} + N_{\text{links}})$ per sample. Vectorized as sparse matrix-vector products: force pass $F = -K_{\text{sparse}}x - Z_{\text{sparse}}v$; integration is a per-mass update, trivially parallel.

## 3. Musical Elements Framework

- **PITCH**: Set by eigenmodes. Single MAT–LIA–SOL oscillator: $f_0 = \tfrac{1}{2\pi}\sqrt{K/M}$. Retune = change $K$ or $M$. Chains/grids give inharmonic partial series; pitch is the fundamental of the modal spectrum.
- **RHYTHM**: The excitation schedule. Pluck impulses at tick-grid onsets (grid-locked); FRO bowing produces stick-slip periodicity (self-oscillating, continuous); BUT contacts produce impact transients at collision instants.
- **HARMONY**: The modal spectrum *is* the harmonic content. Coupling oscillators through LIA links yields sympathetic resonance — the physical equivalent of a chord with shared overtones. Nonlinear links generate intermodulation (sum/difference partials).
- **STRUCTURE**: Topology + parameter trajectories per section. Section A = plucked chain, B = bowed chain, C = membrane grid. Adding/removing links at joins switches the instrument; slow automation of $K$/$Z$/force = continuous timbral morph.
- **TEXTURE**: Network density, damping $Z$, and nonlinearity (FRO/BUT). Sparse = thin/resonant; dense grid = thick/noisy; high $Z$ = dry/percussive; low $Z$ = long ring; FRO/BUT = grit, bow noise, rattle.

## 4. UnitMatrix Integration

- **Rows (Voices)**: Each voice $v$ = an independent CORDIS-ANIMA network. Lead = plucked chain; bass = bowed chain (FRO); pad = membrane grid; percussion = BUT rattle. Each row renders to a mono buffer, then summed or spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)**: Each section $s$ supplies topology/parameter set, excitation pattern, and output-mass selection. Joins = topology switch (discrete) or parameter crossfade (continuous).
- **Cells** $U_{v,s}$:
  - `{PITCH}`: $K$/$M$ retuning → fundamental/modal tuning.
  - `{RHYTHM}`: excitation impulse onsets + bow-force envelope → attack schedule.
  - `{HARMONY}`: chain/grid size + link coupling → overtone structure.
  - `{TEXTURE}`: $Z$, FRO/BUT presence/thresholds, network density → decay, grit, density.
- **Flow**: compose UnitMatrix → validate zero-drift → export MIDI (musicom engine) → build per-voice network → map cells to parameters → simulate at audio rate → sum → post-process (SP-007/SP-008/SP-009/SP-032) → export/spatialize.

## 5. Python / NumPy Implementation Sketch

```python
import numpy as np

class MassInteractionNetwork:
    """CORDIS-ANIMA style mass-interaction network (SP-052 MMINS)."""
    def __init__(self, fs=44100):
        self.fs = fs
        self.T = 1.0 / fs
        self.masses = {}   # id -> dict(M, x, x_prev, F)
        self.links = []    # (type, i, j, params)

    def add_mass(self, m_id, M, x0=0.0):
        self.masses[m_id] = dict(M=M, x=x0, x_prev=x0, F=0.0)

    def add_ground(self, g_id):
        self.masses[g_id] = dict(M=np.inf, x=0.0, x_prev=0.0, F=0.0)  # SOL

    def add_lia(self, i, j, K, Z):
        self.links.append(('LIA', i, j, dict(K=K, Z=Z)))

    def add_res(self, i, j, Z):
        self.links.append(('RES', i, j, dict(Z=Z)))

    def add_fro(self, i, j, Fs, Fd):
        self.links.append(('FRO', i, j, dict(Fs=Fs, Fd=Fd)))

    def add_but(self, i, j, K, x_lim):
        self.links.append(('BUT', i, j, dict(K=K, x_lim=x_lim)))

    def step(self, excitations):
        """One audio sample. excitations: {mass_id: external force}."""
        T = self.T
        for m in self.masses.values():
            m['F'] = 0.0
        for m_id, f in excitations.items():
            self.masses[m_id]['F'] += f
        # 1) force pass
        for typ, i, j, p in self.links:
            mi, mj = self.masses[i], self.masses[j]
            xi, xj = mi['x'], mj['x']
            vi = (mi['x'] - mi['x_prev']) / T
            vj = (mj['x'] - mj['x_prev']) / T
            if typ == 'LIA':
                F = -p['K'] * (xi - xj) - p['Z'] * (vi - vj)
            elif typ == 'RES':
                F = -p['Z'] * (vi - vj)
            elif typ == 'FRO':                      # Coulomb stick-slip (bowing)
                dv = vi - vj
                F = -np.sign(dv) * p['Fd'] if abs(dv) > 1e-6 else 0.0
            elif typ == 'BUT':                      # unilateral stop (impact)
                F = -p['K'] * max(xi - xj - p['x_lim'], 0.0)
            mi['F'] += F
            mj['F'] -= F                            # action-reaction
        # 2) integration pass
        for m in self.masses.values():
            if np.isinf(m['M']):
                continue                            # ground stays fixed
            x_new = 2.0 * m['x'] - m['x_prev'] + (T * T / m['M']) * m['F']
            m['x_prev'], m['x'] = m['x'], x_new
        return self.masses

# --- Example: plucked string = chain of N masses with LIA links ---
net = MassInteractionNetwork(fs=44100)
N = 32
for k in range(N):
    net.add_mass(k, M=0.001)
net.add_ground('g')
for k in range(N - 1):
    net.add_lia(k, k + 1, K=2000.0, Z=0.5)
net.add_lia(N - 1, 'g', K=2000.0, Z=0.5)           # anchor to ground

buf = []
for n in range(44100):                              # 1 second
    exc = {0: 100.0} if n == 0 else {}               # impulse at t=0
    m = net.step(exc)
    buf.append(m[N // 2]['x'])
audio = np.array(buf)
```

**Vectorized variant**: assemble sparse stiffness/damping matrices once; force pass becomes `F = -K_sparse @ x - Z_sparse @ v`; integration is a vectorized per-mass update. Compile with Numba/Cython for real-time.

## 6. Pitfalls

1. **Instability**: centered-difference integrator blows up if $\omega_0 T \ge 2$. Clamp $K$, raise $M$, or oversample; validate max eigenvalue first.
2. **DC drift / undamped ringing**: lossless networks integrate numerical error into DC offset. Add small $Z$ to every LIA; high-pass the output.
3. **Sparse / staccato output**: impulse-only excitation = plucky gaps (011/032 failure mode). Add continuous fill: FRO bowing, high-$Z$ membrane pads, noise-driven rattle (Method Hybridization rule).
4. **Monophonic sine monotony**: single oscillator = pure damped sine. Use chains/grids, couple oscillators, add FRO/BUT.
5. **Pitch sharpness from discretization**: discrete scheme shifts pitch sharp. Pre-warp $K$ via $\omega_d = \tfrac{2}{T}\arcsin(\omega_a T/2)$, or measure and retune.
6. **Nonlinear chatter**: hard BUT/FRO contacts buzz at Nyquist. Regularize contact law, add compliance, or oversample nonlinear links.
7. **Slow pure-Python loop**: vectorize with sparse matrices or compile; DSP is $O(N_{\text{masses}} + N_{\text{links}})$ per sample.

## 7. Comparison With Related Methods

| Method | Domain | Topology | Nonlinearity | Cost |
|---|---|---|---|---|
| Modal Plate/Bar (SP-003) | Frequency domain (modes) | Fixed object | None | $O(N_{\text{modes}})$ |
| Karplus-Strong (SP-011) | Delay line | 1D string | None | $O(N)$ |
| Scanned Synthesis (SP-018) | Mass-spring chain as wavetable | 1D chain | None | $O(N)$ |
| FDTD (SP-040) | PDE on spatial grid | 2D/3D grid | Optional | $O(N_{\text{grid}})$ |
| Modal Bank MBED (SP-042) | Eigenmode resonators | Fixed object | None | $O(N_{\text{modes}})$ |
| **MMINS (SP-052)** | **Lumped mass-interaction graph** | **Arbitrary graph** | **FRO/BUT contact + friction** | $O(N_{\text{masses}} + N_{\text{links}})$ |

## 8. References

- Cadoz, C., Luciani, A., and Florens, J.-L. (1993). "CORDIS-ANIMA: A Modeling and Simulation System for Sound and Image Synthesis: The General Formalism." *Computer Music Journal* 17(1), pp. 19–29. DOI 10.2307/3680567.
- Cadoz, C., Luciani, A., and Florens, J.-L. (1984). "Responsive Input Devices and Sound Synthesis by Stimulation of Instrumental Mechanisms: The CORDIS System." *Computer Music Journal* 8(3), pp. 60–73. DOI 10.2307/3679813.
- Florens, J.-L., and Cadoz, C. (1991). "The Physical Model: Modeling and Simulating the Instrumental Universe." In *Representations of Musical Signals*, MIT Press, pp. 227–268.
- Cadoz, C., Castagné, N., and Tache, O. (2011). "Sound synthesis and musical composition with the physical modeling formalism Cordis-Anima." *Journal of the Acoustical Society of America* 130(4), 2365. DOI 10.1121/1.3654476.
- Kontogeorgakopoulos, A., and Cadoz, C. (2008). "Interfacing Digital Waveguide with CORDIS ANIMA networks." *Journal of the Acoustical Society of America* 123(5), 3902. DOI 10.1121/1.2934998.
- Cadoz, C. (1979). *Synthèse sonore par simulation de mécanismes vibratoires.* Doctoral thesis, INPG, Grenoble, France.
- Florens, J.-L., Cadoz, C., and Luciani, A. (1997). "A MARACA Modelisation and Simulation through the CORDIS-ANIMA Formalism." *Proc. International Symposium on Musical Acoustics (ISMA)*, Edinburgh.
