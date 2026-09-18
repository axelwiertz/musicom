# Report — Method 090: Golomb Ruler Distinct-Difference Composition (GRDC)

**Date:** 2026-09-18 (methods-research cron job)
**Status:** APPENDED to methods_db.md + summary row added + standalone file written.

## Identification

- **Method ID:** 090 (resolved dynamically: max numeric ID in methods_db.md summary table + `method_*.md` / `report_*.md` scan was **089** CRCM; no `method_090*` or `report_090*` files existed; next SP-ID pointer in the DB was SP-088 — separate namespace, non-conflicting)
- **Name:** Golomb Ruler Distinct-Difference Composition (GRDC)
- **Paradigm:** Rules-Based (deterministic combinatorial design; search optimizer only over a strictly defined combinatorial object)
- **LAYER:** **concrete** (realizes pitch pools / onset grids / chord subsets into UnitMatrix cells; feeds `generators/`; L2/L1 SCALE levels — pitch-pool at L2, onset-lattice at L3)
- **One-line description:** Composes from a Golomb ruler / finite Sidon set — marks whose pairwise differences are all distinct — so pitch pools repeat no interval class and rhythmic onsets repeat no gap.

## Summary table row (as inserted at methods_db.md line 100)

| **090** | concrete | Golomb Ruler Distinct-Difference Composition (GRDC) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (ICV-invariant pool) | Grid-Locked | Macro / Ruler Span | $\mathcal{O}(S \cdot m^2)$ search, $\mathcal{O}(m^2)$ verify | Composes from a Golomb ruler / finite Sidon set — marks whose pairwise differences are ALL distinct (optimal Golomb rulers; Sidon density in $\mathbb{Z}_n$). Pitch plane: marks = pitch classes → no interval class repeats (ICV entries ≤ 1; all-interval tetrachord 4-Z15 at $m{=}4$), the maximal-interval-variety opposite of symmetric 080 MMLT subsets. Time plane: marks = onsets → no inter-onset interval repeats, a certificate-backed non-isoperiodic groove (maximal unevenness, deterministic). Harmony = union of per-voice rulers, tension = duplicate-difference count; form = transposition/reflection/mark-insert transforms per section; Shearer's bound $L \gtrsim m^2/2$ makes dense Golomb grooves demand long bars. Position-choosing complement to 089 CRCM (which permutes orderings); uniqueness foil to 011 Euclidean / 069 CWCC evenness; modular (Sidon) cousin of 065 TTSMC aggregates. |

## Line counts

- **Before append:** 18,559 lines
- **After append (section):** 18,678 lines (+119)
- **After summary row:** 18,679 lines (+120 total)

## Files

- **methods_db.md:** section appended at line 18,563 (`# Golomb Ruler Distinct-Difference Composition (GRDC) (Method 090)`), summary row inserted at line 100 (after 089 CRCM, before the `# Sound Production Methods Framework` header).
- **Standalone file:** `/opt/data/projects/Research/CompositionMethods/method_090_GRDC.md`
- **This report:** `/opt/data/projects/Research/CompositionMethods/report_090.md`
- **Candidate code path:** `generators/golomb_ruler.py` (pool + onset generation; `is_golomb` verify, `sidon_pc_pool` search, `golomb_onsets` grid) + SCALE entry in `workflows/paths.py` via `register_method("090", "L3", "generators.golomb_ruler", "Golomb ruler distinct-difference composition")` when registered. Import-pure (stdlib only: itertools/random) so `test_generator_lazy_imports` stays green.

## Research summary

A **Golomb ruler** (order $m$): set of marks with all $\binom{m}{2}$ pairwise differences distinct. Optimal lengths: $m{=}5\to L{=}11$, $m{=}6\to 17$, $m{=}7\to 25$, $m{=}8\to 34$ (Shearer 1998 tables; >~28 open, NP-hard, SAT/SBDD search per Dimitromanolakis 2002). A **finite Sidon set** is the density-optimized modular twin (Bose–Chowla $\approx\sqrt{n}$ in $\mathbb{Z}_n$; Ruzsa $\approx\sqrt{N}$ in intervals). Musical reading:

- **PC plane (Sidon set in $\mathbb{Z}_{12}$):** ICV entries ≤ 1 → no interval class repeats. Max 4-mark example: $\{0,1,4,6\}$ = all-interval tetrachord 4-Z15 (Forte), ICV $[1,1,1,1,1,1]$. Opposite pole of 080 MMLT's interval-duplicating symmetric modes.
- **Time plane:** marks = onsets → all inter-onset intervals unique → deterministic maximal-unevenness groove, certificate-backed non-repetition (foil to 011 Euclidean maximal *evenness*).
- **Harmony:** union of per-voice rulers; duplicate-difference count = tension scalar.
- **Form:** per-section transforms (transpose / reflect / insert-delete marks / switch order $m$).
- **Shearer counting bound** $L \ge m^2/2 - O(m)$: dense Golomb grooves need long bars ($B \gtrsim m^2$ pulses).

Relation to 089 CRCM: CRCM permutes *orderings* (all rows distinct); GRDC chooses *positions* (all distances distinct) — complementary combinatorial objects, both group-theoretic-craft lineage.

## Musical Elements Framework (full)

- **PITCH:** marks → scale degrees / pitch classes mod 12 (Sidon pool). Melody = ordered mark traversal; every leap size unique per span; transposition preserves the ICV fingerprint.
- **RHYTHM:** marks → onset ticks in a bar/window; linear reading = unique IOIs, cyclic reading = unique IOIs mod bar length; accent = mark index parity.
- **HARMONY:** verticalities = simultaneous marks of multiple rulers; cross-voice union checked for Sidon-ness (composite ruler); non-Sidon union = intentional tension.
- **STRUCTURE:** section sequence of ruler transforms (transposition shift, reflection = retrograde, mark insert/delete = density, order switch $m'$ = section character change).
- **TEXTURE:** active-ruler count × mark density; union distance-histogram entropy (flat = glassy pointillism, peaked = conventional).

## UnitMatrix Integration

- **Voices (rows):** one ruler per voice — pitch-ruler voice (melodic pool) or time-ruler voice (percussion/comping onsets).
- **Sections (columns):** each section = one transform of the voice's ruler.
- **Cells:** events from the transformed ruler restricted to the section's tick/pitch window; equal-length rule satisfied by letting the last mark land on the section boundary (terminal landmark at `section_len`), padding sustained marks.
- **Fill order:** per-voice left-to-right, then a per-column cross-voice union Sidon-check post-pass (re-voice ±12 or re-time onsets on violation).

## Pitfalls encountered / documented

1. **Cyclic vs linear distinctness:** a linearly-Sidon PC set can still duplicate an interval *class* ($d$ and $12-d$ present). Verify with `rules/set_theory.py` `interval_vector`, assert `max(ICV) ≤ 1` — not raw difference uniqueness.
2. **Span explosion:** linear rulers grow quadratically (order 12 ≥ 77 units of span) — use modular/Sidon form for 12TET pools, linear rulers only for onset grids.
3. **Thin small rulers:** $m \le 4$ gives ≤ 6 distinct differences — thriftiness audible; use $m \ge 6$ (rhythm) / $m \ge 5$ (pools).
4. **Optimality:** beyond order ~28 optima are unproven — use Shearer verified tables or label heuristics "near-optimal" in provenance.
5. **Sparse-groove hybridization rule:** Golomb onsets are sparse by construction — must pair with a continuous fill layer (026 DPSM / pads / walking bass) per the master-map rule, else staccato output.
6. **Process quirks (this run):** heredoc/execute_code blocked → used the sanctioned `write_file` temp + `cat >>` + `rm` workflow; LaTeX `\\mathcal` escaping checked in the patched row (clean, 0 double-backslashes); no `||` row-prefix appeared (verified); appended section began cleanly after the SP-087 tail (no stray separator merge).

## Verification

- `wc -l methods_db.md` → 18,679 (was 18,559).
- `grep -n '090' methods_db.md` → line 100 (summary row) + line 18,563 (section header).
- Row format check: starts with single `|`, zero `||` prefix, single-backslash LaTeX confirmed (`\mathcal{O}`), 10 classification columns present.
- `_temp_method_090.md` deleted after append.
- **Next free ID: 091** (numeric); next free SP-ID remains SP-088 (sound-production job's namespace).
