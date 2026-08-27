# SP-009 Convolutive Reverberation — "Een Klein Meisje" (live_render)

Nightly production job (autonomous, 2026-08-21).

## Source
- **Composition**: Folk/029-een-klein-meisje — `MIDI/live_render.mid`
- **Voices**: Acoustic Grand Piano (ch0, prog 0), Acoustic Guitar nylon (ch1, prog 24), Acoustic Bass (ch2, prog 32)
- **Tempo**: 108 BPM (set_tempo 555556), 71 s, 480 TPB

## Method: SP-009 Convolutive Reverberation
Acoustic environment emulation via room impulse responses. No measured IRs on
this host, so IRs were **synthesized**: early reflections (6-10 sparse echoes in
first 40 ms, blurred) + exponentially decaying noise tail (Schroeder-style,
-60 dB at RT60) + high-frequency damping (moving average). Per-voice
fftconvolve (scipy), wet/dry mix, then Haas-delay azimuth panning.

| Voice | IR env | RT60 | Wet | Pre-delay | Azimuth | Depth |
|---|---|---|---|---|---|---|
| Piano | church | 3.4 s | 0.38 | 45 ms | -18° | 0.55 |
| Guitar | hall | 2.2 s | 0.30 | 30 ms | +22° | 0.45 |
| Bass | hall | 2.2 s | 0.22 | 20 ms | +5° | 0.35 |

## Master
- Sum → tanh soft clip → peak normalize -1.0 dBFS → WAV (44.1 kHz stereo) → Opus OGG (48k voip)
- Silence fraction: 0.0309 (tail padding after last note is legit; mid-track gaps none)
- Peak 0.701, RMS 0.1081, duration 74.1 s

## Artifacts
- `SP009-klein-meisje-convolutive-reverb.wav` — full mix
- `SP009-klein-meisje-convolutive-reverb.ogg` — Telegram-ready Opus
- `MIDI/029-een-klein-meisje-live_render.mid` — source MIDI copy
- `stems/` — per-voice dry FluidSynth renders
- `provenance.json` — full provenance

## Listen for
- Piano sits in a wide church space (long 3.4 s tail, -18°).
- Guitar is closer, drier, offset right (+22°) — front of the picture.
- Bass stays tight (0.22 wet) so the low end does not blur.
- Early reflections give the room "walls" before the tail blooms.
