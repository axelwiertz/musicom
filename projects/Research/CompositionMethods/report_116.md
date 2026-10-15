# Report: Method 116 — Petri Net Composition (PNC)

**Date**: 2026-10-15
**Agent**: Hermes (cron job)
**Method ID**: 116
**Acronym**: PNC
**Full Name**: Petri Net Composition
**Paradigm**: Rules-Based
**Layer**: concrete
**Previous highest ID**: 115 (Keplerian Orbital Resonance Composition)
**Next free ID after this**: 117

---

## One-line Description

P-timed Petri nets with probabilistic arc weights and music-object places generate symbolic music through token-game simulation: net topology = macro-form, firing schedule = rhythm, concurrent tokens = polyphonic voices.

---

## Classification Details

- **Primary Elements**: Pitch, Rhythm, Harmony, Structure, Texture
- **Tonal Gravity**: Moderate (Token-guided) — tonal centers are encoded by designing pitch-object content and restricting transposition operators in transitions
- **Metric Binding**: Grid-Locked / Continuous — place timing $\tau(p)$ can be discrete (MIDI ticks) or continuous (real time)
- **Memory Depth**: Meso / Net State — the marking (token distribution across places) carries all past firing history; the net topology encodes the full form a priori
- **Time Complexity**: $\mathcal{O}(P \cdot T \cdot F)$ where $P$ = number of places, $T$ = number of transitions, $F$ = total firing count

---

## Summary Table Row

```
| **116** | concrete | Petri Net Composition (PNC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Token-guided) | Grid-Locked / Continuous | Meso / Net State | $\mathcal{O}(P \cdot T \cdot F)$ | P-timed Petri net with probabilistic arc weights: places = music objects (notes, chords, motifs), transitions = music operators (transposition, inversion, concatenation), tokens = active threads/playback triggers. Net topology = macro-form, firing schedule = rhythm, concurrent tokens = polyphonic voices, place timing $\tau(p)$ = note duration and IOI. Reconfigurable on-the-fly for live composition (minimalist phasing). Formal-model counterpoint to 002 Markov / 021 CA; deterministic-stochastic hybrid foil to 034 PCFG / 078 IMEC. |
```

---

## File Statistics

| Metric | Before | After | Delta |
|---|---|---|---|
| methods_db.md lines | 25453 | 25515 | +62 |
| Summary table rows | 115 methods | 116 methods | +1 |
| Database files | 50 method_*.md | 51 method_*.md | +1 |
| Report files | 50 report_*.md | 51 report_*.md | +1 |

---

## Method Section Text (appended)

The full method section appended to `methods_db.md`:

```
### Source
Haus, G. & Rodriguez, A. (1988). "Music description and processing by Petri nets." *Advances in Petri Nets 1988*, LNCS 340, pp. 175–199, Springer. — Baratè, A., Haus, G. & Ludovico, L.A. (2007). "Petri Nets Applicability to Music Analysis and Composition." *Proceedings of the International Computer Music Conference (ICMC 2007)*, Copenhagen, pp. 97–100. — Baratè, A., Haus, G. & Ludovico, L.A. (2014). "Real-time Music Composition through P-timed Petri Nets." *Proceedings of the ICMC-SMC 2014*, Athens, pp. 408–415. — Haus, G. & Rodriguez, A. (1993). "Formal music representation; a case study: the model of Ravel's Bolero by Petri nets." In *Music Processing*, G. Haus (Ed.), Computer Music and Digital Audio Series, pp. 165–232, A-R Editions, Madison.

### Layer
**concrete** — generates events that fill UnitMatrix cells.

### Paradigm
**Rules-Based**

### Description
Petri Net Composition (PNC) uses P-timed Petri nets with probabilistic arc weights as the generative engine for symbolic music...

### Musical Elements Framework
PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE — all five covered in full detail.

### UnitMatrix Integration
Voices = independent token lineages (tracked by split/fusion).
Sections = subnetworks activated by token flow across transition boundaries.
Cell filling = place timing $\tau(p)$ interval decoded to MusicUnit.

### Pitfalls
7 pitfalls documented: net design complexity, timing granularity, state explosion, probabilistic weight tuning, music-object granularity, real-time reconfiguration soundness, explicit tonal control.
```

Full text is at the end of `methods_db.md` and in `method_116_PNC.md`.

---

## Standalone File

- `/opt/data/projects/Research/CompositionMethods/method_116_PNC.md`
- Contains: extended formal definition, 14-parameter P-timed Music Petri Net 9-tuple, firing rule equations, operator table, full Python implementation sketch (~200 lines) with `PetriNetComposer` class, complete references.

---

## Candidate Code Path

```
generators/petri_net_composition.py
```

This module would contain:
- `MusicObject` dataclass (pitches, duration, velocity → `MusicEvent[]`)
- `PetriNet` class (places, transitions, arcs, marking, P-timing)
- `PetriNetSimulator` (firing rule, conflict resolution via arc weights, token-game engine)
- `PetriNetComposer` (net design helpers, simulation loop, `to_unit_matrix()` → `UnitMatrixComposer`)
- Pre-built net topologies: ABA net, rondo net, through-composed net, canon/fugue nets

---

## Related Existing Methods

| Method | Relation |
|---|---|
| 002 Markov | PNC generalizes to concurrent token paths; Markov = single-token linear PNC |
| 011 Voice-Leading Graph | Graph search vs. token-game execution; complementary realizers |
| 021 Cellular Automata | Grid-update rules vs. bipartite net topology; both are discrete-state formal models |
| 034 PCFG Grammar | Tree-rewriting vs. net-marking evolution; PNC has explicit concurrency |
| 055 SAMC | Optimization metaheuristic vs. formal-model simulation |
| 064 MRFCC | Undirected grid vs. directed bipartite graph |
| 078 IMEC | Ising spin-lattice vs. Petri net (both are state-machine formalisms) |
| 111 VTCC | Perfect hocket vs. concurrent polyphony; complementary views of voice interlocking |

---

## Quirks & Pitfalls Encountered During Registration

1. **Shell escaping**: The `sed` command's `a\` append function interprets backslash (`\`) specially, eating LaTeX backslashes. Had to use double backslashes `\\mathcal` and `\\cdot` to get them to survive sed.
2. **File pagination**: `read_file` with `offset/limit` creates a "partial view" warning — the `patch` tool won't match against content read with pagination. Used `sed` and `cp` on tmp files instead.
3. **Table column format**: The summary table rows start with `|` (single pipe) not `||` (double) — the leading empty column in the separator row is not carried into data rows. The header row uses `||` (two pipes = one empty cell separator).
4. **Inconsistent LaTeX escaping**: Some early summary rows use single backslash `$\mathcal{O}(N)$`, later ones use double `$\\mathcal{O}(...)$`. Both render identically in markdown/LaTeX.

---

## Report File

This file: `/opt/data/projects/Research/CompositionMethods/report_116.md`

---

## Next Free ID

After 116, the next free algorithmic-method ID is **117**.
Next free sound-production ID: **SP-115**.
Next free human-craft ID: **HC-066**.