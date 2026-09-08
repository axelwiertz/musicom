# SP-067 — Kelly-Lochbaum Acoustic Tube Model (Vocal Tract Physical Modeling) (KLAT)

- **Method ID:** SP-067
- **Acronym:** KLAT (Kelly-Lochbaum Acoustic Tube)
- **Layer:** absolute (sound production)
- **Category:** Synthesis Engines (physical modeling / scattering junction)
- **Candidate code path:** `sound/synthesis/kelly_lochbaum.py`

## One-line description

Models the vocal tract as an N-section lossless acoustic transmission line: the area function $A_i$ (vowel geometry) sets each junction's reflection coefficient $k_i = \frac{A_i - A_{i+1}}{A_i + A_{i+1}}$, and forward/backward pressure waves scatter through the two-port Kelly-Lochbaum lattice. A glottal pulse train (voiced) or frication noise (unvoiced) excites the glottal end; a $1-z^{-1}$ radiation load terminates the lips. Formants emerge from the area-function geometry — no formant filters specified.

## The physics

The vocal tract is treated as a plane-wave acoustic transmission line. The glottal end is a nearly-closed (high-pressure-reflection) boundary, the lips are a nearly-open (pressure-node) boundary radiating into free air. Between them, the tract cross-sectional area $A(x)$ varies along the length axis $x$. A travelling pressure wave encountering an area change is partially reflected; the reflection coefficient depends only on the area ratio.

## The math (extended)

### 1. Spatial discretization

Split the tract of length $L$ (≈ 17 cm adult male) into $N$ cylindrical sections:

$$\Delta x = \frac{L}{N} = \frac{c}{2 f_s}$$

where $c = 343$ m/s is the speed of sound and $f_s$ is the sampling rate. This makes each section exactly one-half-sample of one-way travel time, so a round trip through a section is one sample — the lattice advances at the audio rate with one unit delay per direction per section.

### 2. Reflection coefficients from the area function

At the junction of section $i$ (area $A_i$) and section $i+1$ (area $A_{i+1}$):

$$k_i = \frac{A_i - A_{i+1}}{A_i + A_{i+1}}, \qquad -1 < k_i < 1$$

Energy is conserved because the transmission coefficient $t_i = 1 - k_i = \frac{2 A_{i+1}}{A_i + A_{i+1}}$ satisfies the power relation $k_i^2 + \frac{A_i}{A_{i+1}} t_i^2 = 1$ (for pressure waves).

### 3. The Kelly-Lochbaum two-port scattering junction

Let $p^+_i$ be the forward (glottis → lips) pressure wave and $p^-_i$ the backward wave in section $i$. The lossless junction is:

$$p^+_{i+1} = (1 + k_i)\, p^+_i + k_i\, p^-_{i+1}$$

$$p^-_i = k_i\, p^+_i + (1 - k_i)\, p^-_{i+1}$$

This scattering matrix

$$\begin{bmatrix} p^+_{i+1} \\ p^-_i \end{bmatrix} = \begin{bmatrix} 1+k_i & k_i \\ k_i & 1-k_i \end{bmatrix} \begin{bmatrix} p^+_i \\ p^-_{i+1} \end{bmatrix}$$

is unitary in the lossless case (its determinant is $1 - k_i^2 - k_i^2 = 1 - 2k_i^2$ … corrected: it is the standard lossless two-port, energy-preserving under the pressure convention). The full tract is a chain of these junctions with one-sample delays between them — a **waveguide chain**, a special case of SP-033's 1D digital waveguide with section-varying characteristic impedance.

### 4. Glottal source

The glottal volume velocity $u_g(t)$ drives the glottal (section 0) boundary:

- **Voiced (Rosenberg / LF):** a quasi-periodic train of skewed glottal pulses at period $T_0 = f_s / f_0$. The Rosenberg pulse over one period is:

$$u_g(t) = \begin{cases} \frac{1}{2}\big(1 - \cos(\pi t / t_o)\big) & 0 \le t \le t_o \\ \cos\big(\pi (t - t_o) / (2 t_c)\big) & t_o < t \le t_o + t_c \\ 0 & t_o + t_c < t \le T_0 \end{cases}$$

with opening time $t_o$ and closing time $t_c$; its spectrum rolls off −12 dB/oct, intrinsically band-limited.

- **Unvoiced / frication:** white noise injected at a constriction (frication) or at the glottis (aspiration), band-limited.

- **Breathy:** a mix — add filtered noise to the glottal flow (noise-to-pulse ratio = breathiness).

### 5. Lip radiation

At the lips (section $N$), the pressure wave reflects with $r_L \approx -1$ (pressure node at the open end). The radiated pressure is, to first order, the time derivative of the lip volume velocity:

$$R(z) = 1 - z^{-1}$$

a +6 dB/oct tilt. Net source+radiation tilt = −12 + 6 = −6 dB/oct (the observed speech spectral tilt).

### 6. Formants emerge from geometry

Uniform tube ($A_i$ constant, $k_i = 0$) → odd quarter-wave resonances:

$$f_n = \frac{(2n+1)c}{4L}$$

For the default 17 cm tract: $f_0 \approx 500$ Hz, $f_1 \approx 1500$ Hz, $f_2 \approx 2500$ Hz — the "schwa" /ə/ formants. Constrictions move them:
- front constriction (palatal) → F2 up (the /i/ cavity)
- back constriction (velar) → F2 down (/u/)
- wide pharynx → F1 up (/a/)

Each vowel is a Fant area function; formant trajectories = interpolation of $A_i(t)$ (not $k_i$ directly) between vowel targets.

## NumPy / Python implementation sketch

```python
import numpy as np

class KellyLochbaum:
    def __init__(self, sr=48000, L=0.17, N=16, c=343.0):
        self.sr = sr
        self.N = N
        self.dx = L / N                  # section length (m)
        # one-way delay per section in samples (fractional -> round for integer delay)
        self.sec_delay = max(1, int(round((self.dx / c) * sr)))  # ~0.5 -> 1 at 48k with dx=c/2fs
        # state: forward (f) and backward (b) pressure waves, length N+1
        self.f = np.zeros(N + 1)
        self.b = np.zeros(N + 1)
        self.rng = np.random.default_rng(0)

    def set_area(self, A):
        """A: array of N+1 section areas (m^2). Build reflection coefficients."""
        A = np.clip(A, 1e-6, None)
        self.k = (A[:-1] - A[1:]) / (A[:-1] + A[1:])   # length N

    def rosenberg(self, t, t_o, t_c):
        """Glottal pulse shape at normalized time t in [0,1)."""
        if t < t_o:
            return 0.5 * (1 - np.cos(np.pi * t / t_o))
        elif t < t_o + t_c:
            return np.cos(np.pi * (t - t_o) / (2 * t_c))
        return 0.0

    def render_note(self, f0, dur, vowel_A, voiced=True, breath=0.0, vibrato=(5.0, 0.01)):
        self.set_area(vowel_A)
        T0 = self.sr / f0
        n = int(dur * self.sr)
        out = np.zeros(n)
        ph = 0.0
        for i in range(n):
            # --- glottal source (voiced pulse train / noise) ---
            f_inst = f0 * (1 + vibrato[1] * np.sin(2*np.pi*vibrato[0]*i/self.sr))
            T_inst = self.sr / f_inst
            ph += 1.0 / T_inst
            if ph >= 1.0:
                ph -= 1.0
            src = self.rosenberg(ph, 0.3, 0.15) if voiced else 0.0
            src += breath * self.rng.standard_normal() * 0.1
            # inject at glottis (forward wave in section 0)
            self.f[0] += src
            # --- scattering lattice (chain of junctions) ---
            for j in range(self.N):
                kj = self.k[j]
                f_next = (1 + kj) * self.f[j] + kj * self.b[j + 1]
                b_prev = kj * self.f[j] + (1 - kj) * self.b[j + 1]
                self.f[j], self.b[j] = f_next, b_prev
            # shift forward waves down, backward waves up (unit delay per section)
            self.f = np.roll(self.f, self.sec_delay)
            self.b = np.roll(self.b, -self.sec_delay)
            # --- lip radiation: pressure = forward wave at lips, R = 1 - z^-1 ---
            lip = self.f[-1]
            out[i] = lip - lip_prev  # first difference (radiation)
            lip_prev = lip
            # glottal boundary reflection: nearly closed
            self.b[0] = 0.99 * self.f[0]
        return out
```

**Notes:** this is a topology sketch — real implementations handle fractional section delay (allpass interpolation), per-section loss (formant bandwidth), time-varying area (ramped coefficients), and a proper glottal boundary scattering (the source must be injected through a time-varying glottal reflection, not merely added). The vectorized form (precomputing the scattering chain as a sparse matrix) matches the per-sample loop exactly.

## References

- Kelly, J. L., & Lochbaum, C. C. (1962). "Speech synthesis." *Proc. Fourth Int. Congress on Acoustics*, Paper G42.
- Markel, J. D., & Gray, A. H. (1976). *Linear Prediction of Speech*. Springer.
- Rabiner, L. R., & Schafer, R. W. (1978). *Digital Processing of Speech Signals*. Prentice-Hall. (Ch. 3.)
- Fant, G. (1960). *Acoustic Theory of Speech Production*. Mouton.
- Fant, G., Liljencrants, J., & Lin, Q. (1985). "A four-parameter model of glottal flow." *STL-QPSR* 26(4).
- Rosenberg, A. E. (1971). "Effect of glottal pulse shape on the quality of natural vowels." *J. Acoust. Soc. Am.* 49(2B), 583–590.
- Smith, J. O. (2010). *Physical Audio Signal Processing*. CCRMA.
- Zölzer, U. (ed.) (2011). *DAFX: Digital Audio Effects*, 2nd ed. Wiley.
