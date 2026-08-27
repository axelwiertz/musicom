# 026 Bossa Nova UnitMatrix Analysis

## UnitMatrix
- Rows: Guitar, Bass, Percussion
- Columns: Intro, A, B, A', Outro
- Cell logic: each cell references a PitchPattern and RhythmPattern

## Rhythm Pattern
- Bossa syncopation
- Percussion row explicit on GM channel 10
- Kick, side stick, hi-hat, conga, shaker

## Verification
- MIDI file generated first
- Percussion events verified by parser
- OGG rendered from same MIDI path
