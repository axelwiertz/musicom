# 012 — Country UnitMatrix

## Concept
Country-pop road song. Built UnitMatrix-first. Rows = musical layers. Columns = form sections.

## Project settings
- Genre: Country
- Subgenre: Country-pop road song
- Key: G major
- Tempo: 96 BPM
- Meter: 4/4
- Total bars: 48
- Form: Intro → Verse 1 → Chorus 1 → Verse 2 → Chorus 2 → Bridge → Final Chorus → Outro

## UnitMatrix
- Each cell stores a base subset pattern.
- Melody cells show scale + degrees.
- Bass cells show root-motion pattern.
- Rhythm cells show country-kit subset.
- Dashboard shows a mini piano roll per cell.

## Layers
- Lead Vocal
- Harmony Vox
- Acoustic Guitar
- Electric Guitar
- Bass
- Drums
- Fiddle
- Pedal Steel

## Files
- [MIDI](MIDI/v2_country_unitmatrix.mid)
- [MusicXML](Scores/v2_country_unitmatrix.musicxml)
- [Flat.io-safe MusicXML](Scores/v2_country_unitmatrix_flat.musicxml)
- [OGG](Audio/v2_country_unitmatrix.ogg)
- [WAV](Renders/v2_country_unitmatrix.wav)
- [Manifest](Analysis/v2_manifest.json)
- [Generator](Scripts/generate_v2.py)
- [Flat.io score](https://flat.io/score/6a29c0bcea370a200ff0388c)
- [Dashboard](index.html)

## Flat.io note
The full UnitMatrix export is kept locally. Flat.io uses the simplified import score for reliable notation upload.

## Iterative workflow
1. Define UnitMatrix first.
2. Fill every cell with a base subset pattern.
3. Render MIDI with explicit percussion on GM channel 10.
4. Verify MIDI before audio.
5. Export MusicXML.
6. Publish to Flat.io.
7. Update dashboard with bars, bases, and mini piano rolls.
