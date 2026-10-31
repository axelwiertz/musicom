# REPORT — 275 Japanese PSO Rondo

**Nightly composition job · 2026-10-30 · Method 117 Particle Swarm Optimization Composition (PSOC)**

## 1. Selection (LAYERED METHODOLOGY)

| Field | Value |
|---|---|
| Style | **Japanese** — random draw from `/opt/data/projects/Styles/` genre folders |
| Method | **117 — Particle Swarm Optimization Composition (PSOC)** |
| Layer | **concrete** (emits raw float-pitch/off-grid events → feeds `generators/` + rules) |
| Paradigm | **Stochastic** |
| Form | **rondo** (`A1 4 / B 4 / A2 4 / C 4 / A3 4 = 20 bars`) — chosen via `pick_form(style)` (not a loop) |
| Key | **A Yo Pentatonic** (major pentatonic: A B C# E F#) |
| Tempo / Meter | 78 BPM · 4/4 · 480 TPB (BAR = 1920) |

Method 117 was drawn from the concrete pool (excluding the last-7-days set
{002, 023, 025, 026, 040, 053, 065, 075, 082, 091, 095, 104, 109, 121}).
The selection seed is the nightly date; ~6/7 nights favour a concrete method,
and this night landed concrete (Stochastic).

## 2. Scale & harmony (A yo pentatonic)

- Pitch classes **{9, 11, 1, 4, 6}** = A B C# E F# · intervals **[0, 2, 4, 7, 9]**.
- Open / suspended sonorities per scale degree (koto-idiomatic quartal/quintal):
  `QUALITY = {1:(0,4,7) A, 2:(0,5,7) B(sus), 3:(0,5,8) C#(sus), 4:(0,5,7) E(sus), 5:(0,5,7) F#(sus)}`.
- Canonical diatonic helper `Scale7ChordDegree.get_diatonic_note()` is used for
  ALL root/degree pitch math (no `% 7` wrappers).
- Rondo progression (per-bar degrees):

| Section | Bars | Degrees | Tension |
|---|---|---|---|
| A1 | 4 | I I V I | 0.45 |
| B  | 4 | iii V iii IV | 0.65 |
| A2 | 4 | I I V I | 0.50 |
| C  | 4 | V IV V iii | 0.80 |
| A3 | 4 | I IV V I | 0.55 |

## 3. Voices & instruments (registry source of truth)

| Voice | Instrument | Program | Channel | Role |
|---|---|---|---|---|
| Lead | Koto | 107 | 0 | PSO-optimized melody |
| Counter | Shakuhachi | 77 | 1 | sustained counterline (octave-up echo) |
| Harmony | Shamisen | 106 | 2 | quarter-note plucked arpeggio |
| Bass | Koto (low register A2) | 107 | 3 | root pedal + in-scale companion |
| Drums | GM kit | 0 | 9 | sparse taiko-flavoured accents |

Instruments resolved via `instrument_registry.by_name()` (koto 107,
shakuhachi 77, shamisen 106) — the full KB, not the 10-entry MidiInstrument enum.

## 4. Two-phase architecture

### Phase 1 — raw PSO draft (single voice, NO harmony)
- 40 particles × 90 iterations over a 120-D continuous space (40 notes ×
  `pitch × onset × velocity`). Fitness = scale proximity + stepwise motion +
  8th-grid metric alignment (weights 1/1/1 per note).
- Global-best particle decoded with RAW float pitch (rounded, **not** snapped)
  and **off-grid** onsets → single Koto voice, own composer, own `validate()`
  gate. Provenance `phase=1`.
- **Result:** 40 raw events, best fitness 99.76.

### Phase 2 — musicom rules post-process (5 voices)
1. **Weight-aware tiered quantize** — `classify_weight(onset, STRONG, BAR)` →
   `ScaleQuantizer(root=57, scale="pentatonic").tiered_quantize(pitch, weight,
   chord_tones)`: strong = scale **and** chord, weak = scale only.
2. **16th grid snap** (`GRID=120`) on every melodic onset.
3. **Dedup** collided (start, pitch) → keep longest.
4. **Voice-leading** — break parallel perfect 5ths/octaves on adjacent onsets.
5. **Tagged ornaments** — 3 chromatic half-step-below approach ornaments on the
   lead (tagged via `oe.ornament="approach"`, `resolve_pitch` set). Lead MAY
   carry tagged ornaments; counter/harmony/bass carry ZERO chromatic.

## 5. Tiered pitch discipline audit (authoritative — `workflows.pitch_audit.audit_voice`)

| Voice | audible | strong_ok | weak_in_scale | tagged (resolving) | non-resolving | untagged_out | strong_viol | **passes** |
|---|---|---|---|---|---|---|---|---|
| Lead | 43 | 6 | 34 | 3 (3) | 0 | 0 | 0 | ✅ |
| Counter | 20 | 0 | 20 | 0 | 0 | 0 | 0 | ✅ |
| Harmony | 80 | 40 | 40 | 0 | 0 | 0 | 0 | ✅ |
| Bass | 40 | 40 | 0 | 0 | 0 | 0 | 0 | ✅ |

**Verdict: `all_pass = true`** — 0 un-tagged out-of-scale, 0 non-resolving
ornaments, 0 strong violations, across all 4 pitched voices.

## 6. Grid audit (mido readback)

| Artifact | voices | off-grid (16th/8th) | zero-drift (equal track lens) | pitched notes |
|---|---|---|---|---|
| phase1 | 1 | **39**/40 (raw, expected) | ✅ (38400) | 40 |
| perfect | 5 | **0**/183 | ✅ (38400 × 5) | 183 |
| humanized | 5 | **168**/183 (>0 proves humanizer ran) | ✅ (38400 × 5) | 183 |

Note: the verify.py scan reports `weak_out_of_scale=3` on the perfect Lead —
these are exactly the 3 **tagged chromatic approach ornaments** (exempt by the
tiered discipline; the authoritative `audit_voice` counts them as
`tagged_resolving=3`, not violations).

## 7. Humanization (always-on, style-derived, seeded)

- `hz_seed = 84037` (md5 of project name) · style **japanese** profile +
  per-instrument DNA via `export_dual` (validate → export perfect → humanize →
  re-validate → export humanized).

| Voice | seed | mean abs shift (ticks) | max shift (ticks) | vel Δ | timing σ (ticks) |
|---|---|---|---|---|---|
| Lead (koto) | 8487737 | 3.21 | 10 | 4.81 | 4.37 |
| Counter (shakuhachi) | 8487738 | 2.45 | 6 | 6.25 | 4.37 |
| Harmony (shamisen) | 8487739 | 2.81 | 8 | 3.45 | 4.37 |
| Bass (koto low) | 8487740 | 5.45 | 13 | 3.25 | 3.74 |
| Drums | 8487741 | **0.62** | 2 | 2.54 | 1.25 |

Drums tightest (0.62 ticks mean shift — anchors grid), bass lays back most
(5.45 ticks = ~8 ms at 78 BPM) — correct role DNA. All voices zero-drift after
humanization (forward-clamp + boundary-clamp + pinned terminal landmark).

## 8. Render & master (FluidSynth → `master()` → Opus OGG)

| Artifact | target LUFS | measured LUFS | true peak | silence | RMS mean | OGG bytes |
|---|---|---|---|---|---|---|
| phase1 | −14.0 | −17.83 | −1.0 dBTP | 37.1% (raw sparse draft) | 0.0967 | 553676 |
| perfect | −14.0 | −15.27 | −1.0 dBTP | 7.0% | 0.1412 | 489648 |
| humanized | −14.0 | −15.43 | −1.0 dBTP | 7.0% | 0.1389 | 488035 |

SoundFont: `discover_soundfont()` → FluidR3_GM.sf2. Mastered to
`target_for_style("japanese")` (falls back to −14.0 — "japanese" is not in
`GENRE_LUFS`, so the balanced −14 default applies) with −1 dBTP ceiling.

**Measured LUFS sits ~1.3 dB below the −14 target**: the piece is transient-rich
(koto/shamisen plucks, high crest factor), so the true-peak limiter engages at
−1 dBTP and pulls the integrated loudness below the nominal target — exactly the
documented "true-peak is a CEILING" behaviour (dynamic material lands quieter
than the LUFS target). True peak is exactly −1.0 dBTP (≤ −1 requirement met).
Phase-1's 37% silence is the intentional sparse single-voice raw draft ("ma"
space); the production renders are 7% silent (healthy).

## 9. Files

| Path | Size |
|---|---|
| `MIDI/275-japanese-pso-rondo-phase1.mid` | 448 B |
| `MIDI/275-japanese-pso-rondo-perfect.mid` | 2249 B |
| `MIDI/275-japanese-pso-rondo-humanized.mid` | 2259 B |
| `Audio/275-japanese-pso-rondo-{phase1,perfect,humanized}.ogg/.wav` | see render_report.json |
| `Analysis/pitch_audit.json`, `verify_report.json`, `render_report.json`, `compose_summary.json` | — |
| `REPORT.md`, `README.md`, `index.html` | — |

## 10. Fixes applied during the run

1. **Harmony root off-key** — `build_harmony` used `diatonic(d-1, base=60)`
   (C4, out of A yo scale) → corrected to `base=57` (A3). This was the 40
   strong / 22 out-of-scale violations in the first audit run.
2. **Phase-1 section anchoring** — `rel_events(seg, 0, s_ticks)` left phase-1
   notes at absolute ticks, dropping everything past the first section → fixed
   to `rel_events(seg, s_start_ticks, s_ticks)` so the raw draft spans the full
   20-bar rondo (40 notes now, was 8).

## 11. Verification summary

- MIDI + OGG non-empty (`> 40` bytes asserted).
- Perfect == 0 off-grid, humanized == 168 off-grid (humanizer ran).
- Tiered harmony: 0 untagged / 0 non-resolving / 0 strong violations.
- Zero-drift readback: all 5 note tracks equal length (38400 ticks).
- Post-master loudness: see §8 (`render_report.json`).
