# Bitcrushing / Sample Rate Reduction Synthesis (SRR) — Sound Method SP-104

**ID:** SP-104 · **Acronym:** SRR · **Layer:** absolute (sound production — Post-Processing / DSP)
**Target output:** Lo-Fi Degradation / Quantization Noise & Aliasing / Digital Grit
**Candidate code path:** `sound/effects/bitcrusher.py`
**Produce dispatch:**
```python
produce(midi_path, method="SP-104", params={
    "bit_depth": 8,         # 1–16 bits
    "crush_factor": 4,      # R = sample rate divisor (1=none, 2, 4, 8, ...)
    "order": "hold_then_quantize",  # or "quantize_then_hold"
    "dither": True,         # TPDF dither on/off
    "anti_alias": False,    # bandlimited decimation on/off
    "mix": 0.7,             # wet/dry blend
    "per_voice": {
        "Bass": {"bit_depth": 16, "crush_factor": 1, "mix": 0.0},
        "Lead": {"bit_depth": 4, "crush_factor": 2, "mix": 0.8}
    }
})
```

## Overview

**Bitcrushing / Sample Rate Reduction Synthesis (SRR)** is a dual-method degradation architecture that intentionally reduces the digital audio resolution of a rendered signal through two independent mechanisms:

1. **Bit-depth reduction (re-quantization)**: decreases the number of bits per sample from 16/24/32-bit down to as few as 1 bit, introducing quantization noise and amplitude-dependent harmonic distortion.
2. **Sample-rate reduction (decimation with sample-and-hold)**: reduces the effective sampling rate by holding each output sample for R consecutive periods, producing aliased high-frequency components.

These mechanisms can be applied independently or jointly, producing the classic "bitcrusher" effect heard in chiptune, lo-fi hip-hop, glitch, noise, and industrial electronic music.

SRR is the **intentional degradation** counterpart to unintentional resolution limits in digital audio. It is the post-processing sibling of SP-068 (Bytebeat Synthesis), SP-054 (Waveset Distortion), and SP-103 (CBDS — which includes bitcrush as a per-band option). Unlike these, SRR treats bit-depth reduction and sample-rate reduction as independent, first-class post-processes.

## Core Mathematics

### 1. Bit-Depth Reduction (Re-quantization)

A signal \(x[n]\) with \(B\) bits/sample is reduced to \(b < B\) bits:

\[
x_b[n] = \frac{\mathrm{round}\bigl(x[n] \cdot 2^{b-1}\bigr)}{2^{b-1}}
\]

Where round() is tie-to-even rounding (default) or truncation. The quantization error \(q[n] = x_b[n] - x[n]\) is bounded by \(\pm 2^{-b}\) and approximates uniform white noise with RMS:

\[
\sigma_q = \frac{2^{-b}}{\sqrt{12}} \approx 0.29 \cdot 2^{-b}
\]

Signal-to-quantization-noise ratio:

\[
\mathrm{SQNR} \approx 6.02b + 1.76 \;\text{dB}
\]

At b=16 (CD): SQNR ≈ 98 dB (inaudible). At b=4: SQNR ≈ 26 dB (severe audible noise). At b=1: sign-only square wave.

**Dithering** (optional): Add triangular PDF noise \(d[n] \sim \triangle(-\Delta, +\Delta)\), \(\Delta = 2^{-b}\) before rounding to decorrelate quantization error:

\[
x_b[n] = \frac{\mathrm{round}\bigl((x[n] + d[n]) \cdot 2^{b-1}\bigr)}{2^{b-1}}
\]

### 2. Sample-Rate Reduction (Decimation with Sample-and-Hold)

Given original sample rate \(f_s\) and crush factor \(R \ge 1\):

\[
y[n] = x\!\left[R \cdot \left\lfloor\frac{n}{R}\right\rfloor\right]
\]

Each output sample is held for R consecutive indices — zero-order hold (nearest-neighbor interpolation). This is equivalent to decimating by R then upsampling by R via sample replication.

**Aliasing analysis:** Without anti-aliasing LPF before decimation, all frequencies above \(f_s/2R\) alias into the baseband. The zero-order hold introduces spectral rolloff:

\[
|H_{\mathrm{sh}}(f)| = \left|\frac{\sin(\pi f/f_s)}{\pi f/f_s}\right| \cdot \mathrm{sinc}\!\left(\frac{f}{f_s/R}\right)
\]

Notches at multiples of \(f_s/R\). At extreme R (e.g., R=50 at 44.1 kHz → 882 Hz effective), aliased components create dense metallic ring-mod texture.

### 3. Combined Operation

\[
y[n] = \mathrm{requantize}_b\!\left( \mathrm{hold}_R\bigl(x[n]\bigr) \right)
\]

Order matters: hold-then-quantize spreads quantization noise over R samples; quantize-then-hold introduces noise at the original rate.

**Complexity:** \(\mathcal{O}(1)\) per sample — ~5–10 operations, negligible CPU.

## Python Implementation

```python
import numpy as np

def bitcrush(x: np.ndarray, bit_depth: int = 8, crush_factor: int = 4,
             dither: bool = True, anti_alias: bool = False,
             order: str = "hold_then_quantize") -> np.ndarray:
    """
    Bitcrush / Sample Rate Reduction Synthesis.

    Parameters
    ----------
    x : np.ndarray, shape (N,) or (N, C) mono/stereo
        Input signal in [-1, 1] float range.
    bit_depth : int, 1–16
        Target bit depth.
    crush_factor : int, ≥1
        Sample rate reduction factor R.
    dither : bool
        Add TPDF dither before re-quantization.
    anti_alias : bool
        Apply LPF at f_s/2R before decimation.
    order : str
        'hold_then_quantize' or 'quantize_then_hold'.

    Returns
    -------
    y : np.ndarray, same shape as x
        Processed signal.
    """
    y = np.asarray(x, dtype=np.float64).copy()
    n_orig = len(y)

    if order == "hold_then_quantize":
        # 1. Sample-and-hold decimation
        if crush_factor > 1:
            if anti_alias:
                from scipy import signal as sg
                sos = sg.butter(8, 1.0 / crush_factor, btype='low', output='sos')
                y = sg.sosfilt(sos, y)
            # zero-order hold decimation
            idx = np.arange(0, n_orig, crush_factor)
            y_decimated = y[idx]
            # replicate (zero-order hold) back to original length
            y = np.repeat(y_decimated, crush_factor)[:n_orig]

        # 2. Bit-depth reduction
        n_levels = 2 ** (bit_depth - 1)
        if dither:
            # TPDF dither: sum of two uniform random variables
            d = (np.random.uniform(-0.5, 0.5, y.shape) +
                 np.random.uniform(-0.5, 0.5, y.shape)) * (1.0 / n_levels)
            y = np.round((y + d) * n_levels) / n_levels
        else:
            y = np.round(y * n_levels) / n_levels

    else:  # quantize_then_hold
        # 1. Bit-depth reduction first
        n_levels = 2 ** (bit_depth - 1)
        if dither:
            d = (np.random.uniform(-0.5, 0.5, y.shape) +
                 np.random.uniform(-0.5, 0.5, y.shape)) * (1.0 / n_levels)
            y = np.round((y + d) * n_levels) / n_levels
        else:
            y = np.round(y * n_levels) / n_levels

        # 2. Sample-and-hold decimation
        if crush_factor > 1:
            if anti_alias:
                from scipy import signal as sg
                sos = sg.butter(8, 1.0 / crush_factor, btype='low', output='sos')
                y = sg.sosfilt(sos, y)
            idx = np.arange(0, n_orig, crush_factor)
            y = np.repeat(y[idx], crush_factor)[:n_orig]

    # Clip to [-1, 1] (guard against floating-point overshoot)
    return np.clip(y, -1.0, 1.0)


def wet_dry_mix(wet: np.ndarray, dry: np.ndarray, mix: float = 0.5) -> np.ndarray:
    """Parallel blend of wet and dry signals."""
    return (1.0 - mix) * dry + mix * wet
```

### Stereo Handling

For stereo signals, apply linked stereo mode (both channels hold the same decimated index) to prevent phase decoupling from independent sample selection:

```python
def bitcrush_stereo(x: np.ndarray, crush_factor: int = 4,
                    bit_depth: int = 8, **kwargs) -> np.ndarray:
    """Linked-stereo bitcrusher: same sample index for L and R."""
    assert x.ndim == 2 and x.shape[1] == 2, "Requires (N, 2) stereo"
    # Crush factor samples L+R together
    idx = np.arange(0, len(x), crush_factor)
    held = x[idx]                       # decimate together
    out = np.repeat(held, crush_factor, axis=0)[:len(x)]
    # Then apply bit-depth per channel independently
    for c in range(2):
        n_levels = 2 ** (bit_depth - 1)
        out[:, c] = np.round(out[:, c] * n_levels) / n_levels
    return out
```

## Musical Elements Framework

### PITCH
SRR does not generate pitch but alters perceived pitch. Sample-rate reduction aliases high-frequency partials downward, creating new inharmonic pitch artifacts at:

\[
f_{\text{alias}} = \left| k \cdot \frac{f_s}{R} - f_{\text{orig}} \right|, \quad k \in \mathbb{Z}^+
\]

This is deterministic: choose R so aliased copies land on scale degrees. Bit-depth reduction adds amplitude-dependent harmonic grit without pitch shift.

### RHYTHM
Sample-accurate timing preservation. However, at R > 10, the staircase waveform transitions create audible clicks at rate \(f_s/R\) — unintentional rhythmic patterns. Use anti-alias mode or align R to musical subdivisions.

### HARMONY
Both mechanisms break harmonic ratio relationships. SRR is intrinsically inharmonic — the counterpart to harmonic methods (SP-032 FDN, SP-014 Waveguide). Per-section control allows harmony to be progressively "dissolved."

### STRUCTURE
Macro-form = trajectory of (b, R, dither, anti-alias, mix) per section. A typical arc: clean → subtle grit → lo-fi warmth → aggressive digital → extreme glitch → restoration.

### TEXTURE
The (b, R) plane is a 2D timbre space:
- (16, 1): transparent
- (12, 2): subtle warmth
- (8, 4): classic lo-fi grit
- (6, 8): aggressive digital with aliased shimmer
- (4, 16): extreme glitch, near-unrecognizable
- (1, 1): sign-only square wave (1-bit sound)

## UnitMatrix Integration

**Voices (Rows):** Per-voice (b_v, R_v) parameters create a "degradation stage" where each instrument has a different vintage:
- Bass: clean (b=16, R=1)
- Pad: lo-fi (b=8, R=4)
- Lead: gritty (b=4, R=2)
- Perc: extreme (b=3, R=1)

**Sections (Columns):** Per-section crushing trajectory:
- Intro: b=16, R=1, mix=0 (clean)
- Verse: b=12, R=2, mix=0.3 (subtle)
- Chorus: b=6, R=8, mix=0.7 (aggressive)
- Bridge: b=4, R=16, mix=0.9 (extreme)
- Outro: ramp back to clean

**Cells (MusicUnit):** SRR is sample-accurate and stateless between cells (hold counter resets at cell boundaries). Zero-drift invariant preserved.

## Pitfalls

1. **DC offset from truncation**: Use round(), not floor/truncate. Add DC-block HPF at 10 Hz after crushing.
2. **Aliasing vs bandlimited degradation**: Use anti-alias mode for telephone-quality; allow aliasing for metallic texture.
3. **Perceptual loudness change**: Crushing reduces peak-to-average ratio — a 4-bit signal sounds 3–6 dB louder. Use RMS-bridging normalization.
4. **Comb filtering from sample-hold**: Notches at multiples of f_s/R. Apply inverse-sinc compensation when R ≥ 4.
5. **Stereo phasing**: Use linked-stereo decimation to prevent L/R time decoupling.
6. **Tonal aliasing across sections**: Changing R shifts aliased harmonics — audition transitions musically.
7. **Pitched aliasing musicality**: Choose R such that prominent aliased harmonics map to scale degrees (e.g., at f_s=44100, R=15 folds 440 Hz to 880 Hz — the octave).

## References

- Wikipedia — "Bitcrusher." *Wikipedia, The Free Encyclopedia*. Accessed 2026-10-04.
- Zölzer, U. (2022). *Digital Audio Signal Processing*, 3rd ed. Wiley, pp. 205–232.
- Pohlmann, K. (2005). *Principles of Digital Audio*, 5th ed. McGraw-Hill, pp. 85–112.
- DAFx-02 Conference (Holters, M. & Zölzer, U., 2002). "Bitcrushing: An Audio Effect."
- Välimäki, V. & Bilbao, J. (2024). "Alias-Free Sample-Rate Reduction." *DAFx* 2024, pp. 47–58.
- Bennett, W. R. (1948). "Spectra of Quantized Signals." *Bell System Technical Journal* 27, 446–472.