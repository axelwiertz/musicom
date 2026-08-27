# HC-016 — Drumband / Marching Percussion & Hornline Arrangement (Field Band Showcraft)

**ID:** HC-016
**Tradition / Culture:** Western marching arts — American drum corps (DCI), university/school marching bands, WGI indoor percussion; rooted in European military field music (fife & drum) and the 19th-c. American band movement
**Primary Elements:** RHYTHM, TEXTURE, STRUCTURE, PITCH, HARMONY
**Status:** ✅ Documented

---

## 1. What it is

The marching-arts arrangement is the craft of writing a complete field show — battery percussion (snare, tenor, bass, cymbal lines), front-ensemble "pit" (marimbas, vibes, timpani, aux), and hornline (brass) — around a drill (visual staging) concept. It is the most **rhythm- and texture-forward** composition tradition in the Western canon: the battery percussion *is* the composition's spine, and every phrase length is dictated by the drill count structure.

Unlike concert arranging (HC-011), where the arranger starts from a melody, the drum-corps arranger starts from a **percussion framework + a drill count sheet**, then layers the horns on top to support the visual program. Melody is the last thing added, not the first.

## 2. Craft procedure (how the human does it, step by step)

1. **Fix the show concept & instrumentation.** Decide show length (DCI 8–12 min; high-school ~7 min), battery size (snare 8–9, tenor 4–5, bass 4–5, cymbal 4–6), pit (4 marimbas, 2–3 vibes, 1 xylophone/glock, timpani, synth), and hornline (trumpets, mellophones, baritones, tubas). Choose source music or compose original.
2. **Lay the battery spine first.** Write the groove / rudiment grid for the snare line — the invariant rhythmic skeleton. Every measure is built from the rudiment vocabulary (paradiddles, flams, drags, diddles, rolls, "puh-duh-duh"). Tenors play melodic patterns across 5–6 drums; basses play splits (unison vs. split 16th runs).
3. **Write correct sticking.** Snare/tenor parts must be physically playable at tempo: the arranger writes sticking (R L R L; paradiddle RLRR LRLL) that alternates hands naturally — no double same-hand stroke at high tempo. "Check the sticks" is the arranger's own constraint gate.
4. **Build bass drum splits.** The bass line (4–5 players) plays melodic contour by splitting successive 16ths across players — down-the-line runs, unison impacts. "Pitch" = which drum, not concert pitch.
5. **Layer the pit.** Marimbas/vibes play chord pads + arpeggios + mallet scale runs; timpani = impacts + rolls at hit points; aux = tambourine/splash colour.
6. **Layer the hornline.** Trumpets on melody (bright, projects outdoors), mellophones on harmony (French-horn range, fill 3rds/5ths), baritones (trombone range, counterline), tubas on bass (root reinforcement). Outdoor voicing = open spacing, melody octave-doubled.
7. **Mark impact points (hits).** Accent points where battery + pit + horns + drill all land together — the structural anchors of the show, the "punctuation" of the arrangement.
8. **Coordinate with the drill.** Phrase lengths must divide evenly into drill sets (8/16/32 counts). Music is written to the count sheet — arranger and drill writer share the same phrase map. Tempo = marching range (120–200 bpm).
9. **Build the show arc.** Opener (statement, loud/fast) → Ballad/Production (slow, exposed, emotional, pit+horns only) → Percussion Feature (battery alone, virtuosic) → Closer (reprise, fastest/loudest, full ensemble).
10. **Balance for outdoor projection.** Lows carry, highs need doubling: arranger octave-doubles the melody, keeps low brass spaced, checks pit-vs-horn balance, and tunes battery for clarity at tempo.

## 3. Real practitioner examples

| Practitioner | Work | What it demonstrates |
| :--- | :--- | :--- |
| Wayne Downey | Blue Devils (DCI, 1970s–2010s) | Championship hornline voicing; the dense, bright "Downey sound" |
| Frank Sullivan | Santa Clara Vanguard snare book | Rudiment-based battery writing; cleanliness at 200+ bpm |
| Jay Bocook | Cadets, Bluecoats, Ohio State University Marching Band | Full-field arranging craft; balancing hornline + battery + pit |
| Dennis DeLucia | Bridgemen (1970s) | Early battery-as-melody innovation; split bass runs |
| Scott Johnson | Blue Devils percussion (2000s–present) | Modern pit/battery integration; mallet runs, electronic texture |
| Jim Prime / Chuck Naffier | Cadets, Cavaliers (drill design) | Music–drill count coordination; phrase = drill set |
| Jim Wunderlich | Crossmen, Glassmen (pit) | Front-ensemble arrangement craft |

## 4. UnitMatrix integration (Musicom engine)

### Voice assignment (5 voices)

| Voice | Role | Content |
| :--- | :--- | :--- |
| Voice 0 | Bass drum line | Split 16th runs + unison impacts; low rhythmic anchor; invariant groove |
| Voice 1 | Snare line | Rudiment grid (paradiddles/flams/rolls); the rhythmic spine — never stops |
| Voice 2 | Tenor/quads | Melodic battery patterns (5–6 drums), cross-rhythms against snare |
| Voice 3 | Pit / front ensemble | Marimbas/vibes chord pads + arpeggios + mallet runs; timpani impacts; harmonic + texture layer |
| Voice 4 | Hornline | Trumpets melody + mellophones/baritones harmony + tubas bass; outdoor open voicing |

### Section map (4 sections)

| Section | Name | Function |
| :--- | :--- | :--- |
| S0 | Opener | Full ensemble statement, loud/fast, dense hit points |
| S1 | Ballad / Production | Slow, exposed, pit + horns only, battery tacet (or minimal) |
| S2 | Percussion Feature | Battery alone, virtuosic rudiment showcase |
| S3 | Closer | Reprise, fastest/loudest, full ensemble + final impact |

### Rules to encode

1. **Battery-spine invariance** — Voice 0+1+2 play continuously (except ballad tacet); the groove never stops.
2. **Rudiment vocabulary constraint** — snare/tenor content restricted to the valid rudiment set + alternate-hand sticking.
3. **Bass-split melodic contour** — Voice 0 runs move across players; unison at impact points.
4. **Impact convergence** — at hit points all sounding voices accent together (downbeat alignment).
5. **Outdoor voicing** — hornline open spacing, melody octave-doubled, low brass spaced ≥ P5.
6. **Ballad tacet** — battery rests during S1; pit + horns carry.
7. **Show-arc density** — dynamic/density increases S0→S3; percussion feature = maximum battery complexity.
8. **Count divisibility** — phrase lengths = multiples of the drill set (8/16/32 counts).
9. **Tempo band** — 120–200 bpm (marching range).

### Why it matters for Musicom

Drumband is the strongest **rhythm-first** human craft in the database — the inverse of melody-first concert writing (HC-011). It maps cleanly onto the UnitMatrix because the battery (Voice 0–2) is a perfect invariant rhythmic spine, and the pit (Voice 3) is a natural **continuous-fill layer** that prevents the "staccato-only" texture problem the engine flagged for sparse rhythmic methods (011/032). It fills an explicitly-requested rotation gap (Drumband) and a genre gap: no prior HC entry covers field-band / percussion-ensemble writing.
