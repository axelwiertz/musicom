# Method SP-116: Discrete Summation Formula Synthesis (DSFS)

**Method ID:** SP-116  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  
**Status:** Canonical Reference Specification  
**Author:** James A. Moorer (1976, CCRMA); extended by Burkhard (2022, complex quadrature DSF)  
**Candidate Implementation:** `sound/synthesis/dsf_synthesis.py`  
**Integration Point:** `workflows.musicom_workflow.produce(method="SP-116")`

---

## 1. Overview & Theoretical Foundations

Discrete Summation Formula Synthesis (DSFS) is a spectral synthesis technique that generates complex harmonic or inharmonic audio spectra by evaluating a closed-form trigonometric summation, avoiding both per-partial additive bank overhead and modulation-based aliasing. Instead of summing $N$ individual sine oscillators (additive synthesis) or relying on frequency modulation with its anti-aliasing burden, DSFS evaluates a single rational expression whose numerator and denominator are each a handful of trigonometric terms — delivering an exactly bandlimited spectrum with exponentially decaying partial amplitudes in $\mathcal{O}(1)$ per sample.

DSFS was discovered by James A. Moorer at Stanford CCRMA in 1975–76 as a generalization of Chowning's frequency modulation synthesis (Chowning 1973). The core insight is that a geometric series of sinusoidal terms has a closed-form rational expression, enabling direct spectral control with computational cost independent of the number of partials.

### 1.1 Relationship to Existing Synthesis Methods

| Method | Technique | Spectrum Control | Aliasing | Computational Cost |
|---|---|---|---|---|
| **SP-010 FM** | Frequency modulation | Bessel sidebands $\propto J_k(\beta)$ | Requires oversampling | $\mathcal{O}(1)$/sample |
| **SP-016 Granular** | Time-domain grain clouds | Indirect (density/pitch/spray) | Grain-window dependent | $\mathcal{O}(G)$/sample |
| **SP-019 Chebyshev** | Polynomial waveshaping | Harmonic amplitudes via Chebyshev coeffs | ADAA or oversampling | $\mathcal{O}(M)$/sample |
| **SP-029 Subtractive** | PolyBLEP osc + filter | Filtered harmonic source | Filter-dependent | $\mathcal{O}(F)$/sample |
| **SP-039 IFFT Additive** | IFFT frame synthesis | Exact per-partial control | None (frame-based) | $\mathcal{O}(M \log M)$/frame |
| **SP-041 Wavetable** | Table-lookup + interpolation | Wavetable-dependent morphing | Nyquist-mipmapped | $\mathcal{O}(1)$/sample + table |
| **SP-116 DSFS (this)** | Closed-form trig summation | Direct $a, f_c, f_m, N$ | Exact via $N$ truncation | $\mathcal{O}(1)$/sample, no table |

DSFS occupies the niche of **algebraic spectral control without banks, without modulation, and without wavetables** — the ideal middle ground between additive synthesis (full spectral control but high cost) and modulation synthesis (cheap but aliasing-prone).

---

## 2. Mathematical Formalism & DSP Mechanics

### 2.1 Core Identity (Finite Single-Sided DSF)

The fundamental DSF synthesis equation generates $N+1$ partials spaced $f_m$ apart starting at $f_c$, with partial amplitudes decaying by factor $a$ each step:

$$x[n] = \sum_{k=0}^{N} a^k \sin(\theta[n] + k \beta[n])$$

where:
- $\theta[n] = 2\pi f_c n / f_s$ (carrier phase)
- $\beta[n] = 2\pi f_m n / f_s$ (modulator phase increment)
- $a \in [0, 1)$ (ratio; spectral rolloff, $a=0$ = pure sine)
- $N \in \mathbb{N}_0$ (partial count — $N+1$ partials total)

This sum has the exact closed form (Jolley 1961; Moorer 1976, eq. 1):

$$x[n] = \frac{\sin\theta - a\!\sin(\theta-\beta) - a^{N+1}\big[\sin(\theta+(N+1)\beta) - a\!\sin(\theta+N\beta)\big]}{1 + a^2 - 2a\cos\beta}$$

**Proof sketch**: Write $\sin(\theta + k\beta) = \Im\, e^{j(\theta+k\beta)}$. The sum becomes:

$$x[n] = \Im\!\left( e^{j\theta} \sum_{k=0}^{N} (ae^{j\beta})^k \right)$$

This is a geometric series: $\sum_{k=0}^{N} r^k = (1 - r^{N+1})/(1 - r)$ where $r = ae^{j\beta}$. Taking the imaginary part yields the closed form above.

### 2.2 Infinite-Sum Form ($N \to \infty, a < 1$)

Permitting the sum to infinity eliminates the $a^{N+1}$ numerator terms:

$$x[n] = \sum_{k=0}^{\infty} a^k \sin(\theta + k\beta) = \frac{\sin\theta - a\sin(\theta-\beta)}{1 + a^2 - 2a\cos\beta}, \quad |a| < 1$$

This is the most economical DSF expression — 3 trigonometric calls + 8 arithmetic operations per sample, or zero trig when using phasor recurrence. The constraint $a < 1$ guarantees absolute convergence. The spectrum contains all harmonics up to Nyquist with amplitudes decaying as $a^k$, providing natural anti-aliasing via spectral rolloff rather than explicit truncation.

### 2.3 Two-Sided (Symmetric) DSF

For spectral energy on both sides of the carrier:

$$x[n] = \sin\theta + \sum_{k=1}^{N} a^k\big[\sin(\theta+k\beta) + \sin(\theta-k\beta)\big]$$

Closed form (Moorer 1976, eq. 3):

$$x[n] = \frac{\sin\theta\,\big(1 - a^2 - 2a^{N+1}[\cos((N+1)\beta) - a\cos(N\beta)]\big)}{1 + a^2 - 2a\cos\beta}$$

This produces partials at $f_c \pm k f_m$, $k = 0,1,\dots,N$, symmetric around $f_c$ with the carrier at full amplitude. The spectrum is always harmonic-symmetric even for irrational $f_c/f_m$, useful for creating "in-key" bells where sidebands decorate the carrier symmetrically.

### 2.4 Harmonic vs. Inharmonic Control

The spectral character is controlled by the frequency ratio $f_c : f_m$:

- **Harmonic** ($f_c/f_m \in \mathbb{Q}$): Partial frequencies $f_k = f_c + k f_m$ form an integer-multiple series when $f_c = f_m$ (pure harmonic: $f_c, 2f_c, 3f_c, \dots$). More generally for $f_c/f_m = p/q$, the fundamental is $f_0 = f_c/p = f_m/q$.
  
- **Inharmonic** ($f_c/f_m \notin \mathbb{Q}$): Partial frequencies never align to a common fundamental, producing bell-like, metallic, or clangorous timbres. The inharmonicity ratio $\mathcal{I} = \max(f_c/f_m, f_m/f_c)$ quantifies spectral density (higher $\mathcal{I}$ = denser).

- **Subharmonic regime** ($f_c < f_m$): The carrier sits below the first sideband, emphasizing difference tones and producing deep, growling textures.

### 2.5 Complex (Quadrature-Stereo) DSF

The complex phasor formulation simultaneously generates cosine (real) and sine (imag) streams:

$$c[n] = e^{ju} \cdot \frac{1 - (ae^{jv})^{N+1}}{1 - ae^{jv}}$$

where $u = 2\pi f_c n / f_s$ and $v = 2\pi f_m n / f_s$.

Extracting:
- $x_L[n] = \Re(c[n])$ — sum of cosines (left channel)
- $x_R[n] = \Im(c[n])$ — sum of sines (right channel)

Each partial appears in both channels but 90° out of phase, producing a spacious, non-localizable stereo field from a single computation — equivalent to a Hilbert-pair stereo without explicit FIR Hilbert filtering. The mono sum $x_L + x_R$ suppresses partials at odd quarter-cycle offsets, giving a natural comb-filtered alternative timbre.

### 2.6 Amplitude Normalization

The DSF signal's amplitude grows with $a$ and $N$ and must be normalized to prevent clipping. The peak amplitude is bounded by the sum of absolute values:

$$A_{\max} = \sum_{k=0}^{N} a^k = \frac{1 - a^{N+1}}{1 - a}$$

The normalized output is:

$$x_{\text{norm}}[n] = \frac{x[n]}{A_{\max}}$$

For the infinite-sum form ($a < 1$): $A_{\max} = 1/(1-a)$.

### 2.7 Efficient Phasor Recurrence

For real-time implementation, the per-sample trig calls can be eliminated:

1. Initialize complex phasors: $z_c \leftarrow e^{j\theta_0}$, $z_m \leftarrow e^{j\beta_0}$.
2. Pre-compute rotation constants: $\Delta_c = e^{j2\pi f_c / f_s}$, $\Delta_m = e^{j2\pi f_m / f_s}$.
3. Per sample:
   - $z_c \gets z_c \cdot \Delta_c$ (1 complex multiply = 4 FP mult + 2 FP add)
   - $z_m \gets z_m \cdot \Delta_m$ (same)
   - Extract $\sin\theta = \Im(z_c)$, $\cos\theta = \Re(z_c)$, $\sin\beta = \Im(z_m)$, $\cos\beta = \Re(z_m)$
   - Evaluate DSF denominator: $d = 1 + a^2 - 2a\cos\beta$
   - Evaluate DSF numerator for chosen form
   - Divide and normalize
4. Every $R = 4096$ samples: renormalize phasors to unit length ($z \gets z/|z|$) to counteract FP rounding drift.

This yields approximately 10–16 arithmetic operations per sample with zero transcendental function calls in the inner loop.

### 2.8 Bandlimiting Strategy

The key advantage of DSFS over FM synthesis is exact bandlimiting. For parameters $(f_c, f_m, N)$:

$$f_{\max} = f_c + N f_m$$

Set $N$ adaptively:

$$N_{\max} = \max\left(0,\; \left\lfloor \frac{f_s/2 - f_c}{f_m} \right\rfloor\right)$$

This guarantees zero aliasing at the specified sample rate without oversampling. For the infinite-sum form, the effective bandwidth is determined by the $a^k$ rolloff: the $-60\text{ dB}$ bandwidth is approximately:

$$B_{-60} \approx \frac{\log(10^{-3})}{\log a} \cdot f_m = \frac{-6.908}{\log a} \cdot f_m$$

### 2.9 Python/NumPy Implementation

```python
import numpy as np

def dsf_infinite(fc, fm, a, duration, sr=44100):
    """
    Infinite-sum DSF synthesis (a < 1).
    Returns: signal ndarray of shape (N,)
    """
    n = np.arange(int(sr * duration))
    theta = 2 * np.pi * fc * n / sr
    beta  = 2 * np.pi * fm * n / sr
    
    sin_t   = np.sin(theta)
    sin_t_b = np.sin(theta - beta)
    cos_b   = np.cos(beta)
    
    denom = 1 + a*a - 2*a * cos_b
    numer = sin_t - a * sin_t_b
    
    signal = np.divide(numer, denom, out=np.zeros_like(numer), where=denom != 0)
    norm = 1.0 / (1.0 - a)
    return signal * norm

def dsf_finite(fc, fm, a, N, duration, sr=44100):
    """
    Finite-sum DSF with exact bandlimiting.
    """
    n = np.arange(int(sr * duration))
    theta = 2 * np.pi * fc * n / sr
    beta  = 2 * np.pi * fm * n / sr
    
    sin_t   = np.sin(theta)
    sin_t_b = np.sin(theta - beta)
    cos_b   = np.cos(beta)
    
    aN1 = a**(N+1)
    sin_t_N1b = np.sin(theta + (N+1)*beta)
    sin_t_Nb  = np.sin(theta + N*beta)
    
    denom = 1 + a*a - 2*a * cos_b
    numer = sin_t - a*sin_t_b - aN1*(sin_t_N1b - a*sin_t_Nb)
    
    signal = np.divide(numer, denom, out=np.zeros_like(numer), where=denom != 0)
    norm = (1 - a) / (1 - a**(N+1))
    return signal * norm

def dsf_two_sided(fc, fm, a, N, duration, sr=44100):
    """
    Two-sided symmetric DSF.
    """
    n = np.arange(int(sr * duration))
    theta = 2 * np.pi * fc * n / sr
    beta  = 2 * np.pi * fm * n / sr
    
    cos_b = np.cos(beta)
    sin_t = np.sin(theta)
    
    aN1 = a**(N+1)
    cos_N1b = np.cos((N+1)*beta)
    cos_Nb  = np.cos(N*beta)
    
    denom = 1 + a*a - 2*a * cos_b
    numer = sin_t * (1 - a*a - 2*aN1*(cos_N1b - a*cos_Nb))
    
    return np.divide(numer, denom, out=np.zeros_like(numer), where=denom != 0)

def dsf_complex_stereo(fc, fm, a, N, duration, sr=44100):
    """
    Quadrature-stereo DSF: returns (left, right) ndarrays.
    """
    n = np.arange(int(sr * duration))
    u = 2 * np.pi * fc * n / sr
    v = 2 * np.pi * fm * n / sr
    
    # Complex phasor method: c = e^{ju} * (1 - (a*e^{jv})^{N+1}) / (1 - a*e^{jv})
    ejv  = np.cos(v) + 1j * np.sin(v)
    num  = 1.0 - (a * ejv)**(N+1)
    den  = 1.0 - a * ejv
    ratio = np.divide(num, den, out=np.zeros_like(num), where=den != 0)
    
    eju  = np.cos(u) + 1j * np.sin(u)
    c = eju * ratio
    
    left  = np.real(c)
    right = np.imag(c)
    
    norm = (1 - a) / (1 - a**(N+1))
    return left * norm, right * norm

def dsf_note(f0, a, brightness, duration, sr=44100):
    """
    High-level note generator. Maps MIDI-style parameters to DSF.
    brightness ∈ [0,1] maps to N and fm/fc ratio.
    """
    fc = f0  # fundamental = center freq
    # Brightness controls partial count and rolloff
    N = int(brightness * 40) + 1  # 1 to 41 partials
    a_eff = 0.3 + brightness * 0.55  # 0.3 to 0.85
    # Harmonic: fm = fc
    fm = fc
    # Clamp N to bandlimit
    Nmax = int((sr/2 - fc) / fm)
    N = min(N, Nmax)
    
    return dsf_finite(fc, fm, a_eff, N, duration, sr)
```

### 2.10 Complexity Summary

| Form | Trig Calls/Sample | Arith Ops/Sample | Memory |
|---|---|---|---|
| Infinite DSF | 3 (or 0 with phasor) | ~8 | 0 bytes (no table) |
| Finite DSF | 5 (or 0 with phasor) | ~12 | 0 bytes |
| Two-sided DSF | 5 (or 0 with phasor) | ~10 | 0 bytes |
| Complex stereo DSF | 0 (phasor only) | ~10 | 0 bytes |

All forms run at $\mathcal{O}(1)$ per sample irrespective of $N$, with zero oversampling and zero wavetable storage.

---

## 3. Musical Elements Framework

### PITCH
The fundamental pitch is set directly by the center frequency $f_c$. For harmonic DSF ($f_c = f_m$), the partial series is $f_c, 2f_c, 3f_c, \dots$, giving a clean pitch at $f_c$. For inharmonic DSF ($f_c/f_m \notin \mathbb{Q}$), the pitch perception is weaker as energy is distributed across inharmonic partials — useful for bell, gong, and metallic textures where pitch is ambiguous. Pitch bending over a note's duration is achieved by linearly sweeping $f_c$ from a start to end frequency; the spectrum glides smoothly since $f_m$ tracks $f_c$ proportionally (if the $f_c/f_m$ ratio is held constant).

### RHYTHM
DSFS is a pitched continuous synthesis engine — rhythm is supplied entirely by the note-event schedule from the UnitMatrix. Each note onset triggers a DSF buffer; the attack transient is the abrupt start of the waveform (unless shaped by a ramp envelope). Rhythmic articulation is achieved through:
- **Staccato**: short durations with fast attack/release ramps (1–2 ms)
- **Legato**: overlapping note releases (connect $k$-th note release to $k{+}1$ note onset)
- **Accent**: higher velocity scales amplitude; also can increase $a$ (brightness boost on accents)
- **Tremolo**: LFO modulation of post-DSF gain at 4–12 Hz

### HARMONY
A single DSF oscillator is monophonic. Polyphony is achieved by summing multiple oscillators (one per UnitMatrix voice). The harmonic relationship between voices is determined by their $f_c$ ratio (e.g., $f_{c2} = 1.5 f_{c1}$ for a fifth, $f_{c2} = 1.25 f_{c1}$ for a major third). Within a single DSF oscillator, the partial structure $f_c + k f_m$ can be tuned to produce internal harmonies: setting $f_m = f_c / 3$ yields partials at $f_c, \frac{4}{3}f_c, \frac{5}{3}f_c, \dots$ — a chord-like spectrum. This is a form of spectral harmony where component partials align to chord tones.

### STRUCTURE
Macro-form is a section-wise schedule of DSF parameter sets:
- **Intro**: low $a$ (muted), low $N$, $f_c = f_m$ (harmonic)
- **Build**: increase $a$ (brighter), increase $N$ (richer)
- **Climax**: high $a$ (near 0.95), large $N$, two-sided form for maximum spectral density, possible inharmonic $f_c/f_m$ for tension
- **Release**: transition back to low $a$, harmonic

Parameter interpolation across section boundaries uses linear trajectories: $a(t)$, $f_c(t)$, $f_m(t)$ swept across the boundary region. $N$ is morphed by crossfading two DSF oscillators with different $N$.

### TEXTURE
DSFS textures are defined by spectral density (product of voice count and $N$), spectral rolloff ($a$), and spectrum type:
- **One-sided**: bright, focused, with energy skewed upward from $f_c$
- **Two-sided**: dense, symmetric, more "filled" texture
- **Infinite-sum**: smooth rolloff, natural hi-cut behavior
- **Quadrature-stereo**: wide, enveloping texture with no explicit stereo processing

Texture evolution: increase $a$ and $N$ over time for tension; switch from one-sided to two-sided for expansion; add inharmonicity for increasing dissonance.

---

## 4. UnitMatrix Integration

### Voices
Each UnitMatrix voice maps to one DSF oscillator with per-voice parameters $(f_c^{(v)}, f_m^{(v)}, a^{(v)}, N^{(v)})$:

- **Lead Voice** (v=0): Harmonic DSF, $f_c = f_m = f_0$, $a=0.6$–0.8, $N$ = bandlimited
- **Bass Voice** (v=1): Harmonic DSF, $f_c = f_m = f_0/2$ or $f_0/4$, $a=0.8$–0.9 (rich low-end), $N$ = 5–10 (fundamental-heavy)
- **Pad Voice** (v=2): Two-sided or quadrature DSF, $f_c = f_0 \cdot r$ (e.g., $r=2$ for octave pad), $f_m$ set for chord spread
- **Percussion Voice** (v=3): Inharmonic DSF, $f_c/f_m = \sqrt{2}$, $a$ near 1, moderate $N$, short duration

The produce workflow iterates each voice's MusicUnits, renders each note as a DSF buffer, applies the note velocity as amplitude scaling, concatenates segments with per-note ramp envelopes, and sums all voices to the stereo output bus.

### Sections
Each section $m$ defines a base parameter set $(f_c^{(m)}, f_m^{(m)}, a^{(m)}, N^{(m)})$. Parameter trajectories between sections use per-note linear interpolation of continuous parameters:

$$p[n] = p_{m-1} + (p_m - p_{m-1}) \cdot \frac{n - n_{m-1}}{n_m - n_{m-1}}$$

where $p \in \{a, f_c, f_m\}$. $N$ interpolation requires crossfade between two DSF oscillators at different $N$ with a fade parameter $\lambda \in [0,1]$:

$$x[n] = \sqrt{1-\lambda}\, x_{N_1}[n] + \sqrt{\lambda}\, x_{N_2}[n] \quad (\text{equal-power crossfade})$$

### Cell Filling
Each cell (voice $v$, section $m$) contains a MusicUnit with 0..K note events. Rendering maps:
1. MIDI pitch $\to$ $f_c = 440 \cdot 2^{(p-69)/12}$
2. Set $f_m$ from section's $f_c/f_m$ ratio: $f_m = f_c / r_m$
3. Look up $(a, N)$ from voice+section timbre map
4. Generate DSF buffer for `duration` samples
5. Apply ramp envelopes (linear attack 2 ms, release 5 ms)
6. Place at onset tick in voice output track

Zero-drift: each note's buffer equals its MIDI duration in samples. Per-voice output sums to section tick count, preserving the UnitMatrix equal-length invariant.

---

## 5. Parameter Space & Sound Examples

| $a$ | $f_c/f_m$ | $N$ | Timbre Description |
|---|---|---|---|
| 0.0 | any | any | Pure sine (carrier only) |
| 0.3 | 1 (harmonic) | 10 | Muted fundamental, soft upper harmonics — flute-like |
| 0.6 | 1 (harmonic) | 20 | Bright harmonic, moderate rolloff — reed/organ |
| 0.85 | 1 (harmonic) | 40 | Rich harmonic, slow decay — brass-like |
| 0.9 | $\sqrt{2}$ (inharmonic) | 30 | Metallic, bell-like: inharmonic partials |
| 0.95 | $\pi/2$ (inharmonic) | 25 | Clangorous, gong-like: dense inharmonic |
| 0.7 | 0.5 (subharmonic) | 15 | Growling: $f_c$ below $f_m$, emphasis on lower partials |
| 0.5 (two-sided) | 1.5 | 10 | Symmetric sidebands: $f_c \pm k f_m$, hollow/phasey texture |
| 0.65 (quadrature) | 1 | 20 | Wide stereo: 90° phase offset per partial/spacious |

---

## 6. Pitfalls & Mitigations

1. **Denominator singularity**: $1 + a^2 - 2a\cos\beta = 0$ when $a=1$ and $\beta=0$. At $\beta=0$, both numerator and denominator vanish — the expression is indeterminate $0/0$. Detect $|\beta| < \epsilon$ (e.g., $10^{-10}$) and substitute the L'Hôpital limit:
   - Finite DSF: $x[n] = \sin\theta \cdot (N+1)$ when $\beta = 0$
   - Infinite DSF: $x[n] = \sin\theta / (1-a)$ when $\beta = 0$
   
   Also guard $a \geq 1$ for infinite form (diverges) and $a < 0$ (spectral inversion, usable but counterintuitive).

2. **Numerical underflow of $a^{N+1}$**: For $a=0.5$, $N > 1075$ causes $a^{N+1} < 10^{-324}$ (double-precision underflow). The effective $N$ saturates; detect and clip or switch to infinite-sum form (which assumes $a^{N+1}=0$ — physically correct in this regime).

3. **Adaptive bandlimiting**: DSFS is alias-free only if $f_c + N f_m < f_s/2$. Always enforce $N_{\max} = \lfloor (f_s/2 - f_c) / f_m \rfloor$. For the infinite-sum form, monitor the $-60\text{dB}$ bandwidth and reduce $a$ if too much high-frequency energy aliases at audible levels.

4. **Boundary clicks**: Abrupt DSF waveform onset/offset creates clicks. Apply 1–5 ms ramp envelopes. Phase-continuous parameter changes (sweeping $f_c$, $a$) should be interpolated across a few samples to suppress zipper noise. The phasor-recurrence variant must reset $z_c, z_m$ at each new note to prevent phase discontinuity.

5. **Static timbre**: Unmodulated DSF at fixed parameters sounds synthetic/static. Mitigations: 
   - ADSR envelope on $a$ (brightness swell)
   - LFO on $f_m$ (vibrato-like shimmer)
   - Crossfade between two DSF streams at different $a$ (evolving brightness)
   - Additive layering with SP-029 subtractive or SP-016 granular for textural complexity

6. **Relation to existing methods**: DSFS is the algebraic-spectral sibling of SP-010 FM, SP-019 Chebyshev Waveshaping, SP-039 IFFT Additive, and SP-041 Wavetable. It fills the gap: closed-form, alias-free, variable-bandwidth spectra with explicit partial-amplitude control and zero wavetable memory. Do not use DSFS where SP-029 subtractive (analog filter emulation) or SP-016 granular (time-domain cloud texture) would be more appropriate — DSFS excels at precise, repeatable, clean spectral design.

---

## 7. References

1. Moorer, J. A. (1976). "The Synthesis of Complex Audio Spectra by Means of Discrete Summation Formulae." *Stanford CCRMA Report STAN-M-5*, Stanford University.

2. Moorer, J. A. (1978). "The Synthesis of Complex Audio Spectra by Means of Discrete Summation Formulae." *Journal of the Audio Engineering Society*, 67(2), 25–36. (Journal reprint of the STAN-M-5 report.)

3. Chowning, J. M. (1973). "The Synthesis of Complex Audio Spectra by Means of Frequency Modulation." *Journal of the Audio Engineering Society*, 21(7), 526–534. (DSFS context: the method Moorer was generalizing.)

4. Jolley, L. B. W. (1961). *Summation of Series*. Dover Publications. (Contains the trigonometric series identity used in DSF.)

5. Burkhard (2022). "The Math behind DSF Synthesis." *Moppel's Limited Synths*. Online resource detailing complex quadrature DSF for the Tetra and Sonitarium synthesizers: https://www.verklagekasper.de/synths/dsfsynthesis/dsfsynthesis.html

6. Stilson, T. & Smith, J. (1996). "Alias-Free Digital Synthesis of Classic Analog Waveforms." *CCRMA*. (DSF-related alias-free oscillator design.)

7. Mathews, M. V. (1969). *The Technology of Computer Music*. MIT Press. (Context: MUSIC V and the first digital synthesis implementations that DSFS was designed for.)

8. Zwicker, E. & Scharf, B. (1965). "A Model of Loudness Summation." *Psychological Review*, 1, 3–26. (References in Moorer for loudness normalization.)

9. Kritov, A. (2002). "Discrete Summation Formula (DSF)." *MusicDSP*. Implementation notes and code: https://www.musicdsp.org/en/latest/Synthesis/68-discrete-summation-formula-dsf.html