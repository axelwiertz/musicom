# 084 — Soul Voice-Leading Graph

Soul study in D minor (92 BPM): a weighted random walk over a tonal-function
graph (Method 011) generates a raw melodic draft (phase 1), then musicom rules
grid-lock, chord-quantize, and voice-lead it into a full 6-voice soul
arrangement (phase 2).

## Listen / Use

- **Full mix**: `Audio/084-soul-voiceleading-graph.ogg`
- **Raw draft (phase 1)**: `Audio/084-soul-voiceleading-graph-phase1.ogg`
- **MIDI**: `MIDI/*.mid` (phase1 + phase2, zero-drift validated)

## Structure

24 bars — Intro | Verse | Chorus | Verse2 | Chorus2 | Outro (4 bars each)

Progression (D-aeolian): `i i VI VII | i VII iv VI | i iv III i | VI VII i VII | i iv v III | VI iv v i`

## Voices

| Voice | Role | Register |
|---|---|---|
| Tenor Sax (lead) | graph-walk melody, chord-tone quantized, leap cap 9 | A3–E6 |
| Rhodes | offbeat 8th comp | C4–C6 |
| Violin | whole-bar triad pad | D4–A4 |
| Acoustic Guitar | 8th strum | C3–C5 |
| Electric Bass | root pulse + 16th next-bar push | Bb1–A2 |
| Drums | backbeat (kick 1&3, snare 2&4, 16th hats, claps in choruses) | ch9 |

## Method

**Two-phase** (mandatory for generative methods):
1. **Phase 1**: `TonalNetworkGenerator` weighted walk over the tonal function
   graph — raw pitch wander around each node's chord tones with unquantized
   fractional-tick rhythm (off-grid by design).
2. **Phase 2**: 8th-grid lock → D-minor scale snap → chord-tone quantization per
   bar → voice-leading (leap cap ≤ 9, parallel/hidden 5ths & 8ves checked via
   `VoiceLeadingRules(style="classical")`) → texture arrangement → zero-drift.

## Verification

`audit_084.py` → **AUDIT PASS** (0 off-grid 16th, 0 out-of-scale, 0 out-of-chord,
0 voice-leading flags). See `REPORT.md` for details.

## Files

- `compose_084.py` — two-phase composition
- `audit_084.py` — grid + harmony + VL audit
- `render_audio.py` / `audio_stats.py` / `audio_provenance.py` — SP-001 pipeline
- `Analysis/` — audit JSONs, grid visualization, render stats

## SoundFont

FluidR3_GM.sf2 via `discover_soundfont()` (preferred). TimGM6mb fallback only.
