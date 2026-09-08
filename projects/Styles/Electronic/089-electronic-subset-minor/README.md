# 089 — Electronic · Subset-Walk Minor

Abstract-layer weekly run: ABS-002 Subset Walker + ABS-001 tension steering
over a 13-node A-minor subset network, closed with a method-006 G7→Am
cadence. A natural minor, 112 BPM, 24 bars.

| | |
|---|---|
| Style | Electronic |
| Layer | abstract |
| Method | ABS-002 + ABS-001 + method-006 close |
| Key / BPM | A natural minor / 112 |
| Form | Intro · Verse · Chorus · Break · Verse2 · Outro (4 bars each) |
| Progression | i v VI III VI III V7 iv7 V7 v7 V7 IIImaj7 VII v iv VI iv v VI III iv III V7 i |
| Voices | Marimba (lead) · Clarinet · Cello · Dulcimer · Double Bass · Drum Kit |
| Audio | `Audio/089-electronic-subset-minor.ogg` (54 s) |
| MIDI | `MIDI/089-electronic-subset-minor.mid` (+ `-phase1.mid` raw draft) |
| Verdict | Grid 0 off-grid · Harmony 0 violations · VL 0 flags · Silence 5% · **AUDIT PASS** |

## Listen
`Audio/089-electronic-subset-minor.ogg` — full mix.
Stems in `Audio/stems/` for DAW import.

## How it was made
Phase 1 = raw single-marimba draft whose pitches are sampled from the current
walked subset (the walk is audible as raw material), rhythm off-grid
euclid-clustered. Phase 2 = 16th-grid lock, A-minor + chord-tone quantize per
bar, voice-leading fixes, then full texture (counterline, pad, arp, bass,
drums). Details + real verification numbers in `REPORT.md`.

## Files
- `compose.py` — two-phase composition (deterministic, seeded)
- `audit.py` — grid + harmony + zero-drift audit (AUDIT PASS)
- `render_audio.py` — SP-001 render + stems + stats
- `MIDI/` `Audio/` `Analysis/` — artifacts + provenance
