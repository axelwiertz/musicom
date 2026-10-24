# Sound Production Method SP-123 — Dynamic Convolution Synthesis (DCL)

**Layer:** absolute (sound production — Post-Processing / DSP). See LAYER_ARCHITECTURE.md.
**Candidate code path:** `sound/effects/dynamic_convolution.py` (new module), IR frames from `sound/effects/ir_designer.py`, invoked from `workflows.musicom_workflow.produce(method="SP-123")` as a post stage in `sound/render/pipeline.py`.

---

## 1. One-line description

Renders audio through a *time-varying impulse response* $h[n,k]$: the convolution kernel itself is animated by a control $\theta(t)$, implemented as partitioned block convolution (Gardner zero-latency scheme; uniform/non-uniform partitions) with per-partition anti-zipper spectrum crossfades — morphing spaces, bodies, filters and vocal tracts along a single automation curve.

## 2. What it is, and what it is not

Static convolution (SP-009) multiplies the signal's spectrum by one fixed IR for the whole render:

$$y[n] = \sum_{k=0}^{L-1} h[k]\, x[n-k] \qquad\Longleftrightarrow\qquad Y(\omega) = H(\omega)\, X(\omega)$$

Dynamic convolution lets the IR move:

$$y[n] = \sum_{k=0}^{L-1} h[n,k]\, x[n-k], \qquad h[n,k] \equiv \text{IR tap } k \text{ applied at output time } n$$

Two operational regimes, one engine:

1. **Parameter-indexed IR morphing** — a family of $M$ IR frames $h_0,\dots,h_{M-1}$ (rooms, plates, bodies, filters, vocal tracts, synthetic `ir_designer` recipes) interpolated by $\theta(t)$: $h[n,k] = \sum_i w_i(\theta(n))\, h_i[k]$.
2. **Blockwise time-varying convolution** — the IR is *replaced* per block on a partition schedule (the real-time auralization / dynamic convolution effects regime).

They unify: blockwise replacement is a very fast morph with a short crossfade.

**Not** SP-009 (static kernel), **not** SP-048 (one-time pre-convolution of an excitation for a KS loop), **not** SP-031 (magnitude-envelope morph in the STFT domain, phase re-synthesized). DCL morphs the kernel itself in the sample domain, so the IR's *phase structure* (early-reflection delays, comb geometry) morphs too — the space's geometry changes, not just its EQ.

## 3. Technical mechanics

### 3.1 Morph interpolation

With normalized weights $\sum_i w_i(\theta) = 1$:

$$h[n,k] = \sum_{i=0}^{M-1} w_i\big(\theta(n)\big)\, h_i[k]
  \qquad\Longrightarrow\qquad
  y[n] = \sum_{i=0}^{M-1} w_i\big(\theta(n)\big)\, \big(x * h_i\big)[n]$$

- Linear: $w_0 = 1-\theta,\ w_1 = \theta$.
- Equal-power: $w_0 = \cos(\tfrac{\pi}{2}\theta),\ w_1 = \sin(\tfrac{\pi}{2}\theta)$ — constant perceived loudness between energy-normalized IRs.

Three implementation choices:

| variant | cost | artifact | use |
|---|---|---|---|
| IR-domain interpolation: $\bar h = \sum w_i h_i$, convolve once | $1\times$ | IRs *interfere* inside one filter mid-fade (comb/partial beating) | room tails, forgiving material |
| Output-domain crossfade: compute $x*h_0$, $x*h_1$, crossfade outputs | $2\times$ | none (both filters pure) | short filter/body IRs |
| **Partition-spectrum interpolation**: crossfade per-partition spectra $H_{i,p}$ at block rate | $1\times$ | closest to output-domain quality; per-partition coherence preserved | **default** |

### 3.2 Partitioned block convolution (Gardner 1995)

Split the IR into $P$ partitions:

$$h[k] \to \{h_p[m]\}_{p=0}^{P-1}, \qquad
y[n] = \sum_{p=0}^{P-1} \big(x * h_p\big)[n - \Delta_p], \qquad
\Delta_p = \sum_{q<p} L_q$$

Uniform: $L_p = L$; non-uniform (Wefers 2015; Stefani/Binelli/Farina 2025): $L_p = L_0\, 2^{p}$ — only the first two small partitions sit in the latency path (latency $\approx 2L_0$) with CPU within ~1.5× of optimal uniform.

Each partial convolution is FFT block convolution (overlap-add/save), block size $B$, transform size $N = B + L_p - 1$ rounded up to a power of two. Per-block cost $O\big(P\, N \log N\big)$; per-sample $O\big(\tfrac{L_{IR}}{L_p}(B+L_p)\log(B+L_p)\big)/B$.

**Zero-latency (Gardner):** the $p=0$ partition runs as direct time-domain taps, so the wet path is sample-aligned with the dry — this is what keeps DCL compatible with the zero-drift invariant (mixing a delayed wet with live dry would comb transients and break sample alignment).

### 3.3 Dynamic update & anti-zipper crossfade

At a morph event (block boundary $b$):

$$H_p^{(b)}(\omega) \;\leftarrow\; \sum_i w_i(\theta_b)\, H_{i,p}(\omega), \qquad p = 0,\dots,P-1$$

Smoothed over $R$ samples with a first-derivative-continuous, equal-power window:

$$c(t) = \sin^2\!\Big(\frac{\pi t}{2R}\Big), \qquad t = 0,\dots,R$$

(zero derivative at both ends → no click). Tail partitions ($p$ large) update on a sparser schedule (1/4–1/8 rate) — perceptual scheduling (Wefers): the tail's fine structure is masked; only its energy envelope is audible.

### 3.4 Normalization

IR frames are equal-energy normalized before morphing: $h_i \leftarrow h_i / \|h_i\|_2$ (optionally per-octave band). Brightness-tracking morphs use **power interpolation** of magnitudes:

$$\big|H(\omega)\big| = \sqrt{w_0 |H_0(\omega)|^2 + w_1 |H_1(\omega)|^2}$$

(linear $|H|$ interpolation sags mid-fade when the spectra are disjoint).

### 3.5 Verification chain

1. Impulse in, $\theta$ frozen → output equals the interpolated IR exactly (identity test).
2. $\theta=\text{const}$ render matches SP-009 static convolution of the same IR bit-for-bit in float (partition machinery is transparent).
3. Zipper test: step $\theta$ with crossfade off → broadband click; with crossfade on → smooth seam.
4. Zero-drift: sample count identical to input, `validate()` passes, cell length in ticks preserved.

## 4. Python/NumPy implementation sketch

```python
import numpy as np

class DynamicConvolution:
    """Time-varying impulse-response convolution (morphing convolution).

    Regime 1 (offline, exact): IR-domain interpolation, direct FFT convolution.
    Regime 2 (blockwise): uniform partitioned convolution with per-partition
    spectrum crossfades — the real-time/dynamic auralization engine.
    """

    def __init__(self, ir_frames: list[np.ndarray], sr: int = 44100,
                 block: int = 1024, crossfade: int = 64, power_law: bool = True):
        # ir_frames: list of M equal-length IRs (already equal-energy normalized)
        self.frames = [np.asarray(f, dtype=np.float64) for f in ir_frames]
        self.M = len(self.frames)
        self.sr = sr
        self.B = block                      # block size
        self.R = crossfade                  # crossfade samples
        self.L = self.frames[0].size
        self.P = int(np.ceil(self.L / self.B))   # uniform partitions
        self.N = self.B + self.B - 1             # transform size (next pow2 below)
        self.N = 1 << int(np.ceil(np.log2(self.N)))
        # partition spectra of every frame: [M, P, N//2+1]
        self.H = np.zeros((self.M, self.P, self.N // 2 + 1), dtype=np.complex128)
        for i, h in enumerate(self.frames):
            hp = np.zeros((self.P, self.N))
            hp[:, :self.B] = h[: self.P * self.B].reshape(self.P, self.B)
            self.H[i] = np.fft.rfft(hp, axis=1)
        self._latches = None                # per-partition current spectrum
        self._state = None                  # overlap history

    def set_morph_position(self, theta: float):
        """Interpolate partition spectra (power law) — the morph core."""
        w = np.empty(self.M)
        if self.M == 2:
            if self.power_law:
                w[0] = np.cos(np.pi / 2 * theta)
                w[1] = np.sin(np.pi / 2 * theta)
            else:
                w[0] = 1.0 - theta
                w[1] = theta
        else:  # M>2: barycentric weights (e.g. linear on a simplex)
            t = np.clip(theta, 0.0, 1.0) * (self.M - 1)
            i = int(t); f = t - i
            w = np.zeros(self.M)
            w[i] = 1 - f
            if i + 1 < self.M:
                w[i + 1] = f
        if self.power_law and self.M == 2:
            Hm = np.sqrt(w[0] * np.abs(self.H[0]) ** 2
                       + w[1] * np.abs(self.H[1]) ** 2)
            # phase continuation: keep phase of the dominant frame
            ph = np.angle(self.H[0]) if w[0] >= w[1] else np.angle(self.H[1])
            target = Hm * np.exp(1j * ph)
        else:
            target = np.zeros_like(self.H[0])
            for i in range(self.M):
                target += w[i] * self.H[i]
        # per-partition crossfade toward target over R samples (block-granular)
        self._target = target
        self._fade = 0

    def process(self, x: np.ndarray, theta_fn=None) -> np.ndarray:
        """Blockwise overlap-add. theta_fn(n_block)->theta drives the morph."""
        x = np.asarray(x, dtype=np.float64)
        n = x.size
        y = np.zeros(n + self.L - 1)
        if self._latches is None:
            self._latches = self.H[0].copy()          # start at frame 0
            self._target = self._latches.copy()
            self._fade = self.R
        nblocks = int(np.ceil(n / self.B))
        for b in range(nblocks):
            if theta_fn is not None:
                self.set_morph_position(theta_fn(b))
            # advance crossfade toward target
            if self._fade < self.R:
                self._fade = min(self._fade + self.B, self.R)
                c = np.sin(np.pi / 2 * self._fade / self.R) ** 2
                Hs = c * self._target + (1 - c) * self._latches
            else:
                Hs = self._latches
            seg = x[b * self.B:(b + 1) * self.B]
            for p in range(self.P):
                X = np.fft.rfft(np.pad(seg, (0, self.N - seg.size)), n=self.N)
                Yb = np.fft.irfft(X * Hs[p], n=self.N)
                start = b * self.B + p * self.B
                y[start:start + self.N] += Yb[:self.N]
            if self._fade >= self.R:
                self._latches = self._target.copy()
        return y[:n]  # strict sample-in/sample-out: same length as input
```

Notes: this sketch is the blockwise engine (regime 2); regime 1 is the special case $P=1$ with the interpolated IR computed directly. For production, use the Gardner zero-latency first partition (direct time-domain taps for $p=0$), non-uniform partition sizes, and `scipy.signal.fftconvolve` for offline renders. Determinism: seed the $\theta$ curve; all FFTs are fixed-size → byte-identical re-renders.

## 5. Musical Elements Framework

- **PITCH:** linear kernel — no new pitch material from a static IR; the *motion* colors pitch: pitched IR frames (chord_body, vowel) glide formants; oscillating $\theta$ = formant vibrato; rhythmic $\theta$ = pitch-color arpeggio of one note.
- **RHYTHM:** morph rhythm (tempo-synced $\theta$: drum bus booth→hall→plate on the grid re-spaces every hit) + partition rhythm (tail update rate 1/4–1/8 = how fast the space breathes).
- **HARMONY:** IR spectrum multiplies the chord spectrum; morphing moves harmonic emphasis (formant bands/comb notches) with zero IMD — linearity means harmonic *motion* without intermodulation dirt.
- **STRUCTURE:** the morph curve is a macro-form; section-scoped targets (intro booth → verse room → chorus cathedral), crossfade spanning seams; repetition = returning to a previous $\theta$ (a previous space).
- **TEXTURE:** texture "bloom" (tails swelling tight→vast), grit control (metallic↔warm), reverse-bloom percussive swells; crossfade duration is itself a texture dial (5 ms snap ↔ 1 bar bloom). Always a genuine convolution — never STFT spectral smear.

## 6. UnitMatrix Integration

- **Voices = rows:** per-voice IR family + per-voice $\theta$ trajectory; bus variant: one morphing convolution on the summed mix (dither/processing once — SP-122 rule).
- **Sections = columns:** per-column breakpoints `morph_target`, `morph_position θ`, `crossfade_samples R`, `tail_update_rate`; crossfade — never reset — carries the kernel across seams.
- **Cells = MusicUnit:** cells trigger morph events (`morph+0.25, crossfade=1 bar`). Invariants: convolution state indexed on the **absolute sample counter**, never reset at seams (reset → click, same bug class as SP-122's RNG reset); strict sample-in/sample-out → `validate()` passes, zero-drift preserved.
- **Produce dispatch:** `produce(method="SP-123")` → `sound/effects/dynamic_convolution.py` → post stage in `sound/render/pipeline.py`; deterministic per seed.

## 7. Pitfalls

1. Zipper noise on abrupt IR swap → always crossfade ≥ a few ms, $\sin^2$ window.
2. IR-domain vs output-domain crossfade is a real fork — interference vs 2× CPU; partition-spectrum interpolation is the default compromise.
3. Loudness pumping → equal-energy-normalize frames, equal-power laws, power-interpolate magnitudes.
4. Latency misaligns dry and wet → Gardner zero-latency first partition; keeps zero-drift.
5. FFT block-boundary clicks → change spectra only at block boundaries, crossfade over the overlap window.
6. Pre-echo → minimum-phase-matched frames or magnitude interpolation with phase continuation for filter-like IRs.
7. CPU blow-up → interpolate partition spectra (1× cost), schedule tails at 1/4–1/8 rate.
8. Linear magnitude interpolation dips → power interpolation $\sqrt{w_0|H_0|^2+w_1|H_1|^2}$.
9. Stereo IR desync → shared $\theta$ and shared crossfade counter for L/R pairs.
10. DCL ≠ SP-009: the frozen-$\theta$ render must match SP-009 static convolution bit-for-bit (regression test).

## 8. References

- Gardner, W. G. (1995). "Efficient Convolution without Input-Output Delay." *J. Audio Eng. Soc.* 43(3), 127–136 (also AES preprint 3897, 1994).
- Wefers, S. (2015). *Partitioned Convolution Algorithms for Real-Time Auralization.* PhD thesis, RWTH Aachen University.
- Stefani, D., Binelli, M. & Farina, A. (2025). "Improved Real-Time Six-Degrees-of-Freedom Dynamic Auralization Through Nonuniformly Partitioned Convolution." *J. Audio Eng. Soc.* DOI: 10.17743/jaes.2022.0224 (verified via Crossref 2026-10-24).
- Gaydecki, P. & Atbas, E. (2023). "Impulse Response Synthesis and Real-Time Convolution for Acoustic Instrument Emulation." *Acoustics 2023.* DOI: 10.25144/16611 (verified via Crossref 2026-10-24).
- Misic, M., Nikolov, D. & Tomasevic, M. (2016). "Analysis of CPU and GPU implementations of convolution reverb effect." *Telfor Journal* 8(2). DOI: 10.5937/telfor1602121m (verified via Crossref 2026-10-24).
- Hehmsoth, C. (2003). "Dynamic Convolution." *Keys* (German), 5/2003 — term coined; issue ref from secondary documentation.
- Native Instruments (2011). *Kontakt 5* — "Dynamic Convolution" engine; feature per release documentation (NI page redirected to Kontakt 8 at fetch 2026-10-24).
- Wikipedia: "Reverb effect" / "Convolution reverb" (fetched 2026-10-24).
