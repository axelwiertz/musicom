# REPORT — 314-abelian-sandpile-suite

**Nightly rework job · 2026-11-20.**

| Field | Value |
|---|---|
| **Project** | `314-abelian-sandpile-suite` (next ID after 313) |
| **Source** | `277-abelian-sandpile-avalanche` (Experimental, D minor, 88 BPM, Method 036 ASAR) |
| **Genre** | Experimental |
| **Method** | 036 — Abelian Sandpile Avalanche Rhythmics (ASAR) |
| **Key** | D minor (aeolian) — pcs `{D,E,F,G,A,Bb,C}` |
| **Tempo / Meter** | 88 BPM · 4/4 · 480 TPB (BAR = 1920) |
| **Form** | through-composed `S1..S8` (4 bars each = **32 bars**) — was 24 bars / 6 sections |
| **Voices** | Lead=Marimba(12) · Counter=Celesta(8) · Harmony=Piano(1) · Pad=String Ensemble(48) · Bass=Double Bass(43) |
| **Seeds** | raw `20261120` · humanize `66824` |

## 1. Audit of source 277

| Standard | Result |
|---|---|
| 1. Engine (UnitMatrixComposer) | PASS |
| 2. Zero-drift | PASS (5 tracks, 46080 ticks) |
| 3. Rhythm-grid sync | PASS (0 off-grid) |
| 4. ≥4 voice tracks | PASS (5) |
| 5. Two-phase (phase1 present) | PASS |
| 6. provenance.json + index.html | **FAIL** (missing both at root) |

**Decision: redesign (standard 6) + extension.** The source's engine code is
compliant; the failure is missing portfolio artifacts. Identity (genre, D
minor, 88 BPM, sandpile method, 5-voice instrumentation) preserved; form
extended 24→32 bars, 6→8 sections, +6 variation techniques; strict per-bar
chord discipline (stronger than the source's tiered discipline); root
`provenance.json` + `index.html` added.

## 2. Form & per-section harmonic regions

| Section | Bars | Progression | Midpoint degree | Variation |
|---|---|---|---|---|
| S1 | 4 | Dm F Bb C | 6 | original |
| S2 | 4 | Dm Gm Dm Am | 1 | original |
| S3 | 4 | Bb C Dm Am | 1 | original |
| S4 | 4 | Gm Dm C Bb | 7 | transpose |
| S5 | 4 | Dm Bb Gm Am | 4 | invert |
| S6 | 4 | F C Dm Bb | 1 | original |
| S7 | 4 | Dm F Bb C | 6 | retrograde |
| S8 | 4 | Dm Gm C Dm | 7 | augment |

Each section has its own short progression; per-section midpoint chords land on
degrees [1, 4, 6, 7] — not all degree i (no bar-0 tonic collapse).
Roots derived via `Scale7ChordDegree.get_diatonic_note` (aeolian offsets).

## 3. Variation techniques (6)

- **transposition** — S4 lead +4 diatonic steps (perfect 4th up)
- **inversion** — S5 lead diatonic mirror around tonic
- **retrograde** — S7 avalanche cascade time-reversed within section
- **augmentation** — S8 durations doubled + tail thinned (half-time)
- **register_shift** — S4 pad +12, S4/S6 drop-center arch high
- **density_arc** — grains/col 3/5/7/11/7/9/5/3
- **counterline_variation** — S4/S5 ascending, S6 8th-note density

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw BTW abelian sandpile on a 14×256 lattice,
  per-section variation transforms applied to the (row,col) topple stream
  BEFORE decode. Float pitch + chromatic jitter, off-grid onsets, single
  voice, no harmony. Own `validate()` gate: PASS (61440 ticks).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): STRICT chord discipline
  (every note snaps to its own bar's chord tone), 16th grid snap, dedup,
  voice-leading (parallel 5th/octave break), 5-voice texture.

## 5. Humanization (dual-version, style-derived, seeded)

`hz_seed = 66824` · style **experimental** profile + per-instrument
DNA. **Bar-accurate clamping**: the humanized composer uses 1-bar sections so
the humanizer's boundary clamp == bar boundary — jitter never re-attributes a
note to the wrong bar's chord.

## 6. Verification (read-only mido)

| Artifact | tracks | tick len | pitched | off-grid | scale viol | chord viol |
|---|---|---|---|---|---|---|
| phase1 | 1 | 61440 | 236 | 229 | 102 | 184 |
| **perfect** | 5 | 61440 | 712 | **0** | **0** | **0** |
| **humanized** | 5 | 61440 | 712 | 566 | **0** | **0** |

Zero-drift: all voice tracks equal length (61440). Perfect off-grid == 0;
humanized off-grid > 0 (jitter ran). Scale + chord violations == 0 in both
phase-2 artifacts.

## 7. Render + master

`target_for_style("experimental")` = **−14.0 LUFS**, ceiling **−1 dBTP**.
SoundFont `FluidR3_GM.sf2`.

| Artifact | LUFS | true peak | silence | OGG bytes |
|---|---|---|---|---|
| Phase 1 (raw) | -14.01 | -1.00 | 26.90% | 620,699 |
| Perfect | -14.00 | -1.00 | 4.53% | 585,661 |
| Humanized | -14.00 | -1.00 | 4.50% | 589,125 |

## 8. Files

- `MIDI/314-abelian-sandpile-suite-phase1.mid` · `-perfect.mid` · `-humanized.mid` (+ provenance sidecars)
- `Audio/314-abelian-sandpile-suite-phase1.ogg` · `-perfect.ogg` · `-humanized.ogg`
- `provenance.json` (root) · `index.html` · `README.md` · `REPORT.md`
- `Analysis/grid_visualization*.txt` · `compose_summary.json` · `verify_report.json` · `render_report.json`
- `compose.py` · `render.py` · `verify.py`
