# Simulated Annealing Metropolis Composition (SAMC) — Method 055

## Overview
**Paradigm:** Stochastic (global-optimization metaheuristic)
**Primary Elements:** PITCH, RHYTHM, HARMONY, STRUCTURE, TEXTURE
**Tonal Gravity:** Strong (Energy-guided)
**Metric Binding:** Grid-Locked / Continuous
**Memory Depth:** Macro / Global Optimum
**Time Complexity:** O(I · S · V)

## Source
Derived from Simulated Annealing (SA), introduced by Kirkpatrick, Gelatt & Vecchi (1983, *Science*) and Černý (1985), building on the Metropolis–Hastings acceptance criterion (Metropolis et al., 1953). SA is a canonical stochastic global optimizer: it escapes local minima by accepting uphill moves with probability exp(−ΔE/T) under a gradually decreasing temperature schedule. Early musical applications include harmonic reduction and voice-leading search (Horner & Goldberg, 1990s). Here it is applied as a whole-UnitMatrix search that treats the composed piece as the global optimum of a weighted musical energy functional.

## Description
SAMC searches the space of possible UnitMatrix fillings for the configuration that minimizes a composite cost (energy) function encoding the composer's musical criteria. Starting from an arbitrary or skeleton seed, it repeatedly proposes small local perturbations (pitch change, onset shift, add/remove note, chord revoice) and accepts them via the Metropolis criterion:

P(accept) = exp(−(E(U′) − E(U)) / (k_B·T))

Always accept downhill; stochastically accept uphill at high temperature to escape local minima. The temperature cools over time (geometric T←αT or linear), so the walk transitions from broad exploration to settled convergence. The final accepted configuration is the near-optimal UnitMatrix under the stated objective. The cooling arc doubles as a built-in macro-form trajectory.

## Musical Elements Framework
- **PITCH:** Propose from scale/chord-neighbor sets. Energy rewards stepwise conjunct voice-leading, target-note proximity, scale adherence; penalizes dissonant leaps. Tonality vs atonality = swap cost terms.
- **RHYTHM:** Shift onsets/durations by a subdivision. Energy rewards groove-locked syncopation against a reference grid, metric stability, or penalizes collisions. Rest-injection carves phrase breaths.
- **HARMONY:** Propose chord voicings from the active progression. Energy scores consonance, functional fit to HOME/LIFT/TENSE/TURN arc, voice-leading cost between chords.
- **STRUCTURE:** Global energy term couples cells across sections — rewards contrast, motif recurrence (self-similarity), and a tension arc aligned with the temperature schedule.
- **TEXTURE:** Energy controls per-cell density: species-like polyphony limits, no parallel motion, no registration collision, stable accompaniment roles.

## UnitMatrix Integration (Voices & Sections)
- **Rows (Voices):** Independent optimization streams sharing one global energy function; voice-specific weights w_v bias roles (lead = melodic energy, bass = root adherence, percussion = groove).
- **Columns (Sections):** Each section = a stage with its own temperature profile; descending temperature across sections encodes macro-form as a cooling arc (exploratory opening → resolved close).
- **Cells U_{v,s}:** {PITCH} proposed pitch set; {RHYTHM} onset/duration schedule; {TEXTURE} density/register coefficient and role weight.
- **Mapping Flow:** (1) seed matrix; (2) define E(U)=w_p·E_pitch+w_r·E_rhythm+w_h·E_harmony+w_s·E_structure+w_t·E_texture + schedule; (3) per-section temperature profiles; (4) iterate: propose move → compute ΔE → Metropolis accept → cool; (5) write final config to UnitMatrix and export via composer validate().

## Pitfalls
1. Premature freezing from rapid cooling → use α≥0.99, reheating, or elbow-multiple-restarts with best-retention (elitism).
2. Imbalanced energy weights → one objective dominates; normalize terms, tune weights.
3. Non-ergodic move sets → unreachable optima; ensure moves span pitch/rhythm/harmony/structure/texture.
4. Expensive full-matrix energy recompute → incremental evaluation of only touched cells.
5. Hard-rule violations → encode as infinite-energy penalties + run composer validate() zero-drift gate.
6. Mis-set T0 → tune so early acceptance ≈0.5–0.8, not 1 (random walk) or 0 (greedy).

## Implementation
See the `simulated_anneal` Python snippet in the main methods_db.md (Method 055 section). Generic over any state; supply `energy_fn` and `propose_move`; elitism retains best-found configuration.