# Report: Method 089 — Change-Ringing Combinatorial Method (CRCM)

**Date:** 2026-09-16 · **Job:** daily method-research cron · **Status:** COMPLETE (appended + verified)

---

## Identity

| Field | Value |
|---|---|
| Method ID | **089** (resolved dynamically: table max was 088 = VTEP; no `method_089*`/`report_089*` existed; numeric ID scan confirms 089 is free) |
| Name | Change-Ringing Combinatorial Method (CRCM) |
| Paradigm | **Rules-Based** (Deterministic) |
| **LAYER** | **concrete** — emits resolved MusicEvents (pitch/onset/duration/velocity) per blow per bell; fills UnitMatrix cells directly. Not abstract (no subset/tension design), not absolute (no audio). |
| One-line | Generates an endless non-repeating permutation stream of n voice-rows under the change-ringing law — every change is a product of disjoint adjacent swaps under a hunting treble ostinato — yielding 100% stepwise interlocking polyphony with zero RNG. |
| Candidate code path | `generators/change_ringing.py` (`ChangeRingingGenerator`, registry id `089`/`CRCM`), sibling of `generators/tintinnabuli.py`. **Not yet implemented in the registry — this job was research/DB only** (spec-only entry; per master-map hard rules it is NOT routable until `register_method()` or a manual registry+SCALE entry lands — the weekly registration job may close this). |
| Line counts | `methods_db.md`: **17907 → 18256** (+349 total; sibling agent appended SP-075 concurrently; my section = +57, my table row = +1) |
| Standalone file | `/opt/data/projects/Research/CompositionMethods/method_089_CRCM.md` (130 lines) |
| Verifier | `/opt/data/projects/Research/CompositionMethods/verify_089_CRCM.py` (executed; all claims below are output of a real run, not assumed) |
| Next free ID | **090** |

## Summary-table row (as appended, line 99 of methods_db.md)

```
| **089** | concrete | Change-Ringing Combinatorial Method (CRCM) | **Rules-Based** | Pitch, Rhythm, Harmony, Structure, Texture | Weak (Mode-locked, function-free) | Grid-Locked | Macro / Lead-Head Cycle | $\mathcal{O}(n)$ per change, $\mathcal{O}(n \cdot L)$ course | Generates an endless non-repeating permutation stream of $n$ voice-rows under the change-ringing law: every change is a product of disjoint adjacent swaps (each voice moves at most one position per blow), the treble plain-hunts as a register ostinato (double blows at extremes), and a lead-end deviation (Plain Bob: "make 2nds") extends the hunt's $2n$ cycle toward the full $n!$ space; lead heads cycle $123456 \to 135264 \to 156342 \to 164523 \to 142635 \to$ rounds (verified). Bells = UnitMatrix voices; changes = isochronous grid slots. Mapping A: bell = fixed pitch, melody = the continuous strike stream, verticalities = change rows (all distinct). Mapping B: pitch = scale degree of position — every line 100% stepwise (verified: 0 leaps > 2nd in 354 steps, 83.6% 2nds + 16.4% unisons), phase-shifted palindromic hunt per voice, deterministic hocket. Calls (bob/single) = form pivots. Group-theoretic sibling of 069/077; historical craft counterpart of 056; motion-law foil to 065 TTSMC. |
```

Classification columns: Tonal Gravity = Weak (Mode-locked, function-free) · Metric Binding = Grid-Locked · Memory Depth = Macro / Lead-Head Cycle · Time Complexity = $\mathcal{O}(n)$ per change, $\mathcal{O}(n \cdot L)$ course.

## Classification details

- **Why Rules-Based**: the change stream is fully determined by (n, method deviation table, call list) — no probabilities, no training, no fitness search. Same determinism class as 056 SCCC / 079 TINC.
- **Why concrete (not abstract)**: the method's output is notes at grid times — it does not design pitch pools or tension curves (abstract) and does not synthesize audio (absolute). It slots directly beside `tintinnabuli.py` in `generators/`.
- **Why novel here**: DB has no change-ringing / adjacent-swap permutation law / hunt ostinato. Near-misses checked and differentiated: 065 TTSMC (serial pitch-class rows — content law, not motion law), 069 CWCC / 077 DBUC / 076 PTM-ASC (word combinatorics without the permutation-motion constraint), 008 Call-Response (role rotation, not group math), 026 DPSM (whole-cycle phasing, not adjacent swaps).

## Verification record (real execution output — `verify_089_CRCM.py`)

```
[1] adjacent-swaps-only=True  60-unique-rows=True  returns-to-rounds=True
[2] lead heads: ['123456', '135264', '156342', '164523', '142635', '123456']
[3] treble positions lead 1: [1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1]
[4] half-lead mirror rows[6+k]==reverse(rows[k]) k=0..5: True
[5] per-bell position jumps >1 across whole course: 0
[6] per-bell degree-path IC histogram (354 in-course steps): {0: 58, 1: 68, 2: 228}
    unisons 16.4% | 2nds 83.6% | 3rds 0.0% | leaps>=ic4 0.0%
[7] distinct vertical sonority sets (mapping A): 60/60
first 12 changes: 123456 214365 241635 426153 462513 645231 654321 563412 536142 351624 315264 132546
```

All five structural claims and both composition-mapping statistics were produced by running the verifier; the half-lead mirror and the 100%-stepwise property were **discovered/confirmed numerically, not asserted from literature**.

## Complete appended method section

The exact text appended to `methods_db.md` (lines 17910–17966) is reproduced in full in `method_089_CRCM.md` (same content, plus a Technical Mechanics section, Python sketch, Comparison With Related Methods, References, and the verification record above). Section headers in the DB: `### Source`, `### Layer`, `### Description`, `### Musical Elements Framework`, `### UnitMatrix Integration (Voices & Sections)`, `### Pitfalls` (8 pitfalls), `### Comparison With Related Methods`, `### References`.

## Musical Elements summary

- **PITCH** — Mapping A: bell = fixed pitch (diatonic ladder, tenor = tonic). Mapping B: pitch = degree of the bell's position; every line verifiably 100% stepwise (0 jumps > 2nd in 354 steps; {unison 16.4%, 2nd 83.6%, ≥3rd 0%}); contours = blue-line hunt/dodge/make-2nds shapes; per-voice phase-shifted palindromic hunts.
- **RHYTHM** — isochronous blows; the rhythm IS the change rate; velocity = position-based (extremes louder, as physical bells) or call-synced accents.
- **HARMONY** — verticalities = change rows (60/60 distinct); mode-locked not functional; tenor tonic anchor; pair with ABS-002 to steer a progression.
- **STRUCTURE** — lead (12 changes) = phrase, plain course (60) = section, calls (bob/single) = form pivots; half-lead mirror = built-in phrase symmetry.
- **TEXTURE** — deterministic hocket (only swapped pairs move per blow); continuous strike stream = the flowing fill layer for the Method Hybridization rule.

## UnitMatrix integration summary

Rows = bells (n = 4–8); sections = leads or courses; cells get `{PITCH}` = change's pitch assignment, `{RHYTHM}` = equal onsets per lead-cell (Euclidean-thinnable), `{HARMONY}` = tenor-pedal sonority (snappable to abstract-layer chords), `{TEXTURE}` = swap-pair accent weight. All cells padded to `section_len` (terminal landmark) → `composer.validate()` passes → `to_midi`. Zero-RNG → byte-identical exports.

## Quirks / pitfalls hit during this job

1. **First generation attempt was mathematically wrong** — my initial "treble-at-lead ⇒ skip (0,1) swap" rule produced a false method (non-adjacent transitions, repeated rows, wrong close). Hand-derived the correct Plain Bob rule (hold positions 1–2 on every 12th change) and re-verified. Lesson encoded as DB Pitfall 3 (off-by-one at double blows / lead end).
2. **Verifier bug**: my adjacency checker demanded diff-runs of exactly 2 positions; a cross change (0,1)(2,3)(4,5) gives one contiguous run of 4. Fixed to accept even-length runs split into pairs. (Lesson: distinguish "disjoint adjacent swaps" from "one swap".)
3. **Symmetry claim needed empirical localization**: the half-lead mirror holds for k=0..5 and is broken exactly by the deviation row — not the whole lead, and not the whole course. Verified numerically before documenting; DB text states the exact range.
4. **Pitch-mapping inversion trap**: bell 1 (treble) is the HIGHEST pitch; my first histogram had the mapping upside-down. Correct mapping `deg(bell) = n − bell` (tenor = degree 0). Documented as DB Pitfall 5.
5. **Patch pitfalls checked and clean**: the new table row contains single-backslash LaTeX (`\mathcal{O}(n)`, `\to`, `\cdot` — repr-verified, 0 double-backslashes) and starts with a single `|` (no `||` prefix).
6. **Sibling-agent file race**: a concurrent agent appended to `methods_db.md` mid-job (17907→18256 lines includes their SP-075 addition). Confirmed no ID collision (their content is SP-* and the numeric table still ends at my 089), my row + section intact, `# Sound Production Methods Framework` header still at line 100. No merge damage.
7. **Workflow constraint honored**: section appended via `write_file` temp + `cat >>` + `rm` (heredoc/execute_code blocked as stated).

## Files touched

| File | Action |
|---|---|
| `/opt/data/projects/Research/CompositionMethods/methods_db.md` | appended 57-line section (line 17910) + 1 summary-table row (line 99) |
| `/opt/data/projects/Research/CompositionMethods/method_089_CRCM.md` | created (130 lines, full write-up w/ math + Python sketch + verification record) |
| `/opt/data/projects/Research/CompositionMethods/verify_089_CRCM.py` | created (executable verifier; `$MUSICOM_PYTHON verify_089_CRCM.py` → all checks pass) |
| `/opt/data/projects/Research/CompositionMethods/report_089.md` | this report |

**Next free ID: 090.**
