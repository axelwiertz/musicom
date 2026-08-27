# HC-015 — Sacred Harp Shape-Note "Dispersed Harmony" Composition

**ID:** HC-015
**Category:** Human-side craft (traditional pedagogy → living practice)
**Tradition / Culture:** American Shape-Note / Sacred Harp singing — Protestant a cappella sacred choral music. Roots in New England "First New England School" singing masters (1770–1820), perpetuated and canonized in the American South (The Sacred Harp, 1844 → present). Anglo-American, not European classical.
**Primary Elements:** PITCH, HARMONY, TEXTURE, STRUCTURE (+ RHYTHM via stress-accent)
**Status:** ✅ Documented

---

## Description

Sacred Harp is a living body of **shape-note singing**: a cappella Protestant choral music where the singers sit in a hollow square (treble / alto / tenor / bass on four sides), there is no conductor and no audience, and the **melody ("air") sits in the TENOR voice — not the soprano**. The name comes from *The Sacred Harp* (1844), a tunebook compiled by B. F. White and E. J. King, but the compositional lineage goes back to the singing masters of the First New England School — William Billings (*The New England Psalm Singer*, 1770), Daniel Read, and their followers — who taught young people to sing correct sacred music in "singing schools."

The signature sound is **"dispersed harmony"**: the harmonic style de-emphasizes the interval of the third in favor of open fourths and fifths, voices are widely spaced and cross one another freely, parallel fifths and cross-relations are not "errors" but idiomatic texture, and melodies favor the **pentatonic or "gapped" (fewer-than-7-note) scale**. Singers read from **four-shape notation** — fa (triangle), sol (oval), la (rectangle), mi (diamond) — a movable "do" system where the shapes denote **scale degrees, not absolute pitch**. There is no instrument giving a starting pitch; a "keyer" intones the first notes and the group replies.

Three canonical tune types define the form grammar:
1. **Hymn tune** — mostly 4-bar phrases, strophic (sung through multiple verses).
2. **Fuguing tune** — a homophonic opening couplet, then a passage where each of the four parts enters in succession (fugue-like imitation), closing homophonically.
3. **Anthem** — non-metrical, scriptural text, through-composed, sung once.

This is a **human composition craft** (how a singing master actually writes a tunebook tune), embedded in an oral/pedagogical performance practice (sing the syllables first, then the words; downbeats accented, "full voice," strict time). It matters for Musicom because it is the rare human model where (a) the lead voice is in the **middle of the texture**, not the top, (b) harmony is **emergent from voice-leading in an open, sub-triadic interval language** rather than functional chord progressions, and (c) "wrong" counterpoint (parallel 5ths, cross-relations) is the *point*, not a defect — directly opposite to species-counterpoint and big-band constraints in the sibling DB.

---

## Craft Steps — how the human composer does it

1. **Choose the text.** Hymn tune/anthem text from Protestant psalm/hymn tradition (metered → strophic hymn; prose scripture → anthem). Text meter drives phrase length.
2. **Write the "air" in the tenor.** Compose the lead melody *for the tenor voice* (the human-authored spine). Typical raw material: pentatonic or gapped scale, strong degree-based contour readable from fa/sol/la/mi shapes.
3. **Harmonize the remaining three parts around the tenor** (not above it): treble sits on top, alto and bass weave below and through the tenor register. Voice-leading is *dispersed*: wide spacing, parts freely cross, open 4th/5th/octave sonorities preferred, thirds present but never structural.
4. **Let the harmony emerge, don't push function.** No I–IV–V syntax. Vertical sonorities fall out of the four polygons; perfect intervals and open voicings give the "hollow" edge. Parallel fifths/octaves and cross-relations are permitted and cultivated.
5. **Choose the tune type for the form:**
   - *Hymn tune*: chain 4-bar phrases into stanzas; repeat per verse.
   - *Fuguing tune*: write a homophonic opening couplet → then a fuging section with all four parts entering in staggered imitation → close homophonically.
   - *Anthem*: through-compose against the prose text, one pass only.
6. **Notate in shape notes** (four-shape system: triangle=fa, oval=sol, rectangle=la, diamond=mi). Shapes encode scale *degrees* (movable "do"), so a singer sight-reads relative function, not absolute pitch.
7. **Score the delivery, not just the pitches.** Write the stress-accent feel into the rhythm: downbeats accented, strict time, no phrase-end pauses — the "sung loud on the beat" pulse that defines the sound.

---

## Practitioner Examples

- **William Billings** — *The New England Psalm Singer* (1770), *The Continental Harmony* (1794); the archetypal singing-master composer of the First New England School. Fuguing tunes and "dispersed" open-fifths harmony define his idiom.
- **Daniel Read** — First New England School singing master; his tunes became part of the shape-note canon transcribed into four-shape notation.
- **B. F. White & E. J. King** — compilers/arrangers/composers of *The Sacred Harp* (1844), ~250+ songs; White organized the singing schools that kept the tradition alive in Georgia/the South.
- **Folk-layer tunes** — mid-19th-c. secular folk melodies harmonized in parts with open fifths and given sacred lyrics (the "primal simplicity" layer); heavy pentatonic emphasis.
- **Modern community singings** — Alabama Sacred Harp Singers (field recordings), UK/Germany/Ireland singings; the oral "raise the 6th in minor" and unwritten-repeat deviations documented in performance practice.

---

## UnitMatrix Integration (Musicom Engine)

### Voices (4-voice hollow square → `create_matrix(num_voices=4, ...)`)

| Voice | Role | Musicom encoding |
| :--- | :--- | :--- |
| **Voice 0** | **Tenor = "air" (lead melody)** — the human-authored spine; the ONE thing a singing master writes first | `add_voice("Tenor", program=MidiInstrument.CHOIR_AAHS, channel=0)` — carries the primary melodic content |
| **Voice 1** | **Treble** — soprano part floating above the tenor, degree-tracking the air at the 3rd/4th/5th above, octave-doubled by women in practice | `add_voice("Treble", ... channel=1)` — above-lead counter/parallel line |
| **Voice 2** | **Bass** — open-fifth/octave foundation, never triadic-functional, wide spacing below tenor | `add_voice("Bass", ... channel=2)` — foundation pedal/roots in open intervals |
| **Voice 3** | **Alto** — inner filler weaving through the tenor register, cross-relations idiomatic | `add_voice("Alto", ... channel=3)` — middle weaving voice |

### Sections (tune-type grammar → `create_matrix(num_sections=N, ...)`)

| Section | Meaning | Rule set |
| :--- | :--- | :--- |
| **S0 — Opening couplet** | Homophonic statement of the air + three harmonic parts (hymn tune verse / fuging-tune head) | air-in-tenor, dispersed voicing, pentatonic/gapped pitch set, stress-accent |
| **S1 — Fuging section** | Four parts enter in staggered imitation (offset 1–2 subdivisions, entry order tenor→…→treble) | imitative entry constraint, each entry = the air shifted to another degree; no dense homophony until all four in |
| **S2 — Homophonic close / stanza repeat** | Return to block chords, cadence on tonic degree (fa of the scale); strophic → repeat S0 | convergence rule, open-fifth cadence, downbeat stress |
| **S3 (anthem only) — text block** | Through-composed text passage, no repeat, free bar layout | non-metrical, sung once |

### Rules to encode (Musicom constraints)

- **Air-in-tenor**: Voice 0 = melodic lead; treble/bass/alto derive from Voice 0's degree contour (never introduce independent primary melodic material).
- **Dispersed harmony**: bass ≥ P5 below tenor (open spacing); prefer vertical intervals {P5, P4, octave}; thirds permitted but non-structural.
- **Sub-triadic language**: no functional chord-progression engine; vertical sonorities = emergent from 4-voice movement (contrast: HC-006 big band uses guide-tone 3rd/7th logic — this does not).
- **Gapped/pentatonic pitch set**: scale-degree collection per tune (pentatonic subset or gapped 6-note); "raise the 6th in minor" oral rule = optional degree mutation.
- **Parallel 5ths / cross-relations ALLOWED** (idiomatic, not an error) — this inverts species-counterpoint and big-band constraints elsewhere.
- **Shape-note degree mapping**: fa/sol/la/mi movable-do → scale degrees; pitch relative (key set by keyer, no absolute tonality enforced).
- **Stress-accent**: velocity accent on beats 1 (downbeat louder), strict time, no phrase-end rests.
- **Fuging-tune entry rule**: S1 = staggered imitative entries, offset 1–2 subdivisions, entry interval = air transposed to another scale degree.

### Why this matters for the engine
This is a **lead-in-the-middle, harmony-as-emergence** model. Musicom normally treats Voice 0 as a bass or top-line spine; Sacred Harp teaches the engine a mode where the *author* writes a middle voice and the surrounding voices are computed around it under an **open-interval, sub-triadic, parallel-tolerant** constraint grammar — the direct complement of the closed-voicing, parallel-5th-free rules in the big-band (HC-006) and counterpoint rows. It also gives the UnitMatrix a native **imitative "fuging section"** section type with staggered entry offsets.

---

## Provenance
- Source: Wikipedia — "Sacred Harp" (retrieved 2026-08-24); sections "The music and its notation," "Musical style," "Origins of the music."
- Cross-ref: Shape note (four-shape fa/sol/la/mi), First New England School (W. Billings, D. Read), B. F. White & E. J. King (The Sacred Harp, 1844).
- Distinct from (no overlap): HC-001 partimento (functional bass + schemata), HC-002 Gamelan, HC-003 Makam, HC-004 Raga-Tala, HC-005 Ewe, HC-006 big band, HC-007 lyric prosody, HC-008 minimalism, HC-009 motivic development, HC-010 fanfare, HC-011 orchestration, HC-012 flamenco, HC-013 Georgian polyphony, HC-014 Pygmy hocket.