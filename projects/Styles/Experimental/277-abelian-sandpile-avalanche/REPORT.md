# REPORT — 277-abelian-sandpile-avalanche

**Primary record.** Nightly composition job · 2026-10-31.

| Field | Value |
|---|---|
| **Project** | `277-abelian-sandpile-avalanche` (next ID after 276) |
| **Style** | **Experimental** — random draw from `/opt/data/projects/Styles/` (47 genre dirs, specials excluded) |
| **Method** | **036 — Abelian Sandpile Avalanche Rhythmics (ASAR)** |
| **Layer** | **concrete** (emits `MusicEvent`s that fill UnitMatrix cells directly; no abstract design stage) |
| **Paradigm** | **Nature-Led** |
| **Form** | **through-composed** `S1 S2 S3 S4 S5 S6` (4 bars each = 24 bars) — via `pick_form(style)` → `form_to_sections` |
| **Key** | **D minor (aeolian)** — pcs `{2,4,5,7,9,10,0}` = D E F G A Bb C |
| **Tempo / Meter** | 88 BPM · 4/4 · 480 TPB (BAR = 1920, 8th 240, 16th 120) |
| **Seeds** | raw `20261031` (nightly date) · humanize `37846` (md5 of project name) |

## 1. Selection (LAYERED METHODOLOGY)

Method 036 was drawn from the **concrete** pool (107 candidates) excluding the
last-7-days set `{001, 002, 023, 025, 026, 040, 043, 051, 053, 065, 075, 082,
091, 095, 098, 104, 109, 111, 113, 117, 121}` + abstract-layer IDs
`{095, 099, 104, 113, 127}`. The previous night (276) was abstract (095 CTC), so
this night the ~6/7 concrete branch fires. Style and form drawn with
`random.Random(20261031)`; form resolved via `pick_form("experimental")` (no
style-hint match → full non-loop palette → `through-composed`).

## 2. Method — Abelian Sandpile (Bak–Tang–Wiesenfeld)

Phase-1 generative core is a faithful implementation of Method 036:

- **Lattice**: 14 pitch rows (two octaves of D minor, D3..C5) × 192 time
  columns (one eighth-note each → 24 bars).
- **Drive**: a "composer's hand" advances the drop site down the columns and
  arches it across the register; per-section grain density `4/6/8/10/8/4`
  produces a sparse → dense → sparse avalanche arc (the through-composed
  narrative).
- **Relaxation**: synchronous chip-firing — a cell with ≥ 4 grains topples
  (−4) and gives 1 grain to each of its 4 lattice neighbours (up/down/left/
  right); boundary grains dissipate. The process is **abelian** (final stable
  state independent of toppling order) and terminates.
- **Decode**: each toppling `(row, col)` → a note. Row → diatonic pitch
  (`Scale7ChordDegree.get_diatonic_note`); column → eighth-note time; velocity
  ∝ column avalanche size. Raw: float pitch + chromatic jitter (±1 semitone),
  off-grid onsets (±40 tick jitter), single voice, no harmony.

Result: **662 topplings** → **255 raw lead events** (front + tail topple per
active column). The avalanche size distribution is power-law (self-organized
criticality), so the raw draft reads as sparse single notes punctuated by
stepwise cascade runs — exactly the "rhythmic trigger + polyphonic density"
signature of the method.

## 3. Form & progression (through-composed, 24 bars)

| Section | Bars | Progression (degrees) | Chords | Drop center | Grains/col |
|---|---|---|---|---|---|
| S1 | 4 | 1 3 6 7 | Dm F Bb C | 2 | 4 |
| S2 | 4 | 1 4 1 5 | Dm Gm Dm Am | 4 | 6 |
| S3 | 4 | 6 7 1 5 | Bb C Dm Am | 6 | 8 |
| S4 | 4 | 4 1 7 6 | Gm Dm C Bb | 9 | 10 |
| S5 | 4 | 1 6 4 5 | Dm Bb Gm Am | 7 | 8 |
| S6 | 4 | 1 4 7 1 | Dm Gm C Dm | 3 | 4 |

Diatonic degree roots computed explicitly with `Scale7ChordDegree.get_diatonic_note`
(aeolian offsets `[0,2,3,5,7,8,10]`) — no `% 7` wrapper, no uppercase-degree
fallback → no minor-key degree-root collapse (verified: per-bar roots distinct).

## 4. Voices & instruments (from `instrument_registry.py`)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Marimba | 12 | 0 | avalanche cascade melody |
| Counter | Celesta | 8 | 1 | descending off-beat aftershock arpeggios |
| Harmony | Piano | 1 | 2 | strong-beat chord stabs |
| Pad | String Ensemble | 48 | 3 | sustained whole-bar chord |
| Bass | Double Bass | 43 | 4 | root pedal (D2 region) |

No channel-9 drums — the sandpile's percussive bursts are the percussion.

## 5. Phase 1 — raw draft

`-phase1.mid`: single Lead voice (Marimba), 254 audible notes, **253/254
off-grid** (proves rawness), **74 out-of-scale** chromatic notes (pre-rules),
1 strong-violation (raw). Own `validate()` gate: PASS (track length 46080).

## 6. Phase 2 — rules post-process

- **Tiered quantize** (`classify_weight` → `ScaleQuantizer.tiered_quantize`):
  strong onsets (beats 1&3) snap scale→chord (hard in-scale AND in-chord); weak
  onsets snap scale only.
- **Grid snap**: every onset → 16th grid (multiple of 120).
- **Dedup** (start,pitch collisions → keep longest) + **voice-leading** (break
  parallel perfect 5ths/octaves).
- **Tagged ornaments**: 7 chromatic approach notes on the lead, tagged
  `weight=weak, ornament=approach, resolve_pitch=<target>` — legal under the
  tiered discipline, each resolves by step to a scale tone within 1 grid step.

## 7. Grid audit (verify.py, mido readback)

| Artifact | pitched | off-grid (16th) | verdict |
|---|---|---|---|
| phase1 | 254 | 253 | raw (expected) |
| **perfect** | 598 | **0** | ✓ grid-locked |
| **humanized** | 598 | **545** | humanizer ran (>0) ✓ |

All 598 perfect-layer onsets are multiples of 120 (0 off-grid). The 70 notes
flagged "off 8th" are lead 16th-offset notes — still on the 16th grid.

Per-voice off-grid (16th) — perfect (0 for every voice) vs humanized (>0 for
every voice, proving the humanizer ran): Lead 0/248, Counter 0/91, Harmony
0/123, Pad 0/59, Bass 0/24.

## 8. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | audible | strong_ok | weak_in_scale | tagged (resolving) | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|
| Lead | 262 | 48 | 207 | 7 (7) | 0 | 0 | 0 | ✓ |
| Counter | 96 | 0 | 96 | 0 | 0 | 0 | 0 | ✓ |
| Harmony | 144 | 144 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Pad | 72 | 72 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Bass | 24 | 24 | 0 | 0 | 0 | 0 | 0 | ✓ |

**Verdict: `all_pass = true`** — 0 untagged out-of-scale, 0 non-resolving, 0
strong violations across all 5 voices. Only the lead carries tagged ornaments
(7, all resolving); the other voices are chromatic-free.

## 9. Humanization (always-on, style-derived, seeded)

`hz_seed = 37846` · style **experimental** profile (timing σ 8.0 ms, velocity σ
6.0, phrase_corr 0.50, layback 0.0 ms) + per-instrument DNA from the registry:

| Voice | child seed | mean abs shift (ticks) | max shift | vel Δ | timing σ (ticks) |
|---|---|---|---|---|---|
| Lead | 3822446 | 4.481 | 15 | 4.279 | 5.632 |
| Counter | 3822447 | 4.469 | 13 | 4.260 | 5.632 |
| Harmony | 3822448 | 3.812 | 15 | 4.639 | 5.632 |
| Pad | 3822449 | 3.486 | 11 | 4.444 | 5.632 |
| Bass | 3822450 | 7.458 | 14 | 4.458 | 7.040 |

Bass lays back most (mean 7.46 ticks ≈ 10.6 ms at 88 BPM — its 8 ms layback
DNA), melodic voices share the style's 5.63-tick timing sigma. Zero-drift
preserved after humanization (all note tracks still 46080).

## 10. Zero-drift

`validate()` PASS on phase-1, phase-2 (perfect) and phase-2 (humanized). mido
readback: all note tracks equal **46080 ticks** for every artifact.

## 11. Render + master

`target_for_style("experimental")` = **−14.0 LUFS** (fallback — "experimental"
is not in `GENRE_LUFS`), ceiling **−1 dBTP**. `discover_soundfont()` →
FluidR3_GM.sf2. All three MIDIs rendered (FluidSynth `-ni -g 1.2 -R no -C no`)
→ mastered (`master()`) → Opus OGG.

| Artifact | integrated LUFS | true peak dBTP | silence ratio | RMS mean | RMS max | OGG bytes |
|---|---|---|---|---|---|---|
| phase1 | −14.02 | −1.00 | 5.51% | 0.154 | 0.313 | 549 804 |
| perfect | −14.00 | −1.96 | 5.77% | 0.132 | 0.206 | 449 259 |
| humanized | −14.00 | −2.25 | 5.79% | 0.133 | 0.222 | 452 012 |

All three ≈ −14 LUFS (target), true peak ≤ −1 dBTP, silence ~5.5–5.8% (healthy,
far below the 30% suspect threshold — the sustained pad/bass keep the track
filled; no mid-track gaps). `phase1` true-peak sits at the −1.00 ceiling
(sparse single-voice marimba — the limiter pulls its few loud cascade peaks
down; correct behaviour, not a defect).

## 12. Files

| File | Size (bytes) |
|---|---|
| `MIDI/277-abelian-sandpile-avalanche-phase1.mid` | 2058 |
| `MIDI/277-abelian-sandpile-avalanche-perfect.mid` | 4868 |
| `MIDI/277-abelian-sandpile-avalanche-humanized.mid` | 4776 |
| `Audio/*.wav` + `*.ogg` (×3) | see render_report.json |
| `Analysis/{grid_visualization,grid_visualization_phase1}.txt` | ✓ |
| `Analysis/{compose_summary,pitch_audit,verify_report,render_report}.json` | ✓ |

## 13. Fixes applied

- **Phase-1 section offset bug**: initial `build_phase1` passed `s_start=0` to
  `rel_events` while feeding absolute-tick events → only section-1 notes
  survived (31 notes). Fixed to `rel_events(seg, s_start, s_ticks)` → full 254
  raw notes recovered.
