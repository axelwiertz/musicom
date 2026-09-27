# Report: SP-097 — Sub-Harmonic Oscillator Synthesis (SHOS)

## Method Identification
- **SP-ID**: SP-097
- **Method Name**: Sub-Harmonic Oscillator Synthesis
- **Acronym**: SHOS
- **Layer**: `absolute` (sound production — synthesis engines)
- **One-line description**: Generates undertone series $f_0/d$ for integer divisors $d$ from a shared master oscillator via phase-accumulator frequency division, producing phase-locked subharmonic chord stacks from a single root note.
- **Candidate code path**: `sound/synthesis/subharmonic.py`

## Summary Table Row (added)
```
| **SP-097** | Sub-Harmonic Oscillator Synthesis (SHOS) | **Synthesis Engines** | Subharmonic Chord Stacks / Divide-Down Bass Enhancement | Generates the undertone series $f_0/d$ for integer divisors $d \in \{1,2,\dots,6\}$ from a shared master oscillator via phase-accumulator frequency division. Produces phase-locked subharmonic chord stacks (root, P8, P12, 2×P8, M17, P19) from a single root note — a single-note chord. Three modes: subharmonic bass enhancement (Dbx 120-style $f_0/2$ synthesis), subharmonic chord stack (Moog Subharmonicon-style multi-divisor mix), and divide-down organ (top-octave frequency chain). Per-divisor gains, per-divisor fine detuning ($\pm\delta_d$ cents), polyrhythmic gating per divisor. $\mathcal{O}(D)$ per sample ($D=|\mathcal{D}|$). Candidate: `sound/synthesis/subharmonic.py`. |
```

## File Paths
- **methods_db.md**: `/opt/data/projects/Research/CompositionMethods/methods_db.md`
- **Standalone method file**: `/opt/data/projects/Research/CompositionMethods/sound_method_SP-097_SHOS.md`
- **Report file**: `/opt/data/projects/Research/CompositionMethods/report_SP-097.md`
- **Temp file**: `_temp_sp097.md` (created and deleted)
- **SoundFont path**: `$MUSICOM_SOUNDFONT` (via `utilities.env`)

## Line Counts
- **Before**: 20814 lines (methods_db.md)
- **After**: 21212 lines (methods_db.md)
- **Delta**: +398 lines
- **Standalone file**: 227 lines

## Complete Section Text Appended

The following section was appended to methods_db.md under the "Sound Production Methods Framework" section (after SP-096 HSOS):

```
# Sound Production Method SP-097 — Sub-Harmonic Oscillator Synthesis (SHOS)

### Source
- Oskar Sala, Mixtur-Trautonium (1948–1952): first electronic instrument with a dedicated subharmonic generator...
- Dbx 100 "Boom Box" (1976) / Dbx 120A Subharmonic Synthesizer...
- Moog Subharmonicon (2020): analog semi-modular synthesizer...
- Technical references: Chamberlin, H. (1985). *Musical Applications of Microprocessors*...
- Candidate code path: `sound/synthesis/subharmonic.py`

### Layer
`absolute` (sound production — synthesis engines).

### Description
Sub-Harmonic Oscillator Synthesis (SHOS) generates the undertone series — frequencies at $f_0/n$ for integer divisors $n$ — from a single master oscillator running at the root pitch. Three use cases: subharmonic bass enhancement (Dbx 120-style), subharmonic chord stacks (Moog Subharmonicon-style), and divide-down organ.

### Technical Mechanics
1. Analog frequency division (flip-flop method): $f_{\text{sub},n} = f_0/n$
2. Digital phase-accumulator frequency division: $\phi_n[n+1] = \phi_n[n] + \Delta_m/n$
3. Phase-locked waveform synthesis: $y[n] = \sum g_d \cdot w_d(\phi_m/d \bmod 2\pi)$
4. Bass enhancement algorithm (Dbx-style): detect $f_0$, synthesize $f_0/2$, envelope match, mix
5. Per-divisor pitch detuning: $f_{\text{sub},d} = f_0/d \cdot 2^{\delta_d/1200}$
6. Polyrhythmic gating: $\text{gate}_d[t] = [t \equiv 0 \pmod{d}]$
7. Cost: $O(D)$, ~13 operations per sample for 6 divisors

### Musical Elements Framework
- PITCH: Undertone series mapping ($d=2$ = P8 below, etc.)
- RHYTHM: Polyrhythmic gating per divisor
- HARMONY: Divisors {1..6} = maj13$^{\text{(omit11)}}$ from single root
- STRUCTURE: Per-section divisor sets = macro-form
- TEXTURE: Density scales with $|\mathcal{D}|$

### UnitMatrix Integration
- Voices = independent SHOS engines with per-voice divisor sets
- Sections = per-section divisor/gain/detune profiles
- Cells = pitch, divisors, gains, detune, waveforms, gate patterns

### Pitfalls
1. Square-wave aliasing: use PolyBLEP
2. Phase accumulator wraparound drift: use 64-bit or reset on zero-crossing
3. Pitch ambiguity below ~40 Hz: limit divisors or use polyrhythmic gating
4. Divisor density at high fundamentals >2kHz: apply lowpass filter
5. Subharmonic monotony: add per-divisor detuning
6. Bass-enhancement phase cancellation: use decorrelation
7. Polyrhythmic period growth: precompute lcm

### Python Implementation Sketch
Full implementation with UnitMatrixComposer integration and wavetable-based per-sample synthesis loop.

### References
Oskar Sala, Chamberlin, Dodge & Jerse, Moog Music, Puckette, Roads
```

## Technical Mechanics Summary

The core of SHOS is phase-accumulator frequency division:
- Master oscillator at $f_0$ increments phase $\phi_m$ by $\Delta_m = 2\pi f_0 / f_s$
- Each subharmonic divisor $d$ reads the slave phase $\phi_d = \phi_m / d \bmod 2\pi$ and evaluates $w(\phi_d)$
- Output is a weighted sum $y[n] = \sum g_d \cdot w(\phi_d[n])$
- The spectrum descends from $f_0$ (division architecture vs multiplication/ascending in all other synthesis)
- Cost is linear in divisor count $D$, one of the cheapest polyphonic methods

## Layer Classification
`absolute` per LAYER_ARCHITECTURE.md: sound production methods that translate symbolic MIDI into final audio waveforms. SHOS directly produces audio buffer samples from pitch, divisor set, and gain parameters — no intermediate symbolic representation.

## Quirks/Pitfalls Hit During Implementation
1. **Summary table pipe formatting**: The existing table has inconsistent pipe prefixes (single `|` for header and early entries, some mix with `||`). After several patch iterations (double→single→triple→double→back), the final table is consistent with `|` prefix matching the header format.
2. **LaTeX backslash escaping**: The patch tool's diff output shows `\$` and `\\$` escaping that differs from the raw file content. Using `cat -A` via terminal revealed the true content.
3. **Patch matching with math symbols**: Dollar signs (`$`) in LaTeX math expressions must match exactly between old_string and the file content. Use terminal-based `sed` when content has abundant math delimiters.
4. **Append operation**: The `cat >>` append worked cleanly. The temp file was 24,616 bytes, which appended 397 new lines to the 20814-line file (20814 → 21211 → 21212 after table edit).

## Verification
- `wc -l methods_db.md` = 21212 (previously 20814, delta +398)
- `grep SP-097` confirms both summary table row AND detailed section
- `sound_method_SP-097_SHOS.md` exists and contains full write-up
- `report_SP-097.md` exists (this file)

## Next Free SP ID
**SP-098** is the next free ID.

---

*Generated 2026-09-27 by sound-production research cron job. Hermes Agent / Nous Research.*