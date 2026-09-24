# Report SP-094 — Through-Zero Frequency Modulation Synthesis (TZFM)

## Method Identification

| Field | Value |
|---|---|
| **Method ID** | SP-094 |
| **Name** | Through-Zero Frequency Modulation Synthesis |
| **Acronym** | TZFM |
| **Layer** | `absolute` (sound production — synthesis engines) |
| **One-line description** | Modulates carrier frequency with depth sufficient to drive the instantaneous frequency below zero, reversing the phase accumulator direction instead of stalling at 0 Hz, preserving pitch regardless of modulation depth. |
| **Candidate code path** | `sound/synthesis/tzfm.py` |

## Summary Table Row

```
|| **SP-094** | Through-Zero Frequency Modulation Synthesis (TZFM) | **Synthesis Engines** | Pitch-Stable Extreme FM / Glassy Digital & Brass Timbres | Modulates carrier frequency with depth sufficient to drive the instantaneous frequency below zero, reversing the phase accumulator direction instead of stalling at 0 Hz. TZFM preserves the carrier pitch $f_c$ exactly regardless of modulation depth $d$ via bidirectional phase accumulation, enabling arbitrarily high modulation indices with zero DC drift. Produces glassy, brassy, and complex bell spectra at extreme depths where conventional FM would detune. $\mathcal{O}(1)$ per sample. Candidate: `sound/synthesis/tzfm.py`. |
```

## File Statistics

| Metric | Value |
|---|---|
| **Line count before** | 20023 |
| **Line count after** | 20256 |
| **Delta** | +233 lines |
| **Detailed section start line** | 20025 |
| **Detailed section end line** | 20255 |

## Files Written

| File | Path |
|---|---|
| **Standalone sound method** | `/opt/data/projects/Research/CompositionMethods/sound_method_SP-094_TZFM.md` |
| **Report** | `/opt/data/projects/Research/CompositionMethods/report_SP-094.md` |

## Verification

| Check | Result |
|---|---|
| `grep 'SP-094' methods_db.md` | 2 matches (summary row + detailed section header) |
| `grep 'SP-093' methods_db.md` | present (not clobbered) |
| `grep 'SP-047' methods_db.md` | present (Vector Synthesis still exists, not duplicated) |
| Standalone file exists | ✅ |
| Line count consistent | 20023 → 20256 |

## Technical Mechanics Summary

TZFM is a modification to the standard digital FM phase accumulator that preserves the sign of the phase increment:

1. **Standard FM**: $\phi[n+1] = (\phi[n] + \Delta\phi) \bmod 1$ — erases negative $\Delta\phi$, oscillator stalls at 0 Hz, DC offset builds, pitch drifts upward.
2. **TZFM**: Same modulo, but the modulo naturally preserves direction — when $\Delta\phi < 0$, $\psi$ _decreases_ because $(\psi + \Delta) \bmod 1$ in IEEE float gives $\psi + \Delta$ (negative) + $1.0$ (the mod effect), producing a descending table read. TZFM is thus implementable with zero extra operations over standard FM in floating point, or with one sign check + conditional in fixed-point.
3. **Pitch stability proof**: $\bar{f} = f_c + d \cdot \overline{m[n]} = f_c$ for any zero-mean modulator, regardless of $d$.
4. **Bessel expansion holds exactly**: $y(t) = \sum J_k(\beta)\cos((f_c + k f_m)t)$ with faithful bandwidth $BW \approx 2(\beta + 1)f_m$ at all $\beta$.
5. **Feedback TZFM** (SP-094 + SP-017 hybrid): carrier output fed back as modulator — produces deterministic chaos, period doubling, and subharmonics at moderate gains; the "complex oscillator" topology.

## Quirks & Pitfalls Hit

1. **Initial method (Vector Synthesis) was a duplicate of SP-047**: Discovered via grep after initial patch — had to revert both the summary row and the detailed section, then rewrite from scratch. SP-047 "Vector Synthesis (4-Corner Wavetable Crossfade)" already exists at line 159 in the SP summary table.
2. **Concatenation issue on append**: The `cat >>` append did not insert a newline before the new content, which merged with the last line of the original file. Fixed by adding `echo "" >>` before append.
3. **Summary table pipe formatting**: After patch, rows had `|||` triple-pipe prefix. Read the actual content with `cat -A` to distinguish line-number separator `|` from content pipes. The double `||` was actually correct.

## Next Free SP ID

The highest existing SP-ID is **SP-094** (this method). The next free SP-ID is **SP-095**.