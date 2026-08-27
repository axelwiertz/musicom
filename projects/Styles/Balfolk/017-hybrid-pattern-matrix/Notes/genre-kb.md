# Genre Pattern Knowledge Base

## Musicom definition

A genre is not a label. A genre is a stable bundle of patterns:

- rhythm DNA
- pitch DNA
- harmony DNA
- bass DNA
- timbre DNA
- form DNA
- production DNA

## Matrix definition

Important correction: `MusicMatrix` is reserved Musicom vocabulary.

In `axelwiertz/musicom`, the concrete class is `UnitMatrix`:

```text
/opt/data/repos/musicom/structures/matrix.py
```

Canonical meaning:

```text
Rows    = voices / pitch-space layers
Columns = measures or sections / time-space segments
Cells   = MusicUnit objects or measure-level musical material
```

The genre matrix fits inside this. It is a semantic label layer over the same voice-by-measure grid.

```text
MusicMatrix rows: Percussion | Bass | Harmony | Lead | Pad
Genre tags:       Rhythm DNA | Bass DNA | Harmony DNA | Melody DNA | Timbre DNA
Columns:          Bar 1      | Bar 2    | Bar 3       | ...
```

So the genre matrix is not a separate competing structure. It is how we annotate MusicMatrix cells for education and composition.

## Balfolk

- Function: dance body.
- Meter: 6/8 jig, 3/4 mazurka, 4/4 schottische.
- Rhythm DNA: jig `█░░█░░`; mazurka beat-2 lean; schottische dotted pointé.
- Pitch: Dorian, Aeolian, Mixolydian.
- Harmony: modal loops; i-VII-IV-i; I-bVII-IV-I.
- Melody: conjunct, singable, often within a 10th.
- Timbre: fiddle, accordion, guitar, drone.
- Form: AABB, repeated dance phrase.

## Jazz

- Function: harmonic motion + improvisation.
- Meter: 4/4 swing.
- Rhythm DNA: triplet swing, 2-and-4 backbeat.
- Pitch: chord tones, chromatic enclosures, approach tones.
- Harmony: ii-V-I, I-vi-ii-V, extended 7ths/9ths/13ths.
- Bass: walking quarter notes.
- Timbre: piano, bass, ride cymbal, sax/brass.
- Form: head-solos-head, 12-bar blues, AABA.

## Classical

- Function: architecture + development.
- Rhythm DNA: motor rhythm, sequence rhythm.
- Pitch: motive, sequence, inversion, augmentation.
- Harmony: I-IV-V-I, circle of fifths, cadences.
- Texture: counterpoint, voice leading.
- Form: antecedent/consequent, binary, ternary, rondo, sonata.

## Electronic / Techno

- Function: loop + timbral evolution.
- Rhythm DNA: four-on-floor `█░░░█░░░█░░░█░░░`.
- Pitch: short modal cells, bass ostinato.
- Harmony: static loops, pedal points.
- Timbre: synth, filter, sub, sidechain, riser.
- Form: 8/16/32-bar blocks, build/drop.

## Cinematic

- Function: narrative emotion.
- Rhythm DNA: ostinato, spiccato, low drum pulse.
- Pitch: modal color. Lydian=wonder, Phrygian=danger, Aeolian=sorrow.
- Harmony: pedal point, modal interchange, chromatic mediants.
- Timbre: strings, brass, choir, sub drone, hybrid synth.
- Form: atmosphere -> tension -> peak -> release.

## Hybrid principle

Keep one genre as base. Borrow one or two rows from another genre.

Examples:

- Balfolk rhythm + Jazz harmony = danceable modal jazz color.
- Classical motor rhythm + Techno kick = orchestral drive.
- Cinematic timbre + Folk jig = epic dance cue.
