# Research Notes

## Research question
How do lyric-craft techniques control musical phrasing, and how can they be encoded into Musicom?

## Techniques reviewed
### Question / answer phrasing
- Question lines create expectation.
- Answer lines create closure.
- Best musical match: rising unresolved contour for question; descending or tonic closure for answer.
- Works at phrase level and section level.

### Tension / release
- Tension is not only harmonic dissonance.
- Tension also comes from delayed rhyme, delayed cadence, and delayed syntactic completion.
- Release happens when rhythm, harmony, and text resolve together.

### Call / response
- Call: initiating phrase, often shorter and more rhythmically active.
- Response: answering phrase, often longer or more stable.
- Good for duet writing, lead/background exchange, and verse/chorus antiphony.

### Enjambment
- Line runs past grammatical boundary.
- In music, do not cadence at line end.
- Keep harmony moving or suspend resolution across the break.

### Caesura
- Mid-line pause or stop.
- In music, use rest, held note, or instrumental gap.
- Should feel like a cut in breath or thought.

### Meter and stress
- Syllable count alone is weak.
- Strong beats should carry stressed syllables.
- Weak syllables can fill pickup notes, offbeats, or passing figures.
- Syncopation works when stress is displaced on purpose, not by accident.

### Internal rhyme
- Rhyme inside the line gives propulsion.
- Good place: mid-phrase, before the terminal cadence.
- Can be used as rhythmic glue for fast lyric delivery.

### Narrative arc
- Verse: setup, detail, low register, lower harmonic pressure.
- Pre-chorus: rising pressure, acceleration, harmonic lift.
- Chorus: title/hook, widest contour, highest release.
- Bridge: contrast, perspective shift, harmonic deviation.
- Final chorus: maximum payoff, often with expansion or variation.

## Musicom comparison
### Existing support
- Musicom already has pitch, rhythm, harmony, structure, matrix, and transformation primitives.
- Method 004 already covers basic prosodic coupling.
- Harmony functions HOME/LIFT/TENSE/TURN can support tension logic.
- UnitMatrix can support phrase layout.

### Missing or weak support
- Stress-aware lyric alignment.
- Syntax-aware phrase segmentation.
- Explicit question/answer resolution planning.
- Call/response role assignment.
- Enjambment and caesura as first-class timing events.
- Rhyme-density metrics.
- Narrative tension curve linked to register and harmony.

## Source titles used
- Songwriting & AI Music Generation
- Musicom README
- Musicom QUICK_REFERENCE
- Composition Methods Database (Elements Framework)
- Prosodic Narrative Coupling (Method 004)
- Session recall: prosody / songwriting / lyric-driven composition research

## Implementation ideas
1. Add a lyric annotation object with fields:
   - text
   - syllables
   - stress pattern
   - punctuation
   - syntactic role
   - rhyme label
2. Add phrase planner:
   - question -> unresolved
   - answer -> resolved
   - call -> initiate
   - response -> echo/contrast
3. Add metrics:
   - stress-beat match score
   - rhyme density
   - cadence closure score
   - tension curve score
4. Add render rules:
   - questions rise
   - answers fall
   - enjambment delays cadence
   - caesura inserts silence
   - bridges invert or widen contour
