# 027 // Delta Blues Shack
- **Genre**: Blues
- **Subgenre**: Delta Blues
- **BPM**: 72
- **Key**: A Pentatonic Minor / Blues Hexatonic
- **Form**: Intro (2 bars) → Verse 1 (12-bar) → Verse 2 (12-bar) → Guitar Solo (12-bar) → Verse 3 (12-bar) → Outro (2-bar)

---

## Pattern-First Architecture

This project is constructed strictly using a **Pattern-First** workflow. We start by extraction and refinement of classical Delta blues structures across distinct, acoustically safe registers.

### Track List & Acoustic Registrations

- **Resonator Guitar (Foreground Lead)**: Register > C4. Delivers expressive, vocal-like call and response melodic phrases, syncopations, and micro-interval sliding inflections.
- **Acoustic Slide (Midground Harmony)**: Register C3-C5. Spaced chord chunks executing the traditional A7-D7-E7 blues shuffles on the 5th and 6th degrees.
- **Mono Fingerstyle Thumb Bass (Subground Bass)**: Register < C3 (< 130Hz). Strictly monophonic rhythmic thumps acting on the primary beats.
- **Stomp Box and Claps (Background Rhythm)**: Channel 10. Simple acoustic foot stomps on beat 1/3, matching claps on beat 2/4, overlaid with swinging triplet subdivision hats.

---

## Composed Patterns

### Starting Pitch Patterns
Melodic motifs follow descending minor contours using scale degree intervals (interval steps derived from `[3, 2, 1, 1, 3, 2]` blues hexatonic scale):
- *A Minor Pentatonic*: `A C D E G` (scale steps 0, 3, 5, 7, 10)
- *Tritone 'Blue' tension note*: `Eb` (scale step 6) is introduced during calls to build tension and resolve to `D` or `E`.

### Starting Rhythm Patterns
- Formatted as a slow, swinging **12/8 triplet shuffle** pattern using metrical gravity:
  - Strong beats: █
  - Triplet subdivisions: ░
- **Rhythm Grid (█ / ░)**:
  - Beat pattern: `█░░█░░█░░█░░` (12 subdivisions per bar)

### Changed and Refined Developmental Operations
- **Fragmentation**: Played during the intense Guitar Solo. Melodic motifs are sliced into tight, high-energy 1-beat repeating triplet calls.
- **Liquidation**: Structural notes are systematically stripped of wide intervals, concluding the solo section with a steady, climbing step-wise turnaround to the final verse.

---

## Verifications & Production
- **Standard Layout**: This project holds complete `Audio`, `MIDI`, `Analysis`, `Notes`, `Scores`, and scripts under `src/` or `Scripts/`.
- **Channel 10 Percussion Safety**: Verified programmatically inside `generate_blues.py`. Standard General MIDI configuration is successfully routed and locked to track-channel 9.
- **Mastering & Headroom**: Headroom normalization pass performed via FluidSynth gain synthesis settings combined with `ffmpeg` gain-boosting, resulting in a professional and clear `-1.0dB` peak output.
