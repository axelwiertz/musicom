# Report — Method 079: Tintinnabuli Composition (TINC)

**Date:** 2026-09-06
**Agent:** musicom-method-master-map research job

## Summary
- **Method ID:** 079
- **Name:** Tintinnabuli Composition (TINC)
- **Paradigm:** Rules-Based (Deterministic)
- **LAYER:** concrete
- **One-line description:** Realize Arvo Pärt's tintinnabuli style ("1 + 1 = 1"): project a stepwise diatonic M-voice note-by-note onto a single fixed tonic triad to form a triad-locked T-voice; every dyad contains exactly one triad tone → constant consonance, no functional harmony, bell-like sacred-minimalist texture.

## ID resolution
Scanned summary table (`| **NNN** |` rows) + standalone `method_*.md` / `report_*.md` files. Highest existing algorithmic ID = **078** (Ising Model Equilibrium Composition). Next free ID = **079**. No Tintinnabuli method existed (grep for tintinnabuli/Pärt/magic-square/dice found only HC-024's historical mention of 18th-c. dice games and 065 TTSMC's "magic square" serial matrix — no duplication).

## Summary-table row appended
```
| **079** | concrete | Tintinnabuli Composition (TINC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Strict (Static Triad) | Grid-Locked / Continuous | Meso / Phrase | $\mathcal{O}(N)$ | Realizes Arvo Pärt's tintinnabuli style (1976, "1 + 1 = 1"): a stepwise diatonic M-voice ($|m_{i+1}-m_i| \le 2$) is projected note-by-note onto a single fixed tonic triad to form a T-voice (nearest triad tone above/below per a position sequence $P$). Every dyad contains exactly one triad tone → constant consonance, no functional harmony; structure from the position pattern + additive note add/drop; bell-like sacred-minimalist texture. Deterministic rules-based sibling of 056 SCCC / 066 GTTM-HC; static-harmony foil to 011 Voice-Leading Graph. |
```

## Line counts
- **Before:** 16135 lines
- **After:** 16256 lines (delta +121)

## Files
- **Standalone:** `/opt/data/projects/Research/CompositionMethods/method_079_TINC.md`
- **DB section:** appended to `/opt/data/projects/Research/CompositionMethods/methods_db.md` (header `# Tintinnabuli Composition (TINC) (Method 079)`, with `### Source`, `### Layer`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Technical Mechanics`, `### Implementation Requirements`, `### Pitfalls`, `### Comparison With Related Methods`, `### References`).

## Candidate code path
`generators/tintinnabuli.py` (new module; concrete layer, feeds `UnitMatrixComposer.fill_voice_section`).

## Classification details
| Axis | Value |
|---|---|
| Paradigm | Rules-Based |
| Layer | concrete |
| Tonal Gravity | Strict (Static Triad) |
| Metric Binding | Grid-Locked / Continuous |
| Memory Depth | Meso / Phrase |
| Time Complexity | $\mathcal{O}(N)$ |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |

## Musical Elements mapping (UnitMatrix)
- **PITCH** = stepwise M-voice + nearest-triad projection T-voice.
- **RHYTHM** = homorhythmic pairing (or decoupled additive onsets).
- **HARMONY** = single static tonic triad; no progression; root/third/fifth coloring.
- **STRUCTURE** = position sequence $P$ + additive note add/drop; per-section mode/register.
- **TEXTURE** = transparent 1+1=1 dyad atoms; bell-like sacred minimalism.
- **Voices (rows)** = M-voice row + one-or-more T-voice rows (all projections of the same M-voice).
- **Sections (columns)** = (mode, triad, position-pattern) triples; additive length.
- **Cells (MusicUnit)** = one dyad (m_i, t_i); both voices share event count → zero-drift gate preserved.

## Pitfalls hit / quirk notes
- Patch pitfall (b) checked: summary row has single `|` prefix (no `||`), confirmed via `grep -c '^| \*\*079\*\*'` → 1.
- Patch pitfall (a) checked: LaTeX uses single backslash `\mathcal{O}(N)` (no double-escape), confirmed via grep for `\\mathcal` → none.
- UTF-8 note: Pärt renders as multi-byte in terminal `cat -A` (M-CM-... escapes) but the bytes on disk are correct UTF-8 ("Pärt"), verified by the raw write_file content; no mangling in the actual file.
- No existing method duplicated; Tintinnabuli was genuinely absent.

## Next free ID
**080**.
