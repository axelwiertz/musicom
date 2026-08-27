# Spectral Delay Filters (SDF) — Sound Production Method SP-050

**ID**: SP-050
**Acronym**: SDF
**Layer**: Post-Processing / DSP
**Target Output**: Band-Based Arpeggio / Spectral Rhythm & Texture
**Date**: 2026-08-22

## One-Line Summary
STFT-domain delay line with independent delay time and feedback gain per frequency bin; partial/formant templates (stretch factor, shift, Hz/cents bandwidth) generate the delay window, harmweights map symbolic rhythms to bands, and GCD quantization locks feedback cycles to the hop grid — one percussive burst becomes a band-based arpeggio, glissando, or polyrhythm.

## Source
Spectral delay is the frequency-domain generalization of the delay line: instead of delaying the whole signal by one time, each frequency band gets its own delay time and feedback gain. The canonical filter formulation is **Pekonen, J., Välimäki, V., Abel, J. S., and Smith, J. O. (2009), "Spectral Delay Filters with Feedback and Time-Varying Coefficients," *Proc. 12th Int. Conference on Digital Audio Effects (DAFx-09)*, Como, Italy, pp. 157–164** — which derives the feedback structure and its stability conditions for time-varying coefficients. Earlier practical work: **Kim-Boyle, D. (2004), "Spectral delays with frequency domain processing," *DAFx-04*, Naples, pp. 42–44** (the Max/pfft~ implementation and the idea of driving delay values from an FFT of a control signal), and **Gibson, J. (2009), "Spectral Delay as a Compositional Resource," *eContact!* 11(4)** (compositional use). The composition-grade parameterization used here — partial/formant templates, atom shapes, and rhythmic quantization — comes from **Cont, A., Laurenzi, C., and Stroppa, M. (2013), "Chromax, the other side of the spectral delay between signal processing and composition," *DAFx-13*, Maynooth, Ireland** (Ircam / Gen~ bin-synchronous implementation, used in Stroppa's *…of Silence* and *Re Orso*).

In the Musicom catalog, SDF fills the *spectral-domain delay* gap: SP-013 (FDL) is a single time-domain delay line, SP-026 (phase vocoder) is analysis-modification-resynthesis for time/pitch, SP-032 (FDN) is algorithmic reverb — none of them applies an independent delay + feedback *per frequency bin*. SDF is the post-processing/DSP counterpart to SP-039 (IFFT additive synthesis): both live in the STFT domain, but SDF delays and feeds back existing bins rather than synthesizing them.

## Description
SDF processes rendered audio in the Short-Time Fourier Transform (STFT) domain. The signal is windowed and FFT'd into frames; each frequency bin $k$ is delayed by its own frame count $d_k$ (equivalently its own time $\tau_k = d_k \cdot H / f_s$, with hop size $H$) and fed back with its own gain $g_k$. A single percussive burst therefore explodes into a *band-based arpeggio*: low bins arrive late, high bins early (or vice versa), each band repeating at its own rate under feedback. The key compositional upgrade over commercial spectral delays (iZotope Spectron, NI Spektral Delay) is the **template**: instead of hand-drawing one envelope, the delay window $\tau(k)$ and feedback window $g(k)$ are generated from *partial atoms* (harmonic/inharmonic spectra via a stretch factor) and *formant atoms*, whose per-bin weights encode symbolic rhythms. Delays are **rhythmically quantized** to integer multiples of the STFT hop size so that feedback cycles stay locked to the score grid — the property that makes SDF a *composable* rhythm engine rather than a smear effect.

## Technical Mechanics

### 1. STFT analysis
The input audio $x(n)$ is framed with window $w$ and hop $H$:

$$X(m, k) = \sum_{n=0}^{N-1} w(n)\, x(n + mH)\, e^{-j 2\pi k n / N}$$

where $m$ is the frame index and $k$ the bin index. The hop size $H$ is the *time quantum* of the whole method: with $f_s = 96$ kHz and $N = 8192$ (Hanning, $H = N/4$), the time resolution is $H/f_s = 21.3$ ms — the smallest delay increment SDF can express.

### 2. Per-bin delay
Each bin is delayed by an integer number of frames:

$$Y(m, k) = X\!\left(m - d_k,\; k\right), \qquad d_k = \mathrm{round}\!\left(\frac{\tau_k \cdot f_s}{H}\right)$$

where $\tau_k$ is the desired delay time for bin $k$. The delay window is the vector $\tau(k) = \tau_{max} \cdot w_k$ over bins; $w_k \in [0,1]$ are the per-bin delay weights. A rectangular delay window delays all bins in a band simultaneously (a single time point); a Gaussian delay window makes outer bins precede the center (a double glissando converging on the central bin).

### 3. Per-bin feedback
Feedback re-injects delayed bins into the current frame:

$$Y(m, k) = X(m, k) + g_k \cdot Y(m - d_k, k)$$

with per-bin feedback gain $g_k$. For time-invariant $g_k$ the structure is stable iff $|g_k| < 1$ for all $k$; Pekonen et al. (2009) derive the stability conditions for time-varying coefficients (the feedback path must remain bounded as $g_k$ and $d_k$ change). At $g_k = 1$ with sample-synchronous scheduling, a burst repeats indefinitely without attenuation — the "infinite echo" regime used for rhythmic loops.

### 4. Partial templates (Chromax)
The delay/feedback window is generated from a set of partial atoms rather than drawn by hand. Each partial $n$ sits at a frequency (McAdams 1982 / OMChroma):

$$f_n = n \cdot s \cdot f_0 + \mathrm{shift} \cdot f_0, \qquad s = \frac{\log b}{\log 2}$$

where $f_0$ is the fundamental, $s$ the stretch factor ($s = 1$ = harmonic series; $s \neq 1$ = stretched/compressed inharmonic spectra), and $\mathrm{shift}$ a constant offset in units of $f_0$. Each partial carries a bandwidth ("variance") expressed in **Hz** (constant width — effective in the low range) or **cents** (width grows with frequency — clustery in the high range). Formant atoms are defined by center frequency, amplitude, bandwidth, and skirt width.

### 5. Rhythmic quantization
To keep feedback cycles musically exact, requested delays are quantized to integer multiples of the hop, then further quantized to the greatest common divisor of the written rhythm and the hop:

$$d_k = \mathrm{round}\!\left(\frac{\tau_k}{H}\right), \quad \text{then snap } d_k \text{ to multiples of } \gcd(\text{pattern unit}, H)$$

The **harmweights** vector assigns each partial a weight $w_n$ that is simultaneously its delay weight and its rhythmic subdivision: a band with weight $w_n = 1/n$ produces a "note" every $1/n$ of the maximum delay. For a 4-band spectrum with weights $1, 0.5, 0.25, 0.125$ and $\tau_{max} = 2$ s, the bands fire at 2 s, 1 s, 0.5 s, 0.25 s — a band-based arpeggio at quaver = 60.

### 6. ISTFT resynthesis
The modified frames are overlap-added back to the time domain with a synthesis window satisfying the constant-overlap-add constraint:

$$y(n) = \frac{\sum_m w_s(n - mH)\, y_m(n - mH)}{\sum_m w_s^2(n - mH)}$$

**Complexity**: per frame — one FFT ($\mathcal{O}(N \log N)$), one per-bin frame-index shift (a circular buffer read per bin), one per-bin multiply-add for feedback, one IFFT. $\mathcal{O}(N \log N)$ per frame; real-time in compiled code (Gen~ runs it sample-synchronously at 96 kHz).

## Musical Elements Framework
- **PITCH**: SDF does not generate pitch — it *resynthesizes* and re-orders it. Partial templates set the *spectral* pitch content ($f_n = n \cdot s \cdot f_0 + \mathrm{shift} \cdot f_0$): harmonic ($s=1$), stretched/compressed ($s \neq 1$), or shifted. Gaussian delay windows produce ascending/descending glissandi toward each band center; rectangular windows produce simultaneous band onsets. Because each band is resynthesized from few bins, the result approaches a narrow mixture of sine tones — SDF sits at the processing/synthesis boundary.
- **RHYTHM**: The core element. Per-bin delay times *are* the rhythm: harmweights map symbolic rhythms to frequency bands, so one noise burst becomes a full band-based arpeggio. Feedback ($g_k$) turns each band into a repeating "note" at its own subdivision; GCD quantization keeps all repetitions locked to the score grid. Poly-rhythmic templates (bands at coprime subdivisions) give true polyrhythm from a single excitation.
- **HARMONY**: The stretch factor $s$ and shift parameter control the harmonic/inharmonic character of the partial template; feedback sustains the harmonic content of each band. Per-band feedback gains shape which harmonics ring longest — a spectral "sustain pedal" that can hold chord tones while letting noise bands die.
- **STRUCTURE**: Macro-form is expressed through template selection and dynamic crossfade. Section A = one delay/feedback template; Section B = another; **spectral interpolation** between templates over a specified duration gives a continuous timbral/rhythmic morph across section joins (the spectral analogue of SP-041 wavetable morphing). Hard template switches give discrete section contrast.
- **TEXTURE**: Bandwidth in Hz vs cents controls spectral thickness (cents = clustery highs, Hz = fat lows). Gaussian atom shapes add glissando texture; feedback builds progressive density (each cycle adds a delayed copy); long feedback on a burst produces accelerating/decelerating "zero-phasing" patterns (the spectral-delay emulation of phase-locked oscillator clusters).

## UnitMatrix Integration (Voices and Sections)
- **Rows (Voices)**: Two modes. (a) **Bus mode**: all voices are summed and passed through one SDF instance — the delay window re-orchestrates the whole mix into a spectral arpeggio. (b) **Per-voice mode**: each voice $v$ gets its own SDF with its own template — voice 1 (lead) = high bins, fast subdivisions; voice 2 (bass) = low bins, long delays; voice 3 (pad) = broad Gaussian window, high feedback; voice 4 (percussion) = noise-band excitation. Each row renders to a mono buffer, then summed or spatialized (SP-021/SP-034/SP-043).
- **Columns (Sections)**: Each section $s$ supplies (a) a partial/formant template (f0, stretch, shift, bandwidth), (b) a delay window shape (rectangular/Gaussian), (c) a feedback window $g_k$, and (d) a rhythmic harmweights vector. Section joins = template crossfade (continuous) or template switch (discrete).
- **Cells** $U_{v,s}$:
  - `{RHYTHM}`: The harmweights vector — per-band delay subdivisions that encode the cell's rhythm.
  - `{PITCH}`: Template f0, stretch $s$, shift — the cell's spectral pitch content.
  - `{TEXTURE}`: Bandwidth (Hz/cents), atom shape (rectangular/Gaussian), feedback gain — the cell's spectral thickness and density.
  - `{HARMONY}`: Stretch factor $s$ and per-band feedback — harmonic/inharmonic balance and sustain.
- **Mapping Flow**:
  1. Compose and fill the UnitMatrix; validate zero-drift; export MIDI via the musicom engine.
  2. Render symbolic MIDI to audio with a synthesis engine (SP-001 FluidSynth, SP-002 VST stacking, or SP-029 subtractive).
  3. Build the per-section templates: partial atoms → delay window $\tau(k)$ and feedback window $g(k)$; quantize delays to the hop grid (GCD quantization).
  4. Run SDF: STFT → per-bin delay + feedback → ISTFT (bin-synchronous scheduling).
  5. Post-process downstream (SP-007 EQ, SP-008 DRC, SP-009/SP-032 reverb); export.

## Implementation Sketch (Python / NumPy)
```python
import numpy as np

def stft(x, win, hop):
    n = len(x); W = len(win); nf = 1 + (n - W) // hop
    X = np.zeros((nf, W // 2 + 1), dtype=complex)
    for m in range(nf):
        frame = x[m * hop : m * hop + W] * win
        X[m] = np.fft.rfft(frame)
    return X

def istft(X, win, hop, out_len):
    W = len(win); nf = X.shape[0]
    y = np.zeros(out_len); wsum = np.zeros(out_len)
    for m in range(nf):
        frame = np.fft.irfft(X[m], W) * win
        s = m * hop
        y[s:s+W] += frame
        wsum[s:s+W] += win ** 2
    return y / np.maximum(wsum, 1e-12)

def spectral_delay(x, fs, win, hop, tau, fb, tau_max=2.0):
    """Per-bin spectral delay + feedback.

    tau : per-bin delay weights in [0,1]  (tau_max scales to seconds)
    fb  : per-bin feedback gains in [0,1)
    """
    W = len(win); nbins = W // 2 + 1
    d = np.round(tau * tau_max * fs / hop).astype(int)   # frame counts
    d = np.maximum(d, 0)
    X = stft(x, win, hop)
    Y = np.zeros_like(X)
    for m in range(X.shape[0]):
        Y[m] = X[m].copy()
        for k in range(nbins):
            src = m - d[k]
            if src >= 0:
                Y[m, k] += fb[k] * Y[src, k]            # feedback
    return istft(Y, win, hop, len(x))

def partial_template(f0, n_partials, stretch=1.0, shift=0.0, bw_hz=50.0,
                     fs=96000, W=8192):
    """Chromax-style partial atom template -> per-bin delay weights."""
    freqs = np.arange(1, n_partials + 1) * stretch * f0 + shift * f0
    bins = np.fft.rfftfreq(W, 1 / fs)
    tau = np.zeros(W // 2 + 1)
    for f, n in zip(freqs, range(1, n_partials + 1)):
        g = np.exp(-0.5 * ((bins - f) / bw_hz) ** 2)     # Gaussian atom
        tau += g * (1.0 / n)                              # harmweight 1/n
    return tau / tau.max()
```

### Vectorized feedback (production)
Replace the nested feedback loop with fancy indexing along the frame axis:

```python
def spectral_delay_fast(x, fs, win, hop, tau, fb, tau_max=2.0):
    W = len(win); nbins = W // 2 + 1
    d = np.maximum(np.round(tau * tau_max * fs / hop).astype(int), 0)
    X = stft(x, win, hop)
    nf = X.shape[0]
    Y = X.copy()
    for m in range(nf):
        src = m - d                       # (nbins,) source frame per bin
        valid = src >= 0
        # gather delayed+feedback bins in one shot
        idx = np.where(valid, src, 0)
        delayed = Y[idx, np.arange(nbins)]          # (nbins,) complex
        Y[m] += np.where(valid, fb * delayed, 0.0)
    return istft(Y, win, hop, len(x))
```

### Tooling notes
- NumPy for framing, FFT, and the per-bin loop; `librosa` or `scipy.signal.stft` for production STFT.
- Compile the frame loop (Numba/Cython) for real-time; the DSP itself is $\mathcal{O}(N \log N)$ per frame.
- The musicom engine handles UnitMatrix fill and zero-drift MIDI export upstream; SDF consumes rendered audio downstream.

## Pitfalls
1. **STFT time-resolution floor**: The hop size is the minimum delay increment — at 96 kHz / 8192-pt Hanning, 21.3 ms. Sub-hop delays are impossible. Fix: quantize all requested delays to integer multiples of $H$ (GCD quantization for rhythmic patterns), or raise the frame rate (smaller $N$, larger overlap).
2. **Feedback instability**: $|g_k| \geq 1$ makes the band ring forever or blow up; time-varying $g_k$ can go unstable even when each instantaneous value is < 1. Fix: cap $g_k < 1$ with a safety margin, and follow the Pekonen et al. (2009) stability conditions when $g_k$ is modulated.
3. **Round-off drift under feedback**: Dynamic (time-varying) delays accumulate timing offsets after each feedback cycle, producing sloppy, unsynchronized rhythms. Fix: bin-synchronous sample-accurate scheduling (Gen~-style) and quantize $d_k$ to the hop grid so every cycle lands on a frame boundary.
4. **Template/spectrum mismatch**: If the template's bands don't overlap the incoming sound's spectrum, the output is irregular and unpredictable. Fix: run a preliminary f0/spectral analysis on the source and build the template from the measured partials.
5. **Sparse/staccato output**: A noise burst through SDF yields isolated band bursts — sparse, gap-filled texture (the 011/032 failure mode). Fix: per the Method Hybridization rule, pair SDF with a continuous fill layer (026 DPSM arpeggios, sustained pads, or high-feedback bands that ring continuously).
6. **Phase/COLA artifacts in resynthesis**: A mismatched synthesis window or non-integer hop produces amplitude modulation and pre-echo. Fix: use a constant-overlap-add window pair (e.g., Hann at $H = N/4$) and normalize by the window-squared sum.
7. **Per-bin Python loop too slow**: The nested frame/bin loop is slow in pure Python. Fix: vectorize the feedback with `np.take` along the frame axis, or compile the loop (Numba/Cython).

## Comparison With Related Methods
| Method | Domain | Delay Structure | Feedback | Rhythmic Control | Cost |
|---|---|---|---|---|---|
| Feedback Delay Line (SP-013) | Time | Single tap | Global | Tap time only | $O(1)$ |
| FDN Reverb (SP-032) | Time | N parallel + unitary mix | Global matrix | None (diffuse) | $O(N)$ |
| Phase Vocoder (SP-026) | STFT | None (time-stretch) | None | None | $O(N \log N)$ |
| IFFT Additive (SP-039) | STFT | None (synthesis) | None | Partial onsets | $O(M \log M)$ |
| **SDF (SP-050)** | **STFT** | **Per-bin** | **Per-bin** | **harmweights + GCD quantization** | $O(N \log N)$ |

## References
- Pekonen, J., Välimäki, V., Abel, J. S., and Smith, J. O. (2009). "Spectral Delay Filters with Feedback and Time-Varying Coefficients." *Proc. 12th Int. Conference on Digital Audio Effects (DAFx-09)*, Como, Italy, pp. 157–164.
- Cont, A., Laurenzi, C., and Stroppa, M. (2013). "Chromax, the other side of the spectral delay between signal processing and composition." *Proc. 16th Int. Conference on Digital Audio Effects (DAFx-13)*, Maynooth, Ireland. HAL: hal-00850751.
- Kim-Boyle, D. (2004). "Spectral delays with frequency domain processing." *Proc. 7th Int. Conference on Digital Audio Effects (DAFx-04)*, Naples, Italy, pp. 42–44.
- Gibson, J. (2009). "Spectral Delay as a Compositional Resource." *eContact!* 11(4), Canadian Electroacoustic Community.
- McAdams, S. (1982). "Spectral fusion and the creation of auditory images." In *Music, Mind and Brain*, M. Clynes (ed.), Plenum Press, pp. 279–298.
- Stroppa, M. (2000). "High-level musical control paradigms for digital signal processing." *DAFx-00*, Verona, Italy.
- Agon, C., Bresson, J., and Stroppa, M. (2010). "OMChroma: Compositional control of sound synthesis." *Computer Music Journal* 35(2), pp. 67–83.
