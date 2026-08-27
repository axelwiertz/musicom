# HC-011 — Orchestration (Instrumentation & Tone-Colour Assignment)

**ID:** HC-011
**Tradition / Culture:** Western Classical — European art-music tradition (Baroque → present), with parallel craft in film scoring, musical theatre, and big band arranging
**Primary Elements:** TEXTURE, PITCH, STRUCTURE, RHYTHM
**Status:** ✅ Documented

---

## 1. What it is

**Orchestration** is the human craft of assigning musical material (melody, harmony, bass, rhythm) to specific instruments, registers, and dynamic levels to produce a desired tone colour. It is distinct from composition: the composer decides *what* notes happen; the orchestrator decides *who* plays them and *how they sound*. Historically composers orchestrated their own work (Bach, Mozart, Berlioz, Wagner, Ravel); in film, theatre, and commercial media, orchestration is a separate profession (the composer hands a piano/vocal score to an orchestrator who "fleshes it out" for the pit or studio ensemble).

The craft's core insight: **a C major chord is not one sound but many**. The same three notes (C–E–G) sound bright and brilliant on trumpets in the upper register at fortissimo, heavy and dark on cellos and double basses sul tasto doubled by bassoons and bass clarinet. Orchestration is the deliberate manipulation of this fact — the composer's "palette" (Berlioz's word) of timbres, blends, and contrasts.

The method is thoroughly codified in a pedagogical lineage: Berlioz's *Grand traité d'instrumentation et d'orchestration modernes* (1844), Rimsky-Korsakov's *Principles of Orchestration* (1912), Cecil Forsyth's *Orchestration* (1914), Walter Piston's *Orchestration* (1955), and Samuel Adler's *The Study of Orchestration* (1982) — the standard conservatory text today.

## 2. Craft procedure (how the human does it, step by step)

1. **Fix the ensemble & instrumentation formula.** Decide the orchestra's composition using the standard abbreviated convention: woodwinds (flute, oboe, clarinet, bassoon), brass (horn, trumpet, trombone, tuba), percussion, strings. Doublings noted with slashes (e.g. `3[1.2.3/pic]` = 3 flutes, 3rd doubling piccolo). The ensemble itself is a compositional choice that constrains every later decision.
2. **Start from the musical idea (melody, chord, or bass line).** The orchestrator begins from material already composed — a melody in the head, a piano score, a lead sheet. Orchestration is *applied to* musical content, not generated from nothing.
3. **Assign the melody (lead role).** Decide which instrument(s) carry the primary line. Default: first violins. Alternatives: trumpets (powerful, high), trombones (heavier, lower), cellos (warm), woodwinds (lyrical). The choice of lead instrument *is* the first expressive decision.
4. **Double and blend.** Add colour by doubling the melody: second violins an octave below, woodwinds in unison, glockenspiel/celesta for sparkle, piccolo + celesta for brightness. Doubling changes timbre without changing pitch content — the orchestrator's cheapest expressive lever.
5. **Voice the accompaniment (harmony layer).** Distribute chord tones across instruments and registers. Monophonic instruments (woodwinds, brass) each take one note; polyphonic instruments (strings, harp, piano) may take several. Decide spacing: close position in upper register = blended, wide spacing in bass = clear; close position in the low register = muddy (a classic error Berlioz deliberately exploited for effect).
6. **Set the bass & pedal foundation.** Assign the bass line to cellos/basses, bassoon, tuba, or timpani; decide whether a pedal point holds the tonal centre. The bass register must stay wide-spaced (≥ P5 between bass voices) to avoid muddiness.
7. **Contrast and colour sections.** Plan timbral variety across the form: alternate string passages with woodwind passages, solo vs. tutti, muted vs. open brass. Mozart's Symphony No. 39 (K543) is the textbook case — strings and woodwinds trade a phrase in dialogue, pizzicato vs. arco, one section at a time.
8. **Plan the tutti and climax.** Reserve the full ensemble (tutti) for structural peaks. Build toward it by adding sections incrementally; the climax is the loudest, highest, densest scoring — often the melody in octaves across all strings plus brass reinforcement.
9. **Check playability & balance.** Verify every part is within instrument range and idiomatic (no impossible double stops, no unplayable brass intervals); check that the melody is not buried by the accompaniment; check dynamics so the lead always projects. This is the orchestrator's quality gate.
10. **Notate the full score.** Produce the conductor's score with all parts aligned, then extract individual parts. In commercial practice the orchestrator works from a sketch (piano/vocal or MIDI mockup) and delivers a finished score.

## 3. Real practitioner examples

| Practitioner | Work | What it demonstrates |
| :--- | :--- | :--- |
| J.S. Bach | *Magnificat* BWV 243, "Et misericordia" (1723) | Muted strings doubled by flutes — subtle mellow blend; changing instrumental colour between groups as expressive device |
| W.A. Mozart | Symphony No. 39 K543, 1st mvt (1788) | String/woodwind dialogue, pizzicato vs. arco contrast, wide 4-octave spacing, viola harmonic colouring — the textbook of blended orchestration |
| Hector Berlioz | *Symphonie fantastique*, "March to the Scaffold" (1830); *Grand traité* (1844) | Timpani + double basses in thick chords against snarling muted brass; close-position low-register chords used *against* the rules for dramatic effect; timbre as free palette |
| Nikolai Rimsky-Korsakov | *Scheherazade* (1888); *Principles of Orchestration* (1912) | Codified the craft: melody distribution, doubling, tutti planning, balance; his own scores are the model of brilliant, colourful scoring |
| Maurice Ravel | Orchestration of Mussorgsky's *Pictures at an Exhibition* (1922); *Boléro* (1928) | Orchestration as a separate art — a piano work transformed into an orchestral showpiece; *Boléro* is a 15-minute study in timbre (same melody, ever-changing orchestration) |
| Richard Wagner | *Der Ring des Nibelungen* (1848–74) | Expanded brass family (Wagner tubas), leitmotif timbre-assignment — each motive has a characteristic orchestral colour |
| Samuel Adler | *The Study of Orchestration* (1982) | The modern pedagogical standard — instrument ranges, blends, scoring exercises |

## 4. UnitMatrix integration (Musicom engine)

### Voice assignment (4 voices)

| Voice | Role | Content |
| :--- | :--- | :--- |
| Voice 0 | Bass + pedal foundation | Bass line on cellos/basses/bassoon/tuba; wide spacing (≥ P5 from next voice); optional tonic pedal |
| Voice 1 | Lead melody | Primary line assigned to one timbre (strings default, or trumpet/cello/woodwind); may be doubled an octave below |
| Voice 2 | Harmony / accompaniment | Chord tones distributed across middle voices (violas, horns, clarinets); close or spread voicing per register rule |
| Voice 3 | Colour / doubling layer | Octave doubling, glockenspiel/celesta sparkle, muted-brass punctuation, timpani accents — timbre modifier, not pitch content |

### Section map (4 sections)

| Section | Name | Function |
| :--- | :--- | :--- |
| S0 | Exposition (strings) | Melody on first violins, accompaniment on lower strings; blended, mid register |
| S1 | Contrast (woodwind) | Same material re-scored for woodwinds; dialogue with strings; timbre change without pitch change |
| S2 | Development (mixed) | Rapid alternation of solo groups, muted brass, pizzicato; maximum timbral variety |
| S3 | Tutti climax | Full ensemble, melody in octaves across all strings + brass reinforcement, loudest/highest/densest scoring |

### Rules to encode

1. **Lead-timbre assignment** — Voice 1 instrument chosen from a timbre palette (strings/trumpet/cello/woodwind); the choice is a per-section parameter.
2. **Doubling rule** — Voice 3 may double Voice 1 at unison/octave (and add sparkle instruments) but never adds new pitch classes; doubling changes timbre only.
3. **Register-spacing rule** — close voicings allowed only above C4; bass voices (Voice 0) spaced ≥ P5 from the next voice above; close-position low-register chords forbidden except as deliberate effect.
4. **Monophonic-vs-polyphonic constraint** — woodwind/brass voices play one note at a time; string/harp/piano voices may hold multiple chord tones.
5. **Tutti reservation** — full ensemble (all 4 voices sounding) only at S3; sections build density incrementally S0→S3.
6. **Timbre-contrast alternation** — adjacent sections must differ in lead timbre (e.g. strings → woodwinds → mixed → tutti); no two consecutive sections with identical scoring.
7. **Playability filter** — every note within instrument range; brass intervals idiomatic; no impossible string double stops (validated per-instrument range table).
8. **Balance rule** — Voice 1 dynamic ≥ accompaniment dynamics at all times (lead always projects); melody never buried.
9. **Climax = max density + max register + max dynamic** — S3 is the monotonic peak of all three axes.

### Why it matters for Musicom

Orchestration is the **missing timbre layer** in the HC database: every prior entry specifies pitch/rhythm/harmony content but leaves *who plays it* unspecified. For the UnitMatrix engine this is the natural bridge between the matrix (Voices × Sections) and the MIDI instrument assignment (`MidiInstrument` per voice) — orchestration *is* the rule system that maps each voice to an instrument, register, and dynamic. The doubling rule is trivially encodable (Voice 3 = transform of Voice 1, no new pitch classes), the register-spacing rule is a hard constraint on voicing generators, and the tutti-reservation rule gives a deterministic section sequencer. It also fills the explicit rotation gap for **Classical** tradition with a craft that is fully codified in the pedagogical literature (Berlioz → Rimsky-Korsakov → Adler), making it one of the most directly implementable human methods in the database.
