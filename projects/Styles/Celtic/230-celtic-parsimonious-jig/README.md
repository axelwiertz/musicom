# 230-celtic-parsimonious-jig

**Celtic double jig × Method 104 (Parsimonious Subset Sequence Composition).**

| Field | Value |
|---|---|
| Project | 230-celtic-parsimonious-jig |
| Style | Celtic (6/8 double jig, D Dorian) |
| Method | 104 — Parsimonious Subset Sequence Composition (PSSC) |
| Layer | **abstract** |
| Key | D Dorian — D E F G A B C (pcs 2,4,5,7,9,11,0) |
| Tempo | 138 BPM (quarter) · 6/8 · 480 TPB · BAR = 1440 ticks |
| Form | 6 sections × 4 bars = 24 bars (Intro → Theme → Turn → Development → Dance → Coda) |
| Voices | Fiddle (110) lead · Flute (74) paired strand · Harp (46) broken chords · Cello (42) drone/bass · bodhrán-style kit (ch9) |

## Method

PSSC generalises Neo-Riemannian parsimonious voice leading (P/L/R) to arbitrary
n-subsets of a scale. The chord progression is a path through the 7-triad
D-Dorian subset network mixing strict parsimonious holds (≥2 common tones,
voice-leading ≤3) and parallel stepwise slides (0 common tones, all voices move
≤2 semitones — the signature i↔VII Dm→C Dorian lift). The fiddle melody is the
generated common-tone **pivot chain**; the flute is the **paired strand**
(inversion-bipartition = the moving non-common tone).

## Two-phase architecture

- **Phase 1** (`MIDI/*-phase1.mid`): raw single-fiddle walk, off-grid onsets,
  unquantized pitch (drift + jitter), no harmony — the parsimonious chain raw.
- **Phase 2** (`MIDI/*.mid`): 8th-grid snap → per-bar chord-tone quantization →
  full 5-voice Celtic texture.

## Verification (all gates PASS)

```
grid 16th off-grid : 0 / 524   (PASS)
grid 8th  off-grid : 0 / 524   (PASS)
out-of-key          : 0 / 420   (PASS, pitched voices)
out-of-chord        : 0 / 420   (PASS, pitched voices)
zero-drift (both)   : PASS
silence (phase2)    : 2.09 %    (no mid-track gaps)
```

## Files

- `MIDI/` — phase1 + phase2 `.mid` + provenance sidecars
- `Audio/` — phase1 + phase2 `.wav` / `.ogg` (Opus 48k)
- `Analysis/` — `grid_visualization.txt`, `summary.json`, `render_stats.json`
- `Scripts/` — `compose.py`, `render_audio.py`
- `REPORT.md` — full record (selection, method, progression, audits, fixes)

See `REPORT.md` for the complete audit and the parsimony edge table.
