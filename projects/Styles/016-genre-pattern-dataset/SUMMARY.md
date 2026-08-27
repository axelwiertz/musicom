# Genre-Pattern Dataset — Progress Summary
## Project 016 — Last Updated: 2026-06-23

### Existing Files (previously completed)
- `bossa_nova.json` — Bossa Nova (Classic)
- `flamenco.json` — Flamenco (Bulerías / Soleá)
- `jazz.json` — Jazz (Bebop / Modal)
- `balfolk.json` — Balfolk (Mazurka / Scottish / Jig)

### NEW Additions (this session)

| File | Genre | Subgenre | Key Features |
|------|-------|----------|-------------|
| `klezmer_freylekhs.json` | Klezmer | Freylekhs (Bulgar) | Freygish scale (Phrygian dominant), secunda afterbeat rhythm, oom-pah bass, krechts/dreydlekh ornamentation, 2/4 dance form, i-V7 harmonic progression |
| `bluegrass_scruggs.json` | Bluegrass | Scruggs-Style Banjo (Bluegrass Breakdown) | Scruggs forward/backward/Foggy Mountain rolls, 8th-note continuous roll patterns, G-run turnaround, mandolin chop on 2&4, two-beat bass, G Mixolydian/pentatonic scale, I-IV-V breakdown harmony, 13 structural rules |
| `ewa_agbadza.json` | West African Ewe Music | Agbadza (Gankogui Timeline, Polyrhythms) | 12/8 compound meter, gankogui 5-stroke bell timeline (█░░█░█░░█░█░), 5:4 cross-rhythm, 3:2 hemiola, 7-layer interlocking percussion matrix, Ewe anhemitonic pentatonic scale, call-and-response vocals, 4 dance sections (Bobo→Adzo→Vutsotsotsi→climax), 12-pulse unit grid with 7 instrument rows, 3 variations (Bobo/Vutsotsotsi/Gakpa) |

### Schema Compliance
All files follow the MusicMatrix schema v1.0:
- ✅ `patterns.pitch` — intervals, contour, modal degrees, characteristic motifs
- ✅ `patterns.rhythm` — onsets, steps, DNA string, metrical gravity, variants
- ✅ `patterns.timbre` — ADSR, vibrato, harmonic profile, ornamentation
- ✅ `musicmatrix_mapping` — rows, cols, unit_matrix grid with per-slot detail
- ✅ `meta` — origin, era, tempo, instrumentation, reference tracks
- ✅ `harmonic_progression` — primary chords, cadences
- ✅ `structural_rules` — genre-specific composition guidelines
- ✅ `unitmatrix_export` — format version, schema, generator compatibility

### Next Candidates
- Gamelan (Central Javanese — slendro/pelog, irama levels)
- Celtic (Irish jig/reel — double jig, slip jig, reel ornamentation)