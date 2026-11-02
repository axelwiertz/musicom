# REPORT — 279-kuramoto-techno-sync

**Primary record.** Nightly composition job · 2026-11-01.

| Field | Value |
|---|---|
| **Project** | `279-kuramoto-techno-sync` (next ID after 278) |
| **Style** | **Techno** — random draw from `/opt/data/projects/Styles/` |
| **Method** | **038 — Kuramoto Oscillator Phase Synchronization (KOPS)** |
| **Layer** | **concrete** (emits `MusicEvent`s that fill UnitMatrix cells directly; no abstract design stage) |
| **Paradigm** | **Nature-Led** |
| **Form** | **intro-break-drop-outro** `Intro 4 / Break 8 / Drop 8 / Outro 4` (24 bars) — via `pick_form("techno")` → `form_to_sections` |
| **Key** | **A minor (aeolian)** — pcs `{9,11,0,2,4,5,7}` = A B C D E F G |
| **Tempo / Meter** | 128 BPM · 4/4 · 480 TPB (BAR = 1920, 8th 240, 16th 120) |
| **Seeds** | raw `20261101` (nightly date) · humanize `4649` (md5 of project name) |

## 1. Selection (LAYERED METHODOLOGY)

Method 038 was drawn from the **concrete** pool (124 candidates) excluding the
last-7-days set. The previous night's composition (277, 2026-10-31) was concrete
(036 ASAR); the abstract branch (`~1/7`) last fired on the rework 276 (095 CTC),
so this night the `~6/7` concrete branch fires. Style drew **Techno** with
`random.Random(20261101)`; form resolved via `pick_form("techno")` →
`intro-break-drop-outro` (the style's driving EDM shape).

## 2. Method — Kuramoto Oscillators (phase synchronization)

Phase-1 generative core is a faithful implementation of Method 038 (KOPS):

- **Ensemble**: N = 16 coupled phase oscillators, `dθᵢ/dt = ωᵢ + (K/N)Σⱼsin(θⱼ−θᵢ)`,
  integrated with the mean-field trick (`r·e^{iψ} = ⟨e^{iθ}⟩`) at dt = 2 ms.
- **Natural frequencies**: `ωᵢ = 2π·0.6·(1 + 0.30·zᵢ)` (Hz-ish, `zᵢ` gaussian) —
  fixed across the piece, so the *coupling alone* drives the arc (faithful to the
  method — no hand modulation of the natural dynamics).
- **Coupling arc** (the "composer's hand" on `K`): `Intro 0.7 → Break 0.7→2.8 →
  Drop 3.5 → Outro 3.5→0.7`.
- **Decode**: oscillator index → diatonic pitch row (`Scale7ChordDegree.
  get_diatonic_note`, A2 up two octaves); each phase wrap of `2π` → a note; onset
  from the fire time; velocity ∝ the local **order parameter** `r`.

**Result**: **425 firings**, and the order parameter tells the sync story:

| Section | firings | mean order param `r` | reading |
|---|---|---|---|
| Intro | 70 | 0.364 | desynchronized (near the N=16 finite-size noise floor `1/√16 ≈ 0.25`) |
| Break | 147 | 0.476 | partial entrainment — emergent polyrhythmic lock-in |
| Drop | 144 | **0.944** | full phase-lock (far above noise) — ensemble collapses onto a unified pulse |
| Outro | 64 | 0.765 | decaying, still partially locked |

Velocity scales with `r`, so the Drop also *hits harder* (louder), not just
denser — the classic Kuramoto "rhythmic lock-in" payoff.

## 3. Form & progression (intro-break-drop-outro, 24 bars)

| Section | Bars | Progression (degrees) | Chords |
|---|---|---|---|
| Intro | 4 | 1 1 6 7 | Am Am F G |
| Break | 8 | 1 6 3 7 (×2) | Am F C G (×2) |
| Drop | 8 | 1 6 1 7 (×2) | Am F Am G (×2) |
| Outro | 4 | 1 6 7 1 | Am F G Am |

Diatonic degree roots computed with `Scale7ChordDegree.get_diatonic_note`
(aeolian offsets `[0,2,3,5,7,8,10]`) — no `%7` wrapper, no uppercase-degree
fallback → no minor-key degree-root collapse (per-bar roots distinct).

## 4. Voices & instruments (from `instrument_registry.py`)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Lead | Synth Voice | 54 | 0 | Kuramoto firing cascade (sync arc) |
| Harmony | Synth Brass 1 | 62 | 1 | strong-beat rave stabs |
| Pad | Synth Pad | 88 | 2 | sustained whole-bar chord |
| Bass | Synth Bass 1 | 38 | 3 | driving 8th-note root pulse |
| Drums | Drum Kit | 0 | 9 | four-on-floor kick, offbeat hats, clap on 2 & 4 |

## 5. Phase 1 — raw draft

`-phase1.mid`: single Lead voice (Synth Voice), 425 audible notes, **421/425
off-grid** (proves rawness), **155 out-of-scale** chromatic notes (pre-rules),
1 strong-violation (raw). Own `validate()` gate: PASS (track length 46080).

## 6. Phase 2 — rules post-process

- **Tiered quantize** (`classify_weight` → `ScaleQuantizer.tiered_quantize`):
  strong onsets (beats 1&3) snap scale→chord (hard in-scale AND in-chord); weak
  onsets snap scale only.
- **Grid snap**: every onset → 16th grid (multiple of 120).
- **Dedup** (start,pitch collisions → keep longest) + **voice-leading** (break
  parallel perfect 5ths/octaves).
- **Tagged ornaments**: 3 chromatic approach notes on the lead, tagged
  `weight=weak, ornament=approach, resolve_pitch=<target>` — legal under the
  tiered discipline, each resolves by step to a scale tone within 1 grid step.

## 7. Grid audit (verify.py, mido readback)

| Artifact | pitched | off-grid (16th) | verdict |
|---|---|---|---|
| phase1 | 425 | 421 | raw (expected) |
| **perfect** | 801 | **0** | ✓ grid-locked |
| **humanized** | 801 | **678** | humanizer ran (>0) ✓ |

All 801 perfect-layer onsets are multiples of 120 (0 off-grid). The 208 notes
flagged "off 8th" are lead 16th-offset notes (multiples of 120, not 240) — still
on the 16th grid. Per-voice off-grid (16th): Lead 0/393, Harmony 0/144, Pad 0/72,
Bass 0/192, Drums 264 (channel 9, written on-grid, skipped by the pitched audit).

## 8. Harmony audit (tiered, `workflows.pitch_audit.audit_voice`)

| Voice | audible | strong_ok | weak_in_scale | tagged (resolving) | untagged_out | non_resolving | strong_viol | PASS |
|---|---|---|---|---|---|---|---|---|
| Lead | 393 | 42 | 348 | 3 (3) | 0 | 0 | 0 | ✓ |
| Harmony | 144 | 144 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Pad | 72 | 72 | 0 | 0 | 0 | 0 | 0 | ✓ |
| Bass | 192 | 48 | 144 | 0 | 0 | 0 | 0 | ✓ |

**Verdict: `all_pass = true`** — 0 untagged out-of-scale, 0 non-resolving, 0
strong violations across all 4 pitched voices. Only the lead carries tagged
ornaments (3, all resolving); Harmony/Pad/Bass are chromatic-free. (The 3
`out_of_scale` hits in verify.py's *naive* scan are exactly these tagged,
resolving lead ornaments — legal under the tiered discipline.)

## 9. Humanization (always-on, style-derived, seeded)

`hz_seed = 4649` · style **techno** profile (timing σ 2.0 ms, phrase_corr tight)
+ per-instrument DNA from the registry:

| Voice | child seed | mean abs shift (ticks) | max shift | vel Δ | timing σ (ticks) |
|---|---|---|---|---|---|
| Lead | 469549 | 1.524 | 6 | 7.092 | 2.048 |
| Harmony | 469550 | 1.625 | 5 | 2.986 | 2.048 |
| Pad | 469551 | 1.486 | 4 | 3.820 | 2.048 |
| Bass | 469552 | **7.979** | 22 | 3.266 | 5.120 |
| Drums | 469553 | 1.345 | 5 | 3.292 | 2.048 |

Bass lays back most (mean 7.98 ticks ≈ 7.8 ms — its 8 ms layback DNA); drums
anchor tight (1.35 ticks ≈ 1.3 ms); melodic voices share the tight 2.05-tick
techno timing sigma. Zero-drift preserved after humanization.

## 10. Zero-drift

`validate()` PASS on phase-1, phase-2 (perfect) and phase-2 (humanized). mido
readback: all note tracks equal **46080 ticks** for every artifact.

## 11. Render + master

`target_for_style("techno")` = **−10.0 LUFS**, ceiling **−1 dBTP**.
`discover_soundfont()` → FluidR3_GM.sf2. All three MIDIs rendered (FluidSynth
`-ni -g 1.2 -R no -C no`) → mastered (`master()`) → Opus OGG.

| Artifact | integrated LUFS | true peak dBTP | silence ratio | RMS mean | RMS max | OGG bytes |
|---|---|---|---|---|---|---|
| phase1 | −11.82 | −1.00 | 7.94% | 0.191 | 0.284 | 257 324 |
| perfect | −10.91 | −1.00 | 12.01% | 0.182 | 0.254 | 296 394 |
| humanized | −10.86 | −1.00 | 11.98% | 0.184 | 0.252 | 297 178 |

All three land at true-peak −1.00 dBTP (the punchy four-on-floor kick + clap
hits the ceiling). Integrated LUFS sits ~0.9 dB below the −10 target because the
true-peak limiter is the **binding constraint** — it is a ceiling, not a make-up
target; a transient-heavy techno mix reaches −1 dBTP before −10 LUFS. This is
correct behaviour (documented: "true-peak is a ceiling, not a target"), not a
defect. Silence 8–12% — healthy, far below the 30% suspect threshold (the
sustained pad + continuous bass + four-on-floor keep the track filled).

## 12. Files

| File | Size (bytes) |
|---|---|
| `MIDI/279-kuramoto-techno-sync-phase1.mid` | 2991 |
| `MIDI/279-kuramoto-techno-sync-perfect.mid` | 8222 |
| `MIDI/279-kuramoto-techno-sync-humanized.mid` | 8217 |
| `Audio/*.wav` (×3) + `Audio/*.ogg` (×3) | see render_report.json |
| `Analysis/{grid_visualization,grid_visualization_phase1}.txt` | ✓ |
| `Analysis/{compose_summary,pitch_audit,verify_report,render_report}.json` | ✓ |

## 13. Fixes applied

- **None required** — the compose pipeline (Kuramoto mean-field simulation →
  raw events → tiered quantize → grid snap → dual export) passed `validate()`,
  zero-drift, grid audit (0 off-grid), and the tiered harmony audit on the first
  run. Coupling values (`0.7/2.8/3.5`) and `ω₀ = 0.6 Hz` were chosen so the
  order parameter cleanly spans desync (0.36) → full lock (0.94) → decay (0.77),
  giving the techno intro→break→drop→outro narrative.