# Report — Method 093: Percolation Process Network Criticality (PPNC)

**Date:** 2026-09-22 (methods-research cron job)  
**Status:** APPENDED to methods_db.md + summary row added + standalone file written.

## Identification

- **Method ID:** 093 (resolved dynamically: max numeric algorithmic-method ID in methods_db.md summary table was **092** DLACG; verified against all existing `method_*.md` and `report_*.md` files; next free ID is 094)
- **Name:** Percolation Process Network Criticality (PPNC)
- **Paradigm:** **Nature-Led** (statistical physics, phase transitions, critical percolation on graphs/lattices)
- **LAYER:** **concrete** (generates discrete note events, cluster-partitioned melodic motifs, rhythmic run durations, and polyphonic chords directly into UnitMatrix cells; feeds `generators/`; operating at L3 meso section coordination and L2 voice contours)
- **One-line description:** Composes via site/bond percolation on a spatio-temporal UnitMatrix lattice $\mathcal{V} \times \mathcal{T}$ near the geometric percolation threshold $p \approx p_c$.

## Summary table row (as inserted at methods_db.md line 103)

```markdown
| **093** | concrete | Percolation Process Network Criticality (PPNC) | **Nature-Led** | Pitch, Rhythm, Harmony, Structure, Texture | Moderate (Critical-connectivity) | Grid-Locked / Continuous | Meso / Cluster Lattice | $\mathcal{O}(V \cdot T)$ direct, $\mathcal{O}(N \alpha(N))$ DSU | Composes via site/bond percolation on a spatio-temporal UnitMatrix lattice $\mathcal{V} \times \mathcal{T}$ near the geometric percolation threshold $p \approx p_c$. Subcritical $p < p_c$ yields sparse pointillistic motifs; critical $p \approx p_c$ yields fractal spanning clusters balancing melodic continuity and rhythmic syncopation; supercritical $p > p_c$ yields dense chordal masses. Connected clusters define motivic phrases, and directed percolation enforces temporal causality. Phase-transition counterpart to 078 IMEC / 082 RBNCC and network-connectivity sibling of 035 PPTNO / 092 DLACG. |
```

## Line counts

- **Before append:** 19,403 lines
- **After append (section):** 19,594 lines (+191 lines)
- **After summary row:** 19,595 lines (+192 lines total)

## Files

- **methods_db.md:** Section appended at line 19,406 (`# Percolation Process Network Criticality (PPNC) (Method 093)`), summary row inserted at line 103 (after 092 DLACG, immediately before the `# Sound Production Methods Framework` header).
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/method_093_PPNC.md`
- **Validation script:** `/opt/data/projects/Research/CompositionMethods/verify_093_PPNC.py`
- **This report:** `/opt/data/projects/Research/CompositionMethods/report_093.md`
- **Candidate code path:** `generators/percolation_criticality.py` (lattice simulation, cluster labeling via DSU/BFS, horizontal spanning detection, and UnitMatrix realization) + SCALE entry in `workflows/paths.py` via `register_method("093", "L3", "generators.percolation_criticality", "Percolation process network criticality")`. Import-pure (stdlib + numpy + structures + workflows only, no heavy lazy-import polluters).

## Research summary

Percolation theory (Broadbent & Hammersley 1957; Stauffer & Aharony 1994; Grimmett 1999) studies connectivity and cluster formation on lattices under probabilistic node/edge occupation. Unlike equilibrium thermal systems (e.g. Method 078 IMEC Ising model) or continuous diffusion processes (Method 092 DLACG), percolation features a purely geometric second-order phase transition at an exact threshold $p_c$:
1. **Subcritical regime ($p < p_c$):** Finite, exponentially decaying cluster sizes ($n_s \sim s^{-\tau} e^{-s/s^*}$). Produces sparse pointillistic motifs, isolated accents, and spacious rests.
2. **Critical regime ($p \approx p_c$, e.g. $p_c^{\text{site}} \approx 0.5927$ in 2D square lattices):** Power-law cluster distribution $n_s(p_c) \propto s^{-\tau}$ ($\tau \approx 2.055$), yielding scale-free, fractal spanning clusters ($D_f \approx 1.896$). Balances cohesive conjunct voice-leading with complex syncopation and emergent long-range musical form.
3. **Supercritical regime ($p > p_c$):** Giant cluster dominates the lattice, creating dense organum, polyphonic mass textures, and choral pads.

In Method 093, the UnitMatrix is mapped as a spatio-temporal lattice $\mathcal{V} \times \mathcal{T}$ (voices $\times$ metric subdivisions). Connected clusters define musical phrases whose horizontal spans govern note durations and whose vertical overlaps determine polyphonic chords and voice-leading. Directed percolation (Hinrichsen 2000) enforces temporal causality.

## Musical Elements Framework (full)

- **PITCH:** Vertical lattice coordinates $v$ map to voices or pitch registers. Horizontal bonds within a cluster constrain melodic transitions to conjunct scale steps ($|\Delta p| \le 2$). Cluster identities index root tonal pivots or scale steps over an active pitch-class pool (ABS-002).
- **RHYTHM:** Horizontal metric slots $t$ map to integer ticks (e.g., 16th notes = 120 ticks at 480 TPB). Contiguous horizontal runs of occupied sites within a single cluster merge into sustained notes. At criticality, the power-law cluster distribution produces organic Zipfian rhythm (short 16ths/8ths punctuated by longer phrase ties).
- **HARMONY:** Vertical bonds between adjacent voices within the same cluster enforce consonant harmonic intervals (unisons, 3rds, 4ths, 5ths, 6ths, 8ves). Unbonded co-occurring events introduce passing or suspended tensions. Dynamic control of $p$ across sections modulates harmonic tension.
- **STRUCTURE:** Macro-form is controlled by an engineered percolation trajectory $p(s)$ across UnitMatrix section columns:
  - *Intro:* Subcritical ($p = 0.32$), sparse pointillistic gestures.
  - *Verse:* Approaching critical ($p = 0.50$), motivic cells consolidate.
  - *Chorus:* Critical percolation ($p = p_c \approx 0.593$), spanning clusters bridge the section with maximum polyphonic coherence.
  - *Bridge:* Subcritical breakdown ($p = 0.28$), textural decay.
  - *Outro:* Supercritical climax transitioning to silence.
- **TEXTURE:** Cluster count and giant cluster fraction $\theta(p)$ directly dictate texture: monophonic/hocketing in subcritical, multi-voiced counterpoint at criticality, and sustained homophonic wall of sound in supercritical.

## UnitMatrix Integration

- **Voices (rows):** Rows $v \in \{0, \dots, V-1\}$ map to distinct instrument voices (e.g. Soprano/Flute, Alto/Violin, Tenor/String Ensemble, Bass/Acoustic Bass).
- **Sections (columns):** Columns represent structural sections, each evaluated with lattice dimensions $(V, T_s)$ and occupation parameter $p_s$.
- **Cells (MusicUnit):** In each cell $(v, s)$, contiguous active runs merge into `MusicEvent` objects with `start_tick`, `end_tick`, `pitch`, and `volume`.
- **Zero-Drift Invariant:** Track lengths are strictly preserved by appending a silent padding event (`pitch=0, volume=0`) terminating at `total_section_ticks`, verified with `composer.validate()`.
- **Hybridization Rule:** Sparse subcritical sections are paired with sustained harmonic pads per Musicom standards.

## Pitfalls & Fixes

1. **Voice Starvation ($p \ll p_c$):** Low occupation probability leaves voices empty. *Fix:* Enforce minimum 1 event seed per bar.
2. **Note Collision Clutter ($p > p_c$):** Giant cluster can saturate every pulse. *Fix:* Restrict supercritical regime to short climaxes and cap maximum simultaneous polyphonic voices.
3. **Aspect Ratio Anisotropy ($T \gg V$):** High time-to-voice ratio shifts critical threshold toward 1D ($p_c \to 1$). *Fix:* Model as $1+1$ directed percolation ($p_c \approx 0.6447$) or evaluate within square metric windows.
4. **MidiInstrument Program Lookup:** GM instrument constants must match engine definitions in `structures/instrument.py` (e.g. `MidiInstrument.STRING_ENSEMBLE` instead of non-existent `VIOLA`). Fixed in sketch and verification script.

## Verification

- `wc -l methods_db.md` → 19,595 lines (+192 lines total delta).
- `grep -n "093" methods_db.md` → line 103 (summary row) + line 19,406 (detailed section header).
- Clean LaTeX formatting: single backslash `\mathcal{O}` and `\alpha`. Single `|` table prefix verified.
- UnitMatrix validation test `verify_093_PPNC.py` passed with `Zero-drift: True`.
- **Next free ID: 094** (numeric algorithmic methods).
