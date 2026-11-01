# Sound Production Method SP-130 — Colored Noise Synthesis (CNS)

**ID:** SP-130 · **Acronym:** CNS · **Layer:** absolute (sound production — LAYER_ARCHITECTURE.md)
**Category:** Synthesis Engines (pitch-less noise-texture generator)
**Candidate code path:** `sound/generators/complex_noise.py` (exists — extend) → full engine `sound/synthesis/noise_synthesis.py`
**Dispatch:** `workflows/musicom_workflow.py::produce(method="SP-130", params={...})`
**Status:** documented + numerically verified 2026-11-01 (NumPy 2.x / SciPy, 48 kHz, 8 s buffers; script `projects/Research/outputs/sp130_research/verify_sp130_cns.py`)

---

## 1. One-line definition

A synthesis engine that generates pitch-less texture with a controllable power-law spectral slope
$S(f) \propto f^{-\gamma}$ — white ($\gamma{=}0$), pink ($\gamma{=}1$), brown ($\gamma{=}2$),
blue ($\gamma{=}{-}1$), violet ($\gamma{=}{-}2$), and exact arbitrary $1/f^\alpha$ — via four
generator families (Voss–McCartney, Paul Kellet 3-cascade, leaky-cumsum/differencers, FFT
powernoise), deterministic per seed and sample-count preserving (zero-drift safe).

---

## 2. Why CNS is not one of the existing methods

| Method | Generates noise? | Kind |
|---|---|---|
| SP-109 SG-ANR | **removes** noise | spectral gating |
| SP-035 GENDYN | stochastic *breakpoints* | pitched-capable waveform synthesis |
| SP-057 Chua | chaotic ODE, 1/f *emergent* | self-oscillating circuit |
| SP-068 Bytebeat | integer expressions | pitched chip timbre |
| SP-087 / SP-089 | noise inside *drum voices only* | 808 snare/cymbal circuits |
| SP-120 PhISEM | particles → resonators | shaken-percussion beds |
| SP-016 Granular | grains of *existing* audio | time/pitch scattering |
| **SP-130 CNS** | **raw colored noise, any slope** | **pitch-less texture engine** |

No entry in the DB generates colored noise as a first-class, parameterized timbre. The DB
itself names the gap: SP-109 is noise *reduction*, SP-087 uses "violet noise" (a
*differentiator*), SP-128 remarks that recombined EMD noise modes make "a colored noise bed
with the colour of the source" — without a color engine to synthesize one. CNS is that engine.

---

## 3. The color taxonomy (technical mechanics)

For a stationary noise process with power spectral density $S(f)$, the **color** is the
power-law exponent $\gamma$ in $S(f)\propto f^{-\gamma}$; in dB/octave the slope is $-3\gamma$.

| Color | $\gamma$ | dB/oct | PSD | Typical use |
|---|---|---|---|---|
| White | $0$ | $0$ | flat | sibilance, air, snare hiss, masking fill |
| Pink | $1$ | $-3$ | $1/f$ | wind, rain, ocean, body bed — **equal energy per octave** |
| Brown/red | $2$ | $-6$ | $1/f^2$ | thunder, sea swell, sub rumble, impacts |
| Blue | $-1$ | $+3$ | $f$ | waterfall, fizz, sparkle |
| Violet | $-2$ | $+6$ | $f^2$ | 808 snare "violet" hiss, sibilance extreme |
| Grey | — | — | ISO-226-shaped | perceived-flat test signal, ambience |

### 3.1 White
$$x[n] \sim \mathcal{U}(-1,1)\quad\text{or}\quad x[n]\sim\mathcal{N}(0,\sigma^2).$$
Every other color is a filter, sum, or difference of white.

### 3.2 Pink — Voss–McCartney (octave-stream sum)
$M$ independent streams; stream $j$ is re-randomized every $2^j$ samples:
$$y[n]=\sum_{j=0}^{M-1} s_j[n],\qquad s_j[n]=\begin{cases}\mathcal{U}(-1,1) & n\equiv 0\pmod{2^j}\\ s_j[n-1] & \text{otherwise}\end{cases}$$
Low-$j$ streams refresh fast (high-frequency content), high-$j$ streams refresh slowly
(low-frequency content); the octave-staircase superposition approximates $1/f$. Variance of
$M$ uniform streams is $M/3$ → normalize by $\sqrt{M/3}$. Standard $M=16$; spectral ripple
≈ ±1 dB (Allan Herriman's analysis, firstpr.com.au). Trammell's stochastic variant (random
stream selection instead of fixed $2^j$) smooths the ripple.

### 3.3 Pink — Paul Kellet 3-cascade one-pole filter
Three leaky integrators summed with a flat trim:
$$y_k[n]=b_k\,y_k[n-1]+a_k\,x[n],\quad
b=(0.99765,\,0.96300,\,0.57000),\quad a=(0.0990460,\,0.2965164,\,1.0526913)$$
$$y[n]=y_0[n]+y_1[n]+y_2[n]+0.1848\,x[n]$$
Unconditionally stable (all poles < 1), $O(1)$ per sample, streaming-friendly.
**Pitfall:** the precomputed 4-tap block form (b0..b4/a0..a4, a0≈0.0555) is numerically
fragile — verified overflow → NaN in float64 direct form. Use the cascade.

### 3.4 Brown/red — leaky random walk
$$y[n]=\alpha\,y[n-1]+x[n],\qquad \alpha=0.999,\quad y\leftarrow y-\overline{y}$$
The leak bounds the DC wander (an un-leaked cumsum walks to ±inf); remove the mean.

### 3.5 Blue / violet — differencers
$$y[n]=x[n]-x[n-1]\ (\text{blue}),\qquad y[n]=x[n]-2x[n-1]+x[n-2]\ (\text{violet})$$
$|H(e^{j\omega})|^2=(2-2\cos\omega)^k$ gives local slopes $+1$/$+2$ near DC but flattens toward
Nyquist: measured full-band (48 kHz, 120 Hz–14 kHz) exponents −1.92 / −3.85. This is the
classic analog hiss character — the TR-808 snare's "violet noise" (SP-087) is exactly a
differentiator. For exact blue/violet use FFT $\alpha=-1/-2$.

### 3.6 Exact arbitrary $1/f^\alpha$ — FFT powernoise (Little et al. 2007)
$$X[k]=f_k^{-\alpha/2}\,e^{j\varphi_k},\quad \varphi_k\sim\mathcal{U}(0,2\pi),\quad X[0]=0,\qquad x=\mathrm{irfft}(X)$$
$\alpha=1$ pink, $2$ brown, $-1$ blue, $-2$ violet, $0$ flat. Exact exponents by construction;
block-based (non-streaming), needs crossfades at $\alpha$ changes.

### 3.7 Grey noise
Pre-filter white by the inverse ISO-226 equal-loudness contour → perceptually flat.

### 3.8 Filtered / morphing noise (the musical textures)
- **Wind** = LP pink, cutoff LFO'd at 0.05–0.3 Hz (turbulence gusting);
- **Sea** = brown + slow amplitude swell (0.05–0.15 Hz);
- **Rain** = dense short grains of HP-filtered noise (Poisson-spaced, cf. SP-016);
- **Breath** = BP noise at formant pairs (cf. SP-066 flute breath ∝ $p_m$; SP-127 aperiodicity);
- **Whisper** = BP noise at $f_0$ through an LPC envelope (SP-028);
- **Pitched noise** = BP resonator bank at chord tones → "noise choir";
- **Riser/lifter** = color sweep $\alpha(t)$ or HP cutoff sweep + exponential gain.

---

## 4. Measured verification (48 kHz, 8 s, Welch Hann 8192, log-log fit 120 Hz–14 kHz)

| Generator | Fitted $\gamma$ | Target |
|---|---|---|
| white (gaussian) | **+0.002** | 0 |
| pink Voss–McCartney 16 streams | **+1.074** | ~1 |
| pink Paul Kellet 3-cascade | **+1.030** | ~1 |
| pink FFT powernoise α=1 | **+1.000** | 1 |
| brown leaky cumsum (α=0.999) | **+1.927** | ~2 |
| brown FFT powernoise α=2 | **+2.000** | 2 |
| blue 1st diff (approx) | **−1.923** | ≈−1 (full-band) |
| blue FFT powernoise α=−1 | **−1.000** | −1 |
| violet 2nd diff (approx) | **−3.848** | ≈−2 (full-band) |
| violet FFT powernoise α=−2 | **−2.000** | −2 |
| grey (FFT α=0) | **+0.000** | 0 |

Determinism: `np.array_equal` True for same seed, False for different seed.
Sample-count preservation: every generator returns exactly $N=\lfloor f_s T\rfloor$ samples.

---

## 5. Python / NumPy implementation sketch

```python
import numpy as np
from scipy import signal
from scipy.fft import rfft, rfftfreq, irfft

FS = 48000

def rng(seed): return np.random.default_rng(seed)

def white(seed, n):
    return rng(seed).standard_normal(n)

def voss_mccartney(seed, n, streams=16):
    r = rng(seed)
    out = np.empty(n); vals = r.uniform(-1, 1, streams)
    for i in range(n):
        for j in range(streams):
            if i % (2 ** j) == 0:
                vals[j] = r.uniform(-1, 1)
        out[i] = vals.sum()
    return out / np.sqrt(streams / 3.0)

def kellet_pink(seed, n):
    x = white(seed, n)
    b = (0.99765, 0.96300, 0.57000)
    a = (0.0990460, 0.2965164, 1.0526913)
    y0 = y1 = y2 = 0.0
    out = np.empty(n)
    for i in range(n):
        w = x[i]
        y0 = b[0]*y0 + a[0]*w; y1 = b[1]*y1 + a[1]*w; y2 = b[2]*y2 + a[2]*w
        out[i] = y0 + y1 + y2 + 0.1848*w
    return out

def brown(seed, n, leak=0.999):
    x = white(seed, n)
    y = np.empty(n); acc = 0.0
    for i in range(n):
        acc = leak*acc + x[i]; y[i] = acc
    return y - np.mean(y)

def blue_diff(seed, n):
    x = white(seed, n)
    return np.diff(x, prepend=x[0])

def violet_diff(seed, n):
    x = white(seed, n)
    return np.diff(np.diff(x, prepend=x[0]), prepend=x[0])

def powernoise(seed, n, alpha):
    """Exact 1/f^alpha by FFT (Little et al. 2007)."""
    r = rng(seed)
    f = rfftfreq(n, 1.0/FS); f[0] = f[1]
    S = f ** (-alpha/2.0); S[0] = 0.0
    X = S * np.exp(1j * r.uniform(0, 2*np.pi, len(f)))
    return irfft(X, n)

def colored(seed, n, color):
    return {"white": lambda: white(seed, n),
            "pink": lambda: kellet_pink(seed, n),
            "pink_fft": lambda: powernoise(seed, n, 1.0),
            "brown": lambda: brown(seed, n),
            "blue": lambda: blue_diff(seed, n),
            "blue_fft": lambda: powernoise(seed, n, -1.0),
            "violet": lambda: violet_diff(seed, n),
            "violet_fft": lambda: powernoise(seed, n, -2.0)}[color]()

def filtered_noise(seed, n, color, ftype, fc, q=0.707, order=2):
    """Reshape a color into the musical textures (wind/breath/air)."""
    x = colored(seed, n, color)
    b, a = signal.butter(order, fc/(FS/2), ftype)
    return signal.lfilter(b, a, x)
```

Streaming note: the time-domain generators are per-sample $O(1)$ and can run inside a
render loop; `powernoise` is block-exact and must be re-rendered per section with
equal-power crossfades when $\alpha$ changes. All paths are deterministic per seed and
return exactly `n` samples → zero-drift safe, reproducible render.

---

## 6. Musical Elements Framework

- **PITCH** — pitch-less by design; pitched noise via BP resonator banks (chord-tone
  resonators = "noise choir"); Voss–Clarke: real music's pitch/loudness fluctuations are
  themselves 1/f — pink is the fluctuation statistic of living music.
- **RHYTHM** — noise is the continuous fill; rhythm enters via note-gated grains
  (velocity → gain, duration → gate), bar-multiple amplitude LFOs, and riser timing;
  `complex_noise.random_gate(density, bpm)` is the rhythmic companion.
- **HARMONY** — spectral-balance harmony: brown = sub-weight, pink = body, blue/violet =
  air; stacked colors = texture chords; scale-locked resonator banks add pitch harmony.
- **STRUCTURE** — the section color schedule is the macro-form (pink intro → brown verse →
  blue riser → white climax → pink fade); 1/f energy = natural tension arcs without notes.
- **TEXTURE** — the method *is* texture; $\alpha$ = one-knob centroid/brightness; density =
  envelope speed; rows sum additively into a layered texture stack.

## 7. UnitMatrix Integration

- **Voices = rows = noise layers.** Per-row `{color, level_db, pan, filter, seed}`;
  child seed `seed*101 + row` (humanize recipe) → per-layer reproducibility.
- **Sections = columns = color schedule.** Column $j$ sets each layer's $\alpha_j$,
  density, filter sweep, level — the texture macro-form; seams are equal-power crossfaded
  (zero-drift preserved, all layers sample-count preserving).
- **Cells = MusicUnit.** Sustained cells = beds; short cells = gated grains/impacts.
- **Dispatch:** `produce(midi_path, method="SP-130", params={"rows": [...], "columns": {...}, "block": 8192, "master_level_db": -6})`.
- **Chain order:** CNS beds → per-row filters → SP-021/SP-129 spatialization → SP-009/SP-032
  ambience → SP-008/SP-107 dynamics → SP-126 loudness → SP-122 dither. CNS is the excitation
  stage for SP-087/089 (noise drums), SP-120 (particle beds), SP-016 (granular clouds).

## 8. Pitfalls

1. Kellet block-coefficient form overflows (verified NaN) — use the 3-cascade form.
2. Differencers are not exact blue/violet (full-band −1.92/−3.85) — FFT α=−1/−2 for exact.
3. Brown needs leak + mean removal; brown/violet crest factors demand headroom discipline.
4. Voss–McCartney ripple: M≥16 streams, or Kellet/FFT for flat pink.
5. FFT powernoise is block-based — crossfade at α changes; time-domain for streaming.
6. White at high level masks/fatigues — spectral-balance stack rule (SP-007/SP-008 partners).
7. Not SP-109 (opposite direction), not SP-035/057/068/120 (see §2 table).
8. Seed discipline: unseeded noise breaks reproducible-render invariant — seed in provenance.

## 9. References

- Voss, R. F. & Clarke, J. (1975). "1/f noise in music and speech." *Nature* 258, 317–318.
- Voss, R. F. & Clarke, J. (1978). "'1/f noise' in music: music from 1/f noise." *JASA* 63, 258–263.
- Gardner, M. (1978). "Mathematical games: white and brown music." *Scientific American* 238(4), 16–32.
- Whittle, R. (1999/2006). "DSP generation of pink noise." https://www.firstpr.com.au/dsp/pink-noise/
  (Kellet 3-cascade filter; Herriman ripple analysis; Burk's Csound `pinkish`).
- Little, M. A. et al. (2007). "Fast computation of 1/f noise." *Phys. Rev. E* 76, 056706.
- Wikipedia: "Pink noise" (Generation — Voss–McCartney pseudocode), "Colors of noise".
- Voss–McCartney: J. Voss (1978) & J. McCartney (1992/94), music-dsp mailing list lineage.
