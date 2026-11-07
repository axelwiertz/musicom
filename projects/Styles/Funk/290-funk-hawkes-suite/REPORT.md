# REPORT — 290-funk-hawkes-suite

**Project:** 290-funk-hawkes-suite
**Style:** Funk
**Method:** 045 Hawkes Process Self-Exciting Composition (HPSEC) — rework
**Layer:** concrete
**Date:** 2026-11-07 (nightly rework agent)
**Seed:** 20261107 · humanize seed 141477975 (SEED*7+1)
**Key:** F natural minor (F G Ab Bb C Db Eb; lead uses pentatonic blues colour)
**BPM:** 100 · 4/4 · 480 TPB (bar = 1920, 8th = 240, 16th = 120)

---

## 1. Source + audit

Chosen source: `088-funk-hawkes` (Funk, F minor, 100 BPM, 6 sections / 24 bars,
Hawkes self-exciting process).

Audit against current engine standards:

| # | Standard | Result |
|---|----------|--------|
| 1 | Engine (UnitMatrixComposer, no raw mido authoring) | PASS |
| 2 | Zero-drift (all voice tracks equal length) | PASS (6 × 46080) |
| 3 | Rhythm-grid sync (pitched onsets % 120/240) | PASS (off-grid 0) |
| 4 | Track setup (≥4 voice tracks) | PASS (6 voices) |
| 5 | Two-phase artifacts (.mid + .mid-phase1) | PASS |
| 6 | provenance.json + index.html | **FAIL** (both missing; sidecars only) |

`redesign_required = true` (standard 6). The musical material is engine-
compliant, so the rebuild preserves the full identity (genre/key/tempo/method/
instrumentation/motif) and re-emits it through the canonical two-phase +
dual-version pipeline, this time WITH dashboard + top-level provenance.

## 2. What changed (rework)

- **Longer form**: 6 → 8 sections, 24 → 32 bars.
  `Intro | Verse | Chorus | Break | Verse2 | Chorus2 | Bridge | Outro`.
- **Per-section harmonic regions**: each section has its OWN 4-bar progression;
  the section ROOT is the MIDPOINT bar chord (index 1), NOT bar 0 — this kills
  the bar-0-always-tonic bug. Section roots: VI, iv, VI, v, III, VI, III, iv
  (all distinct from the tonic `i`).
- **Dual-version export** (new standard): `-perfect` (grid-locked) +
  `-humanized` (style+funk + per-instrument DNA, seeded) via `export_dual`.
- **Dashboard + top-level provenance.json** now present (the audit failure).
- Fixed drum backbeat bug inherited from source: snare/clap now beats 2 & 4
  (480/1440), kick 1 & 3 (0/960), "1& 3&" drive 240/1200 (source had snare on
  beat 3 & 7 = 960/2880, which overflowed the section boundary).

## 3. Variation techniques (6 applied)

| Technique | Where | How |
|-----------|-------|-----|
| Transposition / register shift | Verse2 | lead center +12 (octave up vs Verse) |
| Retrograde | Bridge | lead = reversed Chorus2 pitch sequence |
| Inversion | Bridge | sax = Verse sax inverted around axis 70 |
| Augmentation | Outro | lead doubled durations (half-note spacing, half speed) |
| Diminution | Chorus2 | lead density 48 (16th-note denser than Chorus) |
| Density rise | Chorus2 | full drum kit + claps + crash + 16th hats |
| Counterline | (throughout) | sax call-response answers on beats 2 & 4 |

## 4. Two-phase architecture

**Phase 1** (`-phase1.mid`, single voice, pre-rules): Hawkes self-exciting
point process, Ogata-thinned Exp(λ) sojourn times → FRACTIONAL off-grid ticks,
unquantized pitch drift around section centers with reflecting barriers +
tonic-centering. No harmony/bass/drums.

**Phase 2** (rules): grid-lock 16th + dedup → F-minor-pentatonic snap →
chord-tone quantize per bar (floor `t//BAR` global lookup) → register/range
enforcement → voice-leading leap cap ≤9 → six-voice funk texture →
zero-drift landmark → `validate()` gate.

## 5. Verification (read-only mido audit)

| Check | phase1 | perfect | humanized |
|-------|--------|---------|-----------|
| tracks | 2 (1 voice) | 7 (6 voices) | 7 (6 voices) |
| zero-drift | OK | OK (6 × 61440) | OK (6 × 61440) |
| pitched note_on | 238 | 895 | 895 |
| off-grid | (raw, by design) | **0** | 788 (>0 → jitter ran) |
| scale violations (pc ∉ F-min) | 99 (raw) | **0** | **0** |
| chord violations (t//BAR) | 170 (raw) | **0** | 9* |

\* The 9 humanized "chord violations" are cross-bar jitter attribution, not
pitch errors: the humanizer only shifts timing/velocity (pitch is identical to
the perfect layer, which has 0 chord violations). These 9 notes sit ≤2 ticks
from a bar line and got nudged across it (e.g. a bar-boundary cello pad at
tick 19200 → 19199). Scale violations remain 0 because pitch is unchanged.

## 6. Humanization summary (funk profile + instrument DNA)

| Voice | timing σ (ms) | mean|shift (ticks) | max|shift | mean|Δvel |
|-------|---------------|----------------|---------------|-------------|
| Drums | 2.0 (anchor) | 1.09 | 4 | 3.19 |
| Lead (trumpet) | style 4.0 | ~2.3 | 8 | ~4.0 |
| Bass | 10.0 (+8ms layback) | 7.73 | 26 | 4.67 |

Drums tightest, bass lays back — the role-DNA contract. Seeded per voice
(`SEED*101 + row`), deterministic.

## 7. Artifacts

- `MIDI/290-funk-hawkes-suite-phase1.mid` — raw generative draft (pre-rules)
- `MIDI/290-funk-hawkes-suite-perfect.mid` — grid-locked concrete layer
- `MIDI/290-funk-hawkes-suite-humanized.mid` — style + DNA humanization
- `Audio/290-funk-hawkes-suite-{perfect,humanized}.wav` — mastered (LUFS −13)
- `Audio/290-funk-hawkes-suite-{perfect,humanized}.ogg` — Opus (Telegram)
- `Analysis/grid_visualization.txt`, `Analysis/manifest.json`,
  `Analysis/render_stats.json`, per-artifact `.provenance.json`,
  top-level `provenance.json`, `index.html` dashboard
