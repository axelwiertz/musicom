# 242 — Trap Phase

**Nightly composition job — 2026-10-14**
**Style:** Trap | **Method:** 026 Deconstructive Phase-Shift Minimalism (DPSM) | **Layer:** concrete

## Selection

| Field | Value |
|---|---|
| seed | 20261014 |
| layer roll | 0.7275 → **concrete** (~6/7 concrete cadence) |
| method | **026 Deconstructive Phase-Shift Minimalism** (Rules-Based, DPSM) |
| style | Trap |
| form | **cinematic-build** (Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars) |
| key | D natural minor (aeolian on D, tonic D3 = 50), 4/4, 480 TPB, bar = 1920 ticks |
| bpm | 140 |
| 16th grid | 120 ticks | 8th grid | 240 ticks |

## Method interpretation (concrete → engine)

Method 026: "Multiple identical looping voice streams with dynamic phase
offsets to create complex phasing and emergent rhythms." MIDI is discrete, so
phase shift is expressed as:

1. **Identical loop** — a one-bar, 8-event motif: a 4-tone 7th-chord arpeggio
   contour `[0,1,2,3,2,1,3,0]` at 8th-note spacing. This single cell is the
   whole melodic DNA.
2. **Dynamic phase offsets** — up to four copies of the *same* loop play with
   bar-by-bar phase offsets (in 8th-note units). Loop2 drifts a full 0→7 cycle
   across the Build section (Reich-style); Loop3 drifts across the Rise;
   Peak spreads the four loops at 0/2/4/6 (maximal interference); Resolve
   converges to unison. Offsets rotate by whole 8th notes, so every onset
   stays a multiple of 240 ticks.
3. **Emergent rhythm** — the interference between offset copies is the point
   of the method (phasing texture), not new notes. Every loop/bass/pad note is
   a chord tone of its own bar **and** in D natural minor.

Phase schedule (8th-note units, per section):

| Voice | Intro | Build | Rise | Peak | Resolve |
|---|---|---|---|---|---|
| Loop1 | 0 | 0 | 0 | 0 | 0 |
| Loop2 | — | drift (bar−4)%8 | 4 (frozen) | 2 | — |
| Loop3 | — | — | drift (bar−12)%8 | 4 | — |
| Loop4 | — | — | — | 6 | — |

## Chord path (32 bars) — all diatonic 7th chords in D natural minor

| Section | Bars | Degrees |
|---|---|---|
| Intro | 1–4 | Dm7 (i) ×4 — tonic drone |
| Build | 5–12 | i VI i VI i VII i VII |
| Rise | 13–20 | VI III VI III VII VI VII III |
| Peak | 21–28 | III VII i VI VII i VI VII |
| Resolve | 29–32 | i ×4 — tonic close |

Chord-tone pitch classes: Dm7 = {2,5,9,0}, Bbmaj7 = {10,2,5,9},
Fmaj7 = {5,9,0,4}, C7 = {0,4,7,10}. All ⊂ D natural minor {2,4,5,7,9,10,0}.

## Voices & instruments (from the instrument registry)

| Voice | Instrument | GM program | Channel | Role |
|---|---|---|---|---|
| Loop1–4 | Electric Piano 1 (Rhodes) | 4 | 0–3 | identical phase-shifted loop streams (DPSM core) |
| Bass | Electric Bass (finger) | 33 | 4 | trap 808-style sub following chord roots |
| Pad | Pad 1 (new age) | 88 | 5 | cinematic swell — sustained 7th chords |
| Drums | (GM percussion) | — | 9 | trap kit — half-time kick/clap, hi-hat rolls |

## Arrangement

- **Intro** — single unison loop (Loop1), soft pad drone on Dm7, sparse 8th
  hi-hats. No bass/kick → maximally bare.
- **Build** — Loop2 enters and drifts a full 8-step phase cycle (one 8th per
  bar); half-time kick (1 & 3) + 8th hats join; bass plays root half-notes;
  harmony opens i→VI→VII.
- **Rise** — Loop3 enters and drifts while Loop2 freezes at offset 4; 16th-note
  hi-hat rolls + trap clap backbeat on 3; bass adds the fifth on beat 3; pad
  level steps up. The phasing thickens into a wash.
- **Peak** — all four loops at maximal spread (0/2/4/6) = densest interference;
  driving 8th-note bass pulse, full 16th hats, snare roll into beat 4. Climax.
- **Resolve** — everything strips back to the single unison loop on Dm7 + one
  held bass tonic; the phase cloud collapses back to phase 0.

## Verification (real numbers)

```
zero-drift        : True  (7 tracks x 61440 ticks, all equal)
grid audit (16th=120 / 8th=240) per pitched voice:
  Loop1 (256 notes): off16=0  off8=0
  Loop2 (192 notes): off16=0  off8=0
  Loop3 (128 notes): off16=0  off8=0
  Loop4 ( 64 notes): off16=0  off8=0
  Bass  (100 notes): off16=0  off8=0
  Pad   (128 notes): off16=0  off8=0
  TOTAL off-grid   : 0
harmony audit per pitched voice:
  out-of-scale     : 0   (all notes in D natural minor)
  out-of-chord     : 0   (all notes chord tones of their bar)
voice-leading      : 0 violations (sustained pad voicings — min-motion)
phase-1 raw draft  : 256 events, off-grid by design (single deconstructive
                     loop, no harmony)
```

Audio (FluidR3_GM.sf2 → WAV 44.1 kHz, gain 0.6):

| Render | Duration | Peak (stereo) | RMS | Silence | <-40 dB windows |
|---|---|---|---|---|---|
| phase-2 mix | 62.21 s | 0.909 | −19.60 dB | 10.9% | 7 (all in reverb tail, windows 55–61) |
| phase-1 raw | 56.91 s | 0.307 | −30.97 dB | 13.2% | 2 (tail) |

Silence well under the 30% suspicion threshold; all quiet windows sit in the
post-final-note reverb tail — no mid-track dropout. The sparse Intro (single
loop + soft pad) is the only quiet section and is intentional.

## Files

| Path | Size |
|---|---|
| `MIDI/242-trap-phase.mid` | 11695 B (+ provenance.json) |
| `MIDI/242-trap-phase-phase1.mid` | 2339 B (+ provenance.json) |
| `Audio/242-trap-phase.wav` | 10973228 B |
| `Audio/242-trap-phase.ogg` | 422736 B |
| `Audio/242-trap-phase-phase1.wav` | 10039596 B |
| `Audio/242-trap-phase-phase1.ogg` | 429658 B |
| `Analysis/grid_visualization.txt` | — |
| `Analysis/summary.json` (chord path + phase schedule + contour) | — |
| `Analysis/audit.json` (mido readback) | — |
| `Analysis/render_stats.json` | — |

## Fixes applied during this run

1. **Render clipping** — `produce()` (SP-001) hardcodes Fluidsynth gain 1.2;
   the dense 7-voice trap downbeats summed past 0 dBFS (peak 1.0000, ~0.1%
   samples flat-topped). Re-rendered at gain 0.6 → stereo peak 0.909 with
   **zero** clipped samples, then Opus OGG. (`peaknorm` is unavailable in this
   ffmpeg 8.1.1 build, and is unnecessary at gain 0.6.)

## Provenance

Engine-only composition: `structures`, `workflows.unitmatrix_composer`,
`workflows.provenance`, `visualization.grid`, `rules.voice_leading`, and the
instrument registry (`RHODES`, `ELECTRIC_BASS`, `SYNTH_PAD`). No raw `mido`
authoring (mido used read-only for the independent audit). Both phase MIDIs
pass `validate()` (zero-drift) and carry `classification=ai-generated`
provenance sidecars.
