# Report — Method 076: Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC)

## Summary
- **Method ID**: 076 (next available after DB had advanced to 075 SOM-C)
- **Name**: Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC)
- **Paradigm**: Rules-Based (deterministic substitution)
- **LAYER**: concrete (generates events that fill UnitMatrix cells; feeds `generators/`)
- **One-line description**: Generate music from the Thue–Morse automatic sequence $t(n)=s_2(n)\bmod 2$ (substitution $0{\to}01$, $1{\to}10$): bits map to pitch intervals/onset patterns, Prouhet's equal-power partition gives balanced multi-voice harmony, and self-similarity + overlap-freeness yields non-repeating, recursively nested macro-form.

## Summary-Table Row (appended, line 85)
```
| **076** | concrete | Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Scale-mapped) | Grid-Locked | None (Self-similar recurrence) | $\mathcal{O}(N)$ | Generates music from the Thue–Morse automatic sequence $t(n)=s_2(n)\bmod 2$ (parity of the base-2 digit sum), the fixed point of the substitution $0{\to}01, 1{\to}10$. Bits map to pitch intervals/onset patterns; Prouhet's equal-power partition (1851) gives balanced multi-voice harmony; self-similarity + overlap-freeness (no $XXX$ cube, Thue 1906/1912) yield aperiodic, recursively nested macro-form (statement/complement). Deterministic self-similar sibling of 002 Markov / 053 LFC; word-theoretic cousin of 069 CWCC / 019 L-System; aperiodic-beat cousin of 012 Euclidean Groove. |
```

## Line Count
- Before: 15401
- After: 15512 (delta +111)

## Files
- **DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row at line 85; detailed section starts at line 15403)
- **Standalone**: `/opt/data/projects/Research/CompositionMethods/method_076_PTM-ASC.md`
- **Report**: `/opt/data/projects/Research/CompositionMethods/report_076.md`
- **Candidate code path**: `generators/automatic_sequence.py` (pure sequence math may live in `rules/automatic_sequence.py`)

## Classification Details
| Field | Value |
|---|---|
| Method ID | 076 |
| Name | Prouhet–Thue–Morse Automatic Sequence Composition |
| Acronym | PTM-ASC |
| Paradigm | Rules-Based |
| Layer | concrete |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Weak (Scale-mapped) |
| Metric Binding | Grid-Locked |
| Memory Depth | None (Self-similar recurrence) |
| Time Complexity | O(N) |

## Why this method (novelty check)
Searched `methods_db.md` for `thue`, `morse`, `prouhet`, `automatic sequence`, `paperfold`, `kolakoski`, `de bruijn`, `latin square`, `golomb`. No matches — the Thue–Morse sequence was NOT already in the DB. It is a genuinely novel, classic combinatorial object (Prouhet 1851 / Thue 1906 / Morse 1921) not yet catalogued, and it fills a distinct niche: a **deterministic, self-similar, overlap-free, perfectly balanced aperiodic binary word**. It is the aperiodic-beat cousin of 012 Euclidean Groove (which is *periodic* balanced), a word-theoretic cousin of 069 CWCC (Christoffel words) and 019 L-System (both substitution systems), and a deterministic sibling of 002 Markov / 053 LFC (random lattice walks).

## Complete Method Section (as appended to methods_db.md)
Appended verbatim from `_temp_method_076.md`. Full text is reproduced in `method_076_PTM-ASC.md` (which is a superset — it adds extended math, the implementation sketch, and references). The DB section begins:

```
# Prouhet–Thue–Morse Automatic Sequence Composition (PTM-ASC) (Method 076)
```

and contains the required subsections: `### Layer`, `### Source`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Technical Mechanics`, `### Implementation Requirements (Python / NumPy)`, `### Pitfalls`, `### Comparison With Related Methods`, `### References`.

## Verification
- `wc -l` before 15401 → after 15512 (+111).
- Grep confirms summary row `**076**` present and section header `(Method 076)` at line 15403.
- Both known patch pitfalls clean:
  1. **Backslash escape**: grep for `\\mathcal` / `\\to` / `\\bmod` (double backslash) → 0 matches; the row uses single backslashes.
  2. **`||` prefix**: grep for `^|| **076` → 0 matches; single leading `|`.
- Next free ID: **077**.

## Quirks / Pitfalls Encountered
1. **Stale-ID guard honored**: the DB had already advanced to 075 (the skill's "073/075 exist" hint was right, but the table top showed max 075). Dynamic scan of the summary table confirmed max = 075 → used 076. (Note: the table skips 058 — NODE-CTC has a full detailed section at line 9615 but no summary-table row; 059 follows 057 directly. This is pre-existing, not introduced here.)
2. **Layer tag**: added an explicit `### Layer` line as the FIRST subsection inside the detailed section (the task required the layer stated "in the appended section header"; putting `concrete` both in the `### Layer` subsection and in the summary-table row satisfies the Layer column + section requirement). Prior recent sections (075) did not carry an inline `### Layer`, but the Layer column in the table + the architecture doc require it, so it was included for correctness.
3. **`\bmod` and `\to` macros**: verified no double-escaping was introduced by the patch tool (a known hazard per the task); both stayed single-backslash.
4. **Composition workflow compliance**: the implementation sketch follows AGENTS.md (engine-authored MIDI via `UnitMatrixComposer`, `create_note_unit`, `composer.validate()` gate before `to_midi()`); no raw `mido` authoring, no `sys.path` hacks.

## Next free ID
**077**
