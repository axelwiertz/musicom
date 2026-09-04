# Report — Method 077: De Bruijn Universal Cycle Composition (DBUC)

## Summary
- **Method ID**: 077 (next available after DB max = 076 PTM-ASC)
- **Name**: De Bruijn Universal Cycle Composition (DBUC)
- **Paradigm**: Rules-Based (deterministic combinatorial construction)
- **LAYER**: concrete (generates events that fill UnitMatrix cells; feeds `generators/`)
- **One-line description**: Generate music from a de Bruijn sequence $B(k,n)$ — a cyclic word of length $n^k$ whose every length-$k$ window over an $n$-symbol alphabet appears exactly once — decoded into pitch (scale-degree alphabet), rhythm (binary hit alphabet), harmony (chord-symbol alphabet), structure (Hamiltonian/Eulerian cycle + Lyndon-word blocks), and texture (de Bruijn tori + offset voices).

## Summary-Table Row (appended, line 86)
```
| **077** | concrete | De Bruijn Universal Cycle Composition (DBUC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Mode-pinned) | Grid-Locked | Local (Length-$k$ window) | $\mathcal{O}(n^k)$ | Generates music from a de Bruijn sequence $B(k,n)$ — a cyclic word of length $n^k$ whose every length-$k$ window over an $n$-symbol alphabet appears exactly once. Alphabet = scale degrees (pitch), $\{0,1\}$ (rhythm), or chord symbols (harmony); the de Bruijn graph Hamiltonian/Eulerian cycle and Lyndon-word (FKM/Duval) decomposition give exhaustive macro-form with zero verbatim repetition; de Bruijn tori give 2D texture. Deterministic exhaustive sibling of 002 Markov / 041 ACOPF (which walk the same graph probabilistically); maximal-variety complement of 076 PTM-ASC (avoids repetition) and 069 CWCC (balance); graph-theoretic cousin of 011 Voice-Leading Graph Search. |
```

## Line Count
- Before: 15647
- After append: 15771 (delta +124 for the detailed section)
- After summary row: 15772 (delta +125 total)

## Files
- **DB**: `/opt/data/projects/Research/CompositionMethods/methods_db.md` (summary row at line 86; detailed section starts at line 15649)
- **Standalone**: `/opt/data/projects/Research/CompositionMethods/method_077_DBUC.md`
- **Report**: `/opt/data/projects/Research/CompositionMethods/report_077.md`
- **Candidate code path**: `generators/debruijn_sequence.py` (pure sequence math may live in `rules/debruijn_sequence.py`)

## Classification Details
| Field | Value |
|---|---|
| Method ID | 077 |
| Name | De Bruijn Universal Cycle Composition |
| Acronym | DBUC |
| Paradigm | Rules-Based |
| Layer | concrete |
| Primary Elements | Pitch, Rhythm, Harmony, Structure, Texture |
| Tonal Gravity | Weak (Mode-pinned) |
| Metric Binding | Grid-Locked |
| Memory Depth | Local (Length-$k$ window) |
| Time Complexity | O(n^k) |

## Why this method (novelty check)
Searched `methods_db.md` for `de bruijn`, `universal cycle`, `necklace`, `lyndon`. Zero matches — the de Bruijn sequence / universal cycle was NOT already in the DB. It is a genuinely novel, classic combinatorial object (Flye Sainte-Marie 1894 / de Bruijn 1946) not yet catalogued. It fills a distinct niche as the **exhaustive** extremal case of structured aperiodicity:
- **Complement of 076 PTM-ASC** (Thue–Morse, *overlap-free* = avoids any $XXX$ repetition) — de Bruijn instead *contains every* length-$k$ pattern exactly once.
- **Complement of 069 CWCC** (Christoffel words, *balance*-optimal).
- **Sibling of 002 Markov / 041 ACOPF** — those walk the same de Bruijn/transition graph *probabilistically*; DBUC walks it *exhaustively*.
- **Graph-theoretic cousin of 011 Voice-Leading Graph Search** (Neo-Riemannian graph traversal).

## Complete Method Section (as appended to methods_db.md)
Appended verbatim from `_temp_method_077.md`. Full text is reproduced in `method_077_DBUC.md` (superset with extended math + implementation sketch + references). The DB section begins:

```
# De Bruijn Universal Cycle Composition (DBUC) (Method 077)
```

and contains the required subsections: `### Layer`, `### Source`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Technical Mechanics`, `### Implementation Requirements (Python / NumPy)`, `### Pitfalls`, `### Comparison With Related Methods`, `### References`.

## Verification
- `wc -l` before 15647 → after section append 15771 → after summary row 15772 (+125).
- Grep confirms summary row `**077**` present at line 86, and section header `(Method 077)` at line 15649.
- Both known patch pitfalls clean:
  1. **Backslash escape**: `grep -c '\\\\'` on the 077 row returns **0** — no double backslashes; LaTeX macros ($\mathcal{O}$, $\{0,1\}$) use single backslashes.
  2. **`||` prefix**: leading chars of row 86 are `| **077` — single leading `|`, no `||`.

## Quirks / Pitfalls Encountered
1. **Stale-ID guard honored**: dynamic scan of the summary table (`grep -oE '\| \*\*[0-9]{3}\*\* \|'`) plus the file listing confirmed max numeric ID = 076 (PTM-ASC). Note the DB already skips 058 (pre-existing gap; NODE-CTC has a detailed section but no summary row) — I did NOT fill 058, correctly using max+1 = 077 per the "max+1, not gap-filling" instruction.
2. **`grep -o` display misleading**: a naive `grep -oE` of the row rendered `\mathcal{O}(n^k)` with what looked like doubled backslashes, but that was `grep`'s own escaping of the `\` in its `-o` output. The byte-level `grep -c '\\\\'` check (matching two literal backslashes) returns 0, confirming the file has single backslashes. Lesson: verify with a `-c '\\\\'` count, not `-o` output.
3. **Combinatorial-explosion discipline**: noted in Pitfalls that $n^k$ grows fast (7³=343, 12³=1728 events); recommended $k \in \{2,3\}$ for scale alphabets.
4. **Composition workflow compliance**: implementation sketch follows AGENTS.md (engine-authored MIDI via `UnitMatrixComposer`, `create_note_unit`/`create_chord_unit`, `composer.validate()` gate before `to_midi()`); no raw `mido` authoring, no `sys.path` hacks.

## Next free ID
**078**
