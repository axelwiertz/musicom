# REPORT — 317-factor-oracle-lounge

**Nightly composition job (ID 1fc3fd65d359) · 2026-11-21 · Method 067 (concrete layer).**

| Field | Value |
|---|---|
| **Project** | `317-factor-oracle-lounge` (next ID after 316) |
| **Genre / Style** | Lounge |
| **Method** | 067 — Factor Oracle Guided Improvisation (FOGI) |
| **Layer** | **concrete** (Stochastic; automaton over a seed corpus, no training) |
| **Form** | `intro-a-a-b-a` → `Intro·A1·A2·B·A3`, bars `[4,8,8,8,8]` = **36 bars** |
| **Key** | F major (ionian) — pcs `{F,G,A,Bb,C,D,E}` = `{5,7,9,10,0,2,4}` |
| **Tempo / Meter** | 90 BPM · 4/4 · 480 TPB (BAR = 1920) |
| **Voices** | Lead=Flute(73) · Rhodes(4) · Guitar=Jazz Guitar(26) · Bass=Acoustic Bass(32) · Drums(ch9) |
| **Seeds** | raw `20261121` · humanize `52592` |

## 1. Selection

Seeded (`20261121`) random selection per the LAYERED METHODOLOGY:
- **Style**: Lounge (random over 48 genre folders).
- **Method**: 067 FOGI (random over 96 implementable concrete methods, excluding
  those used in the last 7 days: 001, 007, 012, 015, 019, 023, 025, 026, 032,
  035, 036, 041, 053, 069, 075, 077, 120, 126, 132, 134, 139; and excluding
  AI-Driven/training-dependent methods). ~6/7 concrete weighting → concrete
  chosen.
- **Form**: `pick_form("lounge")` → lounge matches no style hint → full non-loop
  palette → `intro-a-a-b-a`.

## 2. Method — Factor Oracle Guided Improvisation (067 FOGI)

A Factor Oracle (Allauzen–Crochemore–Raffinot 1999) is an automaton with two
link kinds: **forward transitions** (continue the current motif) and **suffix
links** (point at the longest proper suffix that is also a prefix = the
"repeated context"). Walking it forward emits an infinite corpus-styled
improvisation; no training, the automaton IS the model.

| Component | Value | Role |
|---|---|---|
| `CORPUS` | 32 symbols over 7 diatonic degrees (0=F .. 6=E) | melodic pitch DNA |
| `GATE` | `[1,0,1,1,0,1,0,1]` (period 8 eighths, 5 hits/bar) | bossa-lounge onset gate |
| `continue_prob` | 0.8 | forward-step vs recombination ratio |
| `restart_prob` | 0.03 | phrase-breath (return to corpus head) |

`CORPUS = [0,2,4,2, 3,2,1,2, 0,2,3,4, 5,4,3,2, 0,1,2,3, 4,2,0,4, 3,1,2,5, 4,2,0,2]`
(F A C A · Bb A G A · F A Bb C · D C Bb A · F G A Bb · C A F C · Bb G A D ·
C A F A). Internal repetition (the `0,2`/`3,2`/`4,2` fragments) gives suffix
links recurrent "Trojan island" contexts. The walk emits **180 symbols** — the
lead's degree stream over the 288-slot 8th-note grid (36 bars × 8), gated by
`GATE`. The `Intro·A·A·B·A` form supplies the macro-structure; per-bar
7th-chord regions supply the harmonic grammar for the chord-tone snap.

## 3. Form & harmonic regions

`intro-a-a-b-a`, F major, all chords diatonic 7ths (lounge color):

| Section | Bars | Degrees | Chords |
|---|---|---|---|
| Intro | 1-4 | i vi ii V | Fmaj7 Dm7 Gm7 C7 |
| A1 | 5-12 | i vi ii V (×2) | Fmaj7 Dm7 Gm7 C7 (×2) |
| A2 | 13-20 | i vi ii V (×2) | Fmaj7 Dm7 Gm7 C7 (×2) |
| B | 21-28 | IV V iii vi ii V I V | Bbmaj7 C7 Am7 Dm7 Gm7 C7 Fmaj7 C7 |
| A3 | 29-36 | i vi ii V (×2) | Fmaj7 Dm7 Gm7 C7 (×2) |

Per-bar harmonic regions (not a single tonic region) → no bar-0 tonic collapse.

## 4. Two-phase architecture

- **Phase 1** (`-phase1.mid`): raw FO walk, single Flute voice. 180 events,
  off-grid onsets (±60 ticks), float pitch + chromatic jitter (±1), no harmony.
  Own `validate()` gate: PASS (69120 ticks). Scale violations = 60 (expected —
  raw draft is pre-rules, deliberately imperfect).
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): STRICT chord discipline
  (every note snaps to its own bar's 7th-chord tone → in-scale AND in-chord),
  16th-grid snap, 5-voice Lounge texture.

## 5. Humanization (dual-version, style-derived, seeded)

`hz_seed = 52592`. Style `lounge` profile + per-instrument DNA. The phase-2
composer uses 1-bar sections so the humanizer's boundary clamp == bar boundary
(no jittered note crosses a bar line → per-bar chord violations stay 0).

Per-voice DNA (mean/max abs shift in ticks; 1 tick ≈ 1.39 ms @ 90 BPM):

| Voice | seed | n | mean shift | max shift | vel Δ | sigma |
|---|---|---|---|---|---|---|
| Lead (Flute) | 5311792 | 180 | 3.31 | 14 | 5.45 | 5.04 |
| Rhodes | 5311793 | 144 | 3.97 | 11 | 3.97 | 5.04 |
| Guitar (Jazz) | 5311794 | 432 | 3.39 | 12 | 4.80 | 5.04 |
| Bass (Acoustic) | 5311795 | 108 | 5.44 | 12 | 2.97 | 3.60 |
| Drums | 5311796 | 288 | 0.85 | 3 | 2.91 | 1.44 |

Drums anchor (tightest, 0.85 ticks ≈ 1.2 ms); bass lays back (5.44 ticks ≈
7.6 ms, the +8 ms layback); melodic voices governed by the style profile.
Phase-1 raw draft stays un-humanized.

## 6. Verification (read-only mido)

| Artifact | tracks | tick len | pitched | drums | off-grid | untagged out-of-scale | non-resolving | strong viol |
|---|---|---|---|---|---|---|---|---|
| phase1 | 1 | 69120 | 183 | 0 | 179 (raw) | 60 (raw) | 0 | 2 (raw) |
| **perfect** | 5 | 69120 | 864 | 288 | **0** | **0** | **0** | **0** |
| **humanized** | 5 | 69120 | 864 | 288 | 943 (>0, jitter ran) | **0** | **0** | **0** |

- **Zero-drift**: all voice tracks equal length (69120) in all three artifacts.
- **Grid**: perfect off-grid == 0 (both 16th and 8th); humanized off-grid > 0
  (humanizer ran).
- **Tiered harmony** (`workflows.pitch_audit.audit_voice`, per pitched voice):
  all PASS — 0 un-tagged out-of-scale, 0 non-resolving ornaments, 0 strong
  violations. STRICT discipline makes every note in-scale AND in-chord.

Per-voice tiered audit (perfect layer):

| Voice | audible | strong_ok | weak_in_scale | result |
|---|---|---|---|---|
| Lead | 180 | 36 | 144 | PASS |
| Rhodes | 144 | 144 | 0 | PASS |
| Guitar | 432 | 216 | 216 | PASS |
| Bass | 108 | 72 | 36 | PASS |

## 7. Render + master

`target_for_style("lounge")` = **−14.0 LUFS** (fallback; lounge is not in the
genre map), ceiling **−1 dBTP**. SoundFont `FluidR3_GM.sf2`.

| Artifact | LUFS | true peak | silence | RMS mean | OGG bytes |
|---|---|---|---|---|---|
| Phase 1 (raw) | -14.00 | -1.87 | 23.6% | 0.129 | 891,223 |
| Perfect | -14.01 | -1.00 | 3.6% | 0.139 | 775,632 |
| Humanized | -14.01 | -1.00 | 3.6% | 0.140 | 778,740 |

Phase-1 silence (23.6%) is the raw single-voice gated draft (5 hits/bar, no
accompaniment) — expected, not a render bug. Perfect/humanized at ~3.6% are
healthy full-texture renders. Phase-1 true peak sits at −1.87 dBTP (below the
−1 ceiling): `master()` true-peak is a CEILING, not a target — a sparse
single-voice render legitimately lands below it; perfect/humanized hit the −1
dBTP ceiling exactly.

## 8. Files

- `MIDI/317-factor-oracle-lounge-{phase1,perfect,humanized}.mid` (+ provenance sidecars)
- `Audio/317-factor-oracle-lounge-{phase1,perfect,humanized}.ogg`
- `provenance.json` (root) · `index.html` · `README.md` · `REPORT.md`
- `Analysis/grid_visualization*.txt` · `compose_summary.json` · `verification.json` · `render_report.json`
- `compose.py` · `render.py` · `verify.py`

## 9. Fixes applied

- **Duplicate section-name collapse (phase 1)**: the form `intro-a-a-b-a` was
  first authored with three identical `"A"` section names. `fill_voice_section`
  resolves by name (first match), so the three `"A"` sections silently collapsed
  onto one column — phase 1 exported only 20 bars (38400 ticks, 103 notes) with
  the last `"A"`'s content mis-placed. Fixed by using unique section names
  (`Intro·A1·A2·B·A3`); phase 1 now exports the full 69120 ticks / 180+ notes.
  Phase 2 was unaffected (it already used unique 1-bar section names).
