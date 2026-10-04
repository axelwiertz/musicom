# Report SP-104: Bitcrushing / Sample Rate Reduction Synthesis (SRR)

## Metadata

| Field | Value |
|---|---|
| **SP-ID** | SP-104 |
| **Method Name** | Bitcrushing / Sample Rate Reduction Synthesis |
| **Acronym** | SRR |
| **Layer** | absolute (sound production — Post-Processing / DSP) |
| **One-line description** | Intentionally reduces bit depth and/or sample rate of a rendered buffer via re-quantization and sample-and-hold decimation, producing quantization noise, aliased metallic artifacts, and lo-fi texture |
| **Candidate code path** | `sound/effects/bitcrusher.py` |
| **Summary-table row (for Sound Production Methods Framework)** | `|| **SP-104** | Bitcrushing / Sample Rate Reduction Synthesis (SRR) | **Post-Processing / DSP** | Lo-Fi Degradation / Quantization Noise & Aliasing | Intentionally reduces bit depth and/or sample rate of a rendered buffer via re-quantization (rounding to $b$ bits) and sample-and-hold decimation (crush factor $R$). Produces characteristic quantization noise, aliased metallic artifacts, and lo-fi texture. Per-voice $b$ and $R$ create a "degradation stage." $\mathcal{O}(1)$ per sample. Candidate: `sound/effects/bitcrusher.py`. |` |

## Line Count

| Metric | Before | After | Delta |
|---|---|---|---|
| `methods_db.md` line count | 23062 | 23236 | **+174 lines** |

## Files Created

| File | Path | Size |
|---|---|---|
| Detailed section (appended to methods_db.md) | append via `_temp_sp104.md` | ~17 KB |
| Standalone method file | `sound_method_SP-104_SRR.md` | ~11.5 KB |
| Report | `report_SP-104.md` | this file |

## Detailed Section Text (Appended to methods_db.md)

The following section was appended to methods_db.md under the "Sound Production Methods Framework" section:

```
# Bitcrushing / Sample Rate Reduction Synthesis (SRR) (Method SP-104)

### Source
Wikipedia — "Bitcrusher." ... — Zölzer, U. (2022). ... — Pohlmann, K. (2005). ...
— DAFx-02 Conference (Holters, M. & Zölzer, U., 2002). "Bitcrushing: An Audio Effect."
— Välimäki, V. & Bilbao, J. (2024). "Alias-Free Sample-Rate Reduction." *DAFx* 2024.
— Bennett, W. R. (1948). "Spectra of Quantized Signals."

### Layer
**absolute** — sound production (Post-Processing / DSP). Applies bit-depth reduction
(re-quantization) and/or sample-rate reduction (sample-and-hold decimation) to a rendered
mono/stereo audio buffer, producing characteristic lo-fi quantization noise, aliasing
artifacts, and digital distortion. Candidate code path: `sound/effects/bitcrusher.py`.

### Description
Bitcrushing / Sample Rate Reduction Synthesis (SRR) is a dual-method degradation
architecture that intentionally reduces the digital audio resolution of a rendered
signal through two independent mechanisms:
1. Bit-depth reduction (re-quantization)
2. Sample-rate reduction (decimation with sample-and-hold)

### Technical Mechanics
1. Bit-Depth Reduction: x_b[n] = round(x[n] * 2^{b-1}) / 2^{b-1}
   SQNR ≈ 6.02b + 1.76 dB, sigma_q = 2^{-b}/sqrt(12)
2. Sample-Rate Reduction: y[n] = x[R * floor(n/R)]
   Zero-order hold, aliasing at multiples of f_s/2R
3. Combined: y[n] = requantize_b(hold_R(x[n]))
4. Complexity: O(1) per sample

### Musical Elements Framework
PITCH: No pitch generation but aliased copies at |k*f_s/R - f_orig| create new pitches.
RHYTHM: Sample-accurate; staircase clicks at f_s/R can create rhythmic patterns.
HARMONY: Both mechanisms break harmonic ratio relationships — SRR is inharmonic.
STRUCTURE: Per-section (b, R, dither, anti_alias, mix) trajectory.
TEXTURE: 2D timbre space from (16,1)=transparent to (1,1)=sign-only square wave.

### UnitMatrix Integration
Voices: Per-voice (b_v, R_v) = degradation stage for each instrument.
Sections: Per-section crusher parameters define form arc.
Cells: Sample-accurate, zero-drift invariant preserved.

### Pitfalls
1. DC offset from truncation
2. Aliasing vs bandlimited degradation
3. Perceptual loudness change (3-6 dB)
4. Comb filtering from sample-hold
5. Stereo phasing
6. Tonal dependency across sections
7. Pitched aliasing musicality (choose R for consonant folds)
```

## Technical Mechanics Summary

**Core equations:**

1. **Bit-depth reduction**: \(x_b[n] = \mathrm{round}(x[n] \cdot 2^{b-1}) / 2^{b-1}\)
   - SQNR ≈ 6.02b + 1.76 dB
   - Quantization noise RMS = \(2^{-b}/\sqrt{12}\)

2. **Sample-rate reduction (sample-and-hold)**: \(y[n] = x[R \cdot \lfloor n/R \rfloor]\)
   - Aliased partials at \(f_{\text{alias}} = |k \cdot f_s/R - f_{\text{orig}}|\)
   - Zero-order hold rolloff: \(|H_{\mathrm{sh}}(f)| = \mathrm{sinc}(f/f_s) \cdot \mathrm{sinc}(f/(f_s/R))\)

3. **Combined**: \(y[n] = \mathrm{requantize}_b(\mathrm{hold}_R(x[n]))\)

## Quirks and Pitfalls Hit

- **Table format inconsistency**: The SP summary table rows use `||` prefix (double pipe with space) for most recent entries but older entries used `|||` (triple pipe). Used `||` matching the immediate predecessor SP-103 format.
- **LaTeX backslash double-escape watch**: The patch tool may double-escape backslashes. Verified the inserted row has single `\mathcal{O}` and `\$` — no double-escape occurred since the `old_string` and `new_string` had matching escape levels.
- **The `|---|---|` sentinel**: Must be preserved at end of summary table; the new row was inserted before it.
- **No `||` prefix corruption**: Verified the patch didn't add a `||` prefix to the wrong line or convert the sentinel.

## Next Free SP-ID

The next free Sound Production method ID is **SP-105**, ready for the next research agent.

## Verification

- [x] Summary table updated with SP-104 row (line 278)
- [x] Detailed section appended to methods_db.md (~line 23076)
- [x] `sound_method_SP-104_SRR.md` created (standalone)
- [x] `report_SP-104.md` created (this file)
- [x] `_temp_sp104.md` cleaned up
- [x] Line count: 23062 → 23236 (+174)
- [x] Grep confirms "SP-104" appears in both summary table and detailed section