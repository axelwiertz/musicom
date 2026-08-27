# Species Counterpoint Constraint Composition (SCCC) — Method 056

## Overview
**Paradigm:** Rules-Based (traditional craft / constraint satisfaction)
**Primary Elements:** PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE
**Tonal Gravity:** Strict (Mode/Finalis-guided)
**Metric Binding:** Grid-Locked
**Memory Depth:** Meso / Phrase
**Time Complexity:** O(D^N) worst case with backtracking; ~O(N) practical

## Source
Traditional craft method, not computational: species counterpoint was codified by Johann Joseph Fux in *Gradus ad Parnassum* (1725) as a graded pedagogical system for Palestrina-style 16th-century vocal polyphony, and remains the canonical formalization of contrapuntal voice-leading. Modern restatements: Jeppesen (1939), Salzer & Schachter (1969), Kennan (1999). Algorithmic treatment follows the generate-and-test / constraint-satisfaction line: Ebcioğlu's expert system CHORAL (1988) for Bach-style harmonization, and constraint-programming formulations of counterpoint (Anders & Miranda, 2009; Anders 2007). In the Musicom catalog it is the tradition-rooted counterpart to modern constraint methods: where 033 WFCGS collapses grids by local adjacency rules and 050 OTVL optimizes voice leading by transport, SCCC enforces the strictest historical contrapuntal grammar deterministically.

## Description
SCCC treats composition as **constraint satisfaction over simultaneous melodic lines**. A pre-composed or imported monophonic line — the **cantus firmus (CF)** — is the fixed anchor (one note per bar in a mode, conjunct motion, range ≤ a tenth). Counter-voices are solved note-by-note against the CF under two constraint classes:

1. **Melodic (horizontal)** — against the voice's own previous notes: stepwise preference, no leap > octave, no two same-direction leaps summing past an octave, limited repetition, single registral climax, no cross relation.
2. **Harmonic (vertical)** — against the current CF note: only the interval class between the counter-voice and CF is governed. Consonances {0,3,4,7,8,9} always allowed; dissonances {2,5,6} only in species-controlled contexts (passing note, suspension).

The species set the rhythmic scaffolding and therefore the active rule subset:

| Species | Rhythm vs CF | Rule core |
| :--- | :--- | :--- |
| 1 | 1:1 equal values | Consonance only; perfect consonances approached by contrary/oblique motion |
| 2 | 2:1 | Both notes consonant, or second = passing dissonance by step |
| 3 | 4:1 | Framework consonant; intervening scalar passing motion |
| 4 | ties across the beat | Suspension: dissonance on strong beat, tied, resolves down by step |
| 5 | mixed | Consonant framework + rhythmic variety; contextual use of all rules |

Generation is **deterministic backtracking search** (chronological DFS over scale degrees). Empty candidate set → backtrack. Result: a valid counterpoint or a proof of infeasibility. Cadences are formula-driven: approach the final by step (leading tone, or Phrygian half-step), standard closing gestures.

## Musical Elements Framework
- **PITCH:** Deterministic enumeration over mode scale degrees (e.g., dorian [0,2,3,5,7,9,10]); filtered by melodic constraints + vertical interval class vs CF. Pitch is the *output of the constraint filter*, never sampled.
- **RHYTHM:** Dictated by species assignment — uniform longs (1), halves (2), quarters (3), tied syncopation (4), mixed florid (5). Density is a *parameter* (species per voice per section), not an emergent property — opposite of stochastic generators (002, 045).
- **HARMONY:** Vertical dyads governed by interval class vs CF, not functional chords. Consonances {0,3,4,7,8,9}; dissonances {2,5,6} only as passing/suspension. Tonal gravity via the mode finalis anchoring cadences (HOME at phrase ends; LIFT/TENSE via suspension chains).
- **STRUCTURE:** Macro-form inherited from the CF phrase structure — each CF phrase = a Section. Contrast via per-section species profiles (e.g., A: sp1+sp3, B: sp4+sp2, A′: florid 5) or CF transposition/ornamentation. Structure is the *input skeleton*.
- **TEXTURE:** 2–4 voices with hard independence guarantees (no parallel perfect intervals, minimal crossing, registral separation); species contrast (long vs fast motion) yields imitative/hocket/homogeneous textures. Texture = the species assignment matrix.

## UnitMatrix Integration (Voices & Sections)
- **Rows (Voices):** Voice 1 = **Cantus Firmus** (anchor, read-only; importable from 001 skeleton, 025 sieve, 043 attractor contour). Voices 2..V = counterpoint rows solved by backtracking, each with species + register window.
- **Columns (Sections):** Each section = one CF phrase (or transposed/ornamented variant). Per-section: species per voice, registers, cadence formula, staggered CF entry (imitation).
- **Cells U_{v,s}:** {PITCH} CF phrase pitches or solved counter-voice sequence; {RHYTHM} uniform values (CF) or species subdivision/tie pattern; {TEXTURE} species (1–5), allowed interval-class list, register window.
- **Mapping Flow:** (1) compose/import CF, split into phrases → sections; (2) assign species profiles per voice/section; (3) per counter-voice cell run deterministic DFS (melodic constraints carried across section boundaries; vertical interval class vs CF cell); (4) cadence verification at phrase boundaries; (5) fill UnitMatrix, run composer validate() zero-drift gate, export; optional 050 OTVL smoothing / 022 MCWS quantization for chromatic species-5 material.

## Implementation
```python
CONSONANCES = {0, 3, 4, 7, 8, 9}          # unison, 3rds, 5ths, 6ths, 8ve
PASSING_OK  = {2, 5, 6}                   # 2nd, 4th, 7th — passing/suspension only

def _diatonic(midi_pitch, mode):
    return (midi_pitch - mode[0]) % 12 in set(mode)

def _melodic_ok(prev_pitch, cand, max_leap=12, prev_prev=None):
    step = abs(cand - prev_pitch)
    if step > max_leap:
        return False
    if prev_prev is not None:
        d1, d2 = prev_pitch - prev_prev, cand - prev_pitch
        if d1 * d2 > 0 and abs(d1) + abs(d2) > 12:   # same dir, sum > 8ve
            return False
    return True

def solve_counterpoint(cf, species, mode, register=(60, 84), max_leap=12):
    sol = []
    def candidates(i):
        prev = sol[-1] if sol else None
        prev2 = sol[-2] if len(sol) > 1 else None
        out = []
        for p in range(register[0], register[1] + 1):
            if not _diatonic(p, mode):
                continue
            if prev is not None and not _melodic_ok(prev, p, max_leap, prev2):
                continue
            ic = (p - cf[i]) % 12
            if ic in CONSONANCES:
                out.append(p)
            elif ic in PASSING_OK and species >= 2:
                if species == 4 and i > 0 and sol and (sol[-1] - cf[i - 1]) % 12 in CONSONANCES:
                    out.append(p)   # suspension tie candidate
                elif species in (2, 3) and prev is not None:
                    lo, hi = sorted((prev, p))
                    if hi - lo in (3, 4):      # stepwise passing motion
                        out.append(p)
        return out

    def dfs(i):
        if i == len(cf):
            return True
        for p in candidates(i):
            sol.append(p)
            if dfs(i + 1):
                return True
            sol.pop()
        return False

    return sol if dfs(0) else None
```
- Determinism: same CF + species + register → same solution (candidates enumerated ascending; no RNG unless florid species shuffles for variation).
- Post-filter: feed solved voices through the standard Phase-2 musicom voice-leading report check as a double gate (chord-tone quantization is unnecessary — harmony is already satisfied by construction).

## Pitfalls
1. Infeasible CF (too many leaps, range > 10th, unapproachable final) → pre-check CF profile or rewrite CF rather than relaxing constraints.
2. Stacking all species rules on a lower species produces empty candidate sets — enforce only the active species' rule subset.
3. Hidden/consecutive perfect intervals slip in at cadence points or across rests — check cadence pairs too.
4. Register exhaustion from repeated upward steps — add headroom preference + octave-transfer decision point in the search.
5. Cross relations (e.g., F vs F♯ within a phrase) — add chromatic cross-relation check for species 5 / chromatic CF variants.
6. Subdivision-level parallels in species 2/3 — validate on all active subdivision levels, not just note level.
7. Academic stiffness — hybridize for production: 026 DPSM accompaniment fills, 043 attractor ornamentation, or 050 OTVL smoothing; species solves the skeleton, another method supplies the surface.

## References
- Fux, J. J. (1725). *Gradus ad Parnassum* (trans. A. Mann, 1943).
- Jeppesen, K. (1939). *Counterpoint: The Polyphonic Vocal Style of the Sixteenth Century*. Prentice-Hall.
- Salzer, F. & Schachter, C. (1969). *Counterpoint in Composition*. Columbia University Press.
- Kennan, K. (1999). *Counterpoint*, 4th ed. Prentice-Hall.
- Ebcioğlu, K. (1988). "An Expert System for Harmonizing Four-Chord Chorales." *Computer Music Journal* 12(2).
- Anders, T. & Miranda, E. R. (2009). "Interfacing Constraint-Based Models and Generative Systems." *Journal of New Music Research* 38(1).
- Anders, T. (2007). *Compositional Models of Counterpoint*. Ph.D. thesis, University of Plymouth.
