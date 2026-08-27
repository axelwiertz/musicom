# HC-007 — Lyric-Melody Prosody (Text Setting)

**Tradition / Culture:** Western popular song & musical theatre (Tin Pan Alley → Broadway → contemporary pop), USA/UK, ~1900–present. Cross-cultural analogue: any sung-text tradition where melody follows speech accent (e.g. Chinese tone-language opera, Arabic maqam vocal setting, French mélodie).

**Primary Elements:** PITCH, RHYTHM, STRUCTURE, TEXTURE (TEXTURE as register/tessitura support of emotional content).

**Status:** ✅ Documented

---

## Description

Lyric-melody prosody is the craft of matching a melody to the natural stress, rhythm, and emotional contour of spoken language so the words "come across as naturally as possible." The composer does NOT invent a tune and force words onto it (or vice versa); the two are co-authored so that every stressed syllable lands on a strong beat or high/long note, every unstressed syllable falls on a weak beat, musical pauses occur where a speaker would breathe, and the pitch contour mirrors the emotional arc of the line.

Two sub-schools:
1. **Speech-accent alignment (prosody proper):** syllable stress ↔ metrical accent; long notes ↔ important words; phrase breaks ↔ grammatical boundaries.
2. **Emotive prosody (Pattison's "support for what is being said"):** the *whole* song — key, tempo, range, rhyme scheme, line count, harmonic color — supports the meaning. Sad lyric → minor/dark harmony; rising question → rising melodic line; falling resolution → descending cadence.

The term comes from Greek *prosōidía* ("song sung to music"). In pedagogy (Pat Pattison, Berklee; Stephen Sondheim's practice) it is treated as a *constraint*: the text is the boss, and the melody is shaped around it.

---

## Craft Steps (how the human does it)

1. **Write/choose the lyric first** (or at least the stressed-syllable skeleton). Scan the text: mark every stressed syllable and every unstressed syllable, and the grammatical phrase boundaries (where a speaker pauses).

2. **Map stress → meter.** Place stressed syllables on strong beats (downbeats, or beats 1 & 3 in 4/4) and on longer/higher notes. Place unstressed syllables on weak beats (offbeats, pickups/anacrusis) and shorter/lower notes. Never put a long note on "a," "the," "of," "and," "-ing," "-ly."

3. **Map phrase → musical phrase.** Make musical pauses (rests, phrase endings, cadences) coincide with grammatical pauses (commas, periods, line breaks). A musical phrase should not cut a grammatical phrase in half.

4. **Map contour → meaning.** Rising question → rising melodic line; falling statement → descending line; excitement → higher register + wider leaps; intimacy → narrow range, stepwise, lower register. The melody's shape "says" the same thing the words say.

5. **Match emotive prosody at the song level.** Choose key/mode (minor for sad, major for bright), tempo, tessitura, and harmonic color to support the lyric's mood. Rhyme scheme and line count can themselves create prosody (e.g. short clipped lines for anger, long flowing lines for longing).

6. **Refine for singability.** Check the singer can actually execute it: no awkward vowel on a high sustained note (open vowels "ah/oh" sing better high than closed "ee/oo"), no tongue-twisting consonant clusters on fast melismas, breath available before long phrases.

7. **Stress-test by speaking.** Speak the lyric naturally; the melody should be a stylized exaggeration of that speech, never a contradiction of it. If the melody forces a wrong accent ("I LOVE you" instead of "I love YOU"), revise the rhythm or the word order.

---

## Practitioner Examples

- **Stephen Sondheim** (*Company*, *Sweeney Todd*, *Sunday in the Park with George*): the canonical modern master. His stated principle — "content dictates form" — means the lyric's meaning and natural speech rhythm generate the melody, not the reverse. In "The Ladies Who Lunch" (*Company*), the brittle, staccato, syllabic setting mirrors the character's clipped bitterness; in "Send in the Clowns" (*A Little Night Music*), the short phrases and rests land exactly where a rueful speaker would pause.
- **Pat Pattison** (Berklee College of Music): systematized prosody as a teachable method in *Writing Better Lyrics* and *The Essential Guide to Lyric Form and Structure*. His definition: prosody = "the appropriate relationship between elements, whatever they may be" — every element supports what is being said.
- **Cole Porter** (*Anything Goes*, *Night and Day*): master of matching witty, dense internal rhymes to syncopated melodies where the rhyme word always lands on the accented beat.
- **Oscar Hammerstein II** (*Oklahoma!*, *Carousel*): the "lyric-first" school — wrote the words, then Richard Rodgers set them with scrupulous stress alignment (e.g. the natural speech rhythm of "Oh, what a beautiful morning" is preserved note-for-note).
- **Leonard Cohen / Bob Dylan** (folk/rock): prosody via *speech-rhythm* — melodies that hug the contour of conversational delivery, prioritizing the words' natural accent over tunefulness.

---

## UnitMatrix Integration (Musicom)

**Voices:**
- **Voice 0 = Lyric stress grid (invariant spine).** Not an audible voice — a *constraint track* encoding the stressed/unstressed syllable pattern and grammatical phrase boundaries of the text. Acts like the partimento bass or the Ewe bell: the fixed reference every other voice must align to. In Musicom terms: a sparse unit track whose on-beat events mark stressed syllables, off-beat events mark unstressed, and rests mark phrase boundaries.
- **Voice 1 = Lead melody (vocal).** Generated so that note onsets, durations, and pitches obey the stress grid: stressed syllable → downbeat + longer/higher; unstressed → weak beat + shorter/lower. This is the primary melodic output.
- **Voice 2 = Harmony/pad.** Chords chosen by emotive prosody (minor for sad, major for bright), changing at grammatical phrase boundaries, not arbitrary grid points.
- **Voice 3 = Rhythm/percussion (optional).** Accents reinforce stressed syllables; fills occur at phrase breaks (where a speaker breathes).

**Sections:** Sections = grammatical stanza structure (Verse → Pre-Chorus → Chorus → Bridge → Outro). Each section's prosody profile differs: verse = narrow range, speech-like, stepwise (conversational); chorus = wide range, higher tessitura, longer notes on the hook/title words (emotive peak). Section boundaries = where the rhyme scheme and line count change.

**Rules (encode as constraints):**
1. **Stress-accent lock:** `onset(stressed_syllable) ∈ strong_beats`; `onset(unstressed_syllable) ∈ weak_beats`. Violation = prosody error.
2. **Duration weighting:** `duration(word) ∝ semantic_importance` — title/hook words get the longest notes; function words ("the," "and") get the shortest.
3. **Phrase-boundary alignment:** musical rest/cadence must occur at grammatical pause; no musical phrase may split a grammatical phrase.
4. **Contour-meaning mapping:** rising question → ascending pitch sequence; falling statement → descending; excitement → register jump up; intimacy → stepwise narrow range.
5. **Emotive harmony:** mode/key selection function of lyric sentiment (sad→minor, bright→major, tension→dominant/diminished).
6. **Singability filter:** open vowels on high sustained notes; no consonant clusters on fast melismas; breath gaps before long phrases.
7. **Tessitura arc:** verse tessitura < chorus tessitura (chorus = emotional + registral peak).

**Musicom method mapping:** This is a *rules-based* (deterministic) constraint method in the Musicom taxonomy — closest to **056 Species Counterpoint Constraint Composition** (both are traditional-craft constraint solvers) and **033 WFCGS** (both propagate hard constraints over a grid). The stress grid is a deterministic scaffold; melodic fill is constraint-satisfaction, not stochastic. It pairs naturally with **001 Skeleton-First** (stress grid = skeleton) and **022 MCWS** (quantize the resulting melody to scale without breaking stress alignment).

---

## Why it matters for Musicom

Prosody gives Musicom a *text-driven* constraint source it currently lacks: a way to generate melodies whose rhythm and contour are anchored to human speech, not to abstract probability distributions. The stress grid is a clean, deterministic scaffold (like the partimento bass or Ewe bell) that other stochastic methods (002 Markov, 053 Lévy Flight) could then elaborate within — producing "singable," word-shaped melodies instead of purely statistical ones. It also introduces *emotive* harmony selection (mode/tempo/tessitura driven by lyric sentiment) as a first-class rule.
