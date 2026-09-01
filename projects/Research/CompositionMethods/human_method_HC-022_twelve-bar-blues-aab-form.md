# HC-022 — Twelve-Bar Blues AAB Song Form & Blue-Note Melody Construction

**Tradition:** African-American Blues (Deep South USA, ~1860s → present; Delta, Piedmont, Chicago electric, jazz-blues). Rooted in work songs, field hollers, spirituals, and West African (Sahelian) call-and-response + microtonal melodic practice.

**Primary Elements:** STRUCTURE, HARMONY, PITCH, RHYTHM, TEXTURE

**Status:** ✅ Documented

---

## What it is (human-side craft)

The blues is the most widely recycled *compositional form* in American music — a
repeatable 12-bar harmonic grid + a lyric-melody template (AAB) + a pitch
vocabulary (blue notes) that a human songwriter *fills in* rather than invents
from scratch each time. The craft is not "generate a novel chord progression";
it is "state a lyric line, repeat it, answer it" over a fixed three-chord cycle,
and let the voice and instrument converse in call-and-response. Composers
reuse the same grid for a lifetime and differentiate themselves through lyric
specificity, phrasing, blue-note inflection, and the *turnaround* (the last two
bars that hook the progression back to the top).

## Craft process (how the human does it)

1. **Fix key + 12-bar grid.** Lock the I–IV–V chord cycle. Standard layout
   (with "quick change" optional): `I / I / I / I | IV / IV / I / I | V / IV / I / V(turnaround)`.
   All chords voiced as dominant 7ths (the "bluesy" color comes from the ♭7).
2. **Write the AAB lyric.** Line A = a concrete statement (often a two-line
   scene, 4 bars). Line A' = the same line repeated (bars 5–8, over IV — the
   harmonic lift *recontextualizes* the identical words, so no melodic change
   is needed to feel "new"). Line B = the response/comment/punchline (bars 9–12),
   resolving the emotional or narrative tension of A.
3. **Map line → phrase.** Each lyric line occupies ~2 bars of the 4-bar phrase.
   The *other* ~2 bars are left open for an instrumental/vocal **answer**
   (guitar fill, harp lick, piano comp, or a backing vocal). This is the
   call-and-response skeleton: human voice = call, instrument = response, in
   strict alternation.
4. **Compose the melody over the blues scale.** Draw from minor pentatonic +
   blue notes (♭3, ♭5, ♭7). The ♭3/♭7 are sung *microtonally bent* — a quarter-tone
   or so sharp/flat of the tempered pitch — so the "melody" is a band of
   inflection, not a fixed 12-ET sequence. Melisma, wavy intonation, and
   "worried" flattened notes are the signature.
5. **Set the turnaround.** Bars 11–12 (or 9–12 variant) move `V–IV–I` or a
   `ii–V–I` to point the ear back to bar 1. The turnaround is the composer's
   signature slot — where personal harmony substitutions (tritone subs, dim7,
   chromatic walk-downs) get inserted.
6. **Set the groove.** Shuffle/swing 8ths, walking bass (root→5th→♭7→6 per bar),
   backbeat on 2 & 4. The groove is invariant; it carries the trance-like
   repetition that makes the 12-bar cycle feel continuous rather than repetitive.
7. **Repeat-with-variation.** Each pass of the 12 bars is a *chorus*. New lyric
   verses, new melodic inflections, new instrumental fills ride the same grid.
   Improvisation (vocal or solo) is *structured variation over a frozen form*,
   never free invention.
8. **Stress-test by performing.** The form is validated by whether the
   call-and-response *feels* conversational and the turnaround *pulls* back to
   the top — a felt, not notated, criterion.

## Real practitioner examples

- **W.C. Handy** — codified the form in writing (*Memphis Blues* 1912, *St. Louis
  Blues* 1914): first to publish the AAB structure, treating it as a *communicable*
  grid ("to help musicians communicate chord changes").
- **Robert Johnson** — *Cross Road Blues*, *Sweet Home Chicago*: Delta slide-guitar
  call-and-response; voice line answered by bottleneck guitar in the open bars.
- **Bessie Smith / Ma Rainey** — classic "race records" vocal blues; AAB lyric
  with the singer's phrasing bending blue notes against a horn/banjo answer.
- **Willie Dixon** — *Hoochie Coochie Man*, *Wang Dang Doodle*, *Back Door Man*
  (for Muddy Waters / Howlin' Wolf): Chicago electric blues where the riff
  itself becomes the "call" and the band the "response".
- **Muddy Waters** — *I Can't Be Satisfied*: electric slide answer figures.
- **B.B. King** — string-bend/vibrato "vocal" guitar fills as the response voice.
- **John Lee Hooker** — one-chord boogie variant; the drone chord replaces the
  IV/V motion, reducing the grid to a single hypnotic tonic.
- **Jazz-blues extension** — Charlie Parker *Now's the Time* (bebop reharmonization
  over the 12-bar grid), Thelonious Monk, Miles Davis: same form, denser
  substitutions in the turnaround slot.

## UnitMatrix integration

**Voices (5):**

| Voice | Role | Content |
| :--- | :--- | :--- |
| V0 | Harmonic spine | Walking bass on I–IV–V roots (root–5–♭7–6 per bar), dominant-7th color, invariant across choruses |
| V1 | Call (lead vocal) | AAB lyric melody; minor-pentatonic + blue notes; ~2 bars per 4-bar phrase, microtonal ♭3/♭7 inflection |
| V2 | Response (instrumental) | Guitar/harp/piano fill in the 2-bar gap after each lyric line; echoes V1 contour; never overlaps V1's sung phrase |
| V3 | Rhythm/groove | Shuffle-swing 8ths, backbeat 2 & 4, invariant |
| V4 | Turnaround/harmony fill | Comping chords + the bars-11–12 turnaround figure (V–IV–I or ii–V–I), the substitution slot |

**Sections (each chorus = 3 four-bar phrases):**

| Section | Bars | Harmonic area | Lyric role |
| :--- | :--- | :--- | :--- |
| A1 | 1–4 | I | Statement (line A, call) |
| A2 | 5–8 | IV | Repeated statement (line A', same words, lifted harmony) |
| B | 9–12 | V → IV → I → V(turn) | Response/conclusion (line B), turnaround re-entry |

Sections are *cycled*: Intro (turnaround pickup) → Chorus 1 (verse 1) → Chorus 2
(verse 2) → Instrumental chorus (V2 solos) → Final chorus → Outro (turnaround tail).
Every chorus reuses the same 12-bar grid; only V1 lyric + V2 fills + V4 substitutions change.

**Rules to encode:**

- **Grid invariance:** the 12-bar I–IV–V sequence is frozen; no chorus alters it.
- **AAB lyric constraint:** line B (bars 9–12) differs from line A; line A repeats verbatim (or with tiny variation) in A2.
- **Call-and-response mask:** V1 active in bars 1–2 of each phrase; V2 active in bars 3–4 (fill). V1 and V2 never sound simultaneously (alternation gate).
- **Blue-note pitch set:** minor pentatonic {0,3,5,7,10} + ♭5(6); ♭3 and ♭7 permitted with microtonal bend (pitch-bend / quarter-tone offset), ♭5 as passing/neighbor only.
- **Dominant-7th color:** all structural chords are 7th chords (♭7 present).
- **Turnaround rule:** bars 11–12 must end on V (or ii–V–I) resolving to I on bar 1 of next chorus.
- **Groove invariance:** shuffle feel + backbeat constant; walking-bass pattern loops per bar.
- **Repeat-with-variation:** chorus N+1 = chorus N with new lyric (V1) and new fills (V2); structural voices (V0, V3) untouched.

## Quirks / pitfalls

- **Blue note ≠ fixed pitch.** Encoding ♭3/♭7 as exact 12-ET semitones flattens the
  blues into a pentatonic cliché. The human craft lives in the *microtonal bend* —
  Model as a pitch-bend envelope, not a scale-degree.
- **The "answer" is half the phrase.** A novice reading of AAB writes 4 bars of
  continuous melody. The human rule is: sing ~2 bars, *rest* ~2 bars, let an
  instrument speak. Sparse = conversational, not incomplete.
- **Turnaround is where composers sign their name.** The I–IV–V grid is anonymous
  (it predates all practitioners); the bars-11–12 substitution (dim7, tritone sub,
  chromatic walk-down) is the individual signature — treat it as a mutable slot.
- **One-chord variant (John Lee Hooker).** Not every blues fills IV/V; the "drone
  boogie" collapses the grid to a single tonic. The form survives because the AAB
  *lyric* structure, not the harmony, is the load-bearing wall.
- **Overlap with HC-006 (Shout Chorus) and HC-009 (Motivic).** Both descend from
  blues call-and-response; HC-006 is *arranging* the response across horn sections,
  HC-009 is *developing* a motive. This method is the *song-form* root: AAB lyric
  + blue-note melody + turnaround over I–IV–V.

## Sources

- Wikipedia: *Twelve-bar blues*, *Blues*, *Blues scale* (accessed 2026-08-31)
- Kubik, Gerhard — *Africa and the Blues* (Sahelian melodic/microtonal roots)
- Oliver, Paul — *The Story of the Blues* (savanna/string-playing lineage)
- Wald, Elijah — *Escaping the Delta: Robert Johnson and the Invention of the Blues*
- B.B. King / B.B. King & David Ritz — *Blues All Around Me* (call-and-response guitar practice)

**Next free ID:** HC-023
