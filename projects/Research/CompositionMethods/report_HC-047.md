# HC-047 Research Report: Barbershop Quartet Voicing & Overtone Ring Craft

- **Date**: 2026-09-26
- **Method ID**: HC-047
- **Layer**: human (→concrete)
- **Method Name**: Barbershop Quartet Voicing & Overtone Ring Craft (Lock-and-Ring Close Harmony)
- **Tradition / Culture**: African-American → American Barbershop Harmony — USA, ~1880s–present
- **Primary Elements**: HARMONY, PITCH, TEXTURE, STRUCTURE, RHYTHM

---

## 1. What It Is

Barbershop harmony is a uniquely American a cappella vocal craft in which four singers — **Tenor, Lead, Baritone, Bass** — perform a melody in close-position, predominantly homophonic four-part harmony. The defining craft goal is the **"ring"** (also called "lock" or "expanded sound"): an acoustic overtone phenomenon producing a phantom 5th voice audible above the quartet, generated when all four voices lock into just-intonation tuning on dominant seventh chords. The method governs how an arranger distributes chord tones across four voices to maximize overtone reinforcement, maintain voice-leading economy, and drive harmonic momentum through the circle of fifths.

Barbershop is **not** generic a cappella. It is a distinct compositional/arranging craft with specific rules about voicing spacing, chord density, voice-leading economy, and tuning that are different from both classical SATB and jazz vocal harmony. The melody sits in the **Lead** (2nd-highest part), not the top voice — a fundamental difference from most choral traditions.

---

## 2. Historical Roots & Practitioners

### Origins (1880s–1920s)
- African-American improvisational quartet singing in the Southern USA, especially New Orleans
- **"Woodshedding"**: singers learned the craft by ear, improvising three harmony parts around a melody in real time
- The style co-evolved with early jazz; the barbershop seventh (dominant 7th) and circle-of-fifths progressions mirror the harmonic language of ragtime and early jazz
- Earliest written use of "barbershop chord": 1910, "Mr. Jefferson Lord, Play That Barbershop Chord"

### Codification (1938–1970s)
- **SPEBSQSA** (Society for the Preservation and Encouragement of Barber Shop Quartet Singing in America) founded 1938, now **Barbershop Harmony Society**
- Contest system crystallized the voicing rules; the "ring" became the measurable quality criterion
- **The Mills Brothers** (1930s–40s): most commercially successful early quartet. "Paper Doll" (1943) — masterclass in lock-and-ring without microphones
- **The Dapper Dans** (Disneyland, 1960s–present): continuous performance tradition bridging old and new repertoire

### Modern practitioners
- **Vocal Majority** (Dallas, 1972–present): 150-voice chorus, multiple international gold medals; arrangements by Jim Clancy, Joe Connelly, Adam Scott
- **Gas House Gang** (St. Louis, 1986 gold medal): known for theatrical comedy and impeccable ring
- **Dr. David Wright**: definitive historian of barbershop's African-American origins
- **Adam Scott, Don Gray, Walter Latzko, Dave Stephens**: contemporary arranging pedagogues who codified the harmonic/voicing rules

---

## 3. The Craft Procedure (Step by Step)

### Phase 1 — Song Selection
1. Select a song with strong harmonic structure: dominant 7ths, tritones, circle-of-fifths progression (ii→V→I chains), memorable hook
2. Extract the melody — it will go to the **Lead** (2nd-highest part, comfortable mid-range), NOT the top voice

### Phase 2 — Harmonic Grid
3. Notate each beat's chord. The **barbershop seventh** (root–M3–P5–m7) must constitute ≥30% of chords for contest-appropriate work
4. Prioritize circle-of-fifths root movement — ≥70% of chord roots should move by descending 5th

### Phase 3 — Voicing Assignment
5. **Bass**: root or 5th (≥85% of beats). Large leaps normal. Avoid 1st/3rd inversion as default. Never allow "divorced bass" (>12th gap to next voice)
6. **Tenor** (falsetto, highest): sings above Lead, typically 5th, M3, or 7th of chord. Stepwise motion only. Simplest part
7. **Baritone**: fills the chord gap wherever Tenor and Bass don't cover. Moves above and below Lead. **Never doubles Lead** — most common beginner error
8. **Lead**: melody only. Chord tones below Lead provided by Bass/Baritone; above Lead by Tenor
9. Check completeness: every chord = 4 distinct pitch classes. No octave doubling (except final tonic)

### Phase 4 — Voice-Leading
10. Apply woodshedding rule: common-tone retention → stepwise motion when forced to move → only Bass leaps
11. Engineer **scissor moves**: contrary motion between Bass (ascending) and Tenor (descending) — the single most characteristic barbershop gesture
12. Apply **10th spacing target**: Tenor-to-Lead interval ≈10th; Lead-to-Bass ≈10th. This distributes harmonic-series partials evenly for maximum ring

### Phase 5 — The Tag
13. Compose the tag (4–16 bar coda appended after last chorus) — the concentrated craft element:
    - Circle-of-fifths chain (vi→ii→V→I or extended)
    - Rising register in all parts
    - Final dominant 7th with fermata (the ring target)
    - Hold the expanded sound → resolve to tonic

### Phase 6 — Tuning
14. Tune to just intonation:
    - Root: reference
    - M3: 5:4 ratio (−14¢ from equal temperament)
    - P5: 3:2 ratio (pure)
    - m7: 7:4 harmonic seventh (−31¢) or 16:9 (−5¢)
    - Equal temperament kills the ring — the phantom 5th vanishes

### Phase 7 — Form
15. Structure:
    - Pickup (4 bars, establish key, sparse chords)
    - Chorus 1 (16 bars, full melody plain)
    - Chorus 2 (16 bars, ornamented)
    - Release/Bridge (8–16 bars, subdominant lift, register rise)
    - Tag (4–16 bars, circle chain + fermata + resolution)

---

## 4. UnitMatrix Mapping (Musicom Engine Integration)

### Voices

| Voice | Name | Role | UnitMatrix Behavior |
|---|---|---|---|
| **Voice 0** | Bass (spine) | Roots & fifths, large leaps, harmonic anchor | Invariant harmonic floor. Cell = root/5th. Section-constant voice. |
| **Voice 1** | Lead (melody) | Primary tune, mid-range | Primary melodic spine. Cell = melody phrase fragments. Ornamentable per chorus pass. |
| **Voice 2** | Baritone (filler) | Gap-completion chord tone, crosses Lead | Variable-completion voice. Cell = chord set minus {Bass, Lead, Tenor}. Stepwise. |
| **Voice 3** | Tenor (top) | Falsetto above Lead, stepwise, simplest line | Top chord tone (5th/7th/M3). Minimal contour. |
| **Voice 4** | Ring target (validation) | Overtone composite — the phantom 5th | Not a sung voice. Validates partials 4–8 of fundamental reinforce. If below threshold, voicing fails ring test. |

### Sections

| Section | Bars | Function | Rules |
|---|---|---|---|
| S0—Pickup | 4 | Key establish, sparse 3-part | No full 7th yet |
| S1—Chorus 1 | 16 | Full melody, plain delivery | All 4 voices, circle grid |
| S2—Chorus 2 | 16 | Ornamented delivery | Baritone varies, Bass may walk |
| S3—Release | 8–16 | Subdominant lift | Register rises, broader spacing |
| S4—Tag | 4–16 | Circle chain + fermata + resolution | Rising register, dom7 fermata → I |

### Rules (implementable in Musicom engine)

1. **Voicing completeness**: 4 distinct pitch classes per chord, zero octave doubling (except final tonic)
2. **Bass-root default**: root/5th on ≥85% of beats
3. **No baritone-lead unison**: Baritone pitch ≠ Lead pitch at any point
4. **No divorced bass**: max gap Bass→Baritone ≤12th
5. **10th spacing target**: Tenor→Lead ≈10th, Lead→Bass ≈10th
6. **Just intonation tuning model**: M3 = 5:4, m7 = 7:4, P5 = 3:2
7. **Circle-of-fifths dominance**: ≥70% roots move by descending 5th
8. **Barbershop-7th density**: ≥30% of chords
9. **Common-tone retention**: hold pitch when chord allows
10. **Tag escalation**: monotonic register rise in all voices
11. **Stepwise tenor**: Tenor moves by diatonic step only
12. **A cappella only**: no instrumental doubling

---

## 5. Table Row Added

The following row was appended to the Human Composition Methods Framework table in `human_methods_db.md`:

```
| HC-047 | human (→concrete) | Barbershop Quartet Voicing & Overtone Ring Craft (Lock-and-Ring Close Harmony) | African-American → American Barbershop Harmony — USA, ~1880s–present; African-American improvisational quartet roots (New Orleans late 19th c.), codified SPEBSQSA 1938, Barbershop Harmony Society | HARMONY, PITCH, TEXTURE, STRUCTURE, RHYTHM | Select song with strong circle-of-fifths harmony → extract melody for Lead (2nd-highest part) → write harmonic grid (≥30% barbershop 7th chords) → assign 4-part close voicing (Bass=root/5th, Tenor=above Lead, Baritone=gap-fill no unison with Lead, Lead=melody) → apply woodshedding voice-leading (common-tone retention, stepwise motion, Bass leaps) → engineer scissor moves (contrary Bass/Tenor) → tune to just intonation for ring (M3=5:4 −14¢, m7=7:4 −31¢) → compose tag coda (circle chain ii→V→I, rising register, final dom7 fermata holding the expanded sound) → verify 10th-spacing target (Tenor→Lead ≈10th, Lead→Bass ≈10th) → no octave doubling, no instruments, a cappella only | Voice 0 = Bass spine (invariant root/5th floor, large leaps, harmonic anchor). Voice 1 = Lead melody (primary tune, mid-range, ornamentable per chorus pass). Voice 2 = Baritone filler (gap-completion chord tone, crosses Lead, never doubles V1). Voice 3 = Tenor top (falsetto, stepwise, highest chord tone 5th/7th/M3). Voice 4 = Ring target validation (overtone composite — partials 4–8 of fundamental must reinforce). Sections = S0_Pickup (4-bar key establish) → S1_Chorus_1 (16-bar full melody plain) → S2_Chorus_2 (16-bar ornamented) → S3_Release_Bridge (8–16-bar subdominant lift) → S4_Tag (4–16-bar circle chain + fermata + resolution). Rules: 4-distinct-pitch-class completeness, bass-root/5th ≥85%, no baritone-lead unison, no divorced bass (>12th gap), 10th-spacing target, just intonation tuning, circle-of-fifths dominance ≥70% root moves, barbershop-7th density ≥30%, common-tone retention, tag escalation monotonic register rise, stepwise tenor, a cappella only. | The Mills Brothers ("Paper Doll"), The Dapper Dans (Disneyland), Vocal Majority (Dallas, gold medal chorus), Gas House Gang (gold medal quartet), Dr. David Wright (barbershop historian/author), Adam Scott/Don Gray/Walter Latzko (arranging pedagogues) | ✅ Documented |
```

---

## 6. Verification

| Check | Result |
|---|---|
| Detail file exists | ✅ `human_method_HC-047_barbershop-quartet-voicing-ring.md` |
| Report file exists | ✅ `report_HC-047.md` |
| DB table contains HC-047 | ✅ Checked via grep |
| No duplicate HC-047 in DB | ✅ Verified (only 1 match) |
| Next free ID | ✅ **HC-048** |

---

## 7. Quirks & Pitfalls

- **The ring is fragile**: if any voice is even slightly out of just intonation (especially the m7), the phantom 5th overtone collapses. Quartets spend more rehearsal time tuning single chords than running songs.
- **Baritone-Lead doubling**: most common beginner arranging error — the ranges are similar and the same clef, so novices instinctively write the same pitch. This orphans a chord tone and kills the ring.
- **Divorced bass**: leaving the bass an octave+ from the next voice thins out the composite sound. The upper 3 voices may ring beautifully, but the bottom drops out.
- **Overused scissor**: the contrary Bass/Tenor gesture is characteristic but predictable if deployed every cadence.
- **Pitch drift**: without instrumental reference, a cappella groups drift flat, especially on the held dom7 in the tag. Professional quartets internally calibrate to just intonation so the final V→I stays on pitch.
- **Repertoire limitation**: the style requires strong circle-of-fifths harmony. Modal, free-jazz, or atonal material cannot be "barbershop-ified" without losing the identity of the form.
- **Ring expectation**: the phantom 5th is most audible on dominant 7th chords. On passing chords (dim7, minor 7th flat 5) it doesn't ring — the arrangement must strategically place ring-target chords on structural beats only.

---

## 8. Files Created

| File | Path |
|---|---|
| Detail file (full documentation) | `/opt/data/projects/Research/CompositionMethods/human_method_HC-047_barbershop-quartet-voicing-ring.md` |
| Report file (this document) | `/opt/data/projects/Research/CompositionMethods/report_HC-047.md` |
| Database update | `/opt/data/projects/Research/CompositionMethods/human_methods_db.md` (row appended) |