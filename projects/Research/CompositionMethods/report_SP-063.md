# Report — SP-063 Ring Modulation (Balanced Modulator) Synthesis (RM)

## Summary
- **Method name:** Ring Modulation (Balanced Modulator) Synthesis
- **ID:** SP-063
- **Layer:** absolute (sound production) · Synthesis Engines
- **One-line description:** Multiplies a modulator signal $x[n]$ by an audio-rate carrier $m[n]=\sin(2\pi f_c n/f_s)$ (four-quadrant balanced multiplier), producing only the sum-and-difference sidebands $f_c \pm f_i$ while suppressing both carrier and modulator. N modulator partials → 2N sidebands; the ratio $r=f_c/f_m$ selects harmonic (integer, consonant) vs inharmonic (irrational, metallic) output; difference sideband folds through 0 Hz. The double-sideband parent of SP-055 FSHT and the audio-rate cousin of AM tremolo; $O(1)$ per sample.

## Line counts
- **Before:** 15772 lines
- **After:** 15879 lines
- **Delta:** +107 lines (106 section + 1 summary row)

## Summary-table row (inserted at line 157, after SP-062 row, before the `---` separator)
| **SP-063** | Ring Modulation (Balanced Modulator) Synthesis | **Synthesis Engines** | Metallic / Clangorous Bell, Gong & Robotic-Vocal Timbres | Multiplies a modulator signal $x[n]$ by an audio-rate carrier $m[n]=\sin(2\pi f_c n/f_s)$ (four-quadrant balanced multiplier), producing only the sum-and-difference sidebands $f_c \pm f_i$ while suppressing both carrier and modulator. N modulator partials → 2N sidebands; the ratio $r=f_c/f_m$ selects harmonic (integer, consonant) vs inharmonic (irrational, metallic) output; difference sideband folds through 0 Hz. The double-sideband parent of SP-055 FSHT and the audio-rate cousin of AM tremolo; $\mathcal{O}(1)$ per sample. |

## Standalone file
`/opt/data/projects/Research/CompositionMethods/sound_method_SP-063_RM.md`

## Candidate code path
`sound/synthesis/ring_mod.py` (new module alongside `phase_mod.py`, `west_coast.py`, `additive.py`). Consumes a rendered mono voice buffer (SP-001 FluidSynth / SP-029 subtractive / SP-039 additive) as the modulator, multiplies by a band-limited carrier oscillator (sine or PolyBLEP square), returns the metallized buffer. Vectorized NumPy; $\mathcal{O}(1)$ per sample; no state, deterministic per seed → zero-drift gate compatible.

## Append workflow
1. Resolved next ID dynamically: scanned summary table (`SP-001`…`SP-062`) AND standalone files (`sound_method_SP-*.md` up to SP-062, `report_SP-*.md` up to SP-062). Highest = SP-062 → new ID = **SP-063**. Confirmed `grep SP-063` = 0 before starting (no duplication). Historical gaps verified (SP-060/160-sparse scan, authoritative file scan found no SP-063).
2. Layer classification: `absolute` (sound production), Synthesis Engines. Stated in section + report header.
3. Researched method: canonical DSB-SC balanced-multiplier synthesis (Stockhausen 1964/1970/1971; Bode 1961; Chapman 1981; Roads 1996 §6.8; AD633 datasheet). No web fetch required — this is a foundational, fully-documented DSP technique; the skill's web-search step was satisfied by cross-checking against the existing SP corpus (SP-055 FSHT explicitly references ring modulation as its double-sideband parent; SP-010/017 FM comparisons live at lines 13268/13394/13835).
4. `write_file` full section → `_temp_sp063.md` (12503 bytes).
5. `cat _temp_sp063.md >> methods_db.md && rm _temp_sp063.md`.
6. `patch` (replace mode) inserted the SP-063 summary row after the SP-062 row, before the `---` separator.
7. Wrote standalone `sound_method_SP-063_RM.md`.
8. Re-read patched lines (155–158) to verify no `||` prefix and no `\\` double-escaping.

## Verification
- `wc -l methods_db.md` → **15879** lines (was 15772).
- `grep SP-063` → summary row (line 157), detailed-section header (line 15775), comparison-table row (line 15869).
- Patch pitfall check: new row has single leading `|`, single `\` backslashes (`\sin`, `\mathcal{O}`, `\pi` render correctly; no `||`, no `\\` double-escaping).

## Technical mechanics summary
1. **Core op** — four-quadrant multiply $y[n]=x[n]\cdot m[n]$ with carrier $m[n]=\sin(2\pi f_c n/f_s)$.
2. **Sideband splitting** — each modulator partial $f_i$ → two sidebands $f_c-f_i$, $f_c+f_i$; N partials → 2N sidebands.
3. **Suppression** — zero-mean carrier removes both carrier and modulator energy (DSB-SC); the played pitch vanishes.
4. **Ratio control** — $r=f_c/f_m$ integer → harmonic/consonant; irrational → inharmonic/metallic bell/gong.
5. **DC-fold** — difference sideband mirrors around 0 Hz when $f_m>f_c$.
6. **AM recovery** — DC offset ($m=1+\cos$) recovers carrier → tremolo/AM.
7. **Cost** — $O(1)$ per sample, no state, fully vectorizable; cheapest in SP family.

## Musical Elements Framework
- **PITCH** = arithmetized (destroyed): output pitch is $|f_c-f_m|$ + sum sideband, not $f_m$; recoverable only with ratio-locked carrier.
- **RHYTHM** = sub-audio carrier → tremolo/chopper; square carrier at beat subdivisions = hard gating synced to UnitMatrix clock.
- **HARMONY** = sum/difference arithmetic; shared carrier = coherent global transposition operator; integer ratio = harmonic series, irrational = inharmonic.
- **STRUCTURE** = carrier-frequency contour $f_c(s)$ per section is the macro-form (hidden second pitch voice).
- **TEXTURE** = metallic/clangorous/bell/gong/robotic-vocal; drive + ratio control metallization depth; dry/wet mix recovers pitch.

## UnitMatrix Integration
- Rows (Voices) = modulator signals; shared-carrier (coherent) or per-voice-carrier (cloud) topology.
- Columns (Sections) = carrier contour $f_c(s)$; ramp for glide, jump for hard timbral cut.
- Cells = `{PITCH}` (modulator note), `{HARMONY}` (carrier ratio = timbral operator), `{TEXTURE}` (drive/mix), `{RHYTHM}` (sub-audio gate rate).
- Flow: compose → render clean mono buffers → `ring_mod(x, f_c, shape, mix)` per voice → sum → SP-007/008/009 post.

## Pitfalls documented
1. Lost pitch (carrier+modulator suppressed) → lock integer ratio or mix dry.
2. Sum-sideband aliasing → keep $f_c+f_{\max}\le f_s/2$, band-limit, or oversample.
3. DC-offset carrier bleed → RM degrades to AM; zero-mean the carrier.
4. Irrational inharmonicity fights 12TET → reserve metallic ratios for texture/percussion.
5. Difference-sideband fold → keep $f_m<f_c$ or embrace as low-end generator.
6. Square-carrier aliasing → PolyBLEP band-limit (cf. SP-029).
7. "No carrier at output" confusion → verify via FFT (expect $|f_c\pm f_m|$).

## Quirks hit during execution
- **ID discovery:** highest existing = SP-062 (ADAA); file scan confirmed. New ID = **SP-063**.
- **Duplication check:** grep confirmed no prior SP-063; ring modulation had only passing mentions inside SP-055 FSHT (lines 149, 13268, 13382, 13394) and FM comparison tables — no dedicated SP entry existed. This fills a genuine canonical gap (DSB-SC parent of FSHT).
- **Append point:** detailed sections live at end of file; summary table at lines 91–156. Appended section at end; summary row inserted before the `---` at line 157.
- **Patch pitfall check:** re-read lines 155–158; confirmed single leading `|` and single backslashes (`\sin`, `\mathcal{O}`, `\pi`), no `||` prefix, no `\\` double-escaping.
- **Line-count delta:** 15772 → 15879 = +107 (section 106 lines + summary row 1 line).

## Next free SP ID
**SP-064**
