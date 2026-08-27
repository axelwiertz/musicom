# 026 — Bossa Nova UnitMatrix

## Concept
Bossa Nova study built from a UnitMatrix-first workflow. Rows = Guitar, Bass, Percussion. Columns = Intro, A, B, A', Outro.

## Pattern
- **PitchPattern:** retrograde-inverted bossa motif, clamped to playable guitar register.
- **RhythmPattern:** syncopated bossa pulse with explicit percussion row.
- **UnitMatrix:** rows are tracks, columns are form sections, cells are separate Pattern objects.
- **Cell base subset:** each melodic cell shows its scale and/or chord base. Melody cells also show scale degrees.
- **Meter:** 4/4
- **Tempo:** 80 BPM
- **Form:** Intro (4 bars) -> A (12 bars) -> B (8 bars) -> A' (12 bars) -> Outro (4 bars)

## Instrumentation
- Nylon guitar
- Acoustic bass
- Bossa percussion: kick, side stick, hi-hat, conga, shaker

## Files
- [MIDI](MIDI/v1_bossa_nova_unitmatrix.mid)
- [MusicXML](Scores/v1_bossa_nova_unitmatrix.musicxml)
- [Flat.io score](https://flat.io/score/6a29be924f4787e16bad4026)
- [Audio](Audio/v1_bossa_nova_unitmatrix.ogg)
- [Renders](Renders/v1_bossa_nova_unitmatrix.wav)
- [Analysis](Analysis/v1_analysis.md)
- [Generator](Scripts/generate_v1.py)

## Workflow updates
- Every iteration now gets a mini piano roll per UnitMatrix cell in the dashboard.
- Every composition project now exports MusicXML and publishes to Flat.io when token available.

## Workflow correction
This project uses the corrected composer workflow:
1. build UnitMatrix
2. emit MIDI with explicit percussion channel 9
3. verify MIDI percussion events
4. render audio from the exact same MIDI path
5. promote into a numbered real project
