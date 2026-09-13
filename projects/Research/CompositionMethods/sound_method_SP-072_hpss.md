# SP-072 — Harmonic-Percussive Source Separation (HPSS)

**Layer:** absolute (sound production)
**Category:** Post-Processing / DSP
**Target output:** Tonal/Transient Stem Split (Harmonic + Percussive Buffers)
**Complexity:** $O(N \log N)$ per frame (FFT/IFFT) + $O(K \cdot M)$ for the two median filters; deterministic (no RNG)

---

## One-line description

Splits a rendered audio buffer into two re-mixable stems — a **harmonic** stream (sustained/pitched: notes, chords, vocals, pads) and a **percussive** stream (transient/broadband: drums, attacks, plucks, noise) — by exploiting the geometry of the magnitude STFT: harmonic energy forms *horizontal* (time-smooth) ridges, percussive energy forms *vertical* (frequency-smooth) ridges. A time-axis median filter removes transients and keeps tones; a frequency-axis median filter removes tones and keeps transients; a binary or soft mask then splits the complex STFT (reusing the original phase) and inverse STFT reconstructs the two streams.

## Source

- **FitzGerald, D. (2010).** "Harmonic/Percussive Separation Using Median Filtering." *Proc. 13th Int. Conf. on Digital Audio Effects (DAFx-10)*, Graz, Austria. The canonical median-filtering formulation.
- **Driedger, J., Müller, M., & Disch, S. (2014).** "Extending Harmonic-Percussive Separation of Audio Signals." *Proc. ISMIR*, Taipei. The IRLS refinement + cascaded decomposition.
- **Ono, N., Miyamoto, K., Le Roux, J., Kameoka, H., & Sagayama, S. (2008).** "Separation of a Monaural Audio Signal into Harmonic/Percussive Components by Complementary Diffusion on Spectrogram." *Proc. EUSIPCO*.
- **Virtanen, T. (2007).** "Monaural Sound Source Separation by NMF with Temporal Continuity and Sparseness Criteria." *IEEE TASLP* 15(3) — the NMF predecessor.
- **Rafii, Z., & Pardo, B. (2013).** "REPET: A Simple Method for Music/Voice Separation." *IEEE TASLP* 21(1) — the repeating-vs-variable alternative.

## Technical mechanics (extended)

### 1. STFT

Frame the signal $x[n]$ with analysis window $w$ and hop $H$; compute the complex spectrogram

$$X[k,m] = \sum_{n} x[n]\, w[n - mH]\, e^{-j 2\pi k n / N}, \qquad Y[k,m] = |X[k,m]|.$$

### 2. Anisotropic median filtering

Two enhanced magnitude spectrograms via a moving median over a rectangular window:

$$\tilde Y_h[k,m] = \underset{\ell}{\mathrm{median}}\; Y[k,\, m+\ell], \quad \ell \in [-\tfrac{L_h-1}{2}, \tfrac{L_h-1}{2}] \quad \text{(time axis, fixed bin } k)$$

$$\tilde Y_p[k,m] = \underset{\ell}{\mathrm{median}}\; Y[k+\ell,\, m], \quad \ell \in [-\tfrac{L_p-1}{2}, \tfrac{L_p-1}{2}] \quad \text{(frequency axis, fixed frame } m)$$

- $L_h$ (frames): how long a tone must persist to be "harmonic" — $L_h=17$ frames ≈ 200 ms at a 512-sample hop @ 44.1 kHz.
- $L_p$ (bins): how broad a burst must be to be "percussive" — $L_p=17$ bins ≈ 732 Hz wide.

### 3. Masks

**Binary** (FitzGerald):

$$M_h[k,m] = \mathbb{1}\!\left[\tilde Y_h[k,m] > \tilde Y_p[k,m]\right], \qquad M_p = 1 - M_h.$$

**Soft** (smoother, fewer artifacts):

$$M_h = \frac{\tilde Y_h}{\tilde Y_h + \tilde Y_p}, \qquad M_p = \frac{\tilde Y_p}{\tilde Y_h + \tilde Y_p}.$$

### 4. Resynthesis

The mask multiplies the *complex* STFT (original phase reused — no phase estimation), then inverse STFT / overlap-add:

$$x_h[n] = \mathrm{iSTFT}(M_h \odot X), \qquad x_p[n] = \mathrm{iSTFT}(M_p \odot X), \qquad x[n] \approx x_h[n] + x_p[n].$$

### 5. IRLS refinement (Driedger–Müller–Disch 2014)

Replace the median with a differentiable objective:

$$\min_{Y_h, Y_p} \sum_{k,m} \left[ \tfrac12 (Y - Y_h - Y_p)^2 + \lambda\, \big( \| \mathbf{D}_t\, \mathbf{y}_h \|_1 + \| \mathbf{D}_f\, \mathbf{y}_p \|_1 \big) \right]$$

where $\mathbf{D}_t$ is a time-difference operator (penalizing temporal non-smoothness of the harmonic part) and $\mathbf{D}_f$ a frequency-difference operator (penalizing spectral non-smoothness of the percussive part). The $\ell_1$ terms are handled by iterative reweighting: solve the weighted least-squares system with weights from the previous $Y_h, Y_p$ estimate, repeat 2–5×. This drops the filter-length tuning and yields sharper masks.

### 6. Cascaded decomposition

Apply HPSS, then re-apply it to the residual $Y - Y_h - Y_p$ (or to $Y_h$) to extract a finer intermediate layer — e.g. cymbal wash out of a pad, or a second transient layer — building a multi-scale "stem tree".

### 7. Complexity

One FFT + one IFFT per frame: $O(N \log N)$. Sliding-window median (two-heap or running-histogram) is $O(1)$ amortized per bin, so the filter pass is $O(K \cdot M)$ — linear in the spectrogram. Total $O(N \log N)$ per frame; real-time for $N = 1024\text{–}4096$. Deterministic (no RNG) → zero-drift gate trivially satisfied.

## Python/NumPy implementation sketch

```python
import numpy as np
from scipy.signal import stft, istft, medfilt

def hpss(x, fs=44100.0, hop=512, win="hann", nfft=2048,
         lh_frames=17, lp_bins=17, mask="soft", cascade=0):
    """Harmonic-Percussive Source Separation (SP-072).

    Returns (x_h, x_p) re-mixable stems. mask: 'binary'|'soft'.
    cascade: number of extra HPSS passes on the residual (intermediate layers).
    """
    f, t, X = stft(x, fs=fs, window=win, nperseg=nfft,
                   noverlap=nfft - hop, nfft=nfft)
    Y = np.abs(X)

    # --- anisotropic median filters ---
    Yh = medfilt(Y, kernel_size=(1, lh_frames))   # time axis (per bin)
    Yp = medfilt(Y, kernel_size=(lp_bins, 1))     # freq axis (per frame)

    # --- mask ---
    if mask == "binary":
        Mh = (Yh > Yp).astype(float)
        Mp = 1.0 - Mh
    else:  # soft
        denom = Yh + Yp + 1e-12
        Mh = Yh / denom
        Mp = Yp / denom

    # --- resynthesis (phase reused from X) ---
    _, xh = istft(X * Mh, fs=fs, window=win, nperseg=nfft,
                  noverlap=nfft - hop, nfft=nfft)
    _, xp = istft(X * Mp, fs=fs, window=win, nperseg=nfft,
                  noverlap=nfft - hop, nfft=nfft)

    # --- cascade: recover intermediate layers from the residual ---
    layers = [(xh, xp)]
    residual = x - (xh + xp)
    for _ in range(cascade):
        _, _, _, rh, rp = _hpss_once(residual, fs, hop, win, nfft,
                                     lh_frames, lp_bins, mask)
        xh, xp = xh + rh, xp + rp
        residual = residual - (rh + rp)
        layers.append((rh, rp))
    return xh, xp, layers
```

Production code belongs in `sound/effects/hpss.py`, reusing the STFT/overlap-add machinery already present in `phase_vocoder.py`. For a stereo signal, compute a single mask from the mid (mono sum) magnitude and apply it to both channels to preserve stereo coherence (see Pitfall 6).

## Musical Elements Framework

| Element | Mechanism |
|---|---|
| PITCH | the harmonic stream is *all* pitched content (sustained melodies, chords, bass, vocals); the percussive stream is broadband and pitch-less. HPSS is a pitch/noise *splitter*, not a pitch detector |
| RHYTHM | the percussive stream is *all* onset/transient content (kick, snare, hats, plucks); reusing original phase preserves attack timing exactly — a ready-made rhythm layer / transient gate |
| HARMONY | the harmonic stream's spectral envelope carries chord/scale identity; separating *first* then analyzing (chroma, peak-tracking) removes percussion smear and is the single biggest chord-extraction accuracy win |
| STRUCTURE | per-section mask hardness + filter length = macro-form; section joins crossfade the mask blend ratio |
| TEXTURE | the harmonic/percussive balance after independent re-processing is the primary texture knob; cascaded HPSS yields intermediate layers (noise wash, shimmer) for texture thickening/thinning |

## UnitMatrix Integration

- **Rows (Voices)** = per-voice split (render → HPSS → independent re-processing per voice: reverb on pad's harmonic stream, transient shaping on drum's percussive stream) or bus split (sum all voices → HPSS once → global harmonic/percussive layers).
- **Columns (Sections)** = `{STRUCTURE}` = `(mask_mode, L_h, L_p, softness, cascade_depth)` per section; `mask_blend` crossfades the two stems at joins.
- **Cells (MusicUnit)** = `{RHYTHM}` → percussive-stream onset emphasis; `{TEXTURE}` → mask hardness + filter lengths; `{HARMONY}` → harmonic-stream brightness (EQ/reverb send on $x_h$).
- **Flow**: `compose` → `produce(method="SP-072")` → per-voice/bus HPSS → independent harmonic/percussive processing (SP-007/008/009/071) → re-sum → export WAV/OGG.

## Pitfalls

1. **Binary-mask "birdies"** — hard winner-take-all leaves isolated bins flipping between streams (warbling). Fix: soft mask, or time-smooth $M_h$ before multiplying.
2. **Filter-length coupling** — no single $(L_h, L_p)$ works for all material; tune per source or use IRLS to drop length tuning.
3. **Sustained percussion / staccato pitch misclassification** — ride tails → harmonic stream; marimba attacks → percussive stream. HPSS is a soft split, not a perfect classifier.
4. **Phase-reuse smearing** — where sources overlap in time-frequency each stem carries the other's phase. Fix: finer/soft masks, larger overlap.
5. **Window/hop mismatch** — too-large hop under-samples transients; too-small hop shrinks the effective harmonic window. Fix: hop ≈ 512 samples, express $L_h$ in *seconds* (~150–250 ms).
6. **Stereo decorrelation** — per-channel masks differ, breaking the stereo image. Fix: shared mask from the mid (mono sum) magnitude, or mid/side processing.
7. **DC / sub-bass leakage** — near-DC energy lands in whichever stream wins the low bins. Fix: high-pass the input or the harmonic stream at ~20–30 Hz.

## References

- FitzGerald, D. (2010). *Proc. DAFx-10*, Graz.
- Driedger, J., Müller, M., & Disch, S. (2014). *Proc. ISMIR*, Taipei.
- Ono, N., et al. (2008). *Proc. EUSIPCO*, Lausanne.
- Tachibana, H., Ono, N., & Sagayama, S. (2014). *IEEE/ACM TASLP* 22(1).
- Virtanen, T. (2007). *IEEE TASLP* 15(3).
- Rafii, Z., & Pardo, B. (2013). *IEEE TASLP* 21(1).
