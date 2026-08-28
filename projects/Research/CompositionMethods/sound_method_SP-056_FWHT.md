# Walsh Function Synthesis — Method SP-056 (FWHT)

> **Layer**: Synthesis Engines · **Target**: Reedy / Hollow / Chiptune Square-Wave Timbres
> **One-liner**: Additive synthesis in the **sequency domain** — decompose a periodic waveform into a sum of Walsh functions (binary $\pm 1$ square waves) via the Fast Walsh–Hadamard Transform, an $\mathcal{O}(N\log N)$ butterfly that needs *zero multiplications*. Beauchamp's brightness $B = \sum n|a_n| / \sum |a_n|$ is a one-knob timbre morph. The Casio VL-Tone VL-1 lineage.

---

## 1. Core Idea

Ordinary additive synthesis expands a waveform in the **sine** (frequency) basis:

$$x(t) = \sum_{k} a_k \sin(2\pi k f_0 t).$$

Walsh Function Synthesis (SP-056) expands it in the **Walsh** (sequency) basis instead:

$$x(t) = \sum_{n=0}^{N-1} a_n \,\mathrm{WAL}(n,\; f_0 t),$$

where $\mathrm{WAL}(n,\theta)$ is the $n$-th Walsh function — a square wave taking only $\pm 1$, switching sign at dyadic sub-intervals — and $n$ counts its **sequency** (zero-crossings per period), *not* Hz. Three facts drive the method:

1. **Sequency replaces frequency** — the coefficient index counts zero-crossings, so the timbre's "harmonic structure" lives in the distribution of energy across square-wave atoms.
2. **Brightness is one number** — the sequency centroid $B=\sum n|a_n|/\sum|a_n|$ is the perceptually dominant timbre parameter (Beauchamp 1982); a whole timbre morphs with one scalar.
3. **The engine is multiplier-free** — the FWHT butterfly uses only additions/subtractions, and resynthesis is a phase accumulator plus a table read.

The result is a family of *square-wave-derived* timbres — hollow clarinet/reed tones, organ stops, chiptune/8-bit digital color — distinct from the smooth sine timbres of SP-039 and the filtered analog timbres of SP-029.

---

## 2. Mathematical Mechanics

### 2.1 Rademacher and Walsh functions

Let $t \in [0,1)$ with binary expansion $t = \sum_k t_k 2^{-(k+1)}$, $t_k \in \{0,1\}$. The Rademacher functions are the fundamental square waves:

$$r_k(t) = \mathrm{sign}\big(\sin(2^{k+1}\pi t)\big) = (-1)^{t_k}.$$

Walsh functions in **Paley ordering** are products of Rademacher functions weighted by the bits of the index $n = \sum_k n_k 2^k$:

$$\mathrm{WAL}_P(n,t) = \prod_k r_k(t)^{n_k} = (-1)^{\sum_k n_k t_k}.$$

In **sequency (Hadamard/Walsh) ordering** the functions are re-indexed so $\mathrm{WAL}(n,t)$ has exactly $n$ (or $\lceil n/2\rceil$) zero-crossings per period — the square-wave analogue of "the $n$-th harmonic." Low sequency = slow square wave = fundamental/octave-like content; high sequency = fast switching = bright/noise-like content.

### 2.2 The Sylvester–Hadamard matrix

For $N = 2^m$, the $N\times N$ Sylvester–Hadamard matrix is built by Kronecker recursion:

$$H_1 = [1], \qquad H_{2N} = \begin{bmatrix} H_N & H_N \\ H_N & -H_N \end{bmatrix}.$$

Every entry is $\pm 1$, the rows are the $N$ Walsh functions sampled at $N$ dyadic points, and $H_N H_N^T = N I$ (orthogonal). The Walsh coefficients of a length-$N$ sample vector $\mathbf{x}$ are

$$\mathbf{a} = \tfrac{1}{N} H_N \mathbf{x}.$$

### 2.3 The Fast Walsh–Hadamard Transform (FWHT)

Because $H_N$ is $\pm 1$-valued, the transform is an **add-only butterfly** — identical in shape to the FFT but with twiddle factors replaced by $\pm 1$. The in-place butterfly:

```
for h in [1, 2, 4, ..., N/2]:
    for each block of size 2h:
        a, b = x[j], x[j+h]
        x[j], x[j+h] = a + b, a - b
x /= N
```

Cost: $\mathcal{O}(N \log N)$ additions and subtractions, **zero multiplications**.

### 2.4 Resynthesis (inverse transform)

Since $H_N^{-1} = \tfrac{1}{N} H_N$, the inverse is the forward transform up to scale:

$$x[n] = \sum_{k=0}^{N-1} a_k \,\mathrm{WAL}(k, n/N) = \big(H_N \mathbf{a}\big)_n .$$

For time-varying synthesis at fundamental $f_0$, a phase accumulator runs

$$\phi[n] = \phi[n-1] + N f_0 / f_s \pmod N,$$

and the output sample is

$$y[n] = \sum_{k} a_k \, s_k\big[\lfloor \phi[n] \rfloor\big],$$

where $s_k[j] = H_N[k,j] \in \{\pm 1\}$. Equivalently precompute the single weighted column $\mathbf{w}[j] = \sum_k a_k H_N[k,j]$ once ($\mathcal{O}(N^2)$ offline), then $y[n] = \mathbf{w}[\lfloor\phi[n]\rfloor]$ — **a phase accumulator plus one table read**, the cheapest possible additive oscillator.

### 2.5 Brightness (Beauchamp 1982)

The perceptually dominant timbre parameter is the sequency-domain spectral centroid:

$$B = \frac{\sum_n n\,|a_n|}{\sum_n |a_n|}.$$

Beauchamp's procedure: (i) analyze a target tone, (ii) keep the Walsh coefficient *magnitudes* $|a_n|$ (discard signs — phase is perceptually secondary), (iii) tilt/flatten the magnitude spectrum so its centroid equals a desired $B$, (iv) resynthesize. This gives a **one-knob brightness control** — the sequency analogue of a subtractive filter cutoff, but achieved *inside* the additive engine with no filter.

### 2.6 Anti-aliasing / band-limiting

Walsh functions are square waves, so each term carries an infinite set of odd harmonics and aliases when $\eta f_0$ approaches Nyquist. Band-limit by **sequency truncation** (keep only the $K < N$ lowest-sequency terms) and/or choose $N$ an integer sub-multiple of $f_s$ so the highest term's fundamental stays below Nyquist.

**Complexity**: FWHT analysis $\mathcal{O}(N\log N)$ add-only; offline table build $\mathcal{O}(N^2)$; real-time resynthesis $\mathcal{O}(1)$ per sample (table read) or $\mathcal{O}(K)$ (on-the-fly sum).

---

## 3. Python / NumPy Implementation

```python
import numpy as np

def fwht(x):
    """Fast Walsh-Hadamard transform (add-only butterfly). Returns N coeffs."""
    x = np.asarray(x, dtype=np.float64).copy()
    N = x.shape[0]
    assert (N & (N - 1)) == 0, "N must be a power of 2"
    h = 1
    while h < N:
        x = x.reshape(-1, h << 1)
        x[:, :h], x[:, h:] = x[:, :h] + x[:, h:], x[:, :h] - x[:, h:]
        x = x.reshape(-1)
        h <<= 1
    return x / N

def walsh_matrix(n):
    """Rows = Walsh functions in sequency (Hadamard) order, N x N, +-1."""
    # Build Sylvester-Hadamard by recursion, then Gray-code reorder rows.
    H = np.array([[1.0]])
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    m = int(np.log2(n))
    gray = np.arange(n) ^ (np.arange(n) >> 1)   # binary -> Gray code
    return H[gray]

def analyze_walsh(waveform, n):
    """Walsh (sequency) coefficients of one period of `waveform(t)`."""
    t = np.linspace(0.0, 1.0, n, endpoint=False)
    return fwht(waveform(t))

def brightness(a):
    """Sequency-domain spectral centroid (Beauchamp's brightness)."""
    n = np.arange(len(a))
    return float(np.sum(n * np.abs(a)) / (np.sum(np.abs(a)) + 1e-12))

def brightness_match(a, B_target, iters=40):
    """Tilt the Walsh magnitude spectrum so its centroid == B_target."""
    n = np.arange(len(a))
    amag = np.abs(a)
    alpha = 0.0
    for _ in range(iters):
        w = amag * (n + 1.0) ** alpha
        Bk = np.sum(n * w) / (np.sum(w) + 1e-12)
        alpha += 0.1 * (B_target - Bk) / (B_target + 1e-12)
    return np.sign(a) * amag * (n + 1.0) ** alpha

def synthesize(a, f0, fs, dur):
    """Resynthesize a tone at f0 from Walsh coefficients a (N = 2^m)."""
    N = len(a)
    W = walsh_matrix(N)
    w = W.T @ a                                  # weighted column, O(N^2) offline
    nsamp = int(fs * dur)
    phase = (np.arange(nsamp) * N * f0 / fs).astype(np.int64) % N
    return w[phase]

def render_note(a, f0, fs, dur, env):
    """Resynthesize + apply a per-note amplitude envelope."""
    y = synthesize(a, f0, fs, dur)
    t = np.arange(len(y)) / fs
    return y * env(t)
```

**Tooling**: NumPy for the butterfly/table build; `scipy.linalg.hadamard` can replace the recursive build (add the Gray-code reorder). The transform is add-only, so it JIT-compiles with Numba or ports to a microcontroller trivially. The musicom engine handles UnitMatrix fill + zero-drift MIDI export upstream; SP-056 consumes per-note $f_0$/duration and emits a mono buffer (or embeds as a FluidSynth-style tone generator).

---

## 4. Musical Elements Framework

- **PITCH** — entirely from the phase-accumulator rate $\Delta\phi = N f_0/f_s$, decoupled from the coefficient vector $\mathbf{a}$ (which carries only timbre). Free microtuning; vibrato = slow rate modulation.
- **RHYTHM** — envelopes gate the coefficient sum; a *brightness envelope* $B(t)$ per onset makes attacks brighter than releases (sequency analogue of a filter sweep). Single-table-read engine handles dense rhythmic clouds without CPU spikes.
- **HARMONY** — the sequency spectrum $\{|a_n|\}$ and brightness $B$ *are* the harmonic content, in the square-wave basis. Matching $B$ across voices fuses a chord into one color; spreading $B$ stratifies it.
- **STRUCTURE** — macro-form = the **brightness trajectory** $B(s)$ per section + coefficient-vector switching. Section A dark, B bright, A′ dark with a different set; a slow $B$ ramp = continuous timbral crescendo.
- **TEXTURE** — retained-term count $K$ and sequency distribution set "squareness": few low-sequency terms = clean hollow clarinet/chiptune; many high-sequency = bright gritty near-noise. Per-voice $B$/$K$ give stratified rows; add-only engine scales to dense polyphony.

---

## 5. UnitMatrix Integration

- **Rows (Voices)** — each voice $v$ owns a coefficient vector $\mathbf{a}_v$ + brightness $B_v$, its own phase accumulator. Lead = high-$B$ square lead; bass = low-$B$ dark reed; pad = few-term organ stop with slow $B$ LFO; percussion = high-sequency burst (fast decay). Each row → mono buffer → summed or spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)** — each section prescribes $B_s$ + coefficient-set index → timbral macro-form; continuous $B$ crossfade at joins = smooth morph.
- **Cells** $U_{v,s}$:
  - `{PITCH}`: MIDI pitch → per-cell $f_0$ into the accumulator.
  - `{HARMONY}`: per-cell brightness $B_{v,s}$ + retained-term count $K_{v,s}$.
  - `{RHYTHM}`: note on/off + velocity → amplitude envelope gating the sum.
  - `{TEXTURE}`: coefficient-vector selection + per-cell $B$/$\mathbf{a}$ interpolation for morphing.
- **Flow**: fill matrix → validate zero-drift → export MIDI (musicom) → load per-voice Walsh spectra → render each cell (accumulator + table + envelope + brightness) → sum → post-process (SP-007 EQ, SP-008 DRC) → spatialize.

---

## 6. Pitfalls

1. **Aliasing from square-wave atoms** → high-sequency term at high $f_0$ aliases. Fix: sequency-truncate ($\eta_{\max}f_0 < f_s/2$), integer-sub-multiple $N$, or PolyBLEP edges.
2. **Sequency vs frequency confusion** → index $n$ counts zero-crossings, not Hz. Never map MIDI pitch to the index; pitch is the accumulator rate only.
3. **Ordering mismatch** → Paley vs sequency (Hadamard) vs Cal–Sal give different index↔function maps. Fix: one ordering end-to-end (Gray-code permutation).
4. **Brightness-tilt divergence** → zero entries in the magnitude spectrum destabilize the search. Fix: `+1` floor, capped iterations, clamped $B$.
5. **Phase discard loses transients** → magnitude-only trick is fine for sustain, wrong for attacks. Fix: keep signs for percussive material.
6. **Inherently hollow/reedy** → $\pm1$ basis can't do smooth/sine warmth. Fix: use SP-056 for its native color; blend SP-039/SP-029 for smoothness.
7. **Table-lookup quantization** → integer phase index steps at low $N$. Fix: large $N$ (256–1024) or linear column interpolation.
8. **Naive per-sample Python sum** → $\mathcal{O}(KN)$ slow. Fix: precompute $\mathbf{w}[j]$ and do one `w[phase]` gather.

---

## 7. Comparison

| Method | Basis atom | Coefficient domain | Multipliers | Brightness control | Timbre |
|---|---|---|---|---|---|
| IFFT Additive (SP-039) | Sine | Frequency | Yes (complex) | Filter envelope | Smooth, clean |
| Subtractive (SP-029) | Saw/square → filter | Frequency (post-filter) | Yes | Filter cutoff | Warm analog |
| FM/PM (SP-010/017) | Phase sidebands | $J_n(\beta)$ lattice | Yes | Mod index | Bell, brass, digital |
| GENDYN (SP-035) | Random breakpoints | None (stochastic) | Yes | Density/amplitude | Evolving, non-periodic |
| **Walsh (SP-056)** | **Square wave ($\pm1$)** | **Sequency** | **None (add-only)** | **Centroid $B$** | **Reedy, hollow, chiptune** |

---

## 8. References

- Walsh, J. L. (1923). "A Closed Set of Normal Orthogonal Functions." *American Journal of Mathematics* 45(1), 5–24.
- Rademacher, H. (1922). "Einige Sätze über Reihen von allgemeinen Orthogonalfunktionen." *Mathematische Annalen* 87, 112–138.
- Beauchamp, J. W. (1982). "Synthesis by Spectral Amplitude and 'Brightness' Matching of Analyzed Musical Instrument Tones." *Journal of the Audio Engineering Society* 30(6), 396–406.
- Beauchamp, J. W. (1984). *Applications of Walsh and Related Functions: With an Introduction to Sequency Theory.* Academic Press.
- Hadamard, J. (1893). "Résolution d'une question relative aux déterminants." *Bulletin des Sciences Mathématiques* 17, 240–246.
- Casio (1981). *VL-Tone VL-1 Service Manual.* (Walsh-function tone generator.)
- Harmuth, H. F. (1970). *Transmission of Information by Orthogonal Functions.* Springer.
- Smith, J. O. (2010). *Physical Audio Signal Processing.* W3K Publishing.
