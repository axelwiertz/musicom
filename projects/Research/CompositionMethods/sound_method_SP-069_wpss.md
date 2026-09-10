# SP-069 — Wavelet Packet Spectral Synthesis (WPSS)

**Layer:** absolute (sound production)
**Category:** Synthesis Engines
**Target output:** Time-Scale Spectral Sculpting / Octave-Band Resynthesis Timbres
**Complexity:** $\mathcal{O}(N \log N)$ forward + inverse, $\mathcal{O}(N)$ memory, deterministic per seed

---

## One-line description

Decompose audio into octave-spaced, constant-Q scale bands via Mallat's discrete wavelet transform (QMF lowpass/highpass filter pair + decimation), optionally expand to a full wavelet-packet tree with Shannon-entropy best-basis selection, edit the coefficients (per-band gain = critical-band EQ, scale relabel = transposition, coefficient re-spacing = time-stretch, threshold = denoise), then recombine via the inverse transform for perfect-reconstruction spectral sculpting.

## Source

Wavelet analysis-synthesis begins with **Jean Morlet & Alex Grossmann (1984)**, the continuous wavelet transform; **Yves Meyer (1985–87)** proved smooth orthonormal wavelet bases exist. The fast invertible machinery is **Stéphane Mallat (1989)**'s multiresolution pyramid (QMF pair + dyadic decimation, $\mathcal{O}(N)$ per level). Compact filters are **Ingrid Daubechies (1988, 1992)**. Best-basis selection is **Coifman & Wickerhauser (1992)**. First musical use (scalogram) is **Kronland-Martinet, Morlet & Grossmann (1987)**.

## Technical mechanics (extended)

### QMF pair / one level

Scaling (lowpass) filter $h$ and wavelet (highpass) filter $g$ in quadrature-mirror relation $g[k]=(-1)^k h[N-1-k]$. One Mallat level:

$$a_{j+1}[n]=\sum_k h[k]\,a_j[2n-k],\qquad d_{j+1}[n]=\sum_k g[k]\,a_j[2n-k]$$

(convolution + downsample by 2). Iterate on $a$ alone $J$ times → DWT $\{a_J, d_J,\dots,d_1\}$.

### Perfect reconstruction (inverse)

$$\tilde a_j[n]=\sum_k \tilde h[k]\,a_{j+1}[(n-k)/2] + \sum_k \tilde g[k]\,d_{j+1}[(n-k)/2]$$

(upsample + filter + sum; coefficients zero at odd indices). Orthogonal/biorthogonal filters give exact reconstruction and energy conservation.

### Octave constant-Q tiling

Level-$j$ detail ≈ band $[f_s/2^{j+1}, f_s/2^j]$, center $f_j\approx 3f_s/2^{j+2}$, so $Q_j=f_j/B_j\approx 3/2$ — log-spaced, one octave per band, congruent with the ear's critical bands. Heisenberg cell: time extent $\propto 2^j$, frequency extent $\propto 2^{-j}$. Low scale = short window (transients), high scale = long window (pitch).

### Best basis (packet)

Recursively split both $a$ and $d$ (full binary tree depth $D$, $2^D$ uniform leaves ≈ STFT). Retain a node iff
$$\text{Cost}(node) > \text{Cost}(left) + \text{Cost}(right)$$
with additive Cost (Shannon entropy $\sum|c_k|^2\log|c_k|^2$, log-energy, or threshold count).

### Edit operations

- **Harmonic envelope:** $y = \mathrm{idwt}(a_J, G_J d_J,\dots,G_1 d_1)$ — one gain knob per octave = critical-band EQ.
- **Transposition:** relabel $j \to j+s$ (octave shift); semitone steps via packet leaves.
- **Time-stretch:** $d_j[n]\to d_j[\lfloor \alpha n\rfloor]$ with bandlimited interpolation.
- **Cross-synthesis morph:** $G_j=(1-\beta)G_j^A+\beta G_j^B$.
- **Denoise/sparsify:** zero $|d_j[n]|<\tau\sqrt{E_j}$ (wavelet shrinkage).

## Python/NumPy implementation sketch

```python
import numpy as np

def _symwconv(x, f):
    """Convolve x with filter f, symmetric (reflect) extension, trimmed."""
    pad = len(f) - 1
    xp = np.pad(x, (pad, pad), mode='reflect')
    y = np.convolve(xp, f, mode='valid')
    return y

def dwt_pyramid(x, h, g, J):
    """Mallat FWT -> (a_J, [d_J ... d_1]). Or array-level: full coefficient list."""
    a = x.astype(np.float64)
    details = []
    for _ in range(J):
        lo = _symwconv(a, h)[::2]      # lowpass + downsample
        hi = _symwconv(a, g)[::2]      # highpass + downsample
        details.append(hi)
        a = lo
    return a, details

def idwt_pyramid(a, details, hr, gr):
    """Inverse DWT -> reconstruct x."""
    x = a
    for d in reversed(details):
        # upsample by 2 (insert zeros)
        x_up = np.zeros(2 * len(x)); x_up[::2] = x
        d_up = np.zeros(2 * len(d)); d_up[::2] = d
        # synthesis filters (orthogonal: time-reverse of analysis)
        x = _symwconv(x_up, hr) + _symwconv(d_up, gr)
        # trim/align to expected length
    return x

def daubechies(N):
    """Return (h_dec, g_dec, h_rec, g_rec) for dbN via np roots on the
    spectral-factorization of the Daubechies polynomial (see Daubechies 1992)."""
    # ... standard construction; 'pywt' provides this if available
    raise NotImplementedError

def wpss(buffer, family='sym8', J=10, gains=None, transpose_s=0, tau=0.0):
    """Wavelet Packet Spectral Synthesis: forward -> edit -> inverse."""
    h, g, hr, gr = load_filters(family)      # from daubechies() or pywt
    a, details = dwt_pyramid(buffer, h, g, J)
    if gains is None:
        gains = np.ones(J + 1)
    # octave transposition = circular relabel of detail indices
    details = np.roll(details, transpose_s)
    # per-band gain (critical-band EQ)
    for i in range(J):
        details[i] *= gains[i]
    a *= gains[J]
    # wavelet shrinkage denoise
    for i in range(J):
        E = np.sqrt(np.mean(details[i]**2) + 1e-12)
        details[i][np.abs(details[i]) < tau * E] = 0.0
    return idwt_pyramid(a, details, hr, gr)
```

Note: use `pywavelets` (`pywt`) for production filters and the undecimated `pywt.swt` where shift-invariance matters; the above is the transparent NumPy core.

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| PITCH | octave band $j$ (center $3f_s/2^{j+2}$); transpose = relabel $j\to j+s$; scalogram ridge = pitch contour |
| RHYTHM | high-freq details (small $j$) localize transients; $S_j[n]=|d_j[n]|^2$ scalogram = onset/accent grid |
| HARMONY | per-band gain $\{G_j\}$ = harmonic envelope; band stack = voicing; best-basis tree splits harmonic vs percussive |
| STRUCTURE | coarse $a_J$ = macro bed; per-section family/depth/tree = section geometry |
| TEXTURE | retained-band count + shrinkage threshold = density; energy spread across scales = tonal vs noisy |

## UnitMatrix Integration

- **Rows (Voices)** = one DWT chain per voice, mixed in the coefficient (gain) domain before a shared inverse DWT; per-voice octave masks isolate lead/bass/pad/percussion.
- **Columns (Sections)** = `{STRUCTURE}` = `(family, J, tree, scale_mask, transpose_s)`; boundary = new tree/mask.
- **Cells (MusicUnit)** = PITCH→octave label; RHYTHM→scalogram ridge onset; HARMONY→per-band gain vector; TEXTURE→retained bands + threshold.
- **Flow:** per-voice source buffer → `dwt` → apply edits → `idwt` → section buffer → mix → post-FX (SP-007/008/009/032).

## References

- Grossmann & Morlet (1984), "Decomposition of Hardy functions into square integrable wavelets of constant shape," *SIAM J. Math. Anal.* 15(4), 723–736.
- Mallat (1989), "A theory for multiresolution signal decomposition: the wavelet representation," *IEEE TPAMI* 11(7), 674–693.
- Daubechies (1988), "Orthonormal bases of compactly supported wavelets," *Comm. Pure Appl. Math.* 41(7), 909–996.
- Daubechies (1992), *Ten Lectures on Wavelets*, SIAM.
- Coifman & Wickerhauser (1992), "Entropy-based algorithms for best basis selection," *IEEE Trans. Inf. Theory* 38(2), 713–718.
- Kronland-Martinet, Morlet & Grossmann (1987), "Analysis of sound patterns through wavelet transforms," *Int. J. Pattern Recog. & AI* 1(2), 273–302.
- Mallat (2009), *A Wavelet Tour of Signal Processing*, 3rd ed., Academic Press.