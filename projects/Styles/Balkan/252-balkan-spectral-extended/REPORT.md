# REPORT — 252-balkan-spectral-extended (REWORK of 228)

Autonomous nightly REWORK job · 2026-10-19 · job `rework` (senior Musicom agent)

## 1. Selection & audit

| Field | Value |
|---|---|
| Source project | `/opt/data/projects/Styles/Balkan/228-balkan-spectral/` (random pick, 155 eligible) |
| Genre | Balkan |
| Source primary MIDI | `MIDI/228-balkan-spectral.mid` (24 bars, 6×4, G Dorian 7/8) |
| `rework_audit.json` | `Analysis/rework_audit.json` |

**Audit vs current standards** — 5/6 pass, 1 fail ⇒ **redesign required** (but the
musical identity was already fully engine-compliant, so it is an *extension* in
practice):

| # | Standard | Result |
|---|---|---|
| 1 | Engine (UnitMatrixComposer, no raw mido authoring) | **PASS** |
| 2 | Zero-drift (all voice tracks equal length) | **PASS** (4 tracks × 40320) |
| 3 | Rhythm-grid sync (onset % 120/240) | **PASS** (off-grid 0/532) |
| 4 | ≥4 voice tracks | **PASS** (Bass/Accordion/Clarinet/Violin) |
| 5 | Two-phase artifacts (`.mid` + `-phase1.mid`) | **PASS** |
| 6 | provenance.json **+ index.html** | **FAIL** — index.html missing |

## 2. What changed (extension, same DNA)

Preserved identity: **Balkan dajčovo 7/8**, **G Dorian** `{G A Bb C D E F}`,
**132 BPM**, **method 051 SGLM** (Fiedler vector → lead contour, 2nd eigenvector
→ violin counter-axis, algebraic connectivity → tension), instrumentation
**double bass(43)/accordion(21)/clarinet(71)/violin(40)**.

New: **32 bars (8×4)** vs source 24 (6×4). 8 sections: Intro → VerseA → LiftA →
VerseB → Dance → Bridge → Climax → Coda.

## 3. Variation techniques (6 distinct, ≥3 required)

| Section | Function | Technique |
|---|---|---|
| Intro | HOME | sparse intro — counter (violin) tacet |
| VerseA | HOME | baseline full texture (Fiedler lead + eig2 counter) |
| LiftA | TURN | **register shift UP (+12)** on clarinet lead |
| VerseB | TENSE | **counterline prominence** — violin eig2 lead, clarinet sparse |
| Dance | TURN | **diminution** — 16th-note subdivision (lead dens 9/bar) |
| Bridge | TENSE | **retrograde contour + register DOWN (−12)** |
| Climax | HOME | **augmentation** (sustain ×2) + **octave doubling** |
| Coda | HOME | diminution fade to tonic (lead dens 3/bar) |

## 4. Per-section harmonic regions (bar-0 tonic trap avoided)

Each section has its own 4-bar progression with a **varied starting degree** —
section start roots `[0,0,3,2,4,6,3,0]` (five distinct openings, not all `i`).
Full 32-bar progression: `i i VII VII · i VII IV i · IV II VII v · III VII IV i ·
v IV II VII · VII IV II v · IV VII i IV · i VII IV i` (G Dorian spellings).

## 5. Two-phase architecture

- **Phase 1** (`-phase1.mid`): single clarinet walking the HOME-graph Fiedler
  ordering end-to-end, off-grid onsets, ±1.5 semitone jitter + register drift,
  eigenvalue-gap density. Own `validate()` gate PASS.
- **Phase 2** (`-perfect.mid` + `-humanized.mid`): musicom rules — 8th/16th grid
  snap, per-bar chord-tone quantization, register clamp, dedup collided
  `(start_tick,pitch)`, 4-voice texture. Exported as **dual-version** via
  `workflows.humanize.export_dual`.

## 6. Humanization (always-on, style-derived, seeded)

- `style="folk"` (Balkan = folk dance → loose organic profile), `seed=20513007`
  deterministic, per-voice instrument DNA (bass lays back +8 ms, strings breathe).
- Real numbers → `Analysis/summary.json` (`humanize.per_voice`).

## 7. Verification (real numbers, mido read-back)

| Gate | Perfect | Humanized |
|---|---|---|
| voice tracks (equal len) | 4 × 53760 | 4 × 53760 |
| pitched notes | 708 | 708 |
| off-grid (not %120) | **0** | 641 (>0 ⇒ jitter ran) |
| off-8th (16th diminution, still %120) | 24 | 644 |
| out-of-key | **0** | **0** |
| out-of-chord (per-bar t//BAR) | **0** | 17* |

\* The 17 humanized out-of-chord notes are **onset micro-jitter crossing a bar
boundary** (bass roots + melody slot-0 notes at bar starts, ±~9 ticks). Pitch is
unchanged and still in-key (out-of-key = 0); the note merely falls a few ms the
far side of a bar line. Compositional chord discipline (perfect layer) is 0.

## 8. Audio (FluidR3_GM.sf2 → WAV → master −16 LUFS/−1 dBTP → Opus)

See `Analysis/render_stats.json`. Perfect + humanized mastered to `target_for_style("folk")`
= −16.0 LUFS; phase1 rendered raw (draft audition).

## 9. Fixes applied this run

1. **7/8 humanizer span mismatch**: default `beats_per_bar=4` ⇒ `ticks_per_bar
   1920` (4/4), so the humanizer's per-section clamp `span` was 7680 instead of
   the real 6720-tick section, letting note tails overshoot/burn the section
   seam ⇒ zero-drift FAIL (`[53760,53760,53754,53769]`). Fixed with
   `beats_per_bar=14` (`ticks_per_bar = 480×14 = 6720` = one section) + sections
   `bars=1` ⇒ span = 6720 exactly.
2. **Terminal landmark** `_pad()` now *always* emits a pitch-0 landmark at
   `(total−1,total)` so every cell ends exactly on the seam regardless of
   duration-breathing (previously skipped when a note already touched `total`).