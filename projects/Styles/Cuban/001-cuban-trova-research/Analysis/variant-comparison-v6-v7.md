# Variant Comparison v6 vs v7

## v6
```
=== FILE ===
/opt/data/projects/Styles/Cuban/001-cuban-trova-research/MIDI/cuban_seed_v6.mid
type=1 tracks=3 tpb=480 length_sec=60.00 notes=338
tempos: [(1, 96.0)]
time_signatures: [(1, 4, 4)]
keys: []
programs: [(0, 0, 0, 24), (1, 0, 1, 73)]
markers: []

=== TRACKS ===
00 '': notes=50 range=A3-B4 avgVel=86.8 avgDurQ=7.59 msgs=196
01 'Harmonic Voice': notes=72 range=E3-E5 avgVel=56.0 avgDurQ=3.86 msgs=147
02 'Percussion': notes=216 range=C2-A#5 avgVel=55.5 avgDurQ=0.05 msgs=434

=== GLOBAL PITCH CLASSES ===
[('F#', 80), ('D', 74), ('C', 66), ('A', 29), ('E', 25), ('A#', 24), ('G', 16), ('B', 15), ('F', 9)]
outside_C_major=104/338 (30.8%)

=== SECTIONS ===
Whole file: bars 1-25 sec=60.0 notes=338 range=C2-A#5 chrom%=30.8 topPC=[('F#', 80), ('D', 74), ('C', 66), ('A', 29), ('E', 25)] topTracks=[('Percussion', 216), ('Harmonic Voice', 72), ('', 50)]

=== DENSITY BY 8-BAR WINDOW ===
bars 001-008: 118 notes
bars 009-016: 108 notes
bars 017-024: 112 notes

=== LARGE SIMULTANEOUS ATTACKS ===
count: 0

```

## v7
```
=== FILE ===
/opt/data/projects/Styles/Cuban/001-cuban-trova-research/MIDI/cuban_seed_v7.mid
type=1 tracks=3 tpb=480 length_sec=60.00 notes=384
tempos: [(1, 96.0)]
time_signatures: [(1, 4, 4)]
keys: []
programs: [(0, 0, 0, 24), (1, 0, 1, 73)]
markers: []

=== TRACKS ===
00 '': notes=96 range=A3-C5 avgVel=85.6 avgDurQ=1.00 msgs=196
01 'Harmonic Voice': notes=72 range=E3-E5 avgVel=56.0 avgDurQ=3.86 msgs=147
02 'Percussion': notes=216 range=C2-A#5 avgVel=55.5 avgDurQ=0.05 msgs=434

=== GLOBAL PITCH CLASSES ===
[('F#', 80), ('D', 74), ('C', 67), ('F', 35), ('A', 34), ('E', 25), ('A#', 24), ('G', 23), ('B', 17), ('C#', 5)]
outside_C_major=109/384 (28.4%)

=== SECTIONS ===
Whole file: bars 1-25 sec=60.0 notes=384 range=C2-A#5 chrom%=28.4 topPC=[('F#', 80), ('D', 74), ('C', 67), ('F', 35), ('A', 34)] topTracks=[('Percussion', 216), ('', 96), ('Harmonic Voice', 72)]

=== DENSITY BY 8-BAR WINDOW ===
bars 001-008: 124 notes
bars 009-016: 128 notes
bars 017-024: 132 notes

=== LARGE SIMULTANEOUS ATTACKS ===
count: 0

```

## Read
- v7 fixes melody duration pairing.
- v7 removes long held notes from pitch-stack mismatch.
- v7 keeps form and feel.

## Winner
- **v7** for final master.