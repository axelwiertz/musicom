# 203 — Brownian Chorale Variations

**Rework of:** 062-brownian-chorale (autonomous nightly rework job, 2026-09-25)
**Genre:** Experimental
**Method:** 048 — Reflected Brownian Motion Pitch Diffusion (RBMPD)
**Decision:** redesign (source failed audit standards 5 & 6)

## Concept

An extension of the Reflected Brownian Motion chorale. Each voice is a particle
diffusing through a pitch corridor bounded by reflective barriers (register
limits), pulled back to HOME by a tonic drift. Mirror reflections at the barriers
spawn the signature motif repeats and neighbor-tone turns, then pass through the
musicom harmonic + voice-leading rule layer.

## What changed vs 062

| Axis | 062 (source) | 203 (this) |
|---|---|---|
| Form | 8 bars, single block | 16 bars, 4 regions × 4 bars |
| Sections | 8 × 1 bar | 16 × 1 bar |
| Voices | 4 (S/A/T/B) | 6 (S/A/T/B + violin counterline + ch9 drums) |
| Phase-1 MIDI | missing | exported (raw single-voice draft) |
| provenance.json / index.html | missing | present |
| Progression | i-VI-III-VII only | 4 per-region progressions |
| Seed | 4801 | 9007 |

## Key / tempo

C aeolian (root 48) · 84 BPM · 480 ticks/beat · 4/4 · BAR = 1920 ticks

## Form & harmonic regions

| Region | Bars | Degrees | Variation technique |
|---|---|---|---|
| Intro | 1–4 | i · VI · III · VII | source anchor (identity preserved) |
| Verse | 5–8 | III · VII · i · VI | harmonic rotation + register lift |
| Chorus | 9–12 | iv · VII · VI · III | augmentation (8ths) + counterline enters |
| Bridge | 13–16 | v · iv · VII · i | retrograde + density rise |

Each region is its own harmonic region; root/quality derived from the region
midpoint chord (2nd bar) — never the bar-0 tonic bug.

## Two-phase architecture

- **Phase 1** — raw reflected-Brownian pitch walk (unquantized, single voice) →
  `MIDI/203-brownian-chorale-variations-phase1.mid`
- **Phase 2** — musicom rules: chord-tone quantization per bar, classical voice
  leading (VoiceLeadingRules), rhythm-grid snap, register enforcement →
  `MIDI/203-brownian-chorale-variations.mid`

## Files

- `MIDI/203-brownian-chorale-variations.mid` — phase-2 full (rules-processed)
- `MIDI/203-brownian-chorale-variations-phase1.mid` — phase-1 raw draft
- `Audio/203-brownian-chorale-variations.ogg` — Opus render (FluidSynth)
- `Audio/203-brownian-chorale-variations.wav` — PCM render
- `Analysis/grid_visualization.txt` — high-contrast rhythm DNA grid
- `index.html` — VoltAgent dashboard

## Verification (read-only mido audit)

- 6 voice tracks, all length 30720 ticks (zero-drift)
- 0 off-grid pitched onsets · 0 scale violations · 0 chord violations (phase 2)
- silence ratio 6.1% · peak 0.957 · rough LUFS −15.8 dB
