# Report — HC-022: Twelve-Bar Blues AAB Song Form & Blue-Note Melody Construction

**Date:** 2026-08-31 (nightly `daily-human-composition-research` job)
**Method ID:** HC-022
**Next free ID:** HC-023
**Detail file:** `human_method_HC-022_twelve-bar-blues-aab-form.md`
**DB:** `human_methods_db.md` (row appended)

---

## 1. Method name + tradition

**Twelve-Bar Blues AAB Song Form & Blue-Note Melody Construction** —
African-American Blues (Deep South USA, ~1860s → present; Delta, Piedmont,
Chicago electric, jazz-blues). Rooted in work songs, field hollers, spirituals,
and West-African Sahelian call-and-response + microtonal melodic practice
(Kubik, Oliver, Diouf, Wald).

## 2. Why this method (rotation)

Previous nightly methods covered Classical (001, 009, 011, 021), Gamelan (002),
Ottoman (003), Indian (004), Ewe (005), Jazz big-band (006), pop prosody (007),
Minimalism (008), Fanfare (010), Flamenco (012), Georgian (013), Pygmy (014),
Shape-note (015), Drumband (016), Sanjo (017), Cuban son (018), Bulgarian (019),
EDM (020). This run rotates back to **American vernacular song-form** — the
12-bar blues, the single most influential *compositional grid* in 20th-century
popular music and the seed of jazz, R&B, and rock. Genre-diverse, no Balfolk,
no repeat of a prior tradition.

## 3. Craft procedure (how the human does it — the workflow)

1. **Fix key + 12-bar grid.** Lock I–IV–V cycle, all chords voiced as dominant
   7ths. Standard: `I I I I | IV IV I I | V IV I V(turnaround)`, with optional
   "quick change" (IV in bar 2) and "shuffle blues" (V–IV–I–I in last 4).
2. **Write the AAB lyric.** Line A = 4-bar concrete statement (a scene/woe).
   Line A' = same line repeated verbatim over the IV (the harmonic lift
   *recontextualizes* identical words — no melodic change needed to feel new).
   Line B = the response/conclusion/punchline over bars 9–12.
3. **Map line → phrase.** Each lyric line ≈ 2 bars of a 4-bar phrase; the other
   ~2 bars are *left open* for an instrumental answer (guitar fill, harp lick,
   comp). Human voice = call, instrument = response, strict alternation.
4. **Compose melody over the blues scale.** Minor pentatonic {0,3,5,7,10} +
   blue notes ♭3/♭5/♭7. ♭3 and ♭7 sung *microtonally bent* (quarter-tone-ish
   sharp/flat of tempered pitch) → the melody is a band of inflection, not a
   fixed 12-ET sequence. Melisma + wavy intonation are the signature.
5. **Set the turnaround.** Bars 11–12 = V–IV–I or ii–V–I, pointing back to bar 1.
   This is the composer's *signature slot* — tritone subs, dim7, chromatic
   walk-downs get inserted here.
6. **Set the groove.** Shuffle/swing 8ths, walking bass (root–5–♭7–6 per bar),
   backbeat on 2 & 4. Invariant; it carries the trance-like repetition.
7. **Repeat-with-variation.** Each 12-bar pass = a *chorus*. New lyric verse,
   new inflections, new fills ride the same frozen grid. Improvisation =
   structured variation over frozen form, never free invention.
8. **Stress-test by performing.** Validated by whether the call-and-response
   feels conversational and the turnaround *pulls* — a felt, not notated, test.

## 4. Practitioner examples

- **W.C. Handy** — *Memphis Blues* (1912), *St. Louis Blues* (1914): first to
  publish the AAB structure, treating it as a communicable grid.
- **Robert Johnson** — *Cross Road Blues*, *Sweet Home Chicago*: Delta
  slide-guitar call-and-response (voice answered by bottleneck guitar in the
  open bars).
- **Bessie Smith / Ma Rainey** — "race records" vocal blues; AAB lyric with
  blue-note bends against horn/banjo answers.
- **Willie Dixon** — *Hoochie Coochie Man*, *Wang Dang Doodle*, *Back Door Man*
  (for Muddy Waters / Howlin' Wolf): Chicago electric blues where the riff is
  the "call" and the band the "response".
- **Muddy Waters** — *I Can't Be Satisfied*; electric slide answer figures.
- **B.B. King** — string-bend/vibrato "vocal" guitar fills as the response voice.
- **John Lee Hooker** — one-chord drone boogie; collapses IV/V to a single tonic.
- **Charlie Parker** — *Now's the Time*: bebop reharmonization over the grid.

## 5. UnitMatrix mapping (Musical Elements Framework)

**Voices (5):**

| Voice | Role | Content |
| :--- | :--- | :--- |
| V0 | Harmonic spine | Walking bass on I–IV–V roots (root–5–♭7–6 per bar), dominant-7th color, invariant |
| V1 | Call (lead vocal) | AAB lyric melody; minor-pentatonic + blue notes; ~2 bars per 4-bar phrase; microtonal ♭3/♭7 |
| V2 | Response (instrumental) | Guitar/harp/piano fill in the 2-bar gap; echoes V1 contour; never overlaps V1's sung phrase |
| V3 | Rhythm/groove | Shuffle-swing 8ths, backbeat 2 & 4, invariant |
| V4 | Turnaround/harmony fill | Comping chords + bars-11–12 turnaround figure (V–IV–I or ii–V–I), substitution slot |

**Sections (each chorus = 3 four-bar phrases):**

| Section | Bars | Harmonic area | Lyric role |
| :--- | :--- | :--- | :--- |
| A1 | 1–4 | I | Statement (line A, call) |
| A2 | 5–8 | IV | Repeated statement (line A', same words, lifted harmony) |
| B | 9–12 | V → IV → I → V(turn) | Response/conclusion (line B), turnaround re-entry |

Macro-form cycles: Intro (turnaround pickup) → Chorus 1 (verse 1) → Chorus 2
(verse 2) → Instrumental chorus (V2 solos) → Final chorus → Outro (turnaround
tail). Every chorus reuses the same grid; only V1 lyric + V2 fills + V4
substitutions change.

**Rules to encode:**

- **Grid invariance** — 12-bar I–IV–V frozen; no chorus alters it.
- **AAB lyric constraint** — line B differs from line A; line A repeats (verbatim or micro-variation) in A2.
- **Call-and-response mask** — V1 active bars 1–2 of phrase, V2 active bars 3–4; V1/V2 never simultaneous.
- **Blue-note pitch set** — {0,3,5,7,10} + ♭5(6); ♭3/♭7 carry pitch-bend (microtonal); ♭5 passing/neighbor only.
- **Dominant-7th color** — all structural chords include ♭7.
- **Turnaround rule** — bars 11–12 end on V (or ii–V–I) resolving to I on next bar 1.
- **Groove invariance** — shuffle + backbeat constant; walking-bass loops per bar.
- **Repeat-with-variation** — structural voices (V0, V3) frozen; V1/V2/V4 mutate per chorus.

## 6. Table row appended (verbatim)

```
| HC-022 | Twelve-Bar Blues AAB Song Form & Blue-Note Melody Construction | African-American Blues (Deep South USA, ~1860s–present; Delta / Piedmont / Chicago electric / jazz-blues) — rooted in work songs, field hollers, spirituals, West-African Sahelian call-and-response + microtonal melody | STRUCTURE, HARMONY, PITCH, RHYTHM, TEXTURE | Fix key + 12-bar I–IV–V grid (dominant 7ths) → write AAB lyric (line A = 4-bar statement, line A' = same line repeated over IV, line B = response/conclusion) → map line to phrase (sing ~2 bars, leave ~2 bars open for instrumental answer = call-and-response) → compose melody from minor-pentatonic + blue notes (♭3/♭5/♭7, ♭3&♭7 sung microtonally bent) → set turnaround (bars 11–12 V–IV–I or ii–V–I = composer's substitution slot) → set groove (shuffle 8ths + walking bass + backbeat 2&4, invariant) → repeat-with-variation (each 12-bar pass = a chorus; new lyric + new fills over frozen grid) → stress-test by performing (call-and-response feels conversational, turnaround pulls to bar 1) | Voice 0 = walking-bass harmonic spine (I–IV–V roots, root–5–♭7–6 per bar, dominant-7th color, invariant). Voice 1 = lead vocal call (AAB lyric melody, ~2 bars per 4-bar phrase, blue-note inflections). Voice 2 = instrumental response (guitar/harp/piano fill in the open 2 bars, echoes V1 contour, never overlaps V1's sung phrase). Voice 3 = rhythm/groove (shuffle-swing, backbeat 2&4, invariant). Voice 4 = turnaround/harmony fill (comping + bars-11–12 turnaround, the substitution slot). Sections = 3 four-bar phrases per chorus (A1=I bars 1–4 statement, A2=IV bars 5–8 repeated statement, B=V→IV→I→V-turn bars 9–12 response), cycled: Intro→Chorus(verse)→Instrumental chorus→Final chorus→Outro. Rules: grid invariance, AAB lyric constraint, call-and-response alternation mask (V1/V2 never simultaneous), blue-note pitch set {0,3,5,7,10}+♭5 with microtonal bend on ♭3/♭7, dominant-7th color, turnaround resolution to I on next bar 1, groove invariance, repeat-with-variation (structural voices frozen, V1/V2/V4 mutate) | W.C. Handy (Memphis Blues 1912, St. Louis Blues 1914 — first to publish AAB), Robert Johnson (Cross Road Blues, Sweet Home Chicago — slide-guitar answer), Bessie Smith & Ma Rainey (race-record vocal blues), Willie Dixon (Hoochie Coochie Man, Wang Dang Doodle — Chicago electric riff-call), Muddy Waters (I Can't Be Satisfied), B.B. King (string-bend vocal guitar response), John Lee Hooker (one-chord drone boogie), Charlie Parker (Now's the Time — bebop reharmonization) | ✅ Documented |
```

## 7. Verification

- `grep -c 'HC-022' human_methods_db.md` → **1** ✅
- `grep -c 'HC-022' human_method_HC-022_twelve-bar-blues-aab-form.md` → **1** ✅
- Table row present and aligned (single line, pipe-delimited, 8 columns). ✅
- `human_methods_db.md` left untouched apart from the appended row. ✅
- `methods_db.md` (algorithmic, owned by another job) **not touched**. ✅
- Next free ID: **HC-023** (confirmed against `report_HC-021.md` which already
  declared HC-022 as next free).

## 8. Quirks / pitfalls

- **Blue note ≠ fixed pitch.** Encoding ♭3/♭7 as exact 12-ET semitones flattens
  the blues to a pentatonic cliché. Human craft lives in the *microtonal bend* —
  model as a pitch-bend envelope, not a scale degree.
- **The "answer" is half the phrase.** AAB is not 4 bars of continuous melody:
  sing ~2 bars, rest ~2 bars, let an instrument speak. Sparse = conversational,
  not incomplete.
- **Turnaround = signature slot.** The I–IV–V grid is anonymous (predates all
  practitioners); bars-11–12 substitution is the individual signature. Keep
  mutable.
- **One-chord variant (John Lee Hooker).** The drone boogie drops IV/V; the AAB
  *lyric* structure, not the harmony, is the load-bearing wall.
- **Overlap.** HC-006 (Shout Chorus) = *arranging* the response across horn
  sections; HC-009 (Motivic) = *developing* a motive; this method is the
  *song-form root* (AAB lyric + blue-note melody + turnaround over I–IV–V).

## 9. Sources

- Wikipedia: *Twelve-bar blues*, *Blues*, *Blues scale* (accessed 2026-08-31)
- Kubik, Gerhard — *Africa and the Blues*
- Oliver, Paul — *The Story of the Blues*
- Wald, Elijah — *Escaping the Delta: Robert Johnson and the Invention of the Blues*
- B.B. King & David Ritz — *Blues All Around Me*
