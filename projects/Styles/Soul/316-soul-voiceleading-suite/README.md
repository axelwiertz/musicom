# 316-soul-voiceleading-suite

Soul composition, F natural minor, 96 BPM, 40 bars (10 sections).

Extension of `229-soul-voiceleading-rework` (Method 007 Voice-Leading Graph Search).
All 6 engine standards passed on source → extension path (no redesign).

## Listen

- `Audio/316-soul-voiceleading-suite-perfect.ogg` — grid-locked (compositional truth)
- `Audio/316-soul-voiceleading-suite-humanized.ogg` — style-derived humanization

## Edit

- `MIDI/316-soul-voiceleading-suite-perfect.mid`
- `MIDI/316-soul-voiceleading-suite-humanized.mid`
- `MIDI/316-soul-voiceleading-suite-phase1.mid` (raw two-phase draft)

## Form

Intro | Verse | PreChorus | Chorus | Verse2 | PreChorus2 | Chorus2 | Bridge | Chorus3 | Outro
(each 4 bars).

## Variation techniques

Inversion, augmentation, diminution, register shift, transposition, retrograde,
rising counterline, density curve.

## Structure

- `compose.py` — engine-only generator (UnitMatrixComposer + export_dual)
- `verify.py` — read-only mido audit
- `render_audio.py` — FluidSynth render + master + Opus encode
- `Analysis/` — grid visualization, summary, render report
- `REPORT.md` — full decisions + verification numbers
