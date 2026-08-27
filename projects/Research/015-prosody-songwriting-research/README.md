# 015 Prosody / Songwriting Research

## Goal
Find lyric-craft techniques that improve **lyric-driven composition** and convert them into Musicom rules for **rhythm, melody contour, harmony tension, and phrase structure**.

## Source base
- **Songwriting & AI Music Generation** skill: meter, rhyme, internal rhyme, enjambment, caesura, prosody, Suno prompt tags.
- **Musicom README / QUICK_REFERENCE**: current pitch, rhythm, harmony, structure, and transformation primitives.
- **Composition Methods Database**: Methods 001-004, especially **004 Prosodic Narrative Coupling**.
- **Prosodic Narrative Coupling** reference: stress -> velocity, question -> rising contour, assertion -> tonic return.
- Recent session recall on lyric-driven composition and prosody research.

## Key findings
1. **Question/answer phrasing** is the best lyric-to-music driver. Question lines want unfinished cadence, upward contour, open harmony. Answer lines want closure, downward contour, tonic or stable chord.
2. **Call/response** works best as a two-track or two-phrase system: call = shorter, tense, higher activity; response = longer, lower energy, more resolved.
3. **Enjambment** should delay musical closure. Keep harmony or phrase unresolved across the line break.
4. **Caesura** should create a real musical gap. Use rest, sustain, or percussion-only beat.
5. **Meter and stress** matter more than raw syllable count. Strong syllables should land on strong beats or accented syncopation.
6. **Internal rhyme** raises propulsion. Put it on mid-phrase positions, not only line endings.
7. **Narrative arc** needs macro tension curve: setup -> pressure -> break -> release -> afterimage.

## Musicom translation rules
### Rhythm
- Align stressed syllables with metrical accents.
- Use short note values for fast internal rhyme, longer values for punch lines or cadences.
- Put enjambment across barline or phrase boundary.
- Use caesura as a silence token: rest, sustain, or fill drop.

### Melody contour
- Question: rising final syllable, unresolved upper neighbor, or repeated note with lift.
- Answer: falling resolution, tonic landing, or stepwise descent.
- Call: narrower range, more speech-like contour.
- Response: wider interval or contrasting contour.

### Harmony
- Question / tension: dominant, pre-dominant, modal mixture, non-chord tones, suspended sonority.
- Answer / release: tonic, subdominant-to-tonic, resolved suspension.
- Enjambment: delay cadence by one harmonic unit.
- Caesura: harmonic hold or no-chord gap.

### Phrase structure
- Phrase shapes should match text syntax, not only bars.
- Question phrase ends open.
- Answer phrase ends closed.
- Bridge is narrative turn: new perspective, harmonic shift, contour inversion.

## Gaps in current Musicom
- No explicit **prosody parser** for stress, punctuation, enjambment, caesura.
- No **question/answer state machine** for phrase generation.
- No **call/response allocator** across voices or sections.
- No explicit **internal rhyme detector** or rhyme-density target.
- No **narrative-arc curve** tied to harmony or register.
- No lyric-alignment layer that maps syllables to ticks with stress weighting.

## Practical implementation checklist
- [ ] Add lyric parser: syllables, stress, punctuation, line breaks.
- [ ] Add syntax tags: question, answer, enjambment, caesura, call, response.
- [ ] Map stress to beat weight and velocity accent.
- [ ] Map question phrases to unresolved cadences.
- [ ] Map answer phrases to tonic resolution.
- [ ] Add internal rhyme density scoring per phrase.
- [ ] Add phrase-arc controller: tension ramp, release point, afterphrase decay.
- [ ] Extend UnitMatrix or phrase objects with lyric slots.
- [ ] Add validation tests for prosodic alignment.

## Output recommendation
Use this framework for lyric-first compositions and Suno prompts. Build from **syntax -> stress -> contour -> harmony -> form**.
