# Report — HC-028: Jazz Chord-Scale Improvisation & Comping Craft (Bebop/Hard-Bop)

**Date:** 2026-09-06 (nightly `daily-human-composition-research` job)
**Layer:** `concrete` (target when implemented)
**Tradition:** African-American jazz — bebop → hard-bop → post-bop (USA, ~1940s–present)

---

## 1. Method name & tradition

**Jazz Chord-Scale Improvisation & Comping Craft (Bebop/Hard-Bop).** A human-craft
method covering how a working jazz player actually improvises a solo and comps over
a standard: guide-tone lattice, chord-scale mapping, target-note line construction,
chromatic ornamentation, motivic development, and swing time-feel. Standardized from
bebop practice (Parker, Powell, Gillespie) into conservatory pedagogy (George Russell's
*Lydian Chromatic Concept* 1953, Barry Harris, David Baker, Jerry Coker, Mark Levine).

This fills the Jazz gap in the human-methods index: HC-006 covered *arranging*
(big-band shout chorus); HC-028 covers the *in-the-moment* improvisation/comping craft.

## 2. Craft procedure (in detail)

1. **Learn the standard & the form.** Memorize 32-bar AABA / 12-bar blues; sing the
   head so the tune is in the ear, not just on the chart.
2. **Build the guide-tone lattice.** Write the 3rd & 7th of every chord as a two-note
   line. Voice-lead them: on ii–V–I (Dm7–G7–Cmaj7): C→B (7→3), F→E (3→7), F→E
   (7→3 of V). This lattice is the skeleton the whole solo hangs on.
3. **Map chords to chord-scales.** Scale choice resolved against the key: ii7→dorian,
   V7→mixolydian/altered, Imaj7→ionian/lydian. Identify **avoid notes** (4th over
   maj7 = half-step clash with 3rd) vs. guide/color tones.
4. **Practice target-note lines.** Slow tempo: only guide tones (7→3 across each
   change), then chord tones, then connect targets with scale runs. Chord tones on
   strong beats, the rest passing.
5. **Add chromatic ornamentation.** Chromatic approach (half-step below/above target),
   enclosure (upper+lower neighbor before target), passing tones between chord tones.
6. **Develop motivic material.** Short cell (2–6 notes) sequenced/displaced/varied;
   solo arcs sparse→dense, low→high, motif→answer.
7. **Keep swing/time-feel.** Swung 8ths, breath phrasing (rests, ahead/behind beat),
   ride cymbal + 2&4 backbeat constant.
8. **Comp.** (parallel craft) Rootless 3/4-note voicings (3rd+7th+extensions, no root),
   voice-led 7→3 each change, sparse off-beat placement, leave space for soloist.

## 3. Practitioner examples

- **Charlie Parker** — "Koko", "Confirmation": chromatic enclosure + bebop scale over
  rhythm changes; the archetypal chord-tone-targeted, chromatically-decorated line.
- **Bud Powell** — "Bouncing with Bud": rootless LH comping + single-note bebop lines.
- **Dizzy Gillespie** — "A Night in Tunisia": altered dominant / II–V–I lattice exposed.
- **Miles Davis** — "So What" (Kind of Blue, 1959): modal chord-scale, one scale per 8 bars.
- **John Coltrane** — "Giant Steps": guide-tone lattice over major-3rd key cycles;
  later "sheets of sound" = stacked chord-tone arpeggiation.
- **Bill Evans** — rootless voicings + 7→3 voice-leading = modern comping standard.
- **George Russell** — *Lydian Chromatic Concept* (1953): systematized chord-scale mapping.
- **Barry Harris** — 6th-diminished scale = formalized chromatic decoration of chord tones.
- **Mark Levine / Jerry Coker / David Baker** — codified chord-scale + guide-tone pedagogy.

## 4. UnitMatrix mapping

- **Voice 0 = harmonic spine** (bass/rootless comping): invariant guide-tone lattice;
  the reference other voices target. PITCH anchor = 3rd/7th per chord.
- **Voice 1 = solo line** (horn/piano RH): improvised melody; chord/guide tones on
  strong beats, scale/approach motion between.
- **Voice 2 = comping chordal layer** (piano/guitar): rootless voicings, voice-led
  7→3, short off-beat stabs.
- **Voice 3 = time/ride groove** (drums): invariant swing; ride + 2&4 backbeat = the clock.

**Sections:** Head (A) → Solos (B, frozen changes over multiple choruses) → Fours
(trading w/ drums) → Head out (A').

**Rules to encode:**
- Guide-tone invariance (Voice 0 anchors 3rd/7th; Voice 1 lands a target each chord boundary).
- Chord-scale palette (note ∈ scale(chord,key); consonant→strong beat, passing→weak).
- Avoid-note guard (4th over maj7).
- 7→3 / 3→7 voice-leading on ii–V–I.
- Strong-beat target rule + chromatic half-step resolution.
- Swing feel (8th ≈ triplet 2:1), ride invariance, backbeat 2&4.
- Monotonic solo development (sparse→dense, low→high, motivic cell).
- Comping space rule (Voice 2 off-beat/short, never collides with Voice 1).

## 5. Table row added

| HC-028 | human (→concrete) | Jazz Chord-Scale Improvisation & Comping (Bebop/Hard-Bop) | African-American jazz — bebop → hard-bop → post-bop (USA, ~1940s–present) | PITCH, HARMONY, RHYTHM, STRUCTURE, TEXTURE | Learn form & head → build guide-tone lattice (3rd/7th per chord, 7→3 voice-leading) → map chord-scales (avoid vs color tones) → practice target-note lines (chord tones on strong beats) → add chromatic approach/enclosure/passing decoration → develop motivic cells (sequence/vary) → keep swing feel + ride/backbeat constant → comp with rootless voice-led voicings | Voice 0 = harmonic spine (bass/rootless comping = invariant guide-tone lattice). Voice 1 = solo line (target notes on strong beats, decoration between, motivic development arc). Voice 2 = comping chordal layer (rootless voicings, 7→3 voice-led, off-beat). Voice 3 = swing/ride groove (invariant backbeat clock). Sections = Head → Solos (frozen changes, multi-chorus arc) → Fours → Head out. Rules: guide-tone invariance, chord-scale palette, avoid-note guard, 7→3/3→7 cadence voice-leading, strong-beat target, chromatic half-step resolution, swing feel, monotonic development arc, comping space | Charlie Parker (Koko, Confirmation), Bud Powell (Bouncing with Bud), Dizzy Gillespie (A Night in Tunisia), Miles Davis (So What), John Coltrane (Giant Steps, sheets of sound), Bill Evans (Waltz for Debby), George Russell (Lydian Chromatic Concept), Barry Harris (6th-dim scale), Mark Levine/Jerry Coker/David Baker (pedagogy) | ✅ Documented |

## 6. Next free ID

**HC-029**

## 7. Quirks / pitfalls

- **Avoid-note trap**: mapping a single chord-scale without reconciling it against the
  *surrounding key* produces wrong avoid notes (e.g. the natural 4th over maj7 needs
  guard, but lydian #4 is fine). Rule must resolve scale against key, not chord alone.
- **Guide-tone vs. color-tone weighting**: 3rd/7th are the harmonic identity; extensions
  (9/11/13) are decoration. Encoding must weight guide tones strongest at chord boundaries,
  else harmony drifts.
- **Swung 8th is a *feel*, not a fixed ratio**: ≈ 2:1 triplet at slow-mid tempo, straightens
  at fast tempo. A fixed quantization grid misses bebop feel.
- **Solo arc is across *choruses*, not bars**: development happens over multiple 32-bar form
  loops; a per-chorus density ramp is the wrong granularity.
- **Distinct from HC-006**: arranging (fixed written part) vs. improvised in-the-moment line.
  Do not merge.