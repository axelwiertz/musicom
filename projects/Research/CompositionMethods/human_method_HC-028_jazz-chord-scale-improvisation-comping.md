# HC-028 — Jazz Chord-Scale Improvisation & Comping Craft (Bebop/Hard-Bop)

**Layer:** human → `concrete` (target when implemented) — human-craft knowledge; realized through the UnitMatrix into playable voices/events.

**Tradition / Culture:** African-American jazz — the bebop → hard-bop → post-bop lineage
(USA, ~1940s–present), standardized into conservatory pedagogy in the 1950s–70s
(chord-scale system, George Russell's *Lydian Chromatic Concept* 1953; David
Baker, Jerry Coker, Mark Levine *The Jazz Theory Book* 1995).

**Method ID:** HC-028

---

## 1. Description

How a working jazz horn/piano/guitar/bass player actually improvises a solo or
comps (accompanies) over a standard: not random notes per chord, but a layered
craft procedure. The player **hears the form** (head → changes → solos → head),
**internalizes the guide-tone lattice** (3rds & 7ths of each chord = the voice
that defines the harmony), maps each chord to a **chord-scale** (a pitch palette
reconciled against the surrounding key), plays **target-note lines** (loop a path
through guide tones and chord tones), ornaments with **chromatic approach /
enclosure / passing tones**, and keeps **time-feel** (swung 8ths, forward motion,
breath phrasing) constant even while the pitch content gets freer. Comping is the
single-voice inverse: build **rootless left-hand / guitar voicings**, voice-lead
smoothly (7→3, 3→7), and leave rhythmic space.

The craft is three coupled sub-skills a human masters separately and recombines:
**(a)** chord-scale mapping (which notes are consonant/target vs. passing/avoid),
**(b)** guide-tone voice-leading (which notes carry the harmony from chord to chord),
**(c)** melodic line construction (long target-note phrases with chromatic
decoration and swing feel).

## 2. Craft Steps (how the human does it, step by step)

1. **Learn the standard & the form.** Memorize the 32-bar form (AABA, rhythm
   changes) or 12-bar blues; know the changes cold; sing the melody ("play the
   head") so the tune is in the ear, not just the chart.
2. **Build the guide-tone lattice.** For the whole progression, write the 3rd and
   7th of every chord as a two-note line. Voice-lead: on a ii–V–I (Dm7–G7–Cmaj7),
   C→B (the 7 of Dm7 moves to 3 of G7), F→E (the 3 of Dm7 moves to 7 of G7), and
   F→E again resolving G7's 7 down to I's 3. This lattice is the "skeleton" the
   whole solo hangs on.
3. **Map each chord to a chord-scale.** Resolve the scale choice against the key:
   ii7 = dorian, V7 = mixolydian (or altered/whole-tone when resolving to minor),
   Imaj7 = ionian/lydian. Identify **avoid notes** (the 4th over a maj7 chord =
   "avoid" — a half-step clash with the 3rd below) and **guide/color tones**.
4. **Practice target-note lines.** Slow tempo: play only guide-tones (12–18 notes
   per chorus) resolving 7→3 across every change. Then add chord tones; then
   connect targets with scale runs. The rule: **land chord tones on strong beats,
   pass through the rest**.
5. **Add chromatic ornamentation.** Approach any target from above/below by
   half-step (chromatic approach), "enclose" a target by playing upper then lower
   neighbor first, insert passing tones between chord tones. Chromatic notes are
   decoration, resolution is the anchor.
6. **Develop motivic material.** Don't run scales endlessly — take a short phrase
   (2–6 notes) and develop it (sequence, displacement, rhythmic variation) so the
   solo tells a story (sparse → dense, low → high, motif → answer).
7. **Keep the swing/time-feel.** Even while the pitch gets abstract, keep the
   underlying eighth-note placement swung, keep breath phrasing (leave rests, play
   behind/ahead of the beat deliberately), keep the ride cymbal / skip beat
   constant.
8. **Comp.** (Parallel craft — when not soloing.) Build rootless 3/4-note voicings
   (3rd+7th+extensions, drop the root), voice-lead them (7→3 each change), and
   place them sparsely off-beat (Charleston / "and" of 2 / upbeat pushes), leaving
   space for the soloist.

## 3. Practitioner Examples

- **Charlie Parker** — "Koko" (1945), "Confirmation": lightning chromatic
  enclosure + bebop scale (chromatic passing tone between 5th and ♭7th) over rhythm
  changes; the archetypal chord-tone-targeted, chromatically-decorated 8th-note
  line. His Down/Up chromatic approach (approach target from semi-tone below then
  above) is a named pedagogy.
- **Bud Powell** — "Bouncing with Bud": bebop piano, left-hand rootless comping +
  right-hand single-note lines in the Parker mold.
- **Dizzy Gillespie** — "A Night in Tunisia" (bebop tune, altered dominant /
  II–V–I lattice exposed).
- **Miles Davis / Kind of Blue (1959)** — "So What" (modal, dorian): chord-scale
  thinking taken modal — one scale per 8 bars instead of changes.
- **John Coltrane** — "Giant Steps" (1959): the guide-tone/lattice approach taken
  to three-key major-3rd cycles; target tones land every 2 beats across rapid key
  changes; later "sheets of sound" = stacked chord-tone arpeggiation at speed.
- **Bill Evans** — rootless voicings + 7→3 voice-leading as the modern comping
  standard ("Waltz for Debby").
- **George Russell** — *The Lydian Chromatic Concept* (1953): systematized
  chord-scale mapping (scale from chord function, not the other way).
- **Barry Harris** — "6th-diminished scale" pedagogy = systematic passing-tone /
  chromatic decoration of chord tones, the bebop-scale formalization.
- **Mark Levine / Jerry Coker / David Baker** — codified the "chord-scale +
  guide-tone" method in conservatory teaching.

## 4. UnitMatrix Integration

### Voices
- **Voice 0 = harmonic spine** (bass/comping). Walking-bass roots or rootless
  comping voicings; invariant guide-tone skeleton. This is the *reference* the
  other voices target. `PITCH` anchor = guide-tone lattice per chord.
- **Voice 1 = solo line** (horn/piano right-hand). The improvised melody: target
  notes (chord tones / guide tones) on strong beats, scale/approach motion between.
- **Voice 2 = comping chordal layer** (piano/guitar). Rootless voicings voice-led
  7→3, short rhythmic stabs, off-beat placement.
- **Voice 3 = time/ride groove** (drums/ride cymbal + skip beat). Invariant swing
  feel; quarter-note ride + 2&4 backbeat = the clock everything else swings over.

### Sections
- **Head (A)** — melody stated, comping full, soloist rests.
- **Solos (B)** — soloist improvises over frozen changes; comping sparse & reactive;
  multiple chorus passes (each chorus = one full form loop, solo arc across choruses).
- **Fours/trading** — call-and-response with drums (4-bar exchanges).
- **Head out (A')** — melody restated, tagged, close.

### Rules (what would encode it)
- **Guide-tone invariance**: Voice 0 carries the 3rd/7th per chord; Voice 1 must
  target/land on a guide-tone or chord tone at each chord boundary (resolution
  anchor).
- **Chord-scale palette**: note ∈ chord-scale(chord, key); discriminate
  consonant/chord-tone (strong beat) vs. passing/approach (weak beat). Avoid-note
  half-step rule over maj7 (the 4th over maj7).
- **7→3 / 3→7 voice-leading** on ii–V–I cadences (guide tones move by step / common tone).
- **Strong-beat target**: chord tones land on downbeats/mid-strong beats; non-chord
  tones on off-beats; chromatic approaches resolve by half-step.
- **Swing feel**: 8th-note downbeat placement swung (≈ triplet 2:1); ride pattern
  invariant; backbeat 2&4.
- **Density/register arc** across choruses: sparse → dense, low → high, one motif →
  developed variants (monotonic solo-development arc).
- **Motivic development**: small cell (2–6 notes) sequenced/displaced/varied rather
  than diatonic run (recognizability constraint).
- **Comping space**: Voice 2 onsets off-beat/short, never colliding with Voice 1's
  phrase (space rule).

### Provenance
- Layer: `concrete` (target). Human-craft knowledge → realizes material via UnitMatrix.
- Primary elements: PITCH, HARMONY, RHYTHM, STRUCTURE, TEXTURE.
- Not algorithmic generation — NOT routed by SCALE selector as a generator; this is
  the *knowledge* of how jazz players assemble the material, available as rules for
  a future concrete-layer method.