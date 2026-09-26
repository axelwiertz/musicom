# 206-ragtime-skeleton-refinement

**Genre**: Ragtime · **Method**: 001 Skeleton-First Refinement (concrete)
**Key**: C major · **Tempo**: 120 BPM (4/4) · **Form**: Intro|A|B|A2|Trio|Coda (40 bars)

Solo-piano stride rag in the Scott Joplin idiom. Composed with the two-phase
architecture: Phase 1 reads a deterministic scale-degree structural skeleton
into an unquantized single-voice draft; Phase 2 refines it (16th-grid snap,
chord-tone quantization, syncopated elaboration, stride bass + chord comp).

## Listen

- **Audio**: `Audio/206-ragtime-skeleton-refinement.ogg` (Opus)
- **DAW**: `MIDI/206-ragtime-skeleton-refinement.mid`
- **Raw draft**: `MIDI/206-ragtime-skeleton-refinement-phase1.mid`

## Status

- [x] Phase 1 raw draft (own zero-drift gate)
- [x] Phase 2 rules composition (own zero-drift gate)
- [x] Grid audit PASS (0 off-grid 16th)
- [x] Harmony audit PASS (0 out-of-key, 0 out-of-chord)
- [x] FluidSynth render + OGG
- [x] REPORT.md, grid visualization, provenance sidecars

## Files

```
206-ragtime-skeleton-refinement/
├── REPORT.md               # full composition report (primary record)
├── README.md
├── compose.py              # two-phase generator (engine-only)
├── verify.py               # grid + harmony + zero-drift audit (mido read-only)
├── verify_audio.py         # silence/RMS/peak profile
├── MIDI/
│   ├── 206-ragtime-skeleton-refinement.mid           (+ .provenance.json)
│   └── 206-ragtime-skeleton-refinement-phase1.mid    (+ .provenance.json)
├── Audio/
│   ├── 206-ragtime-skeleton-refinement.wav
│   └── 206-ragtime-skeleton-refinement.ogg
└── Analysis/
    ├── grid_visualization.txt
    ├── summary.json
    └── render_stats.json
```
