# Report SP-106: Phaser / Allpass Modulation Synthesis (APS)

## Summary

| Field | Value |
|---|---|
| **SP-ID** | SP-106 |
| **Name** | Phaser / Allpass Modulation Synthesis (APS) |
| **Layer** | absolute (Sound Production — Post-Processing / DSP) |
| **Acronym** | APS |
| **One-line description** | Classic modulation effect using a cascade of allpass filters with LFO-modulated break frequencies to create moving spectral notches through phase cancellation |
| **Summary table row** | `\|\|\| **SP-106** \| Phaser / Allpass Modulation Synthesis (APS) \| **Post-Processing / DSP** \| Phase-Swept Modulation / Spectral Notch Filtering \| Classic modulation effect using a cascade of allpass filters with LFO-modulated break frequencies to create moving spectral notches through phase cancellation when mixed with dry signal. $N/2$ notches for $N$ stages, depth/rate/feedback/sweep controls. $\mathcal{O}(N)$ per sample. Candidate: \`sound/effects/phaser.py\`. \|` |
| **Next free SP ID** | 107 |

## File Statistics

| Metric | Value |
|---|---|
| **methods_db.md before** | 23590 lines |
| **methods_db.md after** | 23734 lines |
| **Delta** | +144 lines (143 from detailed section + 1 from summary row) |
| **Standalone file** | `sound_method_SP-106_APS.md` (7,198 bytes) |
| **Report file** | `report_SP-106.md` |
| **Candidate code path** | `sound/effects/phaser.py` |

## Verification

### Summary table row (line 281)
```
||| **SP-106** | Phaser / Allpass Modulation Synthesis (APS) | **Post-Processing / DSP** | Phase-Swept Modulation / Spectral Notch Filtering | Classic modulation effect using a cascade of allpass filters with LFO-modulated break frequencies to create moving spectral notches through phase cancellation when mixed with dry signal. $N/2$ notches for $N$ stages, depth/rate/feedback/sweep controls. $\mathcal{O}(N)$ per sample. Candidate: `sound/effects/phaser.py`. |
```

### Detailed section header (line 23594)
`# Phaser / Allpass Modulation Synthesis (APS) (Sound Production Method SP-106)`

### grep verification
```
$ grep -n "SP-106" methods_db.md
281:||| **SP-106** | Phaser / Allpass Modulation Synthesis (APS) | ...
23594:# Phaser / Allpass Modulation Synthesis (APS) (Sound Production Method SP-106)
```

## Detailed Section Content Appended

The complete detailed section was appended to the end of methods_db.md. Its structure:

### Source
Zölzer 2011 (DAFX), Smith 2010 (PASP), Kiiski et al. 2016 (DAFx-16), Dattorro 1997 (JAES), Chamberlain 2021 (CCRMA).

### Layer
absolute — Sound Production (Post-Processing / DSP). Code path: `sound/effects/phaser.py`.

### Description
Phaser effect: allpass filters with time-varying break frequencies produce moving spectral notches via phase cancellation when mixed with dry signal. Distinction from flanger (delay-line-based) and relationship to chorus/vibrato.

### Technical Mechanics
- First-order IIR allpass: $H(z) = (a + z^{-1}) / (1 + a z^{-1})$
- Break frequency to coefficient: $a = [\tan(\pi f_b/f_s)-1] / [\tan(\pi f_b/f_s)+1]$
- Allpass chain phase sum: $\Theta_{\mathrm{total}}(\omega) = \sum_i \Theta_i(\omega)$
- Notch condition: $\Theta_{\mathrm{total}}(\omega) = (2k+1)\pi$
- Amplitude response: $|H| = \sqrt{1+g^2+2g\cos(\Theta_{\mathrm{total}})}$
- LFO modulation: sine LFO per stage with phase offset $\phi_i = i\pi/N$
- Feedback: $x'[n] = x[n] + \beta y_{\mathrm{wet}}[n-1]$
- $N/2$ notches for $N$ allpass stages
- Complexity: $\mathcal{O}(N)$ per sample

### Musical Elements Framework
- PITCH: No pitch change; selective partial attenuation creates timbral motion.
- RHYTHM: LFO independent or tempo-synced; transient-preserving.
- HARMONY: Selective cancellation alters perceived chord balance.
- STRUCTURE: Per-section parameter presets define macro-form.
- TEXTURE: Low N=2-4 subtle, N=4-8 classic, N=8-16 dense. Feedback adds resonance.

### UnitMatrix Integration
- Rows (Voices): Per-voice phaser instances with independent parameters
- Columns (Sections): Per-section presets defining phaser parameter arcs
- Cells: PhaserCellConfig dataclass with num_stages, lfo_rate/depth, feedback, sweep_range, wet_mix, stereo_spread, lfo_waveform
- Zero-drift: Allpass filters are unity-gain, no DC accumulation

### Pitfalls
1. Coefficient stability at extreme frequencies (clamp $f_b$ to [20, f_s/2-20] Hz)
2. LFO coefficient update cost (block update or table lookup)
3. Phase cancellation with downstream reverb
4. Transient smearing from dispersive allpass filters
5. LFO waveform choice (sine vs triangle vs square)
6. Notch density vs. CPU
7. Phaser vs. flanger confusion (allpass vs delay-line)
8. Stereo image collapse at mono sum

## Quirks & Pitfalls Hit

1. **Pipe-prefix normalization**: The patch tool's fuzzy matching caused extra `|` characters in the summary table row (`|||` → `||||`). Required a corrective patch to normalize back to `|||`. This is the known patch pitfall (b).

2. **Newline concatenation on append**: The original file did not end with a newline, so `cat temp >> target` concatenated the SP-106 section header with the last line of the existing content. Fixed with `sed -i` to insert a newline before the header.

3. **Symlink path resolution**: The write_file tool uses the resolved path via `musicom` repo, while read_file uses the `/opt/data/projects/` symlink path. Both resolve to the same file but the warning messages can be confusing.

4. **LaTeX backslash escaping**: The patch tool may double-escape LaTeX backslashes from `\` to `\\`. The summary table uses raw `$\\mathcal{O}$` (double backslash in the markdown) which is correct for Markdown that may pass through a LaTeX renderer. The detailed section uses `$\mathcal{O}$` (single backslash) which is correct for the final rendering. Both conventions are present in the existing file.

## Next Steps

- Next free SP ID: **SP-107**
- Implement the Python engine at `sound/effects/phaser.py`
- Add unit tests for the allpass filter chain and LFO modulation
- Integrate with the UnitMatrix workflow via the cell config dataclass
- Test with rendering pipelines (FluidSynth → phaser → output)