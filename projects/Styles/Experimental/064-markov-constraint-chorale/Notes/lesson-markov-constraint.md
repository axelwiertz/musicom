# Lesson — Markov-Constraint Wavefront Sequencing (Method 022)

## What you are hearing

The soprano line of this chorale is NOT a random walk and NOT a composed
melody — it is a **constrained random walk**. Two constraints fight each other
and produce the musical character:

1. **Local (Markov) constraint:** the next pitch must be within 7 semitones of
   the current pitch. This creates the *stepwise, singable* contour — voices
   that can only leap small distances sound vocal, not mechanical.
2. **Global (wavefront) constraint:** every pitch must belong to the G-aeolian
   scale AND sit inside a glide band that slowly rises or falls across the
   section. The band is the "wavefront" sweeping through the section.

The generative method alone produces *scale-legal but harmony-blind* pitches.
That is why Phase 2 exists.

## Why the harmony layer matters

The raw Markov chain does not know about chords. Phase 2:

1. **Quantizes** each soprano pitch to the nearest tone of the current triad —
   the melody becomes consonant with the harmony underneath.
2. **Builds block harmony** — Alto, Tenor and Bass each take a triad tone, so
   every attack is a complete G-minor-family chord.
3. **Corrects voice leading** — inversion rotations are searched so no
   parallel fifths/octaves or hidden fifths slip through (classical
   strictness). Final count: **0 violations**.
4. **Validates the progression** — i-VII-III-VI is checked against the
   function map: tonic may leave anywhere, dominant (VII) resolves to a
   prolongation chord (interrupted cadence), prolongations move freely.

## Listening checklist

- [ ] Hear the stepwise soprano: mostly seconds, occasional thirds — the
      7-semitone Markov cap at work.
- [ ] Hear the density build: section 1 is sparse (55% of 16th slots),
      section 4 is dense (85%). Same material, more motion = tension ramp.
- [ ] Hear the band glide: sections 1 and 3 rise (open, bright), sections 2
      and 4 fall (settle, dark) — the wavefront is audible as register shape.
- [ ] Hear the interrupted cadence VII->III: the phrase *refuses* to land on
      tonic at bar 4, then finally resolves through the VI->i return.

## Exercise

Generate the same MCWS walk with `transition_max_interval = 9` and compare:
the melody gets more angular. Then set `SECTION_DENSITIES` all equal and
listen to what the band glides alone do to the phrasing. Which variable
changes character more — the local cap or the global density?
