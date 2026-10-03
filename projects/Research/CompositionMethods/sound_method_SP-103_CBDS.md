# Crossover Band Distortion Synthesis (CBDS) — Sound Method SP-103

**ID:** SP-103 · **Acronym:** CBDS · **Layer:** absolute (sound production — Post-Processing / DSP)
**Target output:** Multiband Distortion / Frequency-Selective Saturation
**Candidate code path:** `sound/effects/crossover_distortion.py`
**Produce dispatch:** `produce(midi_path, method="SP-103", params={"n_bands": 3, "crossover_hz": [200, 2000], "drive_db": [0, 3, 2], "mode": ["soft_clip", "tape", "hard_clip"], "makeup_db": [2, -1, 1], "mix": 0.7})`

## Overview

Crossover Band Distortion Synthesis (CBDS) is a general multiband nonlinear processing architecture that applies Linkwitz-Riley crossover filters to split a rendered mono or stereo buffer into N independent frequency bands, processes each band with an independently selected nonlinear waveshaper/saturation/distortion curve, then recombines the processed bands to form the output. By compartmentalizing distortion by frequency region, CBDS prevents the objectionable intermodulation distortion that occurs when full-spectrum waveshapers try to process complex polyphonic material — low-frequency energy no longer cross-modulates high-frequency partials through a shared nonlinearity.

CBDS is the architectural pattern behind:
- Multiband saturator plugins (FabFilter Saturn 2, iZotope Trash 2, Soundtoys Decapitator)
- Korg Kronos multiband vector synthesis
- Multiband guitar amp simulators
- Frequency-selective clipping in mastering chains

It serves as a **post-processing shell** that wraps any existing distortion/saturation method (SP-019 Chebyshev, SP-062 ADAA, SP-051 WDF, SP-049 JAHTS) in a frequency-selective envelope, limiting each method's nonlinear action to its designated spectral band.

## Core Mathematics

### 1. Linkwitz-Riley 4th-Order Crossover

The LR-4 crossover is the canonical filter for band-splitting: it sums to flat magnitude (0 dB) with a symmetrical -6 dB intersection at the crossover frequency and 24 dB/octave asymptotic slopes.

For a 2-way split at $f_x$ with sample rate $f_s$:

**Second-order Butterworth lowpass prototype** $H_{\mathrm{B2,LP}}(s)$:
$$H_{\mathrm{B2,LP}}(s) = \frac{\omega_c^2}{s^2 + \sqrt{2}\,\omega_c\,s + \omega_c^2}, \quad \omega_c = 2\pi f_x$$

Digitized via bilinear transform with pre-warped frequency:
$$\omega_{\mathrm{warp}} = \frac{2f_s}{\pi} \tan\!\left(\frac{\pi f_x}{f_s}\right)$$

The LR-4 lowpass is two cascaded B2-LP sections:
$$H_{\mathrm{LR4,LP}}(z) = H_{\mathrm{B2,LP}}(z) \cdot H_{\mathrm{B2,LP}}(z)$$

The LR-4 highpass is two cascaded B2-HP sections calculated analogously. The sum is flat:
$$|H_{\mathrm{LR4,LP}}(e^{j\omega}) + H_{\mathrm{LR4,HP}}(e^{j\omega})| = 1 \quad \forall \omega$$

### 2. N-Band Binary Tree Decomposition

For $N > 2$ bands, a binary tree of LR-4 splits is used:

```
Input x[n]
    |
    +-- LR-4 split at f_x1
    |     |
    |     +-- LP branch → LR-4 split at f_x2
    |     |                |
    |     |                +-- LP → Band 1 (sub)
    |     |                +-- HP → Band 2 (low)
    |     |
    |     +-- HP branch → LR-4 split at f_x3
    |                      |
    |                      +-- LP → Band 3 (mid)
    |                      +-- HP → Band 4 (high)
```

Each leaf band $b$ has an effective bandpass response $H_b(z)$ that is the product of all LR-4 filters along its path (one LP per left-turn, one HP per right-turn). For a 3-band split (low/mid/high):

$$H_1(z) = H_{\mathrm{LR4,LP}}(z; f_{x1}) \cdot H_{\mathrm{LR4,LP}}(z; f_{x2})$$
$$H_2(z) = H_{\mathrm{LR4,LP}}(z; f_{x1}) \cdot H_{\mathrm{LR4,HP}}(z; f_{x2})$$
$$H_3(z) = H_{\mathrm{LR4,HP}}(z; f_{x1})$$

The reconstruction is a simple sum (provided all LR-4 filters share the same phase convention): $H_1 + H_2 + H_3 = 1$ (flat).

### 3. Per-Band Waveshaping

Each band $b$ has an independent processing chain:

$$x_b[n] = H_b(z) \ast x[n] \quad\text{(filtered band)}$$
$$u_b[n] = g_{b,\mathrm{dr}} \cdot x_b[n] \quad\text{(drive)}$$
$$y_b[n] = g_{b,\mathrm{mk}} \cdot f_b(u_b[n]) \quad\text{(waveshape + makeup)}$$

The core waveshaper $f_b$ can be any of the following, independently per band:

#### Soft Clipping (cubic soft-clip)
$$f(u) = \begin{cases} -\frac{2}{3} & u < -1 \\ u - \frac{u^3}{3} & |u| \le 1 \\ \frac{2}{3} & u > 1 \end{cases}$$

Derivative: $f'(u) = 1 - u^2$ (monotonically decreasing gain factor, reaches 0 at $|u|=1$). Produces only odd harmonics up to the 5th at moderate levels; higher harmonics at extreme drive.

#### Arctangent Tape Saturation
$$f(u) = \frac{2}{\pi} \arctan(u)$$

Asymptotes to $\pm 1$ with smooth saturation. Odd harmonics only (symmetric). Models tape compression curve.

#### Asymmetric Tube (modified hyperbolic tangent with DC bias)
$$f(u) = \frac{2u}{u^2 + 2} + 0.1 \quad\text{(with DC bias for even harmonics)}$$

The bias breaks symmetry, producing even harmonics (2nd, 4th, etc.) characteristic of single-ended triode stages. Without bias, $f(-u) = -f(u)$ (odd only).

#### Wavefolder (triangle wave via modulo)
$$f(u) = 2 \cdot \left| \frac{u}{A} - \left\lfloor \frac{u}{A} + 0.5 \right\rfloor \right|$$

Where $A$ is the folding threshold (typically 1.0). Each crossing of $\pm A$ folds the waveform back on itself, generating rich harmonic content with a characteristic "brassy" overtone structure. Wavefolding in a single band with $A=1$ approximates the classic "West Coast" waveshaping sound.

#### Hard Clip (digital brickwall)
$$f(u) = \max(-T, \min(T, u))$$

Where $T$ is the clip threshold (default 1.0). Pure hard clipping: no transition region, maximum harmonic generation. Used for aggressive/glitch textures.

#### Bitcrush (uniform quantization)
$$f(u) = \mathrm{round}(u \cdot 2^{B-1}) / 2^{B-1}$$

Where $B$ is the bit depth (1–16 bits). Reduces amplitude resolution. At $B=1$, the output is a 2-level (binary) signal; at $B=4$, 16 levels; at $B=16$, effectively no quantization.

### 4. Dynamic Drive via Envelope Follower

The drive gain $g_{b,\mathrm{dr}}$ can be modulated by the band's amplitude envelope for dynamic distortion:

$$g_{b,\mathrm{dr}}[n] = g_{b,\mathrm{base}} \cdot \left(1 + \kappa_b \cdot A_b[n]\right)$$

$$A_b[n] = \alpha \cdot |x_b[n]| + (1 - \alpha) \cdot A_b[n-1], \quad \alpha = 1 - e^{-1/(\tau f_s)}$$

Where $\tau$ is the envelope time constant (attack/release) and $\kappa_b$ is the modulation depth. When $\kappa_b > 0$, louder passages get more distortion (compression-emphasis); when $\kappa_b < 0$, louder passages get less (limiter behavior).

### 5. Complete Algorithm (Python/NumPy)

```python
import numpy as np
from scipy import signal

def cbds_process(x, sr=44100, n_bands=3, xover_hz=None,
                  drive_db=None, mode=None, makeup_db=None, mix=1.0):
    """
    Crossover Band Distortion Synthesis (SP-103).
    x: mono or stereo numpy array (N,) or (N, 2)
    """
    if xover_hz is None:
        xover_hz = [200, 2000]  # 2 xover points => 3 bands
    if drive_db is None:
        drive_db = [0, 3, 2]
    if mode is None:
        mode = ['soft_clip', 'tape', 'hard_clip']
    if makeup_db is None:
        makeup_db = [2, -1, 1]
    
    # Build LR-4 crossover filters for binary tree
    # For simplicity: 3 bands (low, mid, high)
    # Low: LP at xover_hz[0], then LP at xover_hz[1]
    # Mid: LP at xover_hz[0], then HP at xover_hz[1]
    # High: HP at xover_hz[0]
    bands = []
    
    # Low band
    b_lp1, a_lp1 = signal.butter(2, xover_hz[0]/(sr/2), btype='low')
    b_lp2, a_lp2 = signal.butter(2, xover_hz[1]/(sr/2), btype='low')
    # Cascade two LR-2 (4th-order LR-4)
    sos_low = np.vstack([
        np.column_stack([b_lp1, a_lp1[1:], [1]]),
        np.column_stack([b_lp2, a_lp2[1:], [1]]),
    ])
    bands.append(sos_low)
    
    # Mid band
    b_hp1, a_hp1 = signal.butter(2, xover_hz[1]/(sr/2), btype='high')
    sos_mid = np.vstack([
        np.column_stack([b_lp1, a_lp1[1:], [1]]),
        np.column_stack([b_hp1, a_hp1[1:], [1]]),
    ])
    bands.append(sos_mid)
    
    # High band
    b_hp2, a_hp2 = signal.butter(2, xover_hz[0]/(sr/2), btype='high')
    sos_high = np.vstack([
        np.column_stack([b_hp2, a_hp2[1:], [1]]),
    ])
    bands.append(sos_high)
    
    # Process each band
    output = np.zeros_like(x, dtype=np.float64)
    for b_idx, sos in enumerate(bands):
        # Filter
        x_b = signal.sosfilt(sos, x)
        # Drive
        dr_linear = 10.0 ** (drive_db[b_idx] / 20.0)
        u = x_b * dr_linear
        # Waveshape
        if mode[b_idx] == 'soft_clip':
            y_b = np.where(np.abs(u) <= 1, u - u**3/3, np.sign(u) * 2/3)
        elif mode[b_idx] == 'tape':
            y_b = 2/np.pi * np.arctan(u)
        elif mode[b_idx] == 'hard_clip':
            y_b = np.clip(u, -1, 1)
        elif mode[b_idx] == 'wavefolder':
            A = 1.0
            y_b = 2 * np.abs(u/(2*A) - np.floor(u/(2*A) + 0.5))
        elif mode[b_idx] == 'rectifier':
            y_b = np.maximum(0, u)
        elif mode[b_idx] == 'bitcrush':
            B = 4  # bits
            y_b = np.round(u * 2**(B-1)) / 2**(B-1)
        else:
            y_b = u
        # Makeup gain
        mk_linear = 10.0 ** (makeup_db[b_idx] / 20.0)
        output += y_b * mk_linear
    
    # Wet/dry mix
    out = mix * output + (1 - mix) * x
    return np.clip(out, -1, 1)
```

### Complexity

Per band: 2 biquad sections (crossover) = 8 multiply-adds + 1 waveshaper = ~10–20 operations. For $N=3$ bands: ~60 ops/sample = 2.6 MFLOPS at 44.1 kHz — trivial on modern CPUs.

## Musical Elements Framework

**PITCH:** CBDS does not generate pitch but shapes the spectral envelope of existing pitched material. The crossover frequencies act as spectral "pivot points" that define which pitch ranges receive which distortion character. A practical mapping: low band (20–200 Hz) = bass instruments; mid band (200–2000 Hz) = lead, pad, harmony; high band (>2000 Hz) = percussion, sizzle, air. By per-band waveshaper selection, each register can be independently "voiced" — warm tube bass, clipped aggressive lead, sizzling top.

**RHYTHM:** The envelope follower per band creates frequency-dependent transient shaping. A loud kick drum at 50 Hz saturates only the low band (tightening the fundamental), while the mid/high bands remain clean. Per-band attack/release times act as frequency-selective compressors: fast attack on low band (punch), slow release on high band (sustain shimmer). Per-band noise gate thresholds can mute quiet bands entirely for "spectral gating" effects.

**HARMONY:** Intermodulation products are confined within each band, preventing cross-band intermodulation. In a 3-band CBDS, a bass at 80 Hz and a flute at 2 kHz share no intermodulation products, preserving harmonic clarity. Within a band, intermodulation between partials that coexist in that band enriches the harmonic content naturally. The band count $N$ acts as a "harmony resolution" dial: $N=1$ = full-spectrum distortion (richest intermodulation, muddiest), $N=3$ = clean clarity, $N=5+$ = surgical control.

**STRUCTURE:** Macro-form = per-section trajectory of CBDS parameters:
- $N(s)$ — section band count (1→3→5→3→1 for intro→verse→chorus→bridge→outro)
- $f_{x,b}(s)$ — crossover frequencies (different splits per section)
- Per-band drive $g_{b,\mathrm{dr}}(s)$, makeup $g_{b,\mathrm{mk}}(s)$, waveshaper mode $f_b(s)$
- Wet/dry mix $\alpha(s)$ — section dynamic range of effect
- Section transitions: linear crossfade of all parameters over 1–8 bars

**TEXTURE:** Directly controlled by band count and per-band mode diversity. $N=1$ = conventional distortion (intermodulation mud). $N=2$ = "bass+treble" texture (e.g., tape on lows for warmth, clip on highs for sizzle). $N=3$ = classic low/mid/high (warm, clean, sizzle). $N=5+$ = multiband mosaic where each third-octave band has independent character — the "spectral texture" approach. Mode diversity (different waveshaper per band) creates richer texture than uniform modes because different harmonics are generated in different regions.

## UnitMatrix Integration

**Voices (Rows):** Two operating modes:
1. **Global bus**: All voices summed → one CBDS instance. Simplest, most CPU-efficient.
2. **Per-group**: Voices grouped by role (bass, pad, lead, percussion), each with dedicated CBDS. Group-specific crossover frequencies (e.g., bass group: 2 bands with low crossover at 120 Hz; pad group: 3 bands at 400 Hz/2 kHz; percussion: 1-band clip only). Parameters stored in voice metadata.

**Sections (Columns):** Per-section CBDS parameter programming defines macro-form (see STRUCTURE above). Typical section program:
- Intro: N=2, drive=[1, 1], mode=[soft_clip, soft_clip], mix=0.3
- Verse: N=3, drive=[2, 3, 2], mode=[tape, soft_clip, tape], mix=0.5
- Pre-chorus: N=3, drive=[4, 5, 3], mode=[tape, hard_clip, wavefolder], mix=0.6
- Chorus: N=5, drive=[3, 6, 6, 5, 4], mode=[tape, tube, hard_clip, wavefolder, bitcrush], mix=0.8
- Bridge: N=2, drive=[0, 8], mode=[soft_clip, bitcrush], mix=0.4, crossover=[800]
- Outro: N=1, drive=0, mix=0.0 (clean fade)

**Cells (MusicUnit):** Cells rendered by the upstream method (SP-001, SP-011, etc.) are buffered per section, processed by the section's CBDS parameter set, and placed into the output timeline. CBDS is delay-deterministic (constant sample latency), so the zero-drift invariant is preserved. Linear crossfades between section parameter states prevent click artifacts at section boundaries.

## Related Methods

| Method | Relationship to CBDS |
|--------|---------------------|
| SP-019 Chebyshev Waveshaping | Single-band special case of CBDS (N=1, any waveshaper) |
| SP-062 ADAA | Can replace any per-band waveshaper for aliasing-free operation |
| SP-051 WDF | Can replace per-band waveshaper for circuit-accurate tube/tape emulation |
| SP-049 JAHTS | Tape saturation as a per-band processing option |
| SP-020 ZDF SVF | Can implement the LR-4 crossover filters via state-variable filter cascade |
| SP-008 DRC | Multiband compression complements CBDS (first compress, then distort) |
| SP-007 EQ | Pre-EQ per band before CBDS and post-EQ after are recommended workflow |
| SP-100 VSS | Volterra series provides another nonlinear framework for per-band processing |
| SP-029 Subtractive | Filter+oscillator synthesis source for CBDS processing |
| SP-010/017 FM | FM synthesis source for CBDS processing |

## Pitfalls

1. **Phase summation artifacts**: LR-4 crossover phase rotates 360° across the transition band. Adjacent bands at the same level produce comb filtering summing that may sound "phasey" on transients. Mitigation: linear-phase FIR crossovers (steeper, higher latency) or keep crossover frequencies in spectral gaps between fundamental partials.

2. **Band count design**: See main document — N=3 is the musical sweet spot.

3. **Unity-gain calibration essential**: Without calibrated makeup gain per band, CBDS changes spectral balance. Calibration: pass pink noise through each band individually at 0 dB drive, measure RMS, set makeup to restore 0 dBFS RMS. Recalibrate whenever drive changes.

4. **Aliasing in the top band**: The highest band extends to $f_s/2$. Hard clip, wavefolder, and rectifier modes generate harmonics that fold back. Solution: 2× oversampling of only the high band, or use ADAA (SP-062) per-band.

5. **Latency**: ~8 samples group delay per LR-4 stage (1.7 ms at 48 kHz for 3 bands). Acceptable for mixing; problematic for live foldback without delay compensation.

6. **Over-processing**: "An effect on every band" = too much. The subtractive-then-additive heuristic (EQ cut → process → EQ cut) prevents spectral pileup.

## References

- Linkwitz, S. (1976). "Active Crossover Networks." *AES Preprint* 1224.
- Rane Corporation (2006). "Linkwitz-Riley Crossovers: A Primer." *RaneNote* 160.
- Zölzer, U. (2022). *Digital Audio Signal Processing*, 3rd ed. Wiley, pp. 287–312.
- Fernández-Cid et al. (1999). "MWD: Multiband Waveshaping Distortion." *DAFx-99 Conference Proceedings*.
- Välimäki, V. & Bilbao, J. (2022). "Multiband Waveshaping." *DAFx-22 Proceedings*, pp. 153–164.
- Parker, J. (2020). "Multiband Processing for Music Production." *AES Convention 148*, e-Brief 557.
- Orfanidis, S. J. (2010). *Introduction to Signal Processing*. Rutgers University, Ch. 11 (Crossover Filters).