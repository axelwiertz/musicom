# SP-016 — Granular Synthesis Engine — Cuban Trova

**Autonomous production pass (nightly cron job, 2026-08-14).**

## Source

| Field | Value |
|---|---|
| Composition | `001-cuban-trova-research` (Cuban) |
| Source MIDI | `daily-2026-07-01_cuban_001-cuban-trova-research_fixed.mid` |
| SHA-256 | `06925233da6c77a9...` |
| Notes | 96, 4 voices, tempo 96 BPM, ~15 s |
| Voices | Flute lead (prog 73), Nylon guitar (24), Electric bass (33), Piano (0) |

## Method — SP-016 Granular Synthesis Engine

From `methods_db.md`:

> **SP-016** | Granular Synthesis Engine | **Synthesis Engines** |
> Textured, Clouds, and Pad Timbres | Time-stretches, freezes, and scatters
> micro-acoustic grains with smooth windowing.

### Implementation

Every voice of the trova is granulated with musicom's canonical
`AperiodicGranulator` (`sound/synthesis/granular.py`):

1. **Dry render** of the full arrangement via FluidSynth CLI (TimGM6mb.sf2,
   `-g 1.2`) → source buffer (17.6 s).
2. **Per-voice stems**: each of the 4 tracks rendered separately so the
   arrangement structure survives inside the cloud.
3. **Granular clouds** per voice with SP-016 parameters (grain 35–60 ms,
   overlap-add with Hann windows, spray jitter 15–30 ms, grain-size jitter
   8–12 ms, density 30–80 grains/s):
   - **Lead flute** → cloud at **+7 semitones** (shimmering upper halo)
   - **Nylon guitar** → cloud at **0 semitones** (textural bed, densest)
   - **Electric bass** → cloud at **−12 semitones** (sub-octave gravity)
   - **Piano** → cloud at **+5 semitones** (crystalline dust)
4. **Mix**: dry bed 0.55 + clouds 0.30–0.35, then **AlgorithmicReverb**
   (Schroeder 8-comb/4-allpass, room 0.7, wet 0.25, width 0.8, modulation 0.1).
5. **Stereo spread** via 12 ms delayed copy (L/R).
6. **Master**: peak normalize to **−1 dBFS**.

### Why this works for trova

The trova is a singer-songwriter form: the guitar *tumbaos* and bass lock the
groove, the flute sings the melody. SP-016 keeps the dry bed at 0.55 so the
danceable core survives, while the clouds time-stretch the material into a
dreamier, doubled-length atmosphere (18 s output vs 15 s source) — a
"trova at dusk" production.

## Outputs

| Artifact | Path |
|---|---|
| WAV (stereo 44.1 kHz, 18 s) | `Audio/SP016-granular-cuban-trova.wav` |
| OGG (Opus 48k voip) | `Audio/SP016-granular-cuban-trova.ogg` |
| Source MIDI (copy) | `MIDI/original_cuban_trova_fixed.mid` |
| Per-voice stems (MIDI) | `MIDI/stem_*.mid` |
| Per-voice dry renders | `Audio/stem_*_dry.wav` |
| Per-voice granular clouds | `Audio/cloud_*.wav` |
| Render info (JSON) | `Analysis/render_info.json` |
| Sound check | `Analysis/check_sound.py`, `Analysis/check_clouds.py` |
| Provenance | `provenance.json` |

## Listen for

- **Pitch-layered cloud**: flute halo +7 st above, bass sub-octave −12 st
  below — the cloud spans ~2 octaves wider than the original.
- **Grain shimmer**: the nylon guitar cloud (80 grains/s, 35 ms grains) is
  the densest texture — the classic SP-016 "cloud" sound.
- **Groove intact**: dry bed at 0.55 keeps the son-style bass/guitar lock
  audible under the haze.
- **Decay tail**: last ~2 s are the granular + reverb tail ringing out.

## Quality gate

- Silence fraction: **12.3%** (under 30% suspect threshold; tail padding only
  — per-second RMS is healthy 0.12–0.15 through sec 15, then natural decay).
- Per-second RMS map: no mid-track dead zones.
- Spectral check: bass-dominant mix (233.5 vs mid 62.5 vs high 3.6), top peak
  ~165 Hz — consistent with bass cloud at −12 st.
- WAV 3.18 MB, OGG 101 KB — non-empty and valid.
- `assert os.path.getsize(...) > 1000` passed for both outputs.
